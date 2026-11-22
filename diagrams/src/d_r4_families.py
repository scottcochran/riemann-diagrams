"""R4 — Families of definite unitary groups, every statement of the chapter, and what each one rests on.

The layout is computed by chapter.py from the chapter's own edges. EXPECTED records the proof-use edges within
the chapter at the blueprint commit the diagrams were written against, and HYPOTHESES the results that proofs name
without listing as uses; the build fails if the blueprint now differs."""
import chapter

ID, SLUG, CH = "R4", "families", "chap-families"

# (used, user): the proof-use edges within the chapter
EXPECTED = [
    ("lem-inert-theta-admissibility-cm", "lem-admissibility-each-place"),
    ("lem-integrable-spectral-setting", "lem-depth-three-to-four"),
    ("lem-measured-setting-standard-character", "lem-integrable-spectral-setting"),
    ("lem-inert-theta-admissibility-cm", "lem-local-models-constructed-points"),
    ("lem-admissibility-each-place", "lem-local-models-constructed-points"),
    ("lem-constructed-points-from-depth-four", "lem-membership-two-passes"),
    ("thm-inner-form-multiplicities-equal", "prop-admissible-data-exist"),
    ("lem-inert-theta-admissibility-cm", "prop-chosen-data-serve-families"),
    ("lem-kernel-conditions-standard-data", "prop-chosen-data-serve-families"),
    ("lem-local-models-constructed-points", "prop-chosen-data-serve-families"),
    ("prop-definite-side-norm-bounds", "prop-defect-condition"),
    ("lem-local-models-weight-range", "prop-exponent-bounds-twisting-places"),
    ("lem-prime-power-lattice-inclusion-exponent", "prop-exponent-bounds-twisting-places"),
    ("thm-good-twists-all-coprime-powers", "prop-good-twists-from-theta-series"),
    ("prop-hecke-integrality-transformation", "prop-good-twists-from-theta-series"),
    ("lem-local-point-data-heights", "prop-height-inequalities-at-points"),
    ("prop-height-inequalities-at-points", "prop-lattice-and-depth-estimates"),
    ("prop-local-data-unitary-shimura-points", "prop-lattice-and-depth-estimates"),
    ("lem-orbit-data-inert-primes", "prop-local-data-unitary-shimura-points"),
    ("prop-good-twists-from-theta-series", "prop-twisting-property-constructed-points"),
    ("prop-hecke-integrality-transformation", "prop-twisting-property-constructed-points"),
    ("thm-inner-form-multiplicities-equal", "thm-basic-conditions-from-local-parameters"),
    ("prop-defect-condition", "thm-basic-conditions-from-local-parameters"),
    ("prop-chosen-data-serve-families", "thm-family-conditions-from-basic"),
    ("prop-small-terms-offdiag-level", "thm-family-conditions-from-basic"),
    ("prop-periods-valuations-good-data", "thm-family-conditions-from-basic"),
    ("prop-counting-constants-constituents", "thm-family-conditions-from-basic"),
    ("thm-twisting-index-and-archimedean-bounds", "thm-family-conditions-from-basic"),
    ("thm-family-membership-admissible-data", "thm-family-data-exists"),
    ("thm-twisting-index-and-archimedean-bounds", "thm-family-data-exists"),
    ("thm-basic-conditions-from-local-parameters", "thm-family-data-exists"),
    ("thm-family-conditions-from-basic", "thm-family-data-exists"),
    ("thm-inner-form-multiplicities-equal", "thm-family-data-exists"),
    ("prop-admissible-data-exist", "thm-family-membership-admissible-data"),
    ("prop-member-hypotheses-from-literature", "thm-family-membership-admissible-data"),
    ("thm-inner-form-multiplicities-equal", "thm-family-membership-admissible-data"),
    ("prop-intermediate-constructions-exist", "thm-family-membership-admissible-data"),
    ("prop-twisting-property-constructed-points", "thm-family-membership-admissible-data"),
    ("lem-membership-two-passes", "thm-family-membership-admissible-data"),
    ("lem-depth-three-to-four", "thm-family-membership-admissible-data"),
    ("thm-pseudo-coefficients-unitary", "thm-inner-form-multiplicities-equal"),
    ("prop-exponent-bounds-twisting-places", "thm-twisting-index-and-archimedean-bounds"),
    ("prop-lattice-and-depth-estimates", "thm-twisting-index-and-archimedean-bounds"),
    ("prop-height-inequalities-at-points", "thm-twisting-index-and-archimedean-bounds"),
]

# (named, in the proof of): results a proof names in its text without listing them as uses
HYPOTHESES = []


def build():
    return chapter.build(ID, CH, EXPECTED, HYPOTHESES)
