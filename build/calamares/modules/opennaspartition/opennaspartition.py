#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
OpenNAS-Lite Calamares job module (skeleton).

Exec phase: seed nasd config on target and install profile-specific packages.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import libcalamares

try:
    import yaml
except ImportError:
    yaml = None


def _config() -> dict:
    return libcalamares.Job.configuration() or {}


def _run_hw_check() -> dict:
    try:
        out = subprocess.check_output(["/usr/local/sbin/opennas-hw-check"], text=True)
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return {"ram_mb": 0, "virtualization": 0, "recommended_profile": "standard"}


def _load_profile_yaml(name: str, profiles_path: str) -> dict:
    path = Path(profiles_path) / f"{name}.yaml"
    if not path.is_file():
        return {"name": name, "missing": True}
    if yaml is None:
        return {"name": name, "path": str(path), "yaml_unavailable": True}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    data.setdefault("name", name)
    return data


def _install_profile_packages(root_mount: str, profile: dict) -> None:
    extra = profile.get("packages_extra") or []
    if not extra:
        return
    cmd = ["chroot", root_mount, "apt-get", "install", "-y", "--no-install-recommends"] + list(extra)
    libcalamares.utils.debug(f"opennaspartition: installing profile packages: {extra}")
    subprocess.check_call(cmd)


def run():
    cfg = _config()
    profiles_path = cfg.get("profilesPath", "/usr/share/opennas/profiles")
    seed_src = cfg.get("seedConfigPath", "/usr/share/opennas/nasd/config.seed.json")
    default_profile = cfg.get("defaultProfile", "standard")

    hw = _run_hw_check()
    recommended = hw.get("recommended_profile", default_profile)
    chosen = libcalamares.GlobalStorage.value("opennasProfile") or recommended

    profile_data = _load_profile_yaml(chosen, profiles_path)

    libcalamares.GlobalStorage.set("opennasProfile", chosen)
    libcalamares.GlobalStorage.set("opennasHwCheck", hw)
    libcalamares.GlobalStorage.set("opennasProfileMeta", profile_data)

    libcalamares.utils.debug(f"opennaspartition: profile={chosen} hw={hw}")

    root_mount = libcalamares.GlobalStorage.value("rootMountPoint")
    if not root_mount:
        return None

    target_nasd = Path(root_mount) / "var/lib/nasd"
    target_nasd.mkdir(parents=True, exist_ok=True)

    seed_dst = target_nasd / "config.seed.json"
    src = Path(seed_src)
    seed_obj = {}
    if src.is_file():
        seed_obj = json.loads(src.read_text(encoding="utf-8"))
    seed_obj.setdefault("schema_version", 1)
    seed_obj["opennas_profile"] = chosen
    seed_obj["setup_complete"] = False
    flags = profile_data.get("feature_flags") or {}
    seed_obj["feature_flags"] = {**seed_obj.get("feature_flags", {}), **flags}
    seed_dst.write_text(json.dumps(seed_obj, indent=2) + "\n", encoding="utf-8")

    profile_install = Path(root_mount) / "usr/share/opennas/profiles"
    profile_install.mkdir(parents=True, exist_ok=True)
    src_profiles = Path(profiles_path)
    if src_profiles.is_dir():
        for item in src_profiles.glob("*.yaml"):
            shutil.copy2(item, profile_install / item.name)

    flags_path = target_nasd / "install-profile.json"
    flags_path.write_text(
        json.dumps(
            {
                "profile": chosen,
                "hw_check": hw,
                "default_filesystem": cfg.get("defaultFilesystem", "btrfs"),
                "zfs_allowed": bool(cfg.get("allowZfs", False)),
                "profile_data": profile_data,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    ram_min = profile_data.get("ram_mb_minimum")
    if ram_min and hw.get("ram_mb", 0) < ram_min:
        libcalamares.utils.warning(
            f"RAM {hw.get('ram_mb')} MiB is below profile minimum {ram_min} MiB for '{chosen}'."
        )

    try:
        _install_profile_packages(root_mount, profile_data)
    except subprocess.CalledProcessError as exc:
        return ("error", f"Profile package install failed: {exc}")

    return None
