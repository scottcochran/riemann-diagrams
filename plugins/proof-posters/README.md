# proof-posters: skills for diagrams drawn from a formal proof

A Claude Code plugin, published from this repository. Its skills hold the method behind riemann-diagrams'
posters: generated diagrams of a formal proof, pinned to exact commits of their sources, whose build fails when
the sources no longer say what is drawn. The method is written so that another project can use it. This
repository is the first user, and its own copy of the project config is `proof-posters.toml` at the root.

## The skills

| Skill | Use it when | It ends with |
|---|---|---|
| [`moving-pins`](skills/moving-pins/SKILL.md) | a source has new commits; a pin, re-read hash or derived-file hash fails; the daily sources check failed | every check passing by recording what the sources say, never by loosening one; the outputs byte-identical over two rounds; the list of posters to re-read |
| [`linking-papers`](skills/linking-papers/SKILL.md) | a reference has no paper in the papers file, or a link needs checking | one verified, stable URL per reference, with how it was found |
| [`extracting-lean-deps`](skills/extracting-lean-deps/SKILL.md) | a derived file about the formal proof must be rebuilt, or a poster needs a new fact about it | derived files read from the published export and the build cache, pinned by hash and commit |
| [`recording-expectations`](skills/recording-expectations/SKILL.md) | an output is added, or what one reads, draws or says changes | every fact read from the sources, what it expects recorded as literals and compared both ways (`check-expectations.py` passing), every sentence one of four kinds, the bytes deterministic, the docs that count updated |
| [`cutting-releases`](skills/cutting-releases/SKILL.md) | a release is due, or one needs checking | a class, a drafted tag message handed to the custodian, and a published release checked against the tree |
| [`linking-posters`](skills/linking-posters/SKILL.md) | posters are to be linked to each other and to their sources, a link lands on nothing, or a reader cannot see where a link went | every link landing on an id that exists, at a pin or an allowed address, its target framed when opened (`check-links.py` passing), and a few targets seen in a browser |

Each skill has a `SKILL.md` and, where a step is mechanical, a script under `scripts/` (Python standard library
only) and reference tables under `references/`. Under Claude Code they are named `proof-posters:<skill>`.
Three skills have a page to learn them from, each built on an example that was run:
`recording-expectations/references/example.md` (one small output, broken by four changes to its source),
`extracting-lean-deps/references/sketch.md` (the method in one picture, and a ten-statement example run through
the reference tools, with each lesson's effect on it, and `docstrings.md` beside it, reading a formalisation's
annotated docstrings, from riemann-masullo-diagrams), and `linking-posters/references/target-highlighting.md`
(the markup and style of a framed target, from riemann-masullo-diagrams, and how to test one without being misled).

What stays out of the plugin because it is this repository's own: the poster recipe
(`.claude/skills/drawing-posters/`), which applies recording-expectations with this repository's library, and the
shared rules (`CLAUDE.md`).

## Installing

In a Claude Code session:

```
/plugin marketplace add scottcochran/riemann-diagrams
/plugin install proof-posters@riemann-diagrams
```

Inside this repository, `.claude/settings.json` already lists the marketplace and enables the plugin. Each
collaborator still installs it once after trusting the folder:
`claude plugin install proof-posters@riemann-diagrams --scope project`. To try a local change before it is
pushed, add the checkout as a marketplace instead: `/plugin marketplace add ./`.

The plugin is the folder `plugins/proof-posters/` of the repository; an install copies only that folder. Its
scripts are under the Apache License 2.0 (`LICENSE`) and its Markdown under CC BY 4.0 (`LICENSE-DOCS`), as the
repository's `NOTICE` divides them.

Outside Claude Code, a skill's folder can be zipped and uploaded as a skill to claude.ai or the API. The
frontmatter uses only `name` and `description`.

## Using it in another project

Write a `proof-posters.toml` at the root of that project, in the form of this repository's. The skills and
scripts read it; nothing in them names a riemann-diagrams path. What it describes:

| Table | What it says |
|---|---|
| `[project]` | the custodian who pushes tags, the default branch, the plan file, the docs that state counts, the project's own poster skill if it has one |
| `[build]` | the regenerate commands, the failure markers, the line that asks for a run again, the environment of each round of the determinism check, the outputs and manifests, the counts each manifest gives per poster, the poster modules, the names of the expectations they record and which of them make a release MINOR |
| `[pins]`, `[[pins.commit]]` | the file the pins live in; each commit pin, with its checkout or the file it is read from |
| `[[pins.reread]]` | each hash that guards prose the posters paraphrase: its source, how to refresh it, what to re-read |
| `[[pins.derived]]` | each derived file, its hash pin and its provenance file |
| `[papers]` | the papers file, the references it must cover, the poster that checks it, the form of an entry |
| `[release]` | where the classification table is, the tag form and the glob that finds the last tag, the workflows, the Pages address, the asset globs, the checksum file, the file that records the release and the key in it that names the tag |
| `[lean]` | the runbook for the derived Lean files, the tools directory, the data's size and where it lives |
| `[links]` | optional, for `check-links.py`: `require_targets` (every link to a poster names an id), `unrendered` (text the poster library must never leave in an output), `allow` (address prefixes allowed besides the pinned commits; without it, other links out are reported, not failed), `frame_classes` (the classes that frame a linked id) |

A project without a part (no papers, no Lean) leaves that table out, and the skill that needs it says so. A
script that needs a key the file lacks stops and names it. The scripts read the pins file as TOML (`.toml`), JSON
(`.json`) or Python (anything else), where a pin is a top-level `NAME = literal`, annotated or not. The poster
modules are read as Python. `load_config` and `pin_value` are copied into each script that uses them, so that each
skill's folder stands alone; the copies are kept identical.

## What the project brings

The skills hold the method and the scripts hold the mechanical steps. The rest is the project's, and the plugin
ships none of it, not even as a template: this repository's files are the worked example. A project without a
part skips the skill that needs it.

| The project needs | Used by | Here |
|---|---|---|
| A build: commands that regenerate every output from the pinned sources, print a line with a failure marker on any failure, and fail when a checkout is at another commit than its pin | moving-pins and `determinism.py`, linking-papers, extracting-lean-deps | `diagrams/gen-diagrams.py`, both sets |
| A pins file that assigns each pin as a top-level `NAME = literal` (or a TOML or JSON key) | `pin-status.py`, `release-facts.py` | `diagrams/src/bp.py` |
| Modules that record what the sources say as module-level Python literals, under the names in `[build].expected_names`, and a build that fails when the sources say otherwise | moving-pins, `release-facts.py` | `diagrams/src/d_*.py`, 20 of them |
| Manifests: JSON objects keyed by output id, with the fields in `[build].manifest_counts` | `release-facts.py` | `diagrams/manifest.json`, `diagrams/map/manifest.json` |
| For each re-read hash, a `refresh` command that fetches the pages again, saves them, and records their hashes | moving-pins, case A | `tools/check-sources.py`, run daily by `.github/workflows/sources.yml` |
| A papers file, and a build check that fails on a reference with no entry or an entry with no reference | linking-papers | `diagrams/src/papers.toml`, checked by `diagrams/src/d_f4_literature.py` |
| A release workflow that, on a pushed tag, publishes the outputs with a checksum file, and optionally a metadata file that names the tag and a Pages site that serves it (set up as `cutting-releases/references/pages-site.md` says; the site is public even for a private repository); on GitHub, since `verify-release.py` uses `gh` | cutting-releases | `.github/workflows/release.yml`, `pages.yml`, `tools/release-notes.py` |
| A runbook and tools that read the formal proof's export and build cache and write the derived files, each with a `meta` file of the commits it was read at. The skill has no scripts | extracting-lean-deps | `tools/lean-edges/` and its `README.md` |
| A poster library that writes ids on what a link may open, links through a registry of every poster's anchors (the committed manifest), and asks for a second run when anchors move; optionally, a style that frames a link's target | linking-posters | `diagrams/src/lib.py` (`REGISTRY`, `Canvas.link`, `halo`, `TOP`) and the generator's `NOTE`; the framing follows riemann-masullo-diagrams' (`references/target-highlighting.md`) |
| Optionally, a skill for adding or reworking a poster with the project's own library, named in `[project].poster_skill` | recording-expectations defers to it for layout and look | `.claude/skills/drawing-posters/` |

The scripts need git and Python 3.11 or later, and `verify-release.py` also needs the GitHub CLI, logged in.
