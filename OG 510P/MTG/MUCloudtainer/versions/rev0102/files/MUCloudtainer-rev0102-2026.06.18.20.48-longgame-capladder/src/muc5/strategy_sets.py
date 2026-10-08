from __future__ import annotations

from pathlib import Path
from typing import List

from .deckspace import DeckVector
from .mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from .payoff import StrategyBundle, load_seed_decks


def code_policy_strategy_bundles(seed_decks_path: str | Path, *, revision_suffix: str = "rev0013") -> List[StrategyBundle]:
    """Reusable public/code-policy smoke population.

    rev0013 defined this inside a script. rev0014 promotes it to a module so
    payoff, statistical gates, and future population tools evaluate the same
    bundles without copy/paste drift.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("pub_fjace_bal", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "heuristic", POLICY_LAND_BAND),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_clock_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "code_overlord_clock_rev0013", POLICY_LAND_BAND),
        StrategyBundle("code_force_sixty", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "code_force_conservative_rev0013", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace_60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
    ]


def statgate_probe_strategy_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """Slightly larger than old smoke, still small enough for frequent reruns."""

    decks = load_seed_decks(seed_decks_path)
    return code_policy_strategy_bundles(seed_decks_path) + [
        StrategyBundle("pub_patient_sixty", "sixty_drawless_control_big", decks["sixty_drawless_control_big"], "patient", POLICY_LAND_BAND),
        StrategyBundle("pub_threat_overlord", "sixty_overlord_heavy", decks["sixty_overlord_heavy"], "threat_rush", POLICY_LAND_BAND_BUSINESS),
    ]


def ranker_mixed_strategy_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0022 mixed public/code/ranker population for racing.

    The point is not to crown a champion from one smoke table.  It gives the
    sequential-race and meta-rank machinery a population containing three policy
    families over overlapping deck shapes: readable public profiles, readable
    code policies, and frozen/blended action-ranker policies.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("ranker_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "linear_ranker_rev0021", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("ranker_threat_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "ranker_blend_threat_rev0022", POLICY_LAND_BAND),
        StrategyBundle("ranker_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "ranker_blend_counter_rev0022", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("ranker_patient_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "ranker_blend_patient_rev0022", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND),
        StrategyBundle("pub_patient_sixty", "sixty_drawless_control_big", decks["sixty_drawless_control_big"], "patient", POLICY_LAND_BAND),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("code_clock_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "code_overlord_clock_rev0013", POLICY_LAND_BAND),
        StrategyBundle("code_force_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "code_force_conservative_rev0013", POLICY_LAND_BAND_BUSINESS),
    ]


def ranker_race_candidates(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """Small rev0022 candidate panel focused on ranker variants."""

    bundles = ranker_mixed_strategy_bundles(seed_decks_path)
    wanted = {"ranker_fjace", "ranker_threat_fovr", "ranker_counter_wall", "ranker_patient_jace60", "code_clock_fovr", "code_jace60"}
    return [b for b in bundles if b.strategy_id in wanted]


def ranker_race_benchmarks(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """Stable rev0022 benchmark opponents for sequential racing."""

    bundles = ranker_mixed_strategy_bundles(seed_decks_path)
    wanted = {"pub_counter_wall", "pub_threat_overlord", "pub_patient_sixty", "code_force_wall", "code_clock_fovr", "code_jace60"}
    return [b for b in bundles if b.strategy_id in wanted]


def mapelite_ranker_variant_bundles(archive_path: str | Path, *, limit_cells: int = 3) -> List[StrategyBundle]:
    """Create same-deck/different-pilot bundles from top MAP-Elites cells.

    This separates the construction question from the pilot question: take a few
    diverse archived decks, then run public/code/ranker controllers on the same
    deck shell.  It is intentionally tiny because these bundles are meant to be
    thrown into promotion-gated races often.
    """

    import csv

    out: List[StrategyBundle] = []
    with Path(archive_path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    # Prefer the top rows, but keep distinct descriptor cells so one clump does
    # not dominate the mini-panel.
    seen: set[tuple[str, str, str]] = set()
    selected = []
    for row in rows:
        key = (str(row.get("desc_size")), str(row.get("desc_threat_bin")), str(row.get("desc_force_bin")))
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) >= limit_cells:
            break
    for idx, row in enumerate(selected):
        deck = DeckVector(
            int(row["deck_size"]),
            int(row["island"]),
            int(row["counterspell"]),
            int(row["force"]),
            int(row["jace"]),
            int(row["overlord"]),
        )
        deck.validate()
        label = f"me{idx:02d}"
        base_policy = POLICY_LAND_BAND_BUSINESS if deck.size == 40 or deck.force >= 8 else POLICY_LAND_BAND
        out.extend([
            StrategyBundle(f"{label}_ranker", f"mapelite_{label}", deck, "linear_ranker_rev0021", base_policy),
            StrategyBundle(f"{label}_ranker_threat", f"mapelite_{label}", deck, "ranker_blend_threat_rev0022", base_policy),
            StrategyBundle(f"{label}_code_clock", f"mapelite_{label}", deck, "code_overlord_clock_rev0013", base_policy),
            StrategyBundle(f"{label}_pub_counter", f"mapelite_{label}", deck, "counter_happy", base_policy),
        ])
    return out



def mlp_ranker_probe_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0023 mixed population for testing the first non-linear ranker.

    The MLP ranker should be evaluated beside the linear ranker, blended
    rankers, readable public profiles, and code-policy baselines.  These bundles
    are deliberately small enough for frequent promotion-gated smoke runs.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("mlp_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "mlp_ranker_rev0023", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("mlp_threat_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "mlp_ranker_blend_threat_rev0023", POLICY_LAND_BAND),
        StrategyBundle("mlp_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "mlp_ranker_blend_counter_rev0023", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("linear_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "linear_ranker_rev0021", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("linear_threat_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "ranker_blend_threat_rev0022", POLICY_LAND_BAND),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
    ]


def mulligan_policy_gate_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0023 same-shell mulligan policy panel.

    Every shell is repeated with keep-always, land-band, and land-band-business.
    This keeps mulligan policy visible as part of the strategy bundle instead of
    letting it silently contaminate deck/pilot comparisons.
    """

    decks = load_seed_decks(seed_decks_path)
    shells = [
        ("fjace_code", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013"),
        ("overlord_threat", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush"),
        ("wall_counter", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy"),
    ]
    policies = [
        ("keep", POLICY_KEEP_ALWAYS),
        ("band", POLICY_LAND_BAND),
        ("business", POLICY_LAND_BAND_BUSINESS),
    ]
    out: List[StrategyBundle] = []
    for shell_id, deck_name, deck, agent in shells:
        for suffix, policy in policies:
            out.append(StrategyBundle(f"{shell_id}_{suffix}", deck_name, deck, agent, policy))
    return out


def learned_mulligan_gate_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0024 same-shell panel adding the learned mulligan ranker.

    The learned pregame policy is evaluated as a first-class bundle component
    beside the three deterministic London-mulligan baselines.  The deck and
    gameplay pilot are held fixed inside each shell, so the table can isolate
    mulligan-agency effects from construction/pilot effects.
    """

    decks = load_seed_decks(seed_decks_path)
    learned = "mulligan_ranker_rev0024"
    shells = [
        ("fjace_code", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013"),
        ("overlord_threat", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush"),
        ("wall_counter", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy"),
    ]
    policies = [
        ("keep", POLICY_KEEP_ALWAYS),
        ("band", POLICY_LAND_BAND),
        ("business", POLICY_LAND_BAND_BUSINESS),
        ("learned", learned),
    ]
    out: List[StrategyBundle] = []
    for shell_id, deck_name, deck, agent in shells:
        for suffix, policy in policies:
            out.append(StrategyBundle(f"{shell_id}_{suffix}", deck_name, deck, agent, policy))
    return out


def outcome_ranker_probe_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0025 population for outcome-weighted action-ranker tests.

    This deliberately mixes baseline public/code policies, imitation rankers, the
    rev0023 MLP, and the new outcome-weighted ranker variants.  It is small
    enough for frequent promotion-gated smoke runs but broad enough to expose
    whether outcome weighting is useful or merely a noisy imitation variant.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("outcome_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "outcome_linear_ranker_rev0025", "mulligan_ranker_rev0024"),
        StrategyBundle("outcome_threat_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "outcome_ranker_blend_threat_rev0025", "mulligan_ranker_rev0024"),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("mlp_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "mlp_ranker_rev0023", "mulligan_ranker_rev0024"),
        StrategyBundle("mlp_threat_fovr", "forty_overlord_impending", decks["forty_overlord_impending"], "mlp_ranker_blend_threat_rev0023", POLICY_LAND_BAND),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
    ]


def mulligan_outcome_gate_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0027 same-shell panel adding the terminal-outcome mulligan ranker.

    This isolates pregame learning by holding each deck/pilot shell fixed and
    varying only the mulligan agent.  The rev0024 ranker remains as the
    pseudo-oracle-seeded baseline; rev0027 adds a ranker fitted from terminal
    game outcomes.
    """

    decks = load_seed_decks(seed_decks_path)
    pseudo = "mulligan_ranker_rev0024"
    outcome = "mulligan_outcome_ranker_rev0027"
    shells = [
        ("fjace_code", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013"),
        ("overlord_threat", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush"),
        ("wall_counter", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy"),
    ]
    policies = [
        ("keep", POLICY_KEEP_ALWAYS),
        ("band", POLICY_LAND_BAND),
        ("business", POLICY_LAND_BAND_BUSINESS),
        ("pseudo", pseudo),
        ("outcome", outcome),
    ]
    out: List[StrategyBundle] = []
    for shell_id, deck_name, deck, agent in shells:
        for suffix, policy in policies:
            out.append(StrategyBundle(f"{shell_id}_{suffix}", deck_name, deck, agent, policy))
    return out


def counterfactual_mulligan_gate_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0029 same-shell panel adding first-look counterfactual mulligan.

    The new policy only changes the first keep/take decision using paired
    keep-vs-mulligan branch data; later bottom/subsequent London-mulligan
    choices delegate to the rev0027 outcome mulligan ranker.  The panel keeps
    deck and gameplay pilot fixed inside each shell so the pregame policy is the
    main varying component.
    """

    decks = load_seed_decks(seed_decks_path)
    pseudo = "mulligan_ranker_rev0024"
    outcome = "mulligan_outcome_ranker_rev0027"
    counterfactual = "mulligan_counterfactual_ranker_rev0029"
    shells = [
        ("fjace_code", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013"),
        ("overlord_threat", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush"),
        ("wall_counter", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy"),
    ]
    policies = [
        ("keep", POLICY_KEEP_ALWAYS),
        ("band", POLICY_LAND_BAND),
        ("business", POLICY_LAND_BAND_BUSINESS),
        ("pseudo", pseudo),
        ("outcome", outcome),
        ("cf", counterfactual),
    ]
    out: List[StrategyBundle] = []
    for shell_id, deck_name, deck, agent in shells:
        for suffix, policy in policies:
            out.append(StrategyBundle(f"{shell_id}_{suffix}", deck_name, deck, agent, policy))
    return out


def repeated_counterfactual_mulligan_gate_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0030 same-shell panel adding repeated-rollout counterfactual mulligan.

    The repeated policy is trained from averaged keep-vs-mulligan branch rollouts
    for the same first seven-card look.  It remains first-look only; later
    mulligans and bottom choices delegate to the rev0027 outcome mulligan ranker.
    """

    decks = load_seed_decks(seed_decks_path)
    pseudo = "mulligan_ranker_rev0024"
    outcome = "mulligan_outcome_ranker_rev0027"
    cf = "mulligan_counterfactual_ranker_rev0029"
    repeat_cf = "mulligan_repeated_counterfactual_ranker_rev0030"
    shells = [
        ("fjace_code", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013"),
        ("overlord_threat", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush"),
        ("wall_counter", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy"),
    ]
    policies = [
        ("keep", POLICY_KEEP_ALWAYS),
        ("band", POLICY_LAND_BAND),
        ("business", POLICY_LAND_BAND_BUSINESS),
        ("pseudo", pseudo),
        ("outcome", outcome),
        ("cf", cf),
        ("repeatcf", repeat_cf),
    ]
    out: List[StrategyBundle] = []
    for shell_id, deck_name, deck, agent in shells:
        for suffix, policy in policies:
            out.append(StrategyBundle(f"{shell_id}_{suffix}", deck_name, deck, agent, policy))
    return out


def mapelite_mulligan_variant_bundles(archive_path: str | Path, *, limit_cells: int = 3) -> List[StrategyBundle]:
    """rev0032 MAP-Elites deck shells crossed with current pilot/mulligan variants.

    This panel is deliberately not a giant metagame sweep.  It asks a narrower
    question: when MAP-Elites proposes a construction shell, do code/public/
    learned-ranker pilots and repeated-counterfactual mulligan policies exploit
    the same shell differently?  The answer should be evaluated through the same
    public DecisionFrame + replay/C++ gates as all other strategies.
    """

    import csv

    rows = list(csv.DictReader(Path(archive_path).open(newline="")))
    selected = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("desc_size")),
            str(row.get("desc_land_bin")),
            str(row.get("desc_threat_bin")),
            str(row.get("desc_force_bin")),
        )
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) >= limit_cells:
            break

    outcome_mull = "mulligan_outcome_ranker_rev0027"
    repeat_cf_mull = "mulligan_repeated_counterfactual_ranker_rev0030"
    out: List[StrategyBundle] = []
    for idx, row in enumerate(selected):
        deck = DeckVector(
            int(row["deck_size"]),
            int(row["island"]),
            int(row["counterspell"]),
            int(row["force"]),
            int(row["jace"]),
            int(row["overlord"]),
        )
        deck.validate()
        label = f"mev{idx:02d}"
        deck_name = f"mapelite_variant_{label}"
        # Four deliberately different controllers/mulligan pairings on the same
        # construction.  This keeps construction-vs-pilot-vs-pregame effects
        # visible without exploding the panel size.
        out.extend([
            StrategyBundle(f"{label}_code_business", deck_name, deck, "code_overlord_clock_rev0013", POLICY_LAND_BAND_BUSINESS),
            StrategyBundle(f"{label}_counter_outcome", deck_name, deck, "counter_happy", outcome_mull),
            StrategyBundle(f"{label}_outcome_repeatcf", deck_name, deck, "outcome_ranker_blend_counter_rev0025", repeat_cf_mull),
            StrategyBundle(f"{label}_mlp_repeatcf", deck_name, deck, "mlp_ranker_blend_threat_rev0023", repeat_cf_mull),
        ])
    return out


def counterfactual_action_ranker_probe_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0033 panel for action-counterfactual gameplay rankers.

    The rev0033 model is trained from branch rollouts over unchosen legal
    gameplay actions rather than pure imitation.  This panel evaluates it as an
    ordinary public strategy-bundle component beside outcome/MLP/code/public
    baselines.  Smoke standings are diagnostic; promotion/statistical/replay/C++
    gates still decide whether rows are usable.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0033", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0033", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0033", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("mlp_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "mlp_ranker_blend_threat_rev0023", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
    ]


def scaled_counterfactual_action_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0034 panel for scaled action-counterfactual gameplay rankers.

    rev0034 uses the same public feature/action interface as rev0033, but is
    trained from a larger branch-rollout label budget with explicit label-noise
    diagnostics.  This panel keeps the new ranker beside rev0033/outcome/MLP/code
    baselines so payoff changes are attributable to the new counterfactual data,
    not a totally different opponent set.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf34_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0034", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf34_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0034", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf34_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0034", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf33_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0033", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("mlp_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "mlp_ranker_blend_threat_rev0023", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
    ]


def budgeted_counterfactual_action_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0035 panel for budgeted high-branch action-counterfactual rankers.

    rev0035 keeps the rev0034 full-menu labels but also admits high-branching
    frames through a small diverse budget.  This panel evaluates the new ranker
    beside rev0034/rev0033/outcome/MLP/code baselines while keeping mulligan
    policies explicit.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf35_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0035", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf35_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0035", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf35_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0035", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf34_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0034", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("mlp_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "mlp_ranker_blend_threat_rev0023", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
    ]

def adaptive_counterfactual_action_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0036 panel for adaptive/racing action-counterfactual rankers.

    rev0036 spends extra branch rollouts on current top contenders rather than
    giving every action a fixed rollout budget.  This panel keeps the new model
    beside the best recent counterfactual/outcome/code baselines.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf36_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0036", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf36_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0036", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf36_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0036", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf35_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0035", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf34_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0034", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
    ]


def disagreement_counterfactual_action_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0038 panel for disagreement-screened action-counterfactual rankers.

    rev0038 samples gameplay frames where several public-safe policies disagree,
    then branches those legal alternatives offline.  This panel evaluates the new
    disagreement-screened ranker beside recent counterfactual/outcome/code
    baselines while keeping mulligan policies explicit.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf38_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0038", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf38_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0038", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf38_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0038", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf36_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0036", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND_BUSINESS),
    ]


def yield_counterfactual_action_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0047 panel for yield-screened action-counterfactual rankers.

    rev0047 uses the rev0046 label-yield queue as a production-shaped collector:
    public frame queueing -> online branch racing -> C++ transition shadow ->
    JSON-backed counterfactual ranker.  This panel evaluates that new ranker
    beside recent outcome/counterfactual/code/public baselines.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf47_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0047", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf47_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0047", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf47_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0047", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf34_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0034", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf38_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0038", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND_BUSINESS),
    ]

def terminal_clean_yield_ranker_bundles(seed_decks_path: str | Path) -> List[StrategyBundle]:
    """rev0049 terminal-clean panel for yield-screened counterfactual rankers.

    rev0049 keeps the rev0047/yield-screened gameplay-policy question but
    evaluates it at the terminal-clean decision ceiling by default rather than
    relying on a lower-ceiling smoke panel plus rescue after the fact.
    """

    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("cf49_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "counterfactual_linear_ranker_rev0049", "mulligan_repeated_counterfactual_ranker_rev0030"),
        StrategyBundle("cf49_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0049", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf49_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "counterfactual_ranker_blend_threat_rev0049", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("cf47_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0047", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("cf34_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counterfactual_ranker_blend_counter_rev0034", "mulligan_outcome_ranker_rev0027"),
        StrategyBundle("outcome_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "outcome_ranker_blend_counter_rev0025", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND_BUSINESS),
    ]

