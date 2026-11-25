# riemann-diagrams: would OPA Rego policies improve the posters' specificity and reproducibility, 2026.11.23

> **Provenance note.** Written 2026.11.23 by the assistant, at the custodian's request, in answer to the question
> in the title. Basis: riemann-diagrams `main` at `bbcc963`, read in full where cited (`PLAN.md`,
> `diagrams/README.md`, `diagrams/TEXT.md`, `diagrams/gen-diagrams.py`, `diagrams/src/bp.py`, `diagrams/src/lib.py`,
> the four workflows), and tla-kit's `GRAPH-AND-DIAGRAMS.md` for the one place it is mentioned. **Nothing was run:**
> no poster was regenerated, no policy was evaluated, and `opa` was not installed. The Rego in §5 is a sketch that
> has not been through `opa`. Where this says what the repository does, it cites the file; where it says what the
> repository does not do, it is the assistant's reading, from a search of the tree, and could have missed
> something. It decides nothing.

## 0. In one paragraph

Rego would not make the posters more reproducible: the bytes are already held by three pins, a deterministic
generator and CI's byte comparison. It could make the **verdict** reproducible, so that a third party can
re-check a release without the generator or the two source checkouts, and it would make one family of rules more
**specific**: the provenance and licence rules, which today hold because of how the generator is written and not
because anything asserts them of the output. Both gains need the generator to write out what it drew as data,
and most of the gain is in that file, not in the language that reads it. The recommendation is to write the
facts first, and to choose between Rego and a separate standard-library checker afterwards. A Rego policy over
the workflow files is a separate, smaller matter and is worth having either way.

## 1. What holds the process today

| What | Where | How it is held |
|---|---|---|
| The sources | `BP_COMMIT`, `MIRROR_PIN`, `MIRROR_COMMIT` in `diagrams/src/bp.py` | The generator refuses a checkout at another commit (`bp.py`, lines 94 to 97, 135 to 146) |
| The pages R1's band 5 paraphrases | `NOTES_SHA256`, `CHECKS_SHA256`, `diagrams/src/checks.toml` | A hash of each passage read; `sources.yml` re-reads them daily |
| The output | The committed SVGs and the two `manifest.json` | `posters.yml` regenerates both sets and fails on the first differing byte |
| What each poster draws | `EXPECTED` and `HYPOTHESES` literals in the poster modules | Compared with the blueprint at build time; a mismatch is an `ERROR` |
| Links | `Canvas.check` in `lib.py` | A link out must be under a pinned commit, or a paper of `papers.toml`, or a page of `checks.toml`; a link in must name a card the manifest lists |
| Layout | `Canvas.check` | Overlapping text, text off the canvas, a glyph the embedded fonts lack |
| A release | `release.yml` | The posters check on the tag, then `pins.json` (the three pins in full and the generator's commit) and `SHA256SUMS` |

The checks are some 85 `raise` and exit sites in `diagrams/src/` and `gen-diagrams.py`, the warnings of
`Canvas.check`, and 75 lines that set or read `EXPECTED` and `HYPOTHESES`. They are described in prose twice, in
`diagrams/README.md` ("What is checked") and in `diagrams/TEXT.md`. Nothing compares the prose with the code;
`TEXT.md` says so of itself ("when the two disagree, the code is right and this document is stale").

`manifest.json` is already a small facts file: for each poster its file, title, counts of cards, arrows and
links, and its anchors. It is written for the links between posters and for the release notes, not for checking.

## 2. Reproducibility

### 2.1 Of the posters: no gain

Rule 4 of `PLAN.md` is that unchanged inputs give unchanged bytes, and CI holds it. A policy engine reads data
and returns a verdict; it draws nothing. Adding one changes no byte of a poster.

### 2.2 Of the verdict: a gain

To confirm today that a release's posters satisfy the rules, a person checks out the blueprint and the mirror at
their pins and runs the generator. The checking and the drawing are one program, so a fault in `bp.py` can be a
fault in both, and the only evidence a release carries that the checks passed is that the release exists.

If the generator wrote, for each poster, what it drew (§4), and a release carried those files, the policy and
the result, then anyone could re-evaluate the result from the release's own assets with one binary. That is a
second reading that does not share the generator's code. It is the same separation tla-kit makes between a
results file and the check that reads it.

### 2.3 Where reproducibility is actually loose

These are in the workflows, not the generator, and none needs Rego to fix, though a policy can keep them fixed:

- **Actions are pinned by tag**, not by commit: `actions/checkout@v5`, `actions/setup-python@v6`,
  `actions/upload-artifact@v7`, `actions/upload-pages-artifact@v5`, `actions/configure-pages@v6`,
  `actions/deploy-pages@v5`. A tag can be moved.
- **The runner is `ubuntu-latest`** in every job.
- **Python is `"3.12"`**, so the patch release floats. `PLAN.md` records that 3.12 and 3.14 gave the same bytes,
  so the risk is small, and the byte comparison would catch a change.
- **The pins are ten characters**, resolved to full commits through the GitHub API at run time (`posters.yml`,
  "Resolve the pins to full commits"). `pins.json` records the full commits at release; `bp.py` does not.
- **The Graphviz diagrams are outside CI**, by `PLAN.md` Phase 2, because `dot` is not deterministic across
  versions. Nothing here changes that.

## 3. Specificity

Rego suits rules of the form "no element of this document may have that property". It is no better than Python
for equality with a recorded list, and it is the wrong tool for geometry.

| Rule | Where it lives now | Fit | Why |
|---|---|---|---|
| The map set quotes nothing of the blueprint's prose or of a Lean signature | By omission: `prose()` returns `None` in map mode (`bp.py`, line 79), and each module branches on `bp.MAP` | **Good** | The assistant found no check of the map output itself. `NOTICE` and `diagrams/README.md` rest on this property, and a new module that forgets the branch would break it silently. |
| Every run of text is one of `TEXT.md`'s four kinds | Prose only | **Good** | It would turn `TEXT.md` from a description into a rule, and end the drift §1 notes. |
| Every link out is under a pinned commit, a paper or a recorded page | `Canvas.check` | Good, but already checked | Moving it gains a second reading, not a new rule. |
| A release's tag is annotated, the custodian's and on `main`; `pins.json` agrees with `bp.py` | Shell in `release.yml` | Good | Admission rules over a small document. |
| Arrows are exactly `EXPECTED`; a trace is exactly its path | The poster modules | Neutral | Set equality. Rego can state it; Python already does. |
| Counts, depth histogram, most-cited references (F3, F4, F6) | The poster modules | Neutral | The same. |
| Text fits its card, nothing overlaps, an arrow does not point upward | `lib.py`, `bp.py` | **Poor** | Numeric geometry over measured text. It should stay where the measuring is. |
| Actions pinned by commit, permissions least, runner named | Nothing | **Good** | The ordinary use of Rego, through `conftest`, over the workflow YAML. |

So the gain in specificity is concentrated in the first two rows. Those are the rules a reader outside the
project most needs to audit, because they are what lets the map set be passed on without the blueprint's licence
or the proof's.

## 4. What it would need: the facts

One JSON file per poster and set, written by the generator beside the SVG, or the manifest's entry extended. At
least:

- the three pins and the poster's id and set (`reader` or `map`);
- each card: its blueprint id, kind, provenance, and its Lean declaration's name, file and line;
- each run of text on a card, with its kind (blueprint prose, front matter or Lean facts, proof source, written
  here, derived) and, for a quotation, where it was taken from;
- each arrow, with whether it is a proof use, a statement use or a dashed hypothesis;
- each link, with its target.

The hard part is the second and third items. The generator builds a card from strings, and a string does not
now carry where it came from; `prose()` is the one place that marks a quotation, and it marks it by returning it
or not. Tagging text by kind at the point it is read is a change through `bp.py` and every poster module. It is
also the change that makes the map rule checkable at all, in any language.

The facts file must itself be byte-stable and held by the CI comparison, like the manifest.

## 5. A sketch of the policy

Not evaluated. It assumes the facts of §4 under `input`.

```rego
package riemann.posters

import rego.v1

quoted_kinds := {"blueprint-prose", "proof-source"}

# The map set quotes nothing.
deny contains msg if {
	input.set == "map"
	some card in input.cards
	some run in card.text
	run.kind in quoted_kinds
	msg := sprintf("%s: map poster quotes %s on card %s", [input.id, run.kind, card.id])
}

# Every run of text has a kind TEXT.md names.
deny contains msg if {
	some card in input.cards
	some run in card.text
	not run.kind in {"blueprint-prose", "front-matter", "proof-source", "written", "derived"}
	msg := sprintf("%s: text of no recorded kind on card %s", [input.id, card.id])
}

# A quotation says where it was taken from, at the pinned commit.
deny contains msg if {
	some card in input.cards
	some run in card.text
	run.kind in quoted_kinds
	not startswith(run.source, input.pins[run.repo].commit)
	msg := sprintf("%s: quotation on card %s is not from a pinned commit", [input.id, card.id])
}
```

And for the workflows, through `conftest`:

```rego
package riemann.workflows

import rego.v1

deny contains msg if {
	some job in input.jobs
	some step in job.steps
	not startswith(step.uses, "./")
	not regex.match(`@[0-9a-f]{40}$`, step.uses)
	msg := sprintf("action not pinned by commit: %s", [step.uses])
}
```

## 6. Costs

1. **A binary.** Rule 6 of `PLAN.md` is "standard library only for the posters, so that anyone with Python 3.12
   can regenerate them". Regenerating would still need only Python; checking would need `opa`, pinned by digest
   as tla-kit pins its tools in `PINS.json`. Whether rule 6 covers checking is the custodian's to say.
2. **Two languages.** A rule stated in both Rego and Python can drift. A rule that moves to the policy should
   leave the generator, except where the generator needs it to draw.
3. **The facts are most of the work and most of the gain.** The same rules can be a short standard-library
   Python checker that reads only the facts file and imports nothing from `diagrams/src/`. That gives the same
   independence from the generator, keeps rule 6 whole, and loses only what Rego has over Python: a declarative
   rule a reader can audit without following control flow, and tooling others already have.
4. **A policy can be wrong too.** It needs fixtures, as the checks have now only by the Phase 2 test of a moved
   pin: a facts file that should fail each rule, and one that should pass.

## 7. Recommendation

1. **Pin the actions by commit and name the runner**, with or without a policy. Then one `conftest` policy over
   `.github/workflows/` to keep it so. This is small and independent of everything else here.
2. **Tag text by kind in the generator and write the facts.** This is the precondition for the map rule and for
   any second reading, and it is useful alone: `TEXT.md`'s tables could be generated from it.
3. **Write the map rule and the provenance rule against the facts**, with fixtures. Choose the language then:
   - Rego, if the policy should be auditable by people who will not read the Python, or shared with tla-kit's
     specification graph, whose plan (`GRAPH-AND-DIAGRAMS.md`, §2.1) names policy among the layers below the
     model;
   - a separate Python checker, if rule 6 is to cover checking.
4. **Leave `EXPECTED`, the counts and the geometry where they are.**
5. **If step 3 is done, ship it in a release**: the facts, the policy's digest and the result beside
   `pins.json`, under `SHA256SUMS`.

## 8. What this does not settle

- Whether the map set does quote nothing today. That is a check of the sixteen map SVGs against the blueprint at
  `BP_COMMIT`, which was not made.
- Whether tagging text by kind can be done without changing a byte of a poster. It should, since it adds data
  beside the drawing, but it was not tried.
- Whether rule 6 extends to checking, and whether a `decisions/` record is wanted for the choice (`PLAN.md`,
  Open, item 4). Both are the custodian's.
