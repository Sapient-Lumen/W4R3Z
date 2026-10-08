from i2p_dht_lab.admission import AdmissionMode, evaluate_identity
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity, find_work_nonce, work_bits
from i2p_dht_lab.ids import bucket_index, node_id_from_parts, xor_distance


def test_node_id_is_destination_key_and_nonce_bound():
    keypair = DhtKeypair.from_seed(b"\x01" * 32)
    identity = NodeIdentity.create(destination="dest-a", keypair=keypair)
    assert identity.node_id == node_id_from_parts("dest-a", keypair.public_key_bytes, b"")
    assert identity.node_id != node_id_from_parts("dest-b", keypair.public_key_bytes, b"")
    assert len(identity.node_id) == 32


def test_work_nonce_and_admission_decision():
    keypair = DhtKeypair.from_seed(b"\x02" * 32)
    nonce = find_work_nonce("dest-work", keypair.public_key_bytes, 8, max_tries=100_000)
    assert work_bits("dest-work", keypair.public_key_bytes, nonce) >= 8
    identity = NodeIdentity(destination="dest-work", public_key=keypair.public_key_bytes, work_nonce=nonce)
    decision = evaluate_identity(identity, mode=AdmissionMode.CONTRIBUTOR)
    assert decision.accepted
    assert decision.work_bits >= 8


def test_identity_challenge_signature():
    keypair = DhtKeypair.from_seed(b"\x03" * 32)
    identity = NodeIdentity.create(destination="dest-challenge", keypair=keypair)
    challenge = b"challenge-0001"
    signature = identity.sign_challenge(keypair, challenge)
    assert identity.verify_challenge(challenge, signature)
    assert not identity.verify_challenge(b"other", signature)


def test_xor_distance_and_bucket_index():
    local = bytes.fromhex("00" * 32)
    remote = bytes.fromhex("00" * 31 + "01")
    far = bytes.fromhex("80" + "00" * 31)
    assert xor_distance(local, remote) == 1
    assert bucket_index(local, remote) == 0
    assert bucket_index(local, far) == 255
    assert bucket_index(local, local) == -1
