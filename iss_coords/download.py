"""Update Space-Track TLEs while retaining the local historical archive."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

from dotenv import load_dotenv
from spacetrack import SpaceTrackClient

from .tle_data import DATA_DIR, SATELLITES, parse_tles, tle_epoch


def atomic_write(path, text):
    """A failed download/write must not destroy the previous archive."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", newline="\n",
                                     dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def update(client, data_dir=DATA_DIR, history=False):
    data_dir.mkdir(parents=True, exist_ok=True)
    marker = data_dir / "last_update_TLE.json"
    now = datetime.now(timezone.utc)
    state = json.loads(marker.read_text()) if marker.exists() else {}
    last = state.get("history" if history else "latest")
    if last and now - datetime.fromisoformat(last) < timedelta(hours=1):
        print("Already checked within the last hour; using cached TLEs.")
        return

    # Fetch latest once for all objects; empty results for decayed objects are normal.
    latest = parse_tles(client.gp(norad_cat_id=[v[0] for v in SATELLITES.values()], format="tle"))
    expected = {str(v[0]) for v in SATELLITES.values()}
    if any(pair[0][2:7] not in expected for pair in latest):
        raise ValueError("Unexpected satellite in Space-Track response")
    for name, (norad, filename) in SATELLITES.items():
        path = data_dir / filename
        old = parse_tles(path.read_text(), norad) if path.exists() else []
        new = [pair for pair in latest if int(pair[0][2:7]) == norad]
        if old:
            state.setdefault("history_epochs", {}).setdefault(
                name, max(tle_epoch(pair[0]) for pair in old).isoformat())
        if history:
            # Epoch checkpoint is separate from the latest-only update so that a
            # later history update still fills gaps. Daily overlap avoids rounding.
            checkpoint = state.get("history_epochs", {}).get(name)
            query = dict(norad_cat_id=norad, orderby="epoch asc", format="tle")
            if checkpoint:
                query["epoch"] = ">" + datetime.fromisoformat(checkpoint).date().isoformat()
            new += parse_tles(client.gp_history(**query), norad)
        if not new and name != "AGILE":
            raise ValueError(f"No current TLE returned for {name}; existing archive retained")
        merged = sorted(set(old + new), key=lambda pair: (tle_epoch(pair[0]), pair))
        if not merged:
            raise ValueError(f"No TLEs available for {name}")
        atomic_write(path, "".join(first + "\n" + second + "\n" for first, second in merged))
        epoch = tle_epoch(merged[-1][0]).isoformat()
        print(f"{name}: {len(merged)} records (+{len(merged)-len(set(old))}); latest epoch {epoch}")
        if history:
            state.setdefault("history_epochs", {})[name] = epoch
        # Retain history checkpoints even if a later satellite fails during a
        # latest-only update; otherwise its newly appended epoch could hide gaps.
        atomic_write(marker, json.dumps(state, indent=2) + "\n")
    state["latest"] = now.isoformat()
    if history:
        state["history"] = now.isoformat()
    atomic_write(marker, json.dumps(state, indent=2) + "\n")


def main(argv=None, *, default_env=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true", help="Also fill missing history since the saved archive epoch")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Directory containing the TLE archives")
    parser.add_argument("--env-file", type=Path, default=default_env or Path.cwd() / ".env")
    args = parser.parse_args(argv)
    load_dotenv(args.env_file, interpolate=False)
    username = os.getenv("SPACETRACK_USERNAME")
    password = os.getenv("SPACETRACK_PASSWORD")
    if not username or not password:
        parser.error("Set SPACETRACK_USERNAME and SPACETRACK_PASSWORD in .env (see .env.example)")
    try:
        with SpaceTrackClient(identity=username, password=password) as client:
            update(client, data_dir=args.data_dir, history=args.history)
    except Exception as exc:
        # Third-party errors may contain request details; never echo credentials.
        print(f"TLE update failed ({type(exc).__name__}); check credentials/network and archive validity.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
