#!/usr/bin/env python3
"""The temporary folder of a card: /tmp/pirca-<CARD-ID>.

Everything temporary that the agents create for a card (generated projects, copies for a control,
a Maven local repository for a test) lives inside it, so one command removes it all.

Usage:
  card_tmp.py create <CARD>   # make the folder (the orchestrator does it at intake)
  card_tmp.py clean  <CARD>   # remove it and everything inside (the orchestrator does it at delivery)

It only touches a folder named exactly /tmp/pirca-<CARD>, where <CARD> looks like ARQ-12.
"""
import os
import re
import shutil
import sys

CARD = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]+$")
BASE = "/tmp"


def folder(card: str) -> str:
    if not CARD.match(card):
        sys.exit(f"card_tmp: '{card}' is not a card id such as ARQ-12")
    return os.path.join(BASE, f"pirca-{card}")


def size_of(path: str) -> tuple[int, int]:
    files = total = 0
    for root, _, names in os.walk(path):
        for name in names:
            try:
                total += os.lstat(os.path.join(root, name)).st_size
                files += 1
            except OSError:
                pass
    return files, total


def create(card: str) -> None:
    path = folder(card)
    os.makedirs(path, exist_ok=True)
    print(path)


def clean(card: str) -> None:
    path = folder(card)
    if not os.path.lexists(path):
        print(f"nothing to remove: {path} does not exist")
        return
    if os.path.islink(path) or not os.path.isdir(path):
        sys.exit(f"card_tmp: {path} is not a plain folder; not touching it")
    files, total = size_of(path)
    failed = []
    shutil.rmtree(path, onerror=lambda _f, p, _e: failed.append(p))
    if failed or os.path.exists(path):
        sys.exit(f"card_tmp: could not remove {len(failed)} path(s) under {path}, e.g. {failed[:3]}")
    print(f"removed {path} ({files} files, {total / 1_000_000:.1f} MB)")


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ("create", "clean"):
        sys.exit(__doc__)
    {"create": create, "clean": clean}[sys.argv[1]](sys.argv[2])


if __name__ == "__main__":
    main()
