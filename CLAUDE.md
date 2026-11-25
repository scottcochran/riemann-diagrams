# riemann-diagrams

Generated SVG posters of the theorem dependency graph of Alpöge's Lean proof of the Riemann Hypothesis, read from
the riemann-blueprint and the community mirror of the formal proof at pinned commits. The build fails when the
sources no longer say what a poster draws. `README.md` says what each poster shows, `diagrams/README.md` what is
checked, `PLAN.md` what is planned, decided and done.

## Rules every change keeps

From `PLAN.md`, "Rules the design keeps". Read them there in full before changing a poster.

1. Every node is read from the files at build time. A poster's own words are marked as its own.
2. The arrows are checked. Each poster records what it expects, so a source change is a failing check, never a
   silent redraw.
3. The sources are pinned (`BP_COMMIT`, `MIRROR_PIN`, `MIRROR_COMMIT` in `diagrams/src/bp.py`). Moving one is
   deliberate: bump, regenerate, fix what the checks report.
4. The output is deterministic, and CI fails on the first byte that differs.
5. No Lean is built. Edges are checked against published files of the formal proof, never claimed proved.
6. Standard library only for the posters, on Python 3.12+.
7. The light page is the content's mean luminance (`diagrams/PAGE.md`).

And:

- **Never loosen a check.** Fix a failure by recording what the source now says, traced to a source line.
- **Never touch a published release or tag:** no edits, moves, deletions or re-creations, and no suggesting them. A
  wrong release gets a successor. The custodian (scottcochran) signs and pushes tags. Draft the message; don't
  push.
- **Stage files by name**, never a directory. Keep notes out of the tree.
- Run Python with `uv run`. The generator is `uv run python diagrams/gen-diagrams.py` (and `--map`). Any
  WARNING or ERROR is a failure. An exit of 1 with a NOTE means anchors moved: run it again.
- The sources are sibling checkouts, `../riemann-blueprint` and `../leanprover-community/riemann-hypothesis`, or
  `RIEMANN_BLUEPRINT` (its `blueprint/` directory) and `RIEMANN_MIRROR`. CI's sparse mirror needs
  `src/Main.lean`, `src/Statements.lean`, `comparator.json`, `lean-toolchain` and `verification/NOTES.md`.

## House style

For READMEs, `PLAN.md` notes, commit messages and tag messages: plain and exact. Give numbers with what they count
("275 of 289"), name pins by name and value, and say what was not checked. No praise words, no hype. Commit
subjects are `<area>: <what changed>` or `Phase <n><x>: <poster>, <what it shows>`. The body says what moved and
what the build now checks. Release notes and tag messages end the licence paragraph the same way each time: the
blueprint's prose under CC BY 4.0 (granted 2026-11-22, `NOTICE`), the Lean signatures unlicensed.

## Skills

The general method is in the `proof-posters` plugin in `./plugins/proof-posters/`, enabled for this repository by
`.claude/settings.json`. It reads this repository's paths from `proof-posters.toml`. The poster recipe is this
repository's own, in `.claude/skills/`.

| Skill | When |
|---|---|
| `proof-posters:moving-pins` | the blueprint or mirror moved; a pin, `NOTES_SHA256`, `CHECKS_SHA256` or a `LEAN_*_SHA256` fails; the daily `sources` run failed |
| `proof-posters:linking-papers` | a reference has no entry in `diagrams/src/papers.toml` |
| `proof-posters:extracting-lean-deps` | a `diagrams/src/lean-*.json` file must be rebuilt (`tools/lean-edges/README.md`) |
| `proof-posters:cutting-releases` | a release is due (PLAN.md, Phase 5), or a published one needs checking |
| `proof-posters:recording-expectations` | the method for any poster: read, record, compare both ways, four kinds of sentence, deterministic |
| `proof-posters:linking-posters` | posters are linked, a link lands on nothing, or a target should be framed when a link opens it |
| `drawing-posters` | a poster is added, or its layout or wording changes |
