# python/run_migrations/main.py
import sys
from alembic.config import Config
from alembic import command
from pathlib import Path

def run_migrations():
    """Run all pending database migrations"""
    try:
        # Get alembic.ini path
        alembic_ini = Path(__file__).parent.parent / "alembic.ini"

        if not alembic_ini.exists():
            return {
                "status": "error",
                "message": f"alembic.ini not found at {alembic_ini}"
            }

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))

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
    result = run_migrations()
    print(json.dumps(result))
    sys.exit(0 if result["status"] == "success" else 1)