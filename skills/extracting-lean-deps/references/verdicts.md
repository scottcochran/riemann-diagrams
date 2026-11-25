# The verdicts on an arrow

For an arrow A → B, from A's `uses` or its proof's, the verdict is the first of these that holds:

| verdict | meaning |
|---|---|
| `no-lean-source` | none of A's Lean names is in the formal proof |
| `no-lean-target` | none of B's Lean names is in the formal proof |
| `hypothesis` | A's Lean reaches B's only through the fields of a structure it takes: B is a hypothesis A carries |
| `direct` | A's Lean reaches B's, through helper declarations that no statement names |
| `through` | A's Lean reaches B's only by way of other statements' Lean (A → C → … → B) |
| `beside` | A's Lean never reaches B's, but some declaration's proof mentions both: B is used next to A |
| `apart` | none of these: the formal proof does not bear the arrow out |

"Reaches" follows references through every declaration that no statement names (helper lemmas, `_proof_n`,
matchers) until it meets one that a statement names. In `beside`, "mentions" includes the types of the proof's
hypotheses, so it is met when B is only assumed where A is applied.

Besides the verdicts, the edges file lists, per statement, the formal uses the blueprint does not draw
(`undrawn`) and the Lean names the proof does not contain (`lean_not_in_proof`). Under `cross_check` it gives the
cache run's counts and every arrow whose verdict differs in that run (`differs`, `moves`).

What a verdict does not say: `direct` means the references are there, not that the blueprint's prose describes
them correctly. `apart` means the formal proof does not bear the arrow out, not that the mathematics is wrong.
