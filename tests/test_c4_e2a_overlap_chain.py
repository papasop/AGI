import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
E2A_REPORT = (
    ROOT
    / "results"
    / "post_publication"
    / "control_extension"
    / "c4"
    / "c4_e2a_arb_multichart_overlap_chain_v1_0.json"
)


class C4E2aOverlapChainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(E2A_REPORT.read_text(encoding="utf-8"))

    def test_status_counts_and_gates(self):
        report = self.report
        self.assertTrue(report["all_gates_pass"])
        self.assertEqual(
            report["scientific_status"],
            "C4_E2A_ARB_MULTICHART_ATLAS_OVERLAP_CHAIN_CERTIFIED",
        )
        self.assertEqual(report["summary"]["chart_count"], 9)
        self.assertEqual(report["summary"]["transition_count"], 8)
        self.assertEqual(len(report["transition_certificates"]), 8)
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(
            sum(
                item["gates"]["positive_volume_overlap_box"]
                for item in report["transition_certificates"]
            ),
            8,
        )

    def test_numeric_reference_values(self):
        summary = self.report["summary"]
        self.assertEqual(
            summary["maximum_neumann_defect_upper"],
            0.018601705183309603,
        )
        self.assertEqual(
            summary["minimum_local_residence_time_lower"],
            6.050195285542712e-10,
        )
        self.assertEqual(
            summary["aggregate_local_residence_budget_lower"],
            4.844642545380921e-09,
        )
        self.assertTrue(summary["aggregate_budget_is_not_a_continuation_time"])

    def test_claim_boundary_excludes_flowpipe_continuation(self):
        boundary = self.report["claim_boundary"].lower()
        next_step = self.report["required_next_step"].lower()
        self.assertIn("does not transport an interval flowpipe", boundary)
        self.assertIn("not a certified continuation horizon", boundary)
        self.assertIn("c4-e2b", next_step)
        self.assertIn("validated ode integrator", next_step)
        self.assertIn("flowpipe", next_step)


if __name__ == "__main__":
    unittest.main()
