import json
from pathlib import Path

from nasd.settings import settings


def discover_catalog() -> list[dict]:
    root = settings.apps_dir
    if not root.is_dir():
        return []
    items: list[dict] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        meta_path = child / "METADATA.json"
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        meta.setdefault("id", child.name)
        meta["template_id"] = child.name
        meta["compose_path"] = str(child / "compose.yaml")
        items.append(meta)
    return items


def get_template(template_id: str) -> dict | None:
    for item in discover_catalog():
        if item.get("id") == template_id or item.get("template_id") == template_id:
            return item
    return None


def template_compose_path(template_id: str) -> Path | None:
    path = settings.apps_dir / template_id / "compose.yaml"
    return path if path.is_file() else None
