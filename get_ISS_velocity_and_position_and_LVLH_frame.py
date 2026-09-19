"""Legacy example; use satellite-coordinates for other satellites or times."""
from iss_coords.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main(["ISS", "2019-03-24T00:31:53.135444Z"]))
