# A worked example: one output, its expectations, and what stops it

A small output, Z1, run as written here. It draws one chapter of a source file: the chapter's statements, the
arrows between them, and one sentence on what the arrows show. Every output on this page is what Python printed.
The source:

```json
{
 "lem-bound":  {"chapter": "zeta", "title": "A bound on the partial sums", "uses": []},
 "lem-shift":  {"chapter": "zeta", "title": "Shifting the contour", "uses": ["lem-bound"]},
 "lem-window": {"chapter": "zeta", "title": "A window with no zeros", "uses": ["lem-shift"]},
 "thm-zeta":   {"chapter": "zeta", "title": "The zero-free region", "uses": ["lem-bound", "lem-shift", "lem-window", "thm-prior"]},
 "thm-prior":  {"chapter": "intro", "title": "A result from another chapter", "uses": []}
}
```

The module, with each kind of line marked (sections 1 to 5 of the skill):

```python
"""Z1: the zeta chapter's statements and the arrows between them, read from source.json."""
import collections
import json
import pathlib

SOURCE = pathlib.Path(__file__).with_name("source.json")   # pinned elsewhere, by commit or hash

# What Z1 expects source.json to say. The build compares each with the source and stops on any difference.
EXPECTED = [("lem-bound", "lem-shift"), ("lem-bound", "thm-zeta"), ("lem-shift", "lem-window"),
            ("lem-shift", "thm-zeta"), ("lem-window", "thm-zeta")]   # (used, user), within the chapter
N_STATEMENTS = 4
HEAVIEST = "thm-zeta"   # the statement that uses the most of the chapter: the last sentence rests on it


def read():
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    ids = sorted(k for k, v in src.items() if v["chapter"] == "zeta")
    edges = sorted((u, s) for s in ids for u in src[s]["uses"] if u in ids)
    return src, ids, edges


def check(ids, edges):
    if len(ids) != N_STATEMENTS:
        raise ValueError(f"Z1: source.json has {len(ids)} zeta statements, N_STATEMENTS says {N_STATEMENTS}: "
                         f"re-read the chapter's list ({', '.join(ids)})")
    have, want = set(edges), set(EXPECTED)
    if have - want:
        raise ValueError(f"Z1: source.json makes arrows EXPECTED does not have: {sorted(have - want)}; "
                         "re-read those statements' uses")
    if want - have:
        raise ValueError(f"Z1: EXPECTED has arrows source.json no longer makes: {sorted(want - have)}; "
                         "re-read those statements' uses")
    uses = collections.Counter(user for _, user in edges)
    top = sorted(uses.items(), key=lambda kv: (-kv[1], kv[0]))
    if top[0][0] != HEAVIEST or (len(top) > 1 and top[1][1] == top[0][1]):
        raise ValueError(f"Z1: HEAVIEST is {HEAVIEST}, and the counts are now {top}: "
                         "re-read the sentence on what the chapter builds toward")


def build():
    src, ids, edges = read()
    check(ids, edges)
    n = sum(1 for _, user in edges if user == HEAVIEST)
    lines = [f"Z1. The zeta chapter: {len(ids)} statements, {len(edges)} arrows between them"]   # framing, computed
    lines += [f"  {i}: \"{src[i]['title']}\"" for i in ids]                                   # quoted
    lines += [f"  {u} -> {s}" for u, s in edges]                                              # read
    lines.append(f"{HEAVIEST} uses {n} of the chapter's other {len(ids) - 1} statements: "    # interpretation,
                 "the chapter builds toward it.")                                             # guarded by HEAVIEST
    lines.append("An arrow says the source cites a result, not that a proof was checked.")    # what is not checked
    return "\n".join(lines)


if __name__ == "__main__":
    print(build())
```

What it records: `EXPECTED` (the arrows, both directions compared), `N_STATEMENTS` (a count), `HEAVIEST` (the
fact the interpretation rests on). The rankings are sorted by count, then by name, and nothing comes from a set's
or a dict's order. Its build:

```
Z1. The zeta chapter: 4 statements, 5 arrows between them
  lem-bound: "A bound on the partial sums"
  lem-shift: "Shifting the contour"
  lem-window: "A window with no zeros"
  thm-zeta: "The zero-free region"
  lem-bound -> lem-shift
  lem-bound -> thm-zeta
  lem-shift -> lem-window
  lem-shift -> thm-zeta
  lem-window -> thm-zeta
thm-zeta uses 3 of the chapter's other 3 statements: the chapter builds toward it.
An arrow says the source cites a result, not that a proof was checked.
```

## What stops it

**An arrow appears in the source** (`lem-window` now also uses `lem-bound`):

```
ValueError: Z1: source.json makes arrows EXPECTED does not have: [('lem-bound', 'lem-window')]; re-read those statements' uses
```

**An arrow disappears** (`lem-window` no longer uses `lem-shift`):

```
ValueError: Z1: EXPECTED has arrows source.json no longer makes: [('lem-shift', 'lem-window')]; re-read those statements' uses
```

**A statement is added** (`lem-tail` joins the chapter):

```
ValueError: Z1: source.json has 5 zeta statements, N_STATEMENTS says 4: re-read the chapter's list (lem-bound, lem-shift, lem-tail, lem-window, thm-zeta)
```

**The pin moves, and the arrows are re-read.** `thm-zeta` now uses only `lem-window`, which uses the other two.
The person moving the pin sets `EXPECTED` to the new arrows, as moving-pins says, each traced to a `uses` line.
The build still stops, on the sentence:

```
ValueError: Z1: HEAVIEST is thm-zeta, and the counts are now [('lem-window', 2), ('lem-shift', 1), ('thm-zeta', 1)]: re-read the sentence on what the chapter builds toward
```

That is the point of guarding an interpretation. The arrows were updated mechanically; the reading "the chapter
builds toward thm-zeta" was not, and the build will not let it stand unread. Setting `HEAVIEST` to `lem-window`
makes the build pass:

```
lem-window uses 2 of the chapter's other 3 statements: the chapter builds toward it.
An arrow says the source cites a result, not that a proof was checked.
```

Whether "the chapter builds toward" `lem-window` is still the right reading, now that `thm-zeta` is the chapter's
theorem and uses only one statement, is the person's call: they may keep the sentence, or change it and the
fact it rests on. The build's job is only to make sure the call is made.

## The same move with the checks taken out

Remove the call to `check()` and make the same move. The build passes, and prints:

```
thm-zeta uses 1 of the chapter's other 3 statements: the chapter builds toward it.
An arrow says the source cites a result, not that a proof was checked.
```

The number is computed, so it followed the source; the sentence after the colon is not, and it is now false. No
check failed and nothing was re-read: a silent redraw. This is what recording expectations prevents.

## What the check script sees

`check-expectations.py` checks the part the other scripts rely on. On Z1 it passes. Here is Z1 with its count
check written as `len(ids) != 4`, so that `N_STATEMENTS` is recorded but never used:

```
ERROR d_z1_zeta.py:11: N_STATEMENTS is recorded and never read in the module: it checks nothing
check-expectations: 1 modules, 3 expectations under 3 of 3 names, 3 of them literals
```

It cannot see a subtler failure: a comparison that is there but only warns, or one that checks one direction. Those
are found by reading the module against section 2 of the skill.

## What a release sees

The pin move above, committed after a tag, with the pins file and manifest updated. `release-facts.py`, from
cutting-releases, with `minor_names = ["EXPECTED"]`:

```
From v1.0.0 to HEAD (<commit>)

Pins
  SOURCE_COMMIT: abc1234 → def5678   MOVED

Posters
  manifest.json: 1 posters
    Z1: cards 4 → 4, arrows 5 → 4

Recorded expectations (module-level names in the poster modules)
  d_z1_zeta.py: changed: EXPECTED, HEAVIEST

Suggested: MINOR
  - SOURCE_COMMIT moved
  - d_z1_zeta.py: EXPECTED changed
  Check for MAJOR by hand: did what a poster is verified against change (a kind of check added, removed or redefined)? That is not visible in these facts.
```

`EXPECTED` and `HEAVIEST` are reported by name, because they are literals under names in `[build].expected_names`.
A change to `EXPECTED` is in `minor_names`, so it is a reason for MINOR by itself; a change to `HEAVIEST` alone
would be reported and left at PATCH.
