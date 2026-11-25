"""R6 — Heights and the covolume bound, every statement of the chapter, and what each one rests on.

The layout is computed by chapter.py from the chapter's own edges. EXPECTED records the proof-use edges within
the chapter at the blueprint commit the diagrams were written against, and HYPOTHESES the results that proofs name
without listing as uses; the build fails if the blueprint now differs. VERDICTS and HYPOTHESES_LEAN record
the same against the formal proof (src/lean-edges.json)."""
import chapter

ID, SLUG, CH = "R6", "heights", "chap-heights"

# (used, user): the proof-use edges within the chapter
EXPECTED = [
    ("lem-flag-cover-pullback", "lem-absolute-siegel-lemma"),
    ("thm-arithmetic-hilbert-samuel-inequalities", "lem-absolute-siegel-lemma"),
    ("lem-de-rham-hodge-tate-relations-dvr", "lem-de-rham-hodge-tate-flag-comparison"),
    ("thm-mean-arithmetic-volume-lower-bound", "lem-height-lower-bound-deep-covers"),
    ("thm-unitary-integral-models", "lem-height-lower-bound-deep-covers"),
    ("lem-reference-weights-deep-covers", "lem-height-lower-bound-deep-covers"),
    ("thm-angehrn-siu-point-separation", "lem-height-lower-bound-deep-covers"),
    ("thm-toroidal-compactification-siegel", "lem-height-lower-bound-deep-covers"),
    ("thm-toroidal-compactification-unitary", "lem-height-lower-bound-deep-covers"),
    ("lem-flag-cover-pullback", "lem-hilbert-samuel-block"),
    ("thm-unitary-integral-models", "lem-reference-weights-deep-covers"),
    ("lem-siegel-tautological-charts", "lem-siegel-minimal-blowup-smooth"),
    ("thm-mumford-degeneration", "lem-siegel-tautological-charts"),
    ("lem-unitary-tautological-charts", "lem-unitary-boundary-prechart"),
    ("thm-unitary-integral-models", "lem-unitary-boundary-separation"),
    ("thm-mumford-degeneration", "lem-unitary-tautological-charts"),
    ("thm-unitary-integral-models", "lem-unitary-tautological-charts"),
    ("lem-flag-cover-pullback", "lem-weyl-antisymmetry-intersection"),
    ("lem-flag-cover-pullback", "thm-arithmetic-hilbert-samuel-inequalities"),
    ("lem-hilbert-samuel-block", "thm-arithmetic-hilbert-samuel-inequalities"),
    ("thm-mean-arithmetic-volume-lower-bound", "thm-covolume-bound"),
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-covolume-bound"),
    ("lem-height-lower-bound-deep-covers", "thm-covolume-bound"),
    ("thm-unitary-integral-models", "thm-covolume-bound"),
    ("thm-mumford-degeneration", "thm-covolume-bound"),
    ("thm-toroidal-compactification-unitary", "thm-covolume-bound"),
    ("thm-toroidal-compactification-siegel", "thm-covolume-bound"),
    ("thm-functorial-resolution", "thm-covolume-bound"),
    ("thm-dieudonne-theory-oc", "thm-covolume-bound"),
    ("thm-angehrn-siu-point-separation", "thm-covolume-bound"),
    ("lem-p-divisible-period-matrices", "thm-dieudonne-theory-oc"),
    ("thm-principalisation-reduces-dimension", "thm-functorial-resolution"),
    ("lem-flag-cover-pullback", "thm-good-towers-from-arakelov-inputs"),
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-good-towers-from-arakelov-inputs"),
    ("lem-absolute-siegel-lemma", "thm-good-towers-from-arakelov-inputs"),
    ("lem-de-rham-hodge-tate-flag-comparison", "thm-good-towers-from-arakelov-inputs"),
    ("thm-unitary-integral-models", "thm-good-towers-from-arakelov-inputs"),
    ("lem-weyl-antisymmetry-intersection", "thm-good-towers-from-arakelov-inputs"),
    ("lem-volume-theorem-from-tower-identities", "thm-good-towers-from-arakelov-inputs"),
    ("lem-de-rham-hodge-tate-flag-comparison", "thm-mean-arithmetic-volume-lower-bound"),
    ("thm-dieudonne-theory-oc", "thm-mean-arithmetic-volume-lower-bound"),
    ("lem-flag-cover-pullback", "thm-mean-arithmetic-volume-lower-bound"),
    ("thm-good-towers-from-arakelov-inputs", "thm-mean-arithmetic-volume-lower-bound"),
    ("lem-absolute-siegel-lemma", "thm-mean-arithmetic-volume-lower-bound"),
    ("thm-unitary-integral-models", "thm-mean-arithmetic-volume-lower-bound"),
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-mean-arithmetic-volume-lower-bound"),
    ("lem-uniformisation-labelled-cover", "thm-mumford-degeneration"),
    ("thm-unitary-integral-models", "thm-mumford-degeneration"),
    ("lem-order-step-reduces-order", "thm-principalisation-reduces-dimension"),
    ("lem-siegel-minimal-blowup-smooth", "thm-toroidal-compactification-siegel"),
    ("thm-unitary-rigid-boundary-charts", "thm-toroidal-compactification-unitary"),
    ("lem-kodaira-spencer-from-rigid-charts", "thm-toroidal-compactification-unitary"),
    ("thm-full-level-ample-models", "thm-unitary-integral-models"),
    ("lem-unitary-boundary-separation", "thm-unitary-rigid-boundary-charts"),
    ("lem-unitary-boundary-prechart", "thm-unitary-rigid-boundary-charts"),
]

# (named, in the proof of): results a proof names in its text without listing them as uses
HYPOTHESES = []

# (used, user): the verdict on each arrow against the formal proof (src/lean-edges.json), where it is not
# `direct`; the build fails if one has another
VERDICTS = {
    ("lem-absolute-siegel-lemma", "thm-good-towers-from-arakelov-inputs"): "beside",
    ("lem-de-rham-hodge-tate-flag-comparison", "thm-mean-arithmetic-volume-lower-bound"): "through",
    ("lem-flag-cover-pullback", "lem-absolute-siegel-lemma"): "apart",
    ("lem-flag-cover-pullback", "lem-hilbert-samuel-block"): "apart",
    ("lem-flag-cover-pullback", "thm-arithmetic-hilbert-samuel-inequalities"): "apart",
    ("lem-flag-cover-pullback", "thm-mean-arithmetic-volume-lower-bound"): "through",
    ("thm-arithmetic-hilbert-samuel-inequalities", "lem-absolute-siegel-lemma"): "apart",
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-covolume-bound"): "through",
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-good-towers-from-arakelov-inputs"): "apart",
    ("thm-arithmetic-hilbert-samuel-inequalities", "thm-mean-arithmetic-volume-lower-bound"): "apart",
    ("thm-dieudonne-theory-oc", "thm-mean-arithmetic-volume-lower-bound"): "through",
    ("thm-functorial-resolution", "thm-covolume-bound"): "through",
    ("thm-mean-arithmetic-volume-lower-bound", "lem-height-lower-bound-deep-covers"): "through",
    ("thm-mumford-degeneration", "thm-covolume-bound"): "through",
}

# (named, in the proof of): what the Lean of the second does with the first: "direct" (uses it),
# "through" (reaches it by way of other statements), or None (does not reach it)
HYPOTHESES_LEAN = {
}


def build():
    return chapter.build(ID, CH, EXPECTED, HYPOTHESES, VERDICTS, HYPOTHESES_LEAN)
