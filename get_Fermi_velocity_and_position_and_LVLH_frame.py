"""Legacy example; use satellite-coordinates for other satellites or times."""
from iss_coords.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main(["Fermi", "2009-12-14T11:53:27.830000Z"]))
