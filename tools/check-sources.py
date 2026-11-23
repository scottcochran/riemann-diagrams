#!/usr/bin/env python3
"""Re-read the pages R1's band 5 paraphrases, and say whether they have changed since diagrams/src/checks.toml
recorded them.

For each entry the page is fetched, its markup removed and its whitespace collapsed, and the passage from the
entry's `from` to its `to` hashed. Exit 0 if every hash is the recorded one, 1 if a page changed or a passage
cannot be found. With --update, the new hashes are written into checks.toml (and `read` set to today); the build
then fails until CHECKS_SHA256 in diagrams/src/bp.py is bumped, which is the moment to re-read the cards of band 5
against the pages. With --save DIR, each page as fetched is kept in DIR, to read or to diff. Standard library only.

    python3 tools/check-sources.py
"""
import datetime
import hashlib
import html
import pathlib
import re
import sys
import tomllib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKS = ROOT / "diagrams" / "src" / "checks.toml"


def passage(page, start, end):
    """The text of an HTML page, markup removed and whitespace collapsed, from `start` to `end` inclusive."""
    t = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", page)
    t = re.sub(r"(?s)<!--.*?-->", " ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    i = t.find(start)
    j = t.find(end, i + 1) if i >= 0 else -1
    if i < 0 or j < 0:
        return None
    return t[i:j + len(end)]


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "riemann-diagrams check-sources"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def main(argv):
    update = "--update" in argv
    save = pathlib.Path(argv[argv.index("--save") + 1]) if "--save" in argv else None
    src = CHECKS.read_text(encoding="utf-8")
    entries = tomllib.loads(src)
    bad = 0
    for key, e in entries.items():
        try:
            page = fetch(e["url"])
        except Exception as ex:   # report and carry on: one unreachable page must not hide the others
            print(f"ERROR {key}: {e['url']}: {ex!r}")
            bad += 1
            continue
        if save:
            save.mkdir(parents=True, exist_ok=True)
            (save / f"{key}.html").write_text(page, encoding="utf-8")
        p = passage(page, e["from"], e["to"])
        if p is None:
            print(f"ERROR {key}: the passage from {e['from']!r} to {e['to']!r} is not on the page")
            bad += 1
            continue
        h = digest(p)
        if h == e["sha256"]:
            print(f"same    {key}: {h[:12]}…, {len(p):,} characters")
            continue
        print(f"changed {key}: {e['sha256'][:12] or '(none)'}… → {h[:12]}…, {len(p):,} characters")
        bad += 1
        if update:
            block = re.search(rf'(?ms)^\[{re.escape(key)}\]\n.*?(?=^\[|\Z)', src)
            new = re.sub(r'(?m)^sha256 = ".*"$', f'sha256 = "{h}"', block.group(0))
            new = re.sub(r'(?m)^read = ".*"$', f'read = "{datetime.date.today().isoformat()}"', new)
            src = src[:block.start()] + new + src[block.end():]
    if update:
        CHECKS.write_text(src, encoding="utf-8")
        if bad:
            print("checks.toml updated: re-read the cards of R1's band 5 against the pages, then set CHECKS_SHA256 "
                  "in diagrams/src/bp.py")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
