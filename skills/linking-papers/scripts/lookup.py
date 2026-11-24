#!/usr/bin/env python3
"""Find the paper behind a citation on Crossref and zbMATH Open, and check a DOI against its own record.

    python3 lookup.py --title "Über einen Satz von Tschebyschef" --author Landau --year 1905
    python3 lookup.py --verify 10.1007/BF01449495 --title "..." --author Landau --year 1905

Search mode prints Crossref's best matches, then zbMATH Open's records for the author and year, each scored by
how closely its title matches (0 to 1), with every link zbMATH holds (DOI, EuDML, numdam, arXiv). Verify mode
fetches the DOI's own Crossref record and says whether its title, an author's surname and the year agree with the
citation. Neither decides: the skill does, from what these print.

Only the citation's title, author and year are sent, with a generic User-Agent; nothing about the project. Standard
library only, Python 3.11+.
"""
import difflib
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

UA = "proof-posters-lookup/0.1"


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def score(a, b):
    return round(difflib.SequenceMatcher(None, " ".join(norm(a)), " ".join(norm(b))).ratio(), 2)


def crossref_item(it):
    title = (it.get("title") or [""])[0]
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (it.get(k) or {}).get("date-parts") or [[None]]
        if parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    authors = [a.get("family", "") for a in it.get("author", [])]
    return title, year, authors, it.get("DOI"), (it.get("container-title") or [""])[0]


def search(title, author, year, rows):
    q = {"query.bibliographic": title, "rows": str(rows)}
    if author:
        q["query.author"] = author
    if year:
        q["filter"] = f"from-pub-date:{int(year) - 1},until-pub-date:{int(year) + 1}"
    print("Crossref")
    try:
        items = get("https://api.crossref.org/works?" + urllib.parse.urlencode(q))["message"]["items"]
    except Exception as e:
        items = []
        print(f"  unavailable: {e!r}")
    for it in items:
        t, y, au, doi, venue = crossref_item(it)
        print(f"  {score(title, t):.2f}  https://doi.org/{doi}\n        {t} — {', '.join(au[:4])} ({y}) {venue}")
    if not items:
        print("  no match")

    print("zbMATH Open")
    terms = [f"au:{author}"] if author else []
    if year:
        terms.append(f"py:{year}")
    if not terms:
        terms.append(f"ti:{title}")
    url = "https://api.zbmath.org/v1/document/_search?" + urllib.parse.urlencode(
        {"search_string": " ".join(terms), "results_per_page": "100"})
    try:
        res = get(url).get("result") or []
    except Exception as e:
        res = []
        print(f"  unavailable: {e!r}")
    ranked = sorted(res, key=lambda r: -score(title, (r.get("title") or {}).get("title", "")))[:rows]
    for r in ranked:
        t = (r.get("title") or {}).get("title", "")
        au = [a.get("name", "") for a in (r.get("contributors") or {}).get("authors", [])]
        links = [f"{l.get('type')}: {l.get('url')}" for l in r.get("links") or [] if l.get("url")]
        src = (r.get("source") or {}).get("source", "")
        print(f"  {score(title, t):.2f}  {r.get('zbmath_url')}\n        {t} — {'; '.join(au[:4])} ({r.get('year')}) {src}")
        for l in links:
            print(f"        {l}")
    if not ranked:
        print("  no match")


def verify(doi, title, author, year):
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    try:
        it = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    except Exception as e:
        print(f"{doi}: no Crossref record ({e!r}); check it at https://doi.org/{doi} by hand")
        return 1
    t, y, au, _, venue = crossref_item(it)
    s = score(title, t) if title else None
    names = {w for a in au for w in norm(a)}
    a_ok = (not author) or any(w in names for w in norm(author))
    y_ok = (not year) or (y is not None and abs(int(year) - int(y)) <= 1)
    print(f"https://doi.org/{doi}\n  {t} — {', '.join(au[:6])} ({y}) {venue}")
    print(f"  title {s if s is not None else '-'}   author {'yes' if a_ok else 'NO'}   year {'yes' if y_ok else 'NO'}")
    good = (s is None or s >= 0.8) and a_ok and y_ok
    print("  agrees with the citation" if good else "  DOES NOT AGREE: do not use it without settling why")
    return 0 if good else 1


def main(argv):
    title, author, year = arg(argv, "--title", ""), arg(argv, "--author"), arg(argv, "--year")
    if "--verify" in argv:
        return verify(arg(argv, "--verify"), title, author, year)
    if not title:
        sys.exit(__doc__)
    search(title, author, year, int(arg(argv, "--rows", "5")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
