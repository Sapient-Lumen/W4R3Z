from src.muc5.deckspace import deck_count, total_deck_count, DeckVector, plausibility_filter


def test_counts():
    assert deck_count(40) == 135751
    assert deck_count(60) == 635376
    assert total_deck_count() == 771127


def test_deck_validation():
    d = DeckVector(40, 20, 8, 6, 4, 2)
    d.validate()
    assert d.pitchable_blue == 20
    assert d.threats == 6
    assert plausibility_filter(d)
