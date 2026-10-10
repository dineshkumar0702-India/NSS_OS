import json
import subprocess


def list_interfaces() -> list[dict]:
    if _which("ip"):
        try:
            out = subprocess.check_output(["ip", "-j", "link", "show"], text=True)
            links = json.loads(out)
            addrs_out = subprocess.check_output(["ip", "-j", "addr", "show"], text=True)
            addrs = json.loads(addrs_out)
            addr_map: dict[str, list] = {}
            for iface in addrs:
                addr_map[iface.get("ifname", "")] = iface.get("addr_info", [])
            items = []
            for link in links:
                name = link.get("ifname")
                if not name or name == "lo":
                    continue
                items.append(
                    {
                        "name": name,
                        "state": link.get("operstate", "unknown").lower(),
                        "mac": link.get("address"),
                        "addresses": addr_map.get(name, []),
                    }
                )
            return items
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
    return []


def _which(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None
