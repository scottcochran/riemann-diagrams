# A sketch to learn the method from

The method in one picture, one small example worked through, each lesson with what it does to that example, and
five questions to check yourself. `verdicts.md` has the definitions; this page shows them at work.

The example was run through the reference tools (riemann-diagrams' `tools/lean-edges/edges.py` and
`verdicts.py`, at commit `c1c64b9`). The verdicts below are their output, and each "in the example" column of the
lessons is what they printed after the change named in that row.

## 1. The picture

```
 blueprint: statements, each naming Lean declarations (`lean`), and arrows A -> B (`uses`, a proof's `uses`)
        |
        |   reading 1, the primary                          reading 2, the cross-check
        |   a published export at the commit                the build cache at a later commit: every
        |   the blueprint pins (lean4export NDJSON).        compiled module, three parts each
        |   It holds only what the main theorems            (.olean, .olean.server, .olean.private).
        |   depend on: a name missing from it is            It holds everything, so a missing name
        |   one the proof does not use.                     says less.
        |        |  checksum packed and unpacked                 |  the commit's own toolchain;
        |        |  index once, then build the graph             |  one process per module reads its parts
        |        v                                               v
        |   graph: declaration -> (kind, what its type references, what its value references)
        |        |                                               |
        +------->+  reach: from each statement's Lean, through   +
                 |  declarations no statement names (helpers),   |
                 |  to the first one a statement names           |
                 v                                               v
            verdict per arrow  ------------------------>  verdict per arrow
                 |                  compared, never chosen between: `differs`, `moves`
                 v
 derived file: verdicts, `undrawn`, `lean_not_in_proof`, `cross_check`
        + a meta file: the commits and checksums it was read from
        -> its hash pinned in the pins file -> the build checks the hash and the commits
```

## 2. One example, worked through

Ten blueprint statements. Each is a file whose front matter names its Lean declarations and its uses:

```
+++
kind = "theorem"
id = "A"
lean = ["a"]
uses = ["B", "C", "D", "E", "F", "G", "H"]
+++
```

| statement | names | uses | | statement | names | uses |
|---|---|---|---|---|---|---|
| A | `a` | B C D E F G H | | F | `f` | |
| B | `b` | | | G | `g` | |
| C | `c` | | | H | `h` (not in the proof) | |
| D | `d` | C | | U | `u` | |
| E | `e` | | | X | `x` (not in the proof) | B |

The proof's declarations, as the graph holds them (one line each, as `Deps.lean` writes them):

```
{"name": "a",      "kind": "theorem",   "type": ["Hyp"],       "value": ["a_aux", "d"]}
{"name": "a_aux",  "kind": "theorem",   "type": [],            "value": ["a_aux2", "u"]}
{"name": "a_aux2", "kind": "theorem",   "type": [],            "value": ["b"]}
{"name": "d",      "kind": "theorem",   "type": [],            "value": ["c"]}
{"name": "Hyp",    "kind": "inductive", "type": [],            "value": []}
{"name": "Hyp.mk", "kind": "ctor",      "type": ["e", "Hyp"],  "value": []}
{"name": "main",   "kind": "theorem",   "type": [],            "value": ["a", "f"]}
```

and `b`, `c`, `e`, `f`, `g`, `u`, each with nothing in it. Drawn from `a`:

```
 a --type--> Hyp ..its fields..> Hyp.mk --> e     E  hypothesis: reached only through a structure a takes
 a --proof-> a_aux --> a_aux2 --> b               B  direct: through two helpers no statement names
                 '---> u                          U  reached, but A does not draw it: undrawn
 a --proof-> d ......> c                          D  direct; C through: the search stops at d, which D names,
                                                     and C is reached only by way of D's Lean
 main --proof-> a, f                              F  beside: never reached from a, but mentioned beside it
 g                                                G  apart: nothing connects them
 H names h, X names x; neither is in the proof    H  no-lean-target (from A); X -> B no-lean-source
```

What the tools give (`verdicts.py`):

| arrow | verdict | why, in the order the verdicts are tried |
|---|---|---|
| X -> B | `no-lean-source` | `x` is not in the proof |
| A -> H | `no-lean-target` | `h` is not in the proof |
| A -> E | `hypothesis` | `e` is reached only by opening `Hyp` into its constructor's fields |
| A -> B | `direct` | `a` -> `a_aux` -> `a_aux2` -> `b`; helpers are walked through |
| A -> D, D -> C | `direct` | `a` mentions `d`; `d` mentions `c` |
| A -> C | `through` | `a` stops at `d` (D's); C is in D's uses, so A reaches it only by way of D |
| A -> F | `beside` | `a` never reaches `f`, but `main`'s proof mentions both |
| A -> G | `apart` | none of the above |

Besides the verdicts: `undrawn` is `{A: [U]}`, and `lean_not_in_proof` is `{H: [h], X: [x]}`. The counts are
3 `direct` and 1 of each other verdict.

## 3. The lessons

From the pitfalls in `SKILL.md` and the comments in the reference tools. Where the example can show one, the last
column is what the tools printed with the mistake put into the example's data.

| The mistake | What you see | Why | Do instead | In the example |
|---|---|---|---|---|
| Read a module's public part only | Almost every arrow `apart`; only what statements' types mention survives | Proofs live in `.olean.private` | Read the three parts together, in order (`readModuleDataParts`) | B, C, D, F: `apart`; E stays `hypothesis` (it is in `a`'s type); `undrawn` empty |
| Read one part alone with `readModuleData` | Reads that follow pointers into regions not mapped | A later part shares objects with the earlier ones | Same: read the parts together | |
| Read several modules in one process | Modules that clash in memory | Parts of different modules can claim the same address | One process per module (`run-deps.sh`) | |
| Collect constants with Lean's `Expr.getUsedConstants` | Stack overflow on deep proofs | It recurses as deep as the term | An explicit worklist, each shared subterm once (`Deps.lean`) | |
| Unpack the cache with leantar's default stack | leantar runs out of stack | It needs a larger one | `RUST_MIN_STACK=8388608` | |
| Pass module paths space- or quote-separated | `xargs` stops at an unmatched quote | Names can hold apostrophes (`HypothesesZ'`) | NUL-separated (`find -print0`, `xargs -0`) | |
| Read the cache with another toolchain | Modules read wrongly or not at all | The format is the compiler's | The commit's own `lean-toolchain` | |
| Stop the search at the first helper | Too few `direct` | Helpers sit between statements | Walk through every declaration no statement names | B: `direct` -> `apart` |
| Do not open a structure a statement takes | `hypothesis` arrows lost | A bundle of hypotheses carries each as a field | Follow an inductive into its constructors' types | E: `hypothesis` -> `apart` |
| Count only what a proof applies, not its hypotheses' types | Too few `beside` | B may only be assumed where A is applied | Count every constant in the value, binder types included | F (`f` dropped from `main`): `beside` -> `apart` |
| Pick one reading where the two disagree | A verdict that depends on which commit you trusted | The export and the cache are different commits | Draw the export's, list the cache's under `differs` and `moves` | |
| Compare names across Lean versions as one set | A toolchain bump looks like a rewrite | Auxiliary (`_proof_n`, `match_n`) and private (`_private.<module>…`) names change with the compiler | Compare user-written, auxiliary and private names separately | |
| Let the library/project rule drift | Weight and drift numbers move with no change in the proof | Which declarations are the project's is a heuristic | Keep the rule stable, and say what it gets wrong | |
| Use the export without its checksums | A wrong or truncated file read as the proof | A download can be cut short | Check the published checksum packed and unpacked | |
| Rebuild one derived file, or set its hash by hand | The build passes on stale data, or fails on commits | Each file is pinned by hash and by the commits in its meta file | Rebuild every file read at the moved pin, in dependency order (the edges file first), then each meta and each hash | |
| Change a verdict's definition or order for one output | Legends and checks that no longer mean what they say | Every output that shows verdicts depends on them | Keep them as defined; a change is a change in what is checked (MAJOR) | |

## 4. Check yourself

1. In the example, `a`'s proof leads to `c`. Why is A -> C `through`, not `direct`?
2. A rebuilt edges file has nearly every arrow `apart`. What is the first thing to check?
3. The export says an arrow is `direct`; the cache run says `apart`. Which goes on the output, and where is the
   other?
4. A statement's only Lean name is missing from the export. What does that say, and what verdict do its arrows
   get?
5. A poster would read better if `beside` counted as `direct`. Can it?

Answers:

1. The search stops at the first declaration a statement names. `d` is D's, so the search ends there, and C is
   reached only by way of D's Lean (A -> D -> C).
2. Whether the private parts were read: proofs live there. With only the public parts, only what statements' types
   mention survives (in the example, only E).
3. The export's, the primary reading. The cache run's verdict is recorded under `cross_check`: the arrow in
   `differs`, and the pair of verdicts in `moves`. Neither is chosen over the other.
4. That the proof does not use that declaration: the export holds only what the main theorems depend on. It is
   listed under `lean_not_in_proof`, and arrows from the statement are `no-lean-source`, arrows to it
   `no-lean-target`.
5. Not for one poster. The definitions are shared by every output and its checks; changing one is a change in
   what is checked, a MAJOR release, and is decided for all of them.
