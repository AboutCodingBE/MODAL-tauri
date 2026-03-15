#!/usr/bin/env python3
"""
Discovers all feature entry points (python/<feature>/main.py) and bundles
each into a standalone executable using PyInstaller.

New features are picked up automatically — no changes to this script needed.

Run from the python/ directory:
    python bundle.py

Output executables are placed in python/dist/.
"""
import subprocess
import sys
from pathlib import Path


def main() -> None:
    python_dir = Path(__file__).parent
    entry_points = sorted(python_dir.glob("*/main.py"))

    if not entry_points:
        print("No feature entry points found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(entry_points)} entry point(s):")
    for ep in entry_points:
        print(f"  {ep.relative_to(python_dir)}")

    for entry in entry_points:
        feature = entry.parent.name
        print(f"\nBundling '{feature}'...")
        subprocess.run(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name", feature,
                "--paths", str(python_dir),
                "--hidden-import", "logging.config",
                "--hidden-import", "alembic",
                "--hidden-import", "sqlalchemy",
                "--collect-all", "shared",
                "--distpath", str(python_dir / "dist"),
                "--workpath", str(python_dir / "build" / feature),
                "--specpath", str(python_dir / "build" / feature),
                str(entry),
            ],
            check=True,
        )
        print(f"  -> dist/{feature}")

    print(f"\nAll {len(entry_points)} features bundled successfully.")


if __name__ == "__main__":
    main()
