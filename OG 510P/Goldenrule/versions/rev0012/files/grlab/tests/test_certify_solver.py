import unittest

from grlab.certify import CertifyError, certify_memory_one_pair


def _memory_one(
    *,
    strategy_id: str,
    p_cc: float,
    p_cd: float,
    p_dc: float,
    p_dd: float,
) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": p_cc,
        "p_cc": p_cc,
        "p_cd": p_cd,
        "p_dc": p_dc,
        "p_dd": p_dd,
    }


class CertifySolverTests(unittest.TestCase):
    def test_always_cooperate_pair(self) -> None:
        a = _memory_one(strategy_id="a", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="b", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        res = certify_memory_one_pair(a, b)
        self.assertAlmostEqual(res["avg_payoff_a"], 3.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 3.0, places=9)
        self.assertAlmostEqual(res["steady_state_distribution"][0], 1.0, places=9)

    def test_always_defect_pair(self) -> None:
        a = _memory_one(strategy_id="a", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        b = _memory_one(strategy_id="b", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        res = certify_memory_one_pair(a, b)
        self.assertAlmostEqual(res["avg_payoff_a"], 1.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 1.0, places=9)
        self.assertAlmostEqual(res["steady_state_distribution"][3], 1.0, places=9)

    def test_cooperator_vs_defector(self) -> None:
        coop = _memory_one(strategy_id="coop", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        defect = _memory_one(strategy_id="def", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        res = certify_memory_one_pair(coop, defect)
        self.assertAlmostEqual(res["avg_payoff_a"], 0.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 5.0, places=9)
        self.assertAlmostEqual(sum(res["steady_state_distribution"]), 1.0, places=9)

    def test_invalid_probability_rejected(self) -> None:
        bad = _memory_one(strategy_id="bad", p_cc=1.1, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        ok = _memory_one(strategy_id="ok", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        with self.assertRaises(CertifyError):
            certify_memory_one_pair(bad, ok)


if __name__ == "__main__":
    unittest.main()
