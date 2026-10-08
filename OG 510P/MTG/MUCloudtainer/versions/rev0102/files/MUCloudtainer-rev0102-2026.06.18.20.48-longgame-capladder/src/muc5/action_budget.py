from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Mapping, Sequence

from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from .decision import DecisionFrame


@dataclass(frozen=True)
class BudgetedActionSelection:
    """A subset of a legal menu selected for expensive branch rollouts.

    Action-counterfactual labels are useful, but branching every legal action can
    become wasteful when a frame has many equivalent card-choice variants.  This
    object keeps the original legal-action indices and records why each action
    survived the budget.  The learning rows must treat labels as being over this
    branched subset, not over the full legal menu.
    """

    indices: tuple[int, ...]
    reasons: Mapping[int, str]
    full_action_count: int
    budget: int

    @property
    def is_subset(self) -> bool:
        return len(self.indices) < int(self.full_action_count)


def action_diversity_key(action: Action) -> tuple[str, str, str]:
    """Coarse action group used by the budgeted counterfactual sampler.

    The grouping is intentionally semantic and stable rather than strategic.  It
    tries to keep at least one representative of each kind of legal option: pass,
    play land, cast each card/payment mode, activate each Jace mode, attack/block
    shape, and each choice-effect/card family.
    """

    kind = str(action.kind)
    p = action.params
    if kind == "PASS":
        return ("00_pass", "", "")
    if kind == "PLAY_ISLAND":
        return ("01_play_land", CARD_ISLAND, "")
    if kind == "CAST":
        card = str(p.get("card", ""))
        if card == CARD_FORCE:
            return ("02_cast_force", str(p.get("payment", "")), str(p.get("pitch_card", "")))
        return ("02_cast", card, str(p.get("mode", p.get("target_card", ""))))
    if kind == "ACTIVATE_JACE":
        return ("03_jace", str(p.get("mode", "")), str(p.get("target_state", p.get("target_player", ""))))
    if kind == "ATTACK":
        return ("04_attack", str(p.get("attack_player", p.get("player_attackers", ""))), str(p.get("attack_jace", p.get("jace_attackers", ""))))
    if kind == "BLOCK":
        return ("05_block", str(p.get("block_player_attackers", p.get("block_player", ""))), str(p.get("block_jace_attackers", p.get("block_jace", ""))))
    if kind == "CHOOSE_FOR_EFFECT":
        effect = str(p.get("effect", ""))
        cardish = str(
            p.get(
                "card",
                p.get(
                    "discard",
                    p.get("pitch_card", p.get("keep", p.get("take", p.get("choice", "")))),
                ),
            )
        )
        # Brainstorm choices can be combinatorial; group by effect plus first
        # visible card-ish payload so the budget does not only keep adjacent
        # equivalent variants.
        return ("06_choice", effect, cardish)
    return ("99_other", kind, action.compact())


def _priority(action: Action) -> tuple[int, str]:
    kind = str(action.kind)
    p = action.params
    if kind == "PASS":
        return (0, "")
    if kind == "PLAY_ISLAND":
        return (1, "")
    if kind == "CAST":
        card = str(p.get("card", ""))
        order = {CARD_COUNTERSPELL: 2, CARD_FORCE: 3, CARD_JACE: 4, CARD_OVERLORD: 5}.get(card, 6)
        return (order, action.compact())
    if kind == "ACTIVATE_JACE":
        order = {"ultimate": 7, "minus1": 8, "zero": 9, "plus2": 10}.get(str(p.get("mode", "")), 11)
        return (order, action.compact())
    if kind == "ATTACK":
        return (12, action.compact())
    if kind == "BLOCK":
        return (13, action.compact())
    if kind == "CHOOSE_FOR_EFFECT":
        return (14, action.compact())
    return (20, action.compact())


def select_budgeted_action_indices(
    frame: DecisionFrame,
    chosen_index: int,
    *,
    budget: int,
    rng: Random,
) -> BudgetedActionSelection:
    """Select a diverse legal-action subset for branch rollouts.

    Always includes the behavior policy's chosen action.  If the menu fits within
    budget, every legal action is kept.  Otherwise, the selector keeps pass/land
    anchors, one representative from as many diversity groups as possible, then
    fills remaining slots with deterministic-random leftovers.  The original
    action indices are preserved.
    """

    n = int(frame.action_count)
    if n <= 0:
        return BudgetedActionSelection(indices=tuple(), reasons={}, full_action_count=0, budget=int(budget))
    if chosen_index < 0 or chosen_index >= n:
        raise ValueError(f"chosen_index {chosen_index} outside legal menu of size {n}")
    b = max(1, min(int(budget), n))
    if n <= b:
        return BudgetedActionSelection(
            indices=tuple(range(n)),
            reasons={i: "full_menu_within_budget" for i in range(n)},
            full_action_count=n,
            budget=b,
        )

    selected: dict[int, str] = {}

    def add(idx: int, reason: str) -> None:
        if len(selected) < b and idx not in selected:
            selected[int(idx)] = reason

    add(chosen_index, "behavior_chosen")
    # Cheap anchors first.
    for idx, action in enumerate(frame.legal_actions):
        if action.kind == "PASS":
            add(idx, "anchor_pass")
        elif action.kind == "PLAY_ISLAND":
            add(idx, "anchor_play_land")
        if len(selected) >= b:
            break

    # One representative per semantic group, ordered by broad tactical category.
    reps: dict[tuple[str, str, str], int] = {}
    for idx, action in enumerate(frame.legal_actions):
        reps.setdefault(action_diversity_key(action), idx)
    rep_indices = sorted(set(reps.values()), key=lambda idx: (_priority(frame.legal_actions[idx]), idx))
    for idx in rep_indices:
        add(idx, "diversity_representative")
        if len(selected) >= b:
            break

    # Fill with random leftovers so large choice spaces do not always bias toward
    # early legal-action slots.  The caller seeds rng deterministically.
    leftovers = [i for i in range(n) if i not in selected]
    rng.shuffle(leftovers)
    for idx in leftovers:
        add(idx, "random_budget_fill")
        if len(selected) >= b:
            break

    return BudgetedActionSelection(
        indices=tuple(sorted(selected)),
        reasons=dict(selected),
        full_action_count=n,
        budget=b,
    )
