from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session as OrmSession, sessionmaker

from nasd.settings import settings


class Base(DeclarativeBase):
    pass


engine: Engine | None = None
_session_factory: sessionmaker[OrmSession] | None = None


def configure_engine() -> None:
    global engine, _session_factory
    if engine is not None:
        engine.dispose()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{settings.db_path}",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    _session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session_factory() -> sessionmaker[OrmSession]:
    if _session_factory is None:
        configure_engine()
    assert _session_factory is not None
    return _session_factory


def get_db() -> Generator[OrmSession, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from nasd import models  # noqa: F401

    configure_engine()
    assert engine is not None
    Base.metadata.create_all(bind=engine)
    with get_session_factory()() as session:
        from nasd.models import SystemConfig, _utcnow

        if session.get(SystemConfig, "schema_version") is None:
            session.add(
                SystemConfig(
                    key="schema_version",
                    value_json="1",
                    updated_at=_utcnow(),
                )
            )
            session.commit()


class _SessionLocal:
    """Callable matching ``sessionmaker()`` usage in tests."""

    def __call__(self) -> OrmSession:
        return get_session_factory()()


SessionLocal = _SessionLocal()
