import pytest

from i2p_dht_lab.bencode import bencode


def test_bencode_canonical_dict_sorting():
    assert bencode({b"z": 1, b"a": b"cat"}) == b"d1:a3:cat1:zi1ee"


def test_bencode_rejects_bool():
    with pytest.raises(TypeError):
        bencode(True)  # type: ignore[arg-type]
