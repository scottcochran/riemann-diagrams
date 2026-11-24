# proof-posters: skills for diagrams drawn from a formal proof

A Claude Code plugin, published from this repository. Its skills hold the method behind riemann-diagrams'
posters: generated diagrams of a formal proof, pinned to exact commits of their sources, whose build fails when
the sources no longer say what is drawn. The method is written so that another project can use it. This
repository is the first user, and its own copy of the project config is `proof-posters.toml` at the root.

## The skills

| Skill | Use it when | It ends with |
|---|---|---|
| [`moving-pins`](moving-pins/SKILL.md) | a source has new commits; a pin, re-read hash or derived-file hash fails; the daily sources check failed | every check passing by recording what the sources say, never by loosening one; the list of posters to re-read |
| [`linking-papers`](linking-papers/SKILL.md) | a reference has no paper in the papers file, or a link needs checking | one verified, stable URL per reference, with how it was found |
| [`extracting-lean-deps`](extracting-lean-deps/SKILL.md) | a derived file about the formal proof must be rebuilt, or a poster needs a new fact about it | derived files read from the published export and the build cache, pinned by hash and commit |
| [`cutting-releases`](cutting-releases/SKILL.md) | a release is due, or one needs checking | a class, a drafted tag message handed to the custodian, and a published release checked against the tree |

Each skill has a `SKILL.md` and, where a step is mechanical, a script under `scripts/` (Python standard library
only) and reference tables under `references/`. Under Claude Code they are named `proof-posters:<skill>`.

What stays out of the plugin because it is this repository's own: the poster recipe
(`.claude/skills/drawing-posters/`) and the shared rules (`CLAUDE.md`).

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

Outside Claude Code, a skill's folder can be zipped and uploaded as a skill to claude.ai or the API. The
frontmatter uses only `name` and `description`.

## Using it in another project

Write a `proof-posters.toml` at the root of that project, in the form of this repository's. The skills and
scripts read it; nothing in them names a riemann-diagrams path. What it describes:

| Table | What it says |
|---|---|
| `[project]` | the custodian who pushes tags, the default branch, the plan file, the docs that state counts |
| `[build]` | the regenerate commands, the failure markers, the outputs and manifests, the counts each manifest gives per poster, the poster modules, the names of the expectations they record and which of them make a release MINOR |
| `[pins]`, `[[pins.commit]]` | the file the pins live in; each commit pin, with its checkout or the file it is read from |
| `[[pins.reread]]` | each hash that guards prose the posters paraphrase: its source, how to refresh it, what to re-read |
| `[[pins.derived]]` | each derived file, its hash pin and its provenance file |
| `[papers]` | the papers file, the references it must cover, the poster that checks it, the form of an entry |
| `[release]` | where the classification table is, the tag form and the glob that finds the last tag, the workflows, the Pages address, the asset globs, the checksum file, the file that records the release and the key in it that names the tag |
| `[lean]` | the runbook for the derived Lean files, the tools directory, the data's size and where it lives |

A project without a part (no papers, no Lean) leaves that table out, and the skill that needs it says so. A
script that needs a key the file lacks stops and names it. The scripts read the pins file as TOML (`.toml`), JSON
(`.json`) or Python (anything else), where a pin is a top-level `NAME = literal`, annotated or not. The poster
modules are read as Python. `load_config` and `pin_value` are copied into each script that uses them, so that each
skill's folder stands alone; the copies are kept identical.
