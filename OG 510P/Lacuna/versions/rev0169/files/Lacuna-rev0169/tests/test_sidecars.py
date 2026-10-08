from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from lacuna.sidecars import scan_sidecar_member_exact_tokens


class SidecarStreamingScanTests(unittest.TestCase):
    def test_exact_token_scan_counts_a_match_crossing_a_chunk_boundary(self) -> None:
        token = b"LACUNA_CANARY_STREAM_BOUNDARY_0123456789"
        other = b"LACUNA_CANARY_SECOND_TOKEN_ABCDEFGHIJ"
        prefix = b"x" * (64 - len(token) // 2)
        body = prefix + token + b"middle" + other + b"tail" + token
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "member.bin"
            path.write_bytes(body)
            result = scan_sidecar_member_exact_tokens(
                path,
                exact_tokens=[token, other],
                label="test member",
                error_prefix="test-sidecar",
                max_bytes=len(body),
                chunk_bytes=64,
            )
        self.assertEqual(result["size"], len(body))
        self.assertEqual(result["sha256"], hashlib.sha256(body).hexdigest())
        self.assertEqual(result["occurrence_counts"], [2, 1])


    def test_exact_token_scan_preserves_nonoverlap_for_self_overlapping_tokens(self) -> None:
        cases = (
            (b"aaaaa", b"aaa", 4),
            (b"aaaaaa", b"aaa", 4),
            (b"abababa", b"ababa", 3),
            (b"zzzzzzzz", b"zz", 3),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "member.bin"
            for index, (body, token, chunk_bytes) in enumerate(cases):
                with self.subTest(index=index, body=body, token=token):
                    path.write_bytes(body)
                    result = scan_sidecar_member_exact_tokens(
                        path,
                        exact_tokens=[token],
                        label="test member",
                        error_prefix="test-sidecar",
                        max_bytes=len(body),
                        chunk_bytes=chunk_bytes,
                    )
                    self.assertEqual(result["occurrence_counts"], [body.count(token)])

    def test_exact_token_scan_accepts_an_empty_token_set_for_digest_only(self) -> None:
        body = b"digest-only"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "member.bin"
            path.write_bytes(body)
            result = scan_sidecar_member_exact_tokens(
                path,
                exact_tokens=[],
                label="test member",
                error_prefix="test-sidecar",
                max_bytes=len(body),
                chunk_bytes=3,
            )
        self.assertEqual(result["occurrence_counts"], [])
        self.assertEqual(result["sha256"], hashlib.sha256(body).hexdigest())


if __name__ == "__main__":
    unittest.main()
