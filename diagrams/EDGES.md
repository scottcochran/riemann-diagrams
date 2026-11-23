# The arrows against the formal proof

The blueprint draws an arrow from one statement to another when the first uses the second. Its arrows are read
from the blueprint's source text, and some of them are wrong. This document says how every arrow was checked
against the references of the published formal proof, what the check found, and what a verdict does and does
not claim. It is derived from `diagrams/src/lean-edges.json` as built on 2026.11.23 by `tools/lean-edges/`, at
the commits that file records; when the file is rebuilt, the numbers here move with it.

The short version: of the blueprint's 2,004 arrows, 1,760 are borne out by the formal proof. That is 1,549
directly, 157 as a hypothesis the Lean carries, and 54 by way of other statements. Another 19 meet the arrow's
target only beside it, and 148 are not borne out. The last 77 cannot be judged, because one end names no Lean
that the proof contains. Two source statements account for 89 of the 148. The proof also makes 1,995 uses that
the blueprint does not draw. The chapter posters R3 to R8 and the traces T1 and T2 show the verdicts, and F7
lays them out chapter against chapter. An arrow
that is not borne out directly is drawn thin, dotted or red, and each chapter poster's card "Against the formal
proof" reads the rest of the chapter against the file.

## 1. Where the formal proof's references come from

No Lean was built. The references come from two published sources, read without compiling anything.

| | The verdicts | The cross-check |
|---|---|---|
| Source | Andrew Sutherland's export of the published proof, `math.mit.edu/~drew/grh/solution.ndjson.zst` | The mirror's public build cache, `rh-cache.taucetiproject.org` |
| Tree | the mirror at `8c90877c`, the commit the blueprint pins (`MIRROR_PIN`) | the mirror at `c900e67c2f` (`MIRROR_COMMIT`) |
| Lean | 4.33.1, lean4export 3.1.0 | 4.37.0-rc1 |
| Size | 7.7 GB packed; 1.07 billion expressions, 1.48 million declarations | 149,216 compiled modules, 86 GB unpacked |
| Checked by | sha256 of the packed and unpacked file | the cache receipt's sha256, then each manifest row's |

The export holds exactly what the five main theorems depend on, nothing more. A declaration missing from it is
therefore one the proof does not use. The cache holds every module of the later tree, used or not. Both are
reduced to the same thing: for every declaration, the constants its type references and the constants its
value (a proof, or a definition's body) references.

## 2. How an arrow is judged

Each blueprint statement names its Lean declarations (the `lean` list in its front matter). For a statement A,
the check starts from A's declarations and follows their references. It passes through every declaration that
no statement names, such as helper lemmas, `_proof_n` auxiliaries and matchers, and stops at the first one that
a statement does name. That statement is one A really uses. A theorem's type gives the statement's uses, and
its value gives the proof's uses. For a definition or a structure, the type, the body and the structure's fields
all count as the statement.

One refinement matters. A Lean theorem often takes a bundle of hypotheses as a structure, such as
`LiteratureCMHypothesis`, and each field of that structure is a statement. The check follows a structure into
its constructor, and so into its fields. A use found only that way is reported as a `hypothesis`: A carries B
as an assumption rather than invoking it.

An arrow A → B, whether from A's `uses` or its proof's, then gets the first of these verdicts that holds:

| Verdict | Meaning | Export | Cache |
|---|---|---:|---:|
| `direct` | A's Lean reaches B's, through helper declarations that no statement names | 1,549 | 1,548 |
| `hypothesis` | A's Lean reaches B's only through the fields of a structure it takes | 157 | 157 |
| `through` | A's Lean reaches B's only by way of other statements' Lean (A → C → … → B) | 54 | 57 |
| `beside` | A's Lean never reaches B's, but some declaration's proof mentions both | 19 | 19 |
| `apart` | none of these: the formal proof does not bear the arrow out | 148 | 146 |
| `no-lean-source` | none of A's Lean names is in the formal proof | 74 | 74 |
| `no-lean-target` | none of B's Lean names is in the formal proof | 3 | 3 |

## 3. The two runs agree

The trees are not the same. About 230,000 project declarations in the export are gone from the later tree,
which pruned heavily. Even so, only 3 of the 2,004 verdicts differ. In one, the export's link is the closer
one. In the other two, the later tree reaches the target by way of another statement, where the export does not
reach it at all:

| Arrow | Export | Cache |
|---|---|---|
| `thm-critical-line-primitive` → `thm-half-plane` | `direct` | `through` |
| `thm-family-data-exists` → `thm-local-parameters-exist` | `apart` | `through` |
| `thm-primitive-suffice` → `def-nonvanishing-half-plane` | `apart` | `through` |

The file records these under `cross_check`, and the verdicts it gives are the export's.

## 4. What the proof does not contain

Ten Lean names that the blueprint gives, across eight statements, are not in the published proof:

| Statement | Lean names not in the proof |
|---|---|
| `thm-riemann-hypothesis` | `UpperTheory.FinalTheorems.riemannHypothesis`, `UpperTheory.riemannHypothesis_of_everyCharacter` |
| `lem-theta-constant-term-big-cone` | `GlobalTheory.T.exists_isCT_integral_eq_cone_integral_add_hasLaw`, `GlobalTheory.ThK.unfoldCTBigCone` |
| `prop-theta-integrals-along-towers` | `GlobalTheory.ThK.ctBigCone` |
| `def-archimedean-bessel-data` | `Formalism.QuantumDeterminants.IsBesselFunctional` |
| `lem-admissibility-each-place` | `GlobalTheory.TwV.admissible_at_each_site` |
| `lem-orbit-data-inert-primes` | `UpperTheory.OrbitFamilyRestriction.exists_rowFamS` |
| `lem-zeta-nonvanishing` | `UpperTheory.zeta_ne_zero_of_everyCharacter` |
| `thm-geometric-lemma` | `UpperTheory.V.Z.Win.Extra.geo` |

Most of these statements name other Lean that the proof does use, so their arrows are still judged.
`thm-riemann-hypothesis`, for example, keeps `riemannHypothesis` and `Formalism.VW.rh_of_every`. Four
statements are left with no Lean at all: `lem-admissibility-each-place`, `lem-theta-constant-term-big-cone`,
`lem-zeta-nonvanishing` and `thm-theta-inputs`. Their 74 outgoing arrows are `no-lean-source`, and the 3
arrows into them from statements that do have Lean are `no-lean-target`.

## 5. Where the disagreements are

The 148 `apart` arrows are not spread evenly. Two source statements account for 89 of them.

- **`prop-theta-integrals-along-towers`, 52 arrows.** Its first Lean name, `GlobalTheory.ThK.ctBigCone`, is
  dead. The mirror removed it in commit `d14c4e4`, and the export does not contain it. Its other name,
  `PositivityTheory.ThKG.Leaves`, is a structure built only by `PositivityTheory.Sph.Tr.closeSph`, which the
  blueprint assigns to `thm-theta-tower-step-identities`. Even that builder reaches only 3 of the arrows'
  targets: `hasse-norm-quadratic`, `hecke-l-entire` and `reduction-theory-unitary`. The arrows appear to
  describe what the removed declaration used, not what the proof does now.
- **`thm-kato-zeta-integral`, 37 arrows.** A placement check on the cache found 36 of the 37 targets applied
  higher up the proof, at `thm-kato-selmer-vanishing`, rather than inside the Kato theorem. The Kato theorem
  takes the inputs it needs as named hypotheses, so the Lean supplies them where the theorem is applied, not
  where it is proved.

The remaining 59 are spread over many statements, none with more than 3.

## 6. Beside A, and what that test is worth

`beside` asks whether any declaration's proof mentions both A's Lean and B's. Reading the five such
declarations behind arrows the blueprint might have attached to the wrong Lean shows how loose that is:

| Arrow | Declaration | How B enters | Does B feed A? |
|---|---|---|---|
| `lem-membership-two-passes` → `thm-siegel-main-theorem-hermitian` | `memberE_closing_alt_alt` | assumed | yes, through another lemma |
| `lem-flag-cover-pullback` → `thm-arithmetic-intersection-theory` | `SquareStatements.tie_of` | a field of a hypothesis bundle | yes, indirectly |
| `thm-families-connected` → `def-family-data` | `zero_free_all_of_green_v_win` | the type of a hypothesis | no, a parallel input |
| `lem-integrable-spectral-setting` → `thm-hc-finiteness-unitary` | `has4_of_has3_of_sExt_none` | assumed | no, a parallel input |
| `thm-member-gap-bound` → `thm-chain-averaging` | `UpperTheory.Comparison₂.core_gm` | applied | no: A's result feeds B's |

In four of the five, B enters only as an assumption. The test counts it because a proof term repeats its
hypotheses' types. So `beside` means that A and B meet in one proof, not that A depends on B.

These five came from 21 arrows where, in the cache run, a declaration next to A's (in the same namespace)
reaches B. That suggested the blueprint might name the wrong Lean for A. A search for other theorems with
exactly A's conclusion found 11 across those 21 arrows, and none of them reaches B. The test found no case of a
wrong name for A.

## 7. What the blueprint does not draw

The formal proof makes 1,995 uses that no arrow records, spread over 267 statements. They are listed per
statement under `undrawn`. They are concentrated in the theorems that assemble the proof:
`thm-grh-from-sha-bound` (128), `thm-grh-from-theta-integrals` (98), `prop-member-hypotheses-from-literature`
(96), `thm-family-data-exists` (84) and `thm-non-endoscopic-hypotheses-hold` (62).

## 8. Where the assumptions enter, and where they are discharged (F8)

The five theorems of `Main.lean` are closed propositions, so every assumption the proof takes is discharged
inside it. `diagrams/src/lean-hypotheses.json`, written by `tools/lean-edges/hypotheses.py` from the export,
follows two kinds, and F8 draws them.

- **Structures of assumptions.** The 157 `hypothesis` arrows pass through 8 structures, each counted where its
  own fields state the arrow's target. They run from 10 statements to 48, 44 of them in the literature chapter.
  17 declarations build these structures, so supply every field. None is a declaration the blueprint names,
  and each is reached by the Lean of some statement, which is where the assumptions are discharged.
- **Stated claims.** 225 statements give a `Prop` definition among their Lean, 289 in all. For 275 some theorem
  of the proof concludes it with no premise typed by a blueprint `Prop` or one of the structures. 6 are
  concluded only under such premises, 7 are never concluded under their own name, and 1 is not in the proof.
  All 184 of the literature chapter's are concluded outright. The test reads types, not proofs, and sees only
  those premises. A theorem concluding a `Prop` of another name that unfolds to the same is not seen either.
- **Axioms.** The export holds three axioms, `Classical.choice`, `Quot.sound` and `propext`, which are exactly
  the ones the mirror's `comparator.json` permits, and no `sorryAx`. This is read from the export, not checked
  by a kernel; it is not a verification of the proof.

## 9. Where the formal work is (F9)

`diagrams/src/lean-weight.json`, written by `tools/lean-edges/weight.py`, counts the declarations under each
statement's Lean. Of the export's 1,484,733 declarations, 1,269,850 are the project's rather
than the library's, by a name rule its docstring gives. 1,229 are named by statements and
1,268,621 are helpers. 502,612 helpers are reached by one statement's Lean only, 179,332
by two, 581,749 by three or more, and 4,928 by none. Sized by distinct expression nodes, the
project's declarations hold 2,503,334,210 nodes, 1,160,103,587 of them in helpers a single statement
reaches.

- **New work carries most of it.** Statements marked new hold 81% of the helpers' size that any single
  statement owns.
- **The heaviest** are `thm-family-membership-admissible-data`, `thm-sha-bound` and `thm-good-towers-from-arakelov-inputs`. The first has 12,225 helpers of its own,
  78,568,819 nodes, across 452 namespaces.
- **Glue.** 73 statements have no helpers of their own. R3's chapter theorem, `thm-zero-free-from-connected`,
  has 2, and shares 48 with other statements: its Lean assembles results proved under
  other statements.

Size measures the terms the compiler wrote, not difficulty. Shared subterms are counted in each declaration.

## 10. What changed between the pins (F10)

`diagrams/src/lean-drift.json`, written by `tools/lean-edges/drift.py`, compares the proof at `MIRROR_PIN`, from
the export, with the proof at `MIRROR_COMMIT`, from the cache closed from the same five theorems, by name, over
the project's declarations. There are 314 commits between them. The closures hold
1,269,850 declarations then and 1,274,580 now.

- **Most of the movement is the compiler's.** 199,833 auxiliary names left and
  193,811 private names joined. Auxiliary and private names change with the Lean version
  (4.33 then, 4.37 now) and with a file's place, so they are counted apart and not compared one to one.
- **User-written names.** 795,187 stayed and 8,324 left. Of those that left,
  7,693 are still compiled at the later commit but no longer used, and 631 are
  gone. 659 joined.
- **The blueprint's 1,194 Lean names.** 1,170 are in both closures,
  8 are still compiled but no longer used, 5
  are gone from the later tree, and 9 are in neither. One, `RiemannHypothesis`, is
  Mathlib's, which the cache does not hold, so it is not compared. The names that are gone: `Formalism.VW.critLine`, `Formalism.VW.gammaFactor_ne_zero`, `Formalism.VW.rh_of_every`, `Formalism.VW.rh_of_right`, `GlobalTheory.T.volume_theorem_of_inputs`.

A renamed declaration counts as one that left and one that joined: names are all the comparison sees.

## 11. What a verdict does not say

- **Not that anything is proved.** A verdict reads references, which is what the compiler wrote, and checks
  nothing. The proof's status is the mirror's Comparator run, and its notes do not yet record a result.
- **Not which kind of use.** The verdict merges statement and proof uses. `edges.py` keeps them apart, but the
  file does not.
- **Not more than the names allow.** A statement whose `lean` list names the wrong declaration is judged by the
  wrong declaration. That is the case of `prop-theta-integrals-along-towers` above, and the reason section 4
  lists every name the proof does not contain.

## Building it again

`tools/lean-edges/README.md` gives every step, with checksums and timings: fetching and indexing the export,
building its reference graph, the cache run, and writing the file. `tools/lean-edges/meta.json` records the
commits and checksums the file was read from. Moving a pin means rebuilding both runs and the file, updating
`meta.json`, and then this document.
