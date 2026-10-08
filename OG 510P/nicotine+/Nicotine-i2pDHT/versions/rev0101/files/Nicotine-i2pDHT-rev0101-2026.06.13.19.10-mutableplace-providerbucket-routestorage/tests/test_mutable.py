from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.mutable import (
    MutableRecord,
    MutableSlotStore,
    StoreCode,
    make_bep46_value,
    make_mutable_torrent_head,
    mutable_magnet_btpk,
    signature_payload,
    target_id_bep44,
)


def test_bep44_signature_payload_vectors():
    assert signature_payload(seq=1, value=b"Hello World!") == b"3:seqi1e1:v12:Hello World!"
    assert signature_payload(seq=1, value=b"Hello World!", salt=b"foobar") == (
        b"4:salt6:foobar3:seqi1e1:v12:Hello World!"
    )


def test_bep44_and_bep46_target_vectors():
    pub = bytes.fromhex("77ff84905a91936367c01360803104f92432fcd904a43511876df5cdf3e7e548")
    assert target_id_bep44(pub).hex() == "4a533d47ec9c7d95b1ad75f576cffc641853b750"
    assert target_id_bep44(pub, b"foobar").hex() == "411eba73b6f087ca51a3795d9c8c938d365e32c1"

    bep46_pub = bytes.fromhex("8543d3e6115f0f98c944077a4493dcd543e49c739fd998550a1f614ab36ed63e")
    assert target_id_bep44(bep46_pub).hex() == "cc3f9d90b572172053626f9980ce261a850d050b"
    assert target_id_bep44(bep46_pub, bytes.fromhex("6e")).hex() == "59ee7c2cb9b4f7eb1986ee2d18fd2fdb8a56554f"


def test_ed25519_mutable_record_verifies_and_tamper_fails():
    keypair = DhtKeypair.from_seed(b"\x11" * 32)
    record = MutableRecord.create(keypair=keypair, seq=7, value={b"hello": b"world"}, salt=b"room:ambient", now=1000)
    assert record.verify()
    assert len(record.target_bep44) == 20
    assert len(record.target_i2p256) == 32
    tampered = replace(record, value={b"hello": b"mallory"})
    assert not tampered.verify()


def test_mutable_slot_store_sequence_cas_and_refresh():
    now = 1000
    keypair = DhtKeypair.from_seed(b"\x22" * 32)
    store = MutableSlotStore.empty()
    rec1 = MutableRecord.create(keypair=keypair, seq=1, value=b"one", now=now)
    rec2 = MutableRecord.create(keypair=keypair, seq=2, value=b"two", now=now + 1)

    assert store.put(rec1, now=now).code == StoreCode.ACCEPTED_NEW
    assert store.put(rec2, now=now + 1, cas=0).code == StoreCode.REJECT_CAS_MISMATCH
    assert store.put(rec2, now=now + 2, cas=1).code == StoreCode.ACCEPTED_UPDATE
    assert store.put(rec1, now=now + 3).code == StoreCode.REJECT_STALE_SEQUENCE
    assert store.put(rec2, now=now + 4).code == StoreCode.ACCEPTED_REFRESH

    same_seq_different_value = MutableRecord.create(keypair=keypair, seq=2, value=b"evil twin", now=now + 5)
    assert store.put(same_seq_different_value, now=now + 5).code == StoreCode.REJECT_EQUAL_SEQUENCE_DIFFERENT_VALUE


def test_bep46_mutable_torrent_head_shape_and_magnet():
    keypair = DhtKeypair.from_seed(b"\x33" * 32)
    info_hash = bytes.fromhex("01" * 20)
    record = make_mutable_torrent_head(keypair=keypair, info_hash=info_hash, seq=3, salt=b"feed:demo", now=1000)
    assert record.kind == "bt.bep46.mutable_torrent_head"
    assert record.value == make_bep46_value(info_hash)
    assert record.verify()
    magnet = mutable_magnet_btpk(record.public_key, record.salt)
    assert magnet.startswith("magnet:?xs=urn:btpk:")
    assert "&s=666565643a64656d6f" in magnet
