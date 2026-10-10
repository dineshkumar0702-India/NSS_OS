import argparse

import uvicorn

from nasd.app import create_app
from nasd.settings import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenNAS-Lite nasd")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.run_dir.mkdir(parents=True, exist_ok=True)
    app = create_app()

    if settings.unix_socket is not None:
        socket_path = settings.unix_socket
        if socket_path.exists():
            socket_path.unlink()
        config = uvicorn.Config(app, uds=str(socket_path), log_level="info", reload=args.reload)
        server = uvicorn.Server(config)
        server.run()
        return

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
