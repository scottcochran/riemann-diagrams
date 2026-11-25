---
name: drawing-posters
description: "Adds a poster to riemann-diagrams or reworks one, applying proof-posters:recording-expectations with this repository's library: the diagrams/src/d_<id>_<slug>.py module and its recorded expectations, the bp.py sources, map mode, the link registry, both sets built and deterministic, a look in both themes, and every doc that lists posters or checks. Use when asked for a new poster, frame or trace, or to change a poster's layout, wording or cards. Not for moving a source pin (proof-posters:moving-pins), rebuilding the Lean-derived files (proof-posters:extracting-lean-deps), or tagging (proof-posters:cutting-releases)."
---

# Drawing posters

This skill is specific to this repository. The method is the plugin's **recording-expectations**
(`skills/recording-expectations/SKILL.md`, `proof-posters:recording-expectations` when the plugin is loaded):
read every fact, record what you expect and compare it both ways, four kinds of sentence, deterministic bytes,
say what is not checked, update the docs that count. Read it first. This skill is how each of those is done here,
with this repository's library, and the shared rules are in `CLAUDE.md`.

## Contents

- Before writing
- The module
- The method, as this repository does it
- Build and look
- The docs a poster touches
- Check before you stop

## Before writing

- Read `PLAN.md` for the poster's entry (the phases list each frame before it is built) and the seven rules at
  its head. A poster with no plan entry gets one first, saying what it shows and what it does not.
- Pick the id and slug. R is a reading at one level, T a trace, F another frame. The id is the next free number
  in its family. The file name is `d_<id lowercase>_<slug with underscores>.py`, and the output is
  `<ID>-<slug>-<date>.svg`.
- Find the closest existing poster and start from its module:
  - a chapter, lemma by lemma: `d_r4_families.py` (layout computed by `chapter.build`), or `d_r3_zero_free.py`
    (layout by hand, `PLACE`);
  - a chain: `d_t1_deepest.py` (`trace.build`);
  - a frame of its own: the F module nearest in kind (tables and matrices in F2/F7, a card grid in F1/F5, a
    figure in F6).

## The module

- Expose `ID`, `SLUG` and `build() -> Canvas`. The generator finds `d_*.py` on its own; there is no list to add it to.
- **Map mode:** under `bp.MAP`, quote nothing of the blueprint's prose or the Lean source (`bp.NOT_QUOTED`
  explains the gap on the card). Keep titles, ids, kinds, provenance, Lean names and locations, and every edge.
- **Links:** an id set in code links on its own through the registry. If the poster draws statements in full and
  should be where an id link from elsewhere lands, add it to `lib.HOME_ORDER` at the right priority. Otherwise
  leave it out.
- Standard library only. Python 3.12+.

## The method, as this repository does it

| recording-expectations | Here |
|---|---|
| 1. Read, don't restate | Everything comes from `bp.load()` and the files it reads: the blueprint at `BP_COMMIT`, `lean-facts.json`, the mirror at `MIRROR_COMMIT`, and the pinned `src/*.json` and `src/*.toml`. A new derived file is pinned by hash in `bp.py`. |
| 2. Record what you expect | `EXPECTED` (the edges between drawn statements, as `(used, user)`), `HYPOTHESES`, `VERDICTS`, `HYPOTHESES_LEAN`, count guards (`N_*`), top-k lists (`TOP`), a trace's path; the full list is `[build].expected_names` in `proof-posters.toml`. The build raises `ValueError` with both values. |
| 3. Four kinds of sentence | `diagrams/TEXT.md`, sections 4 and 5, is the rule. Quotations are in italics or a Lean panel, from a file the card's footer links to. Interpretations are in a grey or amber card, computed or guarded (F2's `HEAVIEST`). |
| 4. Deterministic bytes | The only date is `lib.DATE`. `vary_env` is `PYTHONHASHSEED` 0, then 1. |
| 5. Say what is not checked | The caveats that no Lean was built and that a card says what a statement is, not that it is proved; a poster that shows a verdict says it came from `src/lean-edges.json`. |
| 6. The docs that count | The list under "The docs a poster touches", below. |

## Build and look

```sh
uv run python diagrams/gen-diagrams.py <ID>              # one poster; exits 1 with NOTE if anchors moved: run again
uv run python diagrams/gen-diagrams.py                   # then all, so every poster's links follow
uv run python diagrams/gen-diagrams.py --map             # the map set
uv run python skills/moving-pins/scripts/determinism.py  # both sets, twice, two hash seeds: must be byte-identical
uv run python skills/recording-expectations/scripts/check-expectations.py  # expectations recorded and read
```

Any WARNING or ERROR is a failure: a word too wide for its cell, two texts overlapping, a character outside the
font subsets (add it to `WANT` in `tools/build-fonts.py` and rebuild the fonts), or an anchor that is not an XML
name.

**Look at it** in both themes, opened on its own. Light uses the 93% grey page (`diagrams/PAGE.md`). Render with
Chromium, `colorScheme: 'light'` and `'dark'`, at full width, and read it at zoom: a card's text, the arrows'
ends, the legend against what is drawn. Look at the map set too. Then check that the links resolve: an id on the
poster opens its card on the poster that draws it in full.

## The docs a poster touches

A new poster or a changed one updates every place that lists or counts posters, in the same commit:

- `README.md`: the poster list, and any count ("twenty posters").
- `diagrams/README.md`: "Start here" if it belongs there, the family list, the poster table, the checks table (what
  must match its `EXPECTED`), the "fails if" list if it adds a kind of check, and the files table.
- `diagrams/TEXT.md`: its interpretations and derived relations, and any new kind of text.
- `diagrams/EDGES.md`: a section, if it draws from the formal proof.
- `PLAN.md`: the phase's done note, with the commit and what the build checks.
- `tools/lean-edges/README.md`: if it reads a new derived file.

A poster added or removed is a MINOR release (proof-posters:cutting-releases). A layout or wording change that
moves no expectation is PATCH.

## Check before you stop

- recording-expectations' own list holds.
- `determinism.py` (the plugin's, in `skills/moving-pins/scripts/`) passes. The committed SVGs and manifests are
  the regenerated ones, so `git status -- diagrams` is clean after a fresh run.
- Both sets look right in both themes, and the map set quotes nothing.
- Every doc above that names posters or checks names this one. Files are staged by name.
