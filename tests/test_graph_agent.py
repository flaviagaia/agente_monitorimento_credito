from __future__ import annotations

import unittest

from src.graph_agent import run_monitoring


class CreditMonitoringGraphTest(unittest.TestCase):
    def test_monitoring_flow_runs(self) -> None:
        report = run_monitoring("MON-1002")
        self.assertEqual(report["customer_id"], "MON-1002")
        self.assertIn("risk_level", report)
        self.assertIn("recommended_action", report)
        self.assertGreaterEqual(len(report["monitoring_flags"]), 1)

    def test_high_risk_customer_is_prioritized(self) -> None:
        report = run_monitoring("MON-1003")
        self.assertEqual(report["risk_level"], "alto")
        self.assertIn("monitoramento ativo", report["recommended_action"])


if __name__ == "__main__":
    unittest.main()
