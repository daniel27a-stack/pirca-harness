#!/usr/bin/env python3
"""pirca board operations. Today backed by Trello (the `trello` CLI); nothing outside this file
knows that. Board and list ids live in ../board.json.

Usage:
  board.py find     <CARD-ID>                         # JSON: id, name, list, url
  board.py snapshot <CARD-ID> <OUT.md>                # write the card as markdown
  board.py move     <CARD-ID> <LIST>                  # LIST: decisiones|backlog|en-curso|en-revision|hecho
  board.py comment  <CARD-ID> (--text TEXT | --file PATH)

Long texts are split into several comments: the Trello API rejects long requests (HTTP 414),
which is why descriptions are never rewritten with long content.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parent.parent / "board.json").read_text(encoding="utf-8"))
LIST_NAMES = {v: k for k, v in CONFIG["lists"].items()}


def trello(*args) -> object:
    out = subprocess.run(["trello", *args], capture_output=True, text=True)
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        sys.exit(f"board: unexpected output from trello: {out.stdout or out.stderr}")
    if not data.get("ok"):
        sys.exit(f"board: {data.get('error')}")
    return data["data"]


def find(card_id: str) -> dict:
    prefix = f"{card_id} ·"
    matches = [c for c in trello("cards", "list", "--board", CONFIG["board"]["id"]) if c["name"].startswith(prefix)]
    if len(matches) != 1:
        sys.exit(f"board: expected exactly one card named '{prefix} ...', found {len(matches)}")
    card = trello("cards", "get", "--card", matches[0]["id"])
    return {"id": card["id"], "name": card["name"], "list": LIST_NAMES.get(card["idList"], card["idList"]),
            "url": card.get("url"), "desc": card.get("desc", "")}


def chunks(text: str, size: int) -> list[str]:
    parts, current = [], ""
    for para in re.split(r"(\n\n)", text):
        if len(current) + len(para) > size and current:
            parts.append(current)
            current = ""
        while len(para) > size:
            parts.append(para[:size])
            para = para[size:]
        current += para
    if current.strip():
        parts.append(current)
    return parts


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("find").add_argument("card")
    sp = sub.add_parser("snapshot"); sp.add_argument("card"); sp.add_argument("out")
    sp = sub.add_parser("move"); sp.add_argument("card"); sp.add_argument("list", choices=sorted(CONFIG["lists"]))
    sp = sub.add_parser("comment"); sp.add_argument("card")
    g = sp.add_mutually_exclusive_group(required=True); g.add_argument("--text"); g.add_argument("--file")
    a = p.parse_args()

    card = find(a.card)
    if a.cmd == "find":
        print(json.dumps({k: card[k] for k in ("id", "name", "list", "url")}, ensure_ascii=False))
    elif a.cmd == "snapshot":
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(f"# {card['name']}\n\n- Card id: {card['id']}\n- List: {card['list']}\n"
                               f"- URL: {card['url']}\n\n{card['desc']}\n", encoding="utf-8")
        print(a.out)
    elif a.cmd == "move":
        trello("cards", "move", "--card", card["id"], "--list", CONFIG["lists"][a.list])
        print(f"{a.card} -> {a.list}")
    elif a.cmd == "comment":
        text = a.text if a.text is not None else Path(a.file).read_text(encoding="utf-8")
        parts = chunks(text, CONFIG["max_text_per_request"])
        for i, part in enumerate(parts, 1):
            label = f"({i}/{len(parts)})\n" if len(parts) > 1 else ""
            trello("comments", "add", "--card", card["id"], "--text", label + part)
        print(f"{a.card}: {len(parts)} comment(s)")


if __name__ == "__main__":
    main()
