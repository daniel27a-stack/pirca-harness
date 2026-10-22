#!/usr/bin/env python3
"""pirca code-hosting operations. Today backed by GitHub (git + the `gh` CLI); nothing outside
this file knows that. Pushing to main is impossible: the harness hook blocks it and so does this
script.

Usage:
  forge.py push      <REPO-PATH> <BRANCH>                       # git push -u origin BRANCH
  forge.py pr-create <REPO-PATH> --title TITLE --body-file PATH  # prints the PR URL
  forge.py pr-state  <PR-URL>                                    # JSON: state, merged, merged_at
  forge.py pr-review <PR-URL>                                    # JSON: title, body, reviews, comments, commits, files
"""
import argparse
import json
import subprocess
import sys

PROTECTED = {"main", "master"}


def run(cmd: list[str], cwd: str | None = None) -> str:
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"forge: {' '.join(cmd[:3])} failed: {(out.stderr or out.stdout).strip()}")
    return out.stdout


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("push"); sp.add_argument("repo"); sp.add_argument("branch")
    sp = sub.add_parser("pr-create"); sp.add_argument("repo")
    sp.add_argument("--title", required=True); sp.add_argument("--body-file", required=True)
    sub.add_parser("pr-state").add_argument("url")
    sub.add_parser("pr-review").add_argument("url")
    a = p.parse_args()

    if a.cmd == "push":
        if a.branch in PROTECTED:
            sys.exit("forge: pushing to main/master is not allowed; changes reach main through a PR")
        run(["git", "-C", a.repo, "push", "-u", "origin", a.branch])
        print(f"pushed {a.branch}")
    elif a.cmd == "pr-create":
        branch = run(["git", "-C", a.repo, "rev-parse", "--abbrev-ref", "HEAD"]).strip()
        if branch in PROTECTED:
            sys.exit("forge: the worktree is on main/master; a PR needs a feature branch")
        print(run(["gh", "pr", "create", "--base", "main", "--head", branch,
                   "--title", a.title, "--body-file", a.body_file], cwd=a.repo).strip().splitlines()[-1])
    elif a.cmd == "pr-state":
        d = json.loads(run(["gh", "pr", "view", a.url, "--json", "state,mergedAt"]))
        print(json.dumps({"state": d["state"].lower(), "merged": d["state"] == "MERGED", "merged_at": d["mergedAt"]}))
    elif a.cmd == "pr-review":
        print(run(["gh", "pr", "view", a.url, "--json", "title,body,reviews,comments,commits,files"]).strip())


if __name__ == "__main__":
    main()
