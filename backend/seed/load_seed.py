#!/usr/bin/env python3
"""One-off script: load catalog demo data from JSON into PostgreSQL."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

SEED_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = SEED_ROOT.parent
sys.path.insert(0, str(SEED_ROOT))

from loader import SeedLoader, SeedLoadError  # noqa: E402

DEFAULT_SEED_FILE = SEED_ROOT / "data" / "seed.json"


def _resolve_database_url(explicit_url: str | None) -> str:
    if explicit_url:
        return explicit_url

    load_dotenv(BACKEND_ROOT / ".env")

    url = os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL")
    if not url:
        raise SeedLoadError(
            "Set DATABASE_URL_SYNC or DATABASE_URL in backend/.env, "
            "or pass --database-url."
        )

    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return url


@click.command()
@click.option(
    "--file",
    "seed_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    default=DEFAULT_SEED_FILE,
    show_default=True,
    help="Path to seed JSON file.",
)
@click.option(
    "--database-url",
    default=None,
    help="PostgreSQL URL (sync). Defaults to DATABASE_URL_SYNC from .env.",
)
def main(seed_file: Path, database_url: str | None) -> None:
    """Reset and load customers, products, warehouses, and inventory from JSON."""
    try:
        url = _resolve_database_url(database_url)
        result = SeedLoader(url).load_from_file(seed_file)
    except SeedLoadError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"seed failed: {exc}") from exc

    click.echo(
        "Seed complete: "
        f"1 customer, {result.product_count} products, "
        f"{result.warehouse_count} warehouses, {result.inventory_count} inventory rows"
    )
    click.echo(f"Default customer_id: {result.customer_id} ({result.customer_email})")
    click.echo(
        "Use customer_id=1 for POST /orders. "
        "Example product_ids: 1, 9, 14 (order in data/seed.json)."
    )


if __name__ == "__main__":
    main()
