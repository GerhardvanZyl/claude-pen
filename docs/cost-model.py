#!/usr/bin/env python3
"""Estimate cost difference between dev-loop (full) and dev-loop-lite.

All token figures are assumptions, labelled below. The structure matters more
than the absolute numbers -- change the assumptions and re-run.

Unity loops: dev-loop-unity and dev-loop-unity-lite extend the same lane and
round pricing with a gated, Fable-priced Visual lane and Fable-priced scene
building (the Phase 0a bible, the Phase 1 visual build), printed separately
below rather than folded into the scenarios above.
"""

# --- Pricing, USD per million tokens ---------------------------------------
PRICE = {
    "opus":   (5.0,  25.0),
    "sonnet": (3.0,  15.0),
    "haiku":  (1.0,   5.0),
    # Visual-judgment model behind sidekick-visual / reviewer-visual in the
    # Unity loops. ~2x Opus per token -- an assumption from the brief, not a
    # published rate card.
    "fable":  (10.0, 50.0),
}

# Reasoning tokens are billed as OUTPUT. Effort scales them heavily.
EFFORT = {None: 1.0, "medium": 1.0, "high": 1.8, "xhigh": 3.0}


def cost(model, effort, tok_in, tok_out_base):
    pin, pout = PRICE[model]
    tok_out = tok_out_base * EFFORT[effort]
    return (tok_in * pin + tok_out * pout) / 1_000_000


# --- Per-invocation token assumptions --------------------------------------
# Reviewers: input-heavy (prompt + card + brief + diff + files), output-light
# (findings JSON + log + one line back), but reasoning inflates output.
REV_IN, REV_OUT = 35_000, 2_500

# Implementation / fixes: large input, large output (code + reasoning).
IMP_IN, IMP_OUT = 55_000, 12_000

# Lead turn per phase: reading counts, plans, triage files.
LEAD_IN, LEAD_OUT = 30_000, 3_000
LEAD = ("opus", "high")

# The Visual lane (reviewer-visual, Fable) reads captures and reference
# images every pass on top of the usual prompt/card/brief text -- assumption:
# ~4 named shots plus 2-3 references per review, each costing roughly what a
# few thousand tokens of text would once encoded, so call Visual's input 3x a
# text-only lane's. Output stays findings-JSON-sized.
VIS_IN, VIS_OUT = REV_IN * 3, REV_OUT


def lane(model, effort):
    tok_in, tok_out = (VIS_IN, VIS_OUT) if model == "fable" else (REV_IN, REV_OUT)
    return cost(model, effort, tok_in, tok_out)


# --- FULL LOOP --------------------------------------------------------------
full_lanes = {
    "requirements":  ("opus",   "high",  1.0),   # always
    "technical":     ("opus",   "xhigh", 1.0),   # always
    "tests":         ("sonnet", "high",  1.0),   # always
    "architecture":  ("opus",   "xhigh", 0.7),   # gated: prob applicable
    "standards":     ("sonnet", "high",  1.0),
    "security":      ("opus",   "xhigh", 0.6),
    "deadcode":      ("sonnet", "high",  0.4),
    "minimalism":    ("sonnet", "high",  0.6),
    "artifacts":     ("sonnet", "high",  0.4),
}

lite_lanes = {
    "correctness":   ("sonnet", "high",  1.0),
    "structure":     ("sonnet", "high",  1.0),
    "tests":         ("haiku",  None,    1.0),
    "security":      ("sonnet", "high",  0.6),
}


def review_round(lanes):
    return sum(lane(m, e) * p for m, e, p in lanes.values())


def expected_lanes(lanes):
    return sum(p for _, _, p in lanes.values())


# Rounds actually run (round 2+ reruns only lanes that owned findings ~ 45%).
RERUN_FRACTION = 0.45


def loop_cost(lanes, rounds, verify_prob):
    # round 1 runs all applicable lanes; subsequent (possibly fractional)
    # rounds rerun only the lanes that owned accepted findings
    extra = max(rounds - 1, 0.0)
    review = review_round(lanes) * (1 + extra * RERUN_FRACTION)

    lead = cost(*LEAD, LEAD_IN, LEAD_OUT) * (2 + rounds * 2)   # plan + triage per round
    verify = cost("opus", "high", REV_IN, REV_OUT * 1.4) * verify_prob
    return review, lead, verify


# Implementation is now IDENTICAL in both loops.
impl = (
    cost("sonnet", "high", IMP_IN, IMP_OUT)          # phase 1 implement
    + cost("sonnet", "high", IMP_IN * 0.7, IMP_OUT * 0.8)  # phase 2 tests
)


def fixes(rounds):
    return cost("sonnet", "high", IMP_IN * 0.6, IMP_OUT * 0.5) * (rounds - 0.5)


def total(lanes, rounds, verify_prob):
    r, l, v = loop_cost(lanes, rounds, verify_prob)
    return {"review": r, "lead": l, "verify": v,
            "impl": impl, "fixes": fixes(rounds),
            "total": r + l + v + impl + fixes(rounds)}


# --- UNITY LOOPS -------------------------------------------------------
# Both are fixed at 2 rounds plus a Visual-only confirmation pass (Phase 7),
# not a variable round count like the scenarios above -- the design caps
# them there deliberately. Structure is consolidated and runs round 1 only,
# so it is excluded from the round-2 rerun fraction rather than folded into
# it like the always-rerun lanes.

# Unity-lite: reused lite agents, Correctness/Tests rerun-eligible.
# Tests is reviewer-lite-tests -- haiku, no effort setting -- same as the
# base lite loop's "tests" lane above, not the sonnet tier the other
# unity-lite lane runs at.
unity_lite_rerun_lanes = {
    "correctness": ("sonnet", "high", 1.0),   # always
    # Gated on C# (runtime/editor/test code) changing -- most game changes
    # carry C#, while pure scene or asset changes do not.
    "tests":       ("haiku",  None,   0.8),
}
unity_lite_once_lanes = {
    "structure":   ("sonnet", "high", 1.0),   # round 1 only
}
# Contained changes still touch a scene sometimes, but new art direction is
# out of scope for this loop -- assume Visual applies about half the time.
UNITY_LITE_VISUAL_PROB = 0.5

# Unity (full): reused full-loop agents at the same tiers, minus Security
# (ineligible by definition) and Architecture/Standards/Dead code/Minimalism
# (folded into Structure).
unity_rerun_lanes = {
    "requirements": ("opus",   "high",  1.0),   # always
    "technical":    ("opus",   "xhigh", 0.7),   # gated
    # Gated on C# (runtime/editor/test code) changing -- most game changes
    # carry C#, while pure scene or asset changes do not.
    "tests":        ("sonnet", "high",  0.8),
    "artifacts":    ("sonnet", "high",  0.4),   # gated
}
unity_once_lanes = {
    "structure":    ("sonnet", "high", 1.0),    # round 1 only
}
# This loop's remit is new scenes/looks and multi-system work, so visual
# scope is the common case, not the exception.
UNITY_VISUAL_PROB = 0.8

# Phase 0a -- sidekick-visual (Fable) writes the scene bible. Full loop
# only, one pass, no building, but still image-heavy (reads references plus
# the existing asset inventory). Only runs when the change has visual scope
# from references or a new look, so weight it by that same probability.
BIBLE_OUT = REV_OUT * 1.5


def bible_cost(visual_prob):
    return cost("fable", None, VIS_IN, BIBLE_OUT) * visual_prob


# Phase 1 -- scene composition/lighting/framing/posing/materials build on
# Fable rather than the code sidekick, at up to two self-QA iterations per
# handoff (each iteration re-looks at a fresh capture, hence VIS_IN on top
# of implementation-sized text I/O). Modeled as an addition to, not a
# replacement of, the ordinary code-implementation cost, since most Unity
# changes carry both code and scene work.
VISUAL_IMPL_IN, VISUAL_IMPL_OUT = IMP_IN + VIS_IN, IMP_OUT
QA_ITERATIONS = 1.5  # average of "at most two"


def visual_impl_cost(visual_prob):
    return cost("fable", None, VISUAL_IMPL_IN, VISUAL_IMPL_OUT) * QA_ITERATIONS * visual_prob


# Phase 7 -- visual-only confirmation after round 2, run only when an
# accepted finding this run was visual. Recaptures affected shots and reruns
# only the Visual lane; assumption: about 40% of visual-scoped runs carry an
# accepted visual finding by round 2.
VISUAL_CONFIRM_FINDING_PROB = 0.4


def visual_confirmation_cost(visual_prob):
    return lane("fable", None) * visual_prob * VISUAL_CONFIRM_FINDING_PROB


def loop_cost_unity(rerun_lanes, once_lanes, visual_prob, rounds, verify_prob):
    extra = max(rounds - 1, 0.0)
    review_no_visual = review_round(rerun_lanes) * (1 + extra * RERUN_FRACTION) + review_round(once_lanes)
    review_visual = lane("fable", None) * visual_prob * (1 + extra * RERUN_FRACTION)
    review = review_no_visual + review_visual
    lead = cost(*LEAD, LEAD_IN, LEAD_OUT) * (2 + rounds * 2)
    verify = cost("opus", "high", REV_IN, REV_OUT * 1.4) * verify_prob
    return review, review_no_visual, lead, verify


def total_unity(rerun_lanes, once_lanes, visual_prob, rounds, verify_prob, has_bible):
    r, r_no_visual, l, v = loop_cost_unity(rerun_lanes, once_lanes, visual_prob, rounds, verify_prob)
    confirm = visual_confirmation_cost(visual_prob)
    bible = bible_cost(visual_prob) if has_bible else 0.0
    vimpl = visual_impl_cost(visual_prob)
    total_impl = impl + vimpl
    fx = fixes(rounds)
    return {"review": r, "review_no_visual": r_no_visual, "lead": l, "verify": v,
            "confirm": confirm, "bible": bible, "impl": total_impl, "fixes": fx,
            "total": r + l + v + confirm + bible + total_impl + fx}


scenarios = [
    ("Typical  (full 2 rounds / lite 1.5)", total(full_lanes, 2, 0.8),
                                            total(lite_lanes, 1.5, 0.25)),
    ("Clean    (full 1 round  / lite 1)",   total(full_lanes, 1, 0.6),
                                            total(lite_lanes, 1, 0.15)),
    ("Messy    (full 3 rounds / lite 2)",   total(full_lanes, 3, 1.0),
                                            total(lite_lanes, 2, 0.5)),
]

print(f"Expected lanes per round -- full: {expected_lanes(full_lanes):.1f}"
      f"   lite: {expected_lanes(lite_lanes):.1f}\n")

hdr = f"{'Scenario':<38}{'Full':>9}{'Lite':>9}{'Saving':>9}"
print(hdr); print("-" * len(hdr))
for name, f, l in scenarios:
    saving = (f["total"] - l["total"]) / f["total"] * 100
    print(f"{name:<38}${f['total']:>8.2f}${l['total']:>8.2f}{saving:>8.0f}%")

print("\nBreakdown, typical scenario (USD):")
f, l = scenarios[0][1], scenarios[0][2]
print(f"{'component':<14}{'full':>9}{'lite':>9}{'delta':>9}")
print("-" * 41)
for k in ("review", "lead", "verify", "impl", "fixes"):
    print(f"{k:<14}${f[k]:>8.2f}${l[k]:>8.2f}${f[k]-l[k]:>8.2f}")
print(f"{'TOTAL':<14}${f['total']:>8.2f}${l['total']:>8.2f}${f['total']-l['total']:>8.2f}")

rev_share_f = f["review"] / f["total"] * 100
impl_share_f = (f["impl"] + f["fixes"]) / f["total"] * 100
print(f"\nReview is {rev_share_f:.0f}% of a full run; "
      f"implementation+fixes is {impl_share_f:.0f}%.")

# Sensitivity: what if the diff is large (implementation dominates)?
print("\nSensitivity -- saving vs implementation size:")
_base_impl = impl
for mult in (0.25, 0.5, 1.0, 2.0, 4.0):
    impl = _base_impl * mult
    ff = total(full_lanes, 2, 0.8)
    ll = total(lite_lanes, 1.5, 0.25)
    s = (ff["total"] - ll["total"]) / ff["total"] * 100
    print(f"  implementation x{mult:<5} saving {s:>4.0f}%")
impl = _base_impl

# --- Unity loops, vs the typical full run -----------------------------------
full_typical = scenarios[0][1]
unity_scenarios = [
    ("dev-loop-unity-lite", total_unity(unity_lite_rerun_lanes, unity_lite_once_lanes,
                                         UNITY_LITE_VISUAL_PROB, 2, 0.25, has_bible=False)),
    ("dev-loop-unity",      total_unity(unity_rerun_lanes, unity_once_lanes,
                                         UNITY_VISUAL_PROB, 2, 0.5, has_bible=True)),
]

print("\nUnity loops vs the typical full run (USD):")
hdr2 = (f"{'Loop':<20}{'Review':>9}{'Lead':>7}{'Verify':>8}{'Confirm':>9}{'Bible':>7}"
        f"{'Impl':>8}{'Fixes':>7}{'Total':>9}{'vs full':>9}")
print(hdr2); print("-" * len(hdr2))
print(f"{'dev-loop (full)':<20}{full_typical['review']:>9.2f}{full_typical['lead']:>7.2f}"
      f"{full_typical['verify']:>8.2f}{0.0:>9.2f}{0.0:>7.2f}{full_typical['impl']:>8.2f}"
      f"{full_typical['fixes']:>7.2f}{full_typical['total']:>9.2f}{'1.00x':>9}")
for name, u in unity_scenarios:
    ratio = u["total"] / full_typical["total"]
    print(f"{name:<20}{u['review']:>9.2f}{u['lead']:>7.2f}{u['verify']:>8.2f}"
          f"{u['confirm']:>9.2f}{u['bible']:>7.2f}{u['impl']:>8.2f}{u['fixes']:>7.2f}"
          f"{u['total']:>9.2f}{ratio:>8.2f}x")

print(f"\nReview cost excluding the Visual lane (full has no Visual lane at all,"
      f" so this is the comparable figure vs its {full_typical['review']:.2f}):")
for name, u in unity_scenarios:
    print(f"  {name:<20} ${u['review_no_visual']:.2f}  (with Visual: ${u['review']:.2f})")
