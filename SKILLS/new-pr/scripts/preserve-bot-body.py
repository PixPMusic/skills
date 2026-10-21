#!/usr/bin/env python3
"""Replace the authored PR-body prefix while preserving bot-managed blocks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


MARKERS = (
    "<!-- CURSOR_SUMMARY -->",
    "<!-- Macroscope's pull request summary starts here -->",
)


def preserved_suffix(current: str) -> str:
    positions = [current.find(marker) for marker in MARKERS]
    starts = [position for position in positions if position >= 0]
    return current[min(starts) :] if starts else ""


def merge_body(current: str, authored: str) -> str:
    prefix = authored.rstrip()
    suffix = preserved_suffix(current)
    if not suffix:
        return f"{prefix}\n"
    return f"{prefix}\n\n{suffix}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--authored", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = merge_body(
        args.current.read_text(),
        args.authored.read_text(),
    )
    if args.output:
        args.output.write_text(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
