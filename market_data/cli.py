import argparse
import json
import sys
from collections.abc import Iterable
from typing import TextIO

from .application import MarketDataApplication
from .clock import ManualClock, SystemClock
from .config import load_json, load_settings
from .transport import dispatch


def run_lines(lines: Iterable[str], output: TextIO, app: MarketDataApplication) -> None:
    for line in lines:
        if not line.strip():
            continue
        try:
            command = json.loads(line)
            if isinstance(command, dict) and command.get("op") == "clock_set":
                if not isinstance(app.clock, ManualClock):
                    raise ValueError("clock_set requires manual clock mode")
                app.clock.set(command.get("now_ms"))
                result = {"now_ms": app.clock.now_ms()}
            else:
                result = dispatch(app, command)
        except (json.JSONDecodeError, ValueError) as exc:
            result = {"error": str(exc)}
        output.write(json.dumps(result, separators=(",", ":")) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Market-data watchlist snapshot service")
    parser.add_argument("--input")
    parser.add_argument("--catalog", default="config/instruments.json")
    parser.add_argument("--settings", default="config/settings.json")
    parser.add_argument("--clock", choices=("system", "manual"), default="system")
    parser.add_argument("--start-ms", type=int, default=0)
    args = parser.parse_args(argv)
    clock = ManualClock(args.start_ms) if args.clock == "manual" else SystemClock()
    app = MarketDataApplication(load_json(args.catalog), load_settings(args.settings), clock)
    if args.input:
        with open(args.input, encoding="utf-8") as source:
            run_lines(source, sys.stdout, app)
    else:
        run_lines(sys.stdin, sys.stdout, app)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
