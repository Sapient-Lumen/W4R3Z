from src.muc5.deckspace import DeckVector
from src.muc5.probability import hypergeom_at_least, prob_force_with_pitch, deck_probe


def test_hypergeom_sanity_edges():
    assert hypergeom_at_least(40, 0, 7, 1) == 0.0
    assert hypergeom_at_least(40, 40, 7, 1) == 1.0
    assert hypergeom_at_least(40, 10, 0, 1) == 0.0


def test_force_pitch_requires_another_blue_card():
    all_force_no_pitch = DeckVector(40, 39, 0, 1, 0, 0)
    assert prob_force_with_pitch(all_force_no_pitch, 7) == 0.0
    many_force = DeckVector(40, 30, 0, 10, 0, 0)
    assert prob_force_with_pitch(many_force, 7) > 0.0


def test_deck_probe_returns_bounded_probabilities():
    d = DeckVector(40, 24, 6, 4, 3, 3)
    probe = deck_probe(d)
    for key, value in probe.to_row().items():
        if key.startswith("p_") or key == "crude_probe_score":
            assert 0.0 <= value <= 1.0, key
