#!/usr/bin/env python3
"""nasctl — OpenNAS-Lite management CLI."""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

DEFAULT_URL = os.environ.get("NASD_URL", "http://127.0.0.1:8741")


def _client() -> httpx.Client:
    token = os.environ.get("NASD_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    cred = Path.home() / ".config" / "nasctl" / "credentials"
    if not token and cred.is_file():
        for line in cred.read_text(encoding="utf-8").splitlines():
            if line.startswith("token="):
                headers["Authorization"] = f"Bearer {line.split('=', 1)[1].strip()}"
    return httpx.Client(base_url=DEFAULT_URL, headers=headers, timeout=30.0)


def cmd_status(_args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.get("/api/v1/system/status")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def cmd_capabilities(_args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.get("/api/v1/system/capabilities")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def cmd_login(args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.post("/api/v1/auth/login", json={"username": args.username, "password": args.password})
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def cmd_updates(_args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.get("/api/v1/updates/status")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def cmd_advisor(_args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.get("/api/v1/security/advisor")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def cmd_disks(_args: argparse.Namespace) -> int:
    with _client() as c:
        r = c.get("/api/v1/storage/disks")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="nasctl")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="System status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("capabilities", help="Hardware capabilities")
    p.set_defaults(func=cmd_capabilities)

    p = sub.add_parser("login", help="Login (session cookie stored by httpx)")
    p.add_argument("username")
    p.add_argument("password")
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("disks", help="List disks")
    p.set_defaults(func=cmd_disks)

    p = sub.add_parser("updates", help="OTA update status")
    p.set_defaults(func=cmd_updates)

    p = sub.add_parser("advisor", help="Security advisor")
    p.set_defaults(func=cmd_advisor)

    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except httpx.HTTPStatusError as exc:
        print(exc.response.text, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
