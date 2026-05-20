from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.sqlalchemy_database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def ensure_database_exists() -> None:
    database_url = make_url(settings.sqlalchemy_database_url)

    if database_url.get_backend_name() != "postgresql":
        return

    database_name = database_url.database
    if not database_name:
        return

    if _database_exists(database_url):
        return

    if not settings.auto_create_database:
        raise RuntimeError(
            f"PostgreSQL database '{database_name}' does not exist. "
            "Create it manually or enable AUTO_CREATE_DATABASE."
        )

    _create_database(database_url, database_name)


def _database_exists(database_url: URL) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except OperationalError as exc:
        if _is_missing_database_error(exc):
            return False
        raise RuntimeError(_connection_help_message(database_url, exc)) from exc


def _create_database(database_url: URL, database_name: str) -> None:
    admin_url = database_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", echo=False)

    try:
        with admin_engine.connect() as connection:
            existing = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name},
            ).scalar_one_or_none()

            if existing:
                return

            quoted_database_name = admin_engine.dialect.identifier_preparer.quote(database_name)
            connection.exec_driver_sql(f"CREATE DATABASE {quoted_database_name}")
    except OperationalError as exc:
        raise RuntimeError(_connection_help_message(database_url, exc)) from exc
    finally:
        admin_engine.dispose()


def _is_missing_database_error(exc: OperationalError) -> bool:
    message = str(exc).lower()
    return "does not exist" in message and "database" in message


def _connection_help_message(database_url: URL, exc: OperationalError) -> str:
    return (
        f"Unable to connect to PostgreSQL at {database_url.host}:{database_url.port} for database "
        f"'{database_url.database}'. Ensure the server is running and the credentials in .env are correct. "
        f"Original error: {exc}"
    )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()