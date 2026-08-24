#!/usr/bin/env python3
"""Estimate cost difference between dev-loop (full) and dev-loop-lite.

All token figures are assumptions, labelled below. The structure matters more
than the absolute numbers -- change the assumptions and re-run.
"""

# --- Pricing, USD per million tokens ---------------------------------------
PRICE = {
    "opus":   (5.0,  25.0),
    "sonnet": (3.0,  15.0),
    "haiku":  (1.0,   5.0),
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


def lane(model, effort):
    return cost(model, effort, REV_IN, REV_OUT)


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
