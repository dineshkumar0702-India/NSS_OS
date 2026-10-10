import json
import subprocess
from pathlib import Path


def list_block_devices() -> list[dict]:
    if _command_exists("lsblk"):
        try:
            out = subprocess.check_output(
                ["lsblk", "-J", "-b", "-o", "NAME,PATH,SIZE,TYPE,MODEL,SERIAL"],
                text=True,
            )
            data = json.loads(out)
            items: list[dict] = []
            for dev in data.get("blockdevices", []):
                if dev.get("type") != "disk":
                    continue
                items.append(
                    {
                        "path": dev.get("path") or f"/dev/{dev.get('name')}",
                        "size_bytes": int(dev.get("size") or 0),
                        "model": (dev.get("model") or "").strip() or None,
                        "serial": (dev.get("serial") or "").strip() or None,
                        "smart_status": None,
                    }
                )
            return items
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass

    items = []
    block = Path("/sys/block")
    if not block.is_dir():
        return items
    for name in sorted(block.iterdir()):
        if name.name.startswith("loop"):
            continue
        size_path = name / "size"
        size_bytes = 0
        if size_path.is_file():
            size_bytes = int(size_path.read_text().strip()) * 512
        items.append(
            {
                "path": f"/dev/{name.name}",
                "size_bytes": size_bytes,
                "model": None,
                "serial": None,
                "smart_status": None,
            }
        )
    return items


def device_exists(path: str) -> bool:
    return Path(path).exists()


def _command_exists(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None
