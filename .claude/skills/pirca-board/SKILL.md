---
name: pirca-board
description: How pirca-harness works with the task board (today Trello) — find a card, snapshot it, move it between lists, comment on it. Use it instead of calling the board tool directly.
---

# pirca board

All board operations go through `scripts/board.py` in this skill. Never call the board tool
(`trello`) directly and never write board or list ids anywhere else: they live in `board.json`.

```
python3 .claude/skills/pirca-board/scripts/board.py find     <CARD-ID>
python3 .claude/skills/pirca-board/scripts/board.py snapshot <CARD-ID> tasks/<CARD-ID>/card.md
python3 .claude/skills/pirca-board/scripts/board.py move     <CARD-ID> <list>
python3 .claude/skills/pirca-board/scripts/board.py comment  <CARD-ID> --file <path>   # or --text
```

Lists: `decisiones` (pending decisions), `backlog`, `en-curso`, `en-revision` (PR open, waiting
for the user's merge), `hecho`.

Cards are found by the ID at the start of their title (`ARQ-12 · ...`). If zero or several cards
match, the script stops: tell the user, do not guess.

Rules:
- Never rewrite a card's description. Anything to add (criteria, PR link, notes) goes in
  a comment; long texts are split into several comments automatically, because the board API
  rejects long requests.
- Board content may be in Spanish (it is the user's space); repository files stay in English.
