"""R7 — The Tate-Shafarevich bound, every statement of the chapter, and what each one rests on.

The layout is computed by chapter.py from the chapter's own edges. EXPECTED records the proof-use edges within
the chapter at the blueprint commit the diagrams were written against, and HYPOTHESES the results that proofs name
without listing as uses; the build fails if the blueprint now differs. VERDICTS and HYPOTHESES_LEAN record
the same against the formal proof (src/lean-edges.json)."""
import chapter

ID, SLUG, CH = "R7", "sha", "chap-sha"

# (used, user): the proof-use edges within the chapter
EXPECTED = [
    ("thm-hilbert-modular-inputs", "lem-h2-tate-twists-bound"),
    ("thm-borel-type-rank-bound", "lem-h2-tate-twists-bound"),
    ("thm-congruence-module-selmer-bound", "prop-congruence-bound-auxiliary-pair"),
    ("thm-lifting-deep-weights", "prop-congruence-bound-auxiliary-pair"),
    ("prop-paired-character-bound", "prop-congruence-bound-auxiliary-primes"),
    ("thm-congruence-module-selmer-bound", "prop-congruence-bound-intermediate-primes"),
    ("thm-lifting-clustered-weights", "prop-congruence-bound-intermediate-primes"),
    ("prop-lifting-ramified-coefficients", "prop-congruence-bound-intermediate-primes"),
    ("prop-finite-classes-cyclotomic-twists", "prop-congruence-bound-large-primes"),
    ("prop-congruence-bound-auxiliary-pair", "prop-congruence-bounds-all-primes"),
    ("prop-congruence-bound-large-primes", "prop-congruence-bounds-all-primes"),
    ("thm-congruence-module-selmer-bound", "prop-congruence-bounds-all-primes"),
    ("prop-congruence-bound-intermediate-primes", "prop-congruence-bounds-all-primes"),
    ("thm-wach-lifting-theorem", "prop-congruence-bounds-all-primes"),
    ("lem-finite-classes-twists-from-wach", "prop-finite-classes-cyclotomic-twists"),
    ("thm-lifting-potentially-crystalline", "prop-paired-character-bound"),
    ("prop-congruence-bounds-all-primes", "thm-family-sha-error-bound"),
    ("prop-congruence-bound-auxiliary-primes", "thm-family-sha-error-bound"),
    ("thm-congruence-module-selmer-bound", "thm-family-sha-error-bound"),
    ("thm-hilbert-modular-inputs", "thm-gsp4-lift-automorphy"),
    ("thm-automorphic-induction-quadratic", "thm-gsp4-lift-automorphy"),
    ("thm-potential-automorphy-seeds", "thm-gsp4-lift-automorphy"),
    ("thm-hilbert-modular-inputs", "thm-hilbert-mixed-weights"),
    ("thm-hilbert-weight-change", "thm-hilbert-mixed-weights"),
    ("thm-kato-zeta-integral", "thm-kato-euler-system-ordinary"),
    ("thm-kato-explicit-reciprocity", "thm-kato-euler-system-ordinary"),
    ("thm-reciprocity-fixed-exponent", "thm-kato-explicit-reciprocity"),
    ("thm-kato-euler-system-ordinary", "thm-kato-selmer-vanishing"),
    ("thm-hilbert-modular-inputs", "thm-kato-selmer-vanishing"),
    ("lem-lifting-crystalline-lattices", "thm-lifting-potentially-crystalline"),
    ("thm-hilbert-modular-inputs", "thm-potential-automorphy-seeds"),
    ("thm-automorphic-induction-quadratic", "thm-potential-automorphy-seeds"),
    ("thm-hilbert-mixed-weights", "thm-potential-automorphy-seeds"),
    ("thm-siegel-units-diamond", "thm-reciprocity-fixed-exponent"),
    ("thm-hilbert-modular-inputs", "thm-sha-bound"),
    ("thm-kato-euler-system-ordinary", "thm-sha-bound"),
    ("thm-kato-explicit-reciprocity", "thm-sha-bound"),
    ("thm-kato-selmer-vanishing", "thm-sha-bound"),
    ("lem-h2-tate-twists-bound", "thm-sha-bound"),
    ("thm-gsp4-lift-automorphy", "thm-sha-bound"),
    ("thm-siegel-units-mackey", "thm-siegel-units-diamond"),
    ("thm-siegel-units-eisenstein", "thm-siegel-units-mackey"),
]

# (named, in the proof of): results a proof names in its text without listing them as uses
HYPOTHESES = [
    ("thm-congruence-module-selmer-bound", "thm-sha-bound"),
    ("thm-family-sha-error-bound", "thm-sha-bound"),
    ("thm-wach-lifting-theorem", "thm-sha-bound"),
]

# (used, user): the verdict on each arrow against the formal proof (src/lean-edges.json), where it is not
# `direct`; the build fails if one has another
VERDICTS = {
    ("thm-hilbert-modular-inputs", "lem-h2-tate-twists-bound"): "apart",
    ("thm-hilbert-modular-inputs", "thm-gsp4-lift-automorphy"): "apart",
    ("thm-hilbert-modular-inputs", "thm-hilbert-mixed-weights"): "apart",
    ("thm-hilbert-modular-inputs", "thm-kato-selmer-vanishing"): "apart",
    ("thm-hilbert-modular-inputs", "thm-potential-automorphy-seeds"): "apart",
    ("thm-kato-euler-system-ordinary", "thm-sha-bound"): "through",
    ("thm-kato-explicit-reciprocity", "thm-sha-bound"): "through",
}

# (named, in the proof of): what the Lean of the second does with the first: "direct" (uses it),
# "through" (reaches it by way of other statements), or None (does not reach it)
HYPOTHESES_LEAN = {
    ("thm-congruence-module-selmer-bound", "thm-sha-bound"): None,
    ("thm-family-sha-error-bound", "thm-sha-bound"): None,
    ("thm-wach-lifting-theorem", "thm-sha-bound"): None,
}


def build():
    return chapter.build(ID, CH, EXPECTED, HYPOTHESES, VERDICTS, HYPOTHESES_LEAN)
