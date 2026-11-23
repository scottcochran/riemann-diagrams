# lean-edges: the blueprint's arrows against the formal proof

These scripts write `diagrams/src/lean-edges.json`, a verdict on every arrow of the riemann-blueprint, read from
the references of the published formal proof. The posters read only that file. Nothing here is needed to
regenerate a poster, and no Lean is built: the proof's references come from a published export, and a second run
over the mirror's public build cache checks them.

The data is large (an 8 GB export that indexes to 9 GB, and 95 GB for the cache), so it lives outside the repository.
Below, `$D` is that directory, `$BP` the riemann-blueprint's `blueprint/` directory at `BP_COMMIT`, and `py` stands for
`uv run --no-project --python 3.12 --with orjson python -I`.

## The verdicts

For an arrow A → B (from A's `uses`, or its proof's), the first of these that holds:

| verdict | meaning |
|---|---|
| `no-lean-source` | none of A's Lean names is in the formal proof |
| `no-lean-target` | none of B's Lean names is in the formal proof |
| `hypothesis` | A's Lean reaches B's only through the fields of a structure it takes: B is a hypothesis A carries |
| `direct` | A's Lean reaches B's, through helper declarations that no statement names |
| `through` | A's Lean reaches B's only by way of other statements' Lean (A → C → … → B) |
| `beside` | A's Lean never reaches B's, but some declaration's proof mentions both: B is used next to A |
| `apart` | none of these: the formal proof does not bear the arrow out |

"Reaches" follows references through every declaration that no blueprint statement names (helper lemmas,
`_proof_n`, matchers) until it meets one that a statement names. In `beside`, "mentions" includes the types
of the proof's hypotheses, so it is met when B is only assumed where A is applied.

The file also lists, per statement, the formal uses the blueprint does not draw (`undrawn`) and the Lean names
the proof does not contain (`lean_not_in_proof`). Under `cross_check` it gives the cache run's counts and every
arrow where that run's verdict differs (`differs`, `moves`).

## The proof: Sutherland's export (the verdicts)

The export holds the dependency closure of the five main theorems at the mirror commit the blueprint pins
(`MIRROR_PIN`), so a declaration missing from it is one the proof does not use.

```sh
mkdir -p $D/export && cd $D/export
curl -fLO https://math.mit.edu/~drew/grh/solution.ndjson.zst
echo "61a8938ad5f5e57397c1c0e3b954916af546d9004ade01c3555744a681b05381  solution.ndjson.zst" | shasum -a 256 -c
zstd -dc --long=30 solution.ndjson.zst | shasum -a 256    # 5ea74b912147c5c93cc2b6d70cc727cf908df2f62ac6a20480a3fa02f6be244e
zstd -dc --long=30 solution.ndjson.zst | py tools/lean-edges/export.py ingest $D/export-index    # 8 min, 9 GB
py tools/lean-edges/export_graph.py $D/export-index $D/export-run/edges.graph.pkl                  # 10 min
py tools/lean-edges/edges.py - $BP $D/export-run/edges                                             # reads the graph above
```

`export.py query` answers questions about the export directly (which names it has, who mentions a name, what a
declaration reaches); its docstring has the format.

## The cross-check: the mirror's build cache

Every compiled module of the mirror at one commit, fetched from the cache its `lake exe cache get` reads, then
read by `Deps.lean`. It needs the commit's Lean toolchain (here `leanprover/lean4:v4.37.0-rc1`, the one in
`lean-toolchain`), whose `bin/` has `leantar`.

```sh
C=c900e67c2fcd1fdb041685820bbd2b867fbc5a4b
py tools/lean-edges/fetch.py $D $C ~/.elan/toolchains/leanprover--lean4---v4.37.0-rc1/bin all    # 5 GB, 86 GB unpacked
(cd tools/lean-edges && lake build deps)
tools/lean-edges/run-deps.sh $D/oleans $D/deps                                                     # 149,216 modules
py tools/lean-edges/edges.py $D/deps $BP $D/edges
```

Pitfalls: a module's parts (`.olean`, `.olean.server`, `.olean.private`) must be read together
(`readModuleDataParts`), since proofs live in the private part; leantar needs `RUST_MIN_STACK=8388608` (fetch.py
sets it); module names can contain apostrophes, so run-deps.sh passes paths NUL-separated.

## The file

```sh
py tools/lean-edges/verdicts.py $BP $D/export-run/edges $D/edges --meta tools/lean-edges/meta.json > diagrams/src/lean-edges.json
```

`meta.json` records the commits and checksums the file was read from. Moving a pin means rebuilding both runs
and the file, and updating `meta.json`.

## The assumptions file

`diagrams/src/lean-hypotheses.json`, which F8 reads, is written from the export and from `lean-edges.json`
(its `hypothesis` arrows), so it is rebuilt after it:

```sh
py tools/lean-edges/hypotheses.py $BP $D/export-index $D/export-run/edges.graph.pkl diagrams/src/lean-edges.json \
  --meta tools/lean-edges/meta-hypotheses.json > diagrams/src/lean-hypotheses.json                 # 2 min
```

It holds the structures behind the hypothesis arrows, with their fields, takers and builders; for every
statement's `Prop` definition, the theorems that conclude it and their premises; and the export's axioms.
`hypotheses.py`'s docstring defines each part, and what its test does not see.
