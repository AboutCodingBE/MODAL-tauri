# python/run_migrations/main.py
import sys
import os
from alembic.config import Config
from alembic import command
from pathlib import Path

def run_migrations(python_dir: str = None):
    """Run all pending database migrations"""
    try:
        # Use provided directory or fall back to dev location
        if python_dir:
            # Production: use passed directory
            base_dir = Path(python_dir)
        else:
            # Development: use script location
            base_dir = Path(__file__).parent.parent

        alembic_ini = base_dir / "alembic.ini"
        migrations_dir = base_dir / "migrations"

        if not alembic_ini.exists():
            return {
                "status": "error",
                "message": f"alembic.ini not found at {alembic_ini}"
            }

        if not migrations_dir.exists():
            return {
                "status": "error",
                "message": f"migrations/ not found at {migrations_dir}"
            }

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))
        alembic_cfg.set_main_option("script_location", str(migrations_dir))

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        return {
            "status": "success",
            "message": "Database migrations completed successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Migration failed: {str(e)}"
        }

if __name__ == "__main__":
    import json

    # Get python directory from arguments if provided
    python_dir = sys.argv[1] if len(sys.argv) > 1 else None

    result = run_migrations(python_dir)
    print(json.dumps(result))
    sys.exit(0 if result["status"] == "success" else 1)