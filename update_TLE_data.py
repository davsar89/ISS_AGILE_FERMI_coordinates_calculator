"""Compatibility entry point; credentials remain beside this script."""
from pathlib import Path
from iss_coords.download import atomic_write, main, update

if __name__ == "__main__":
    raise SystemExit(main(default_env=Path(__file__).resolve().parent / ".env"))
