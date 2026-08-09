from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = (
    ROOT
    / "results"
    / "post_publication"
    / "prospective"
    / "pulser_wiener"
    / "pulser_shot_delay_stability_map_v1_3_console_transcript.md"
)
CANONICAL_REPORT = TRANSCRIPT.with_name(
    "pulser_shot_delay_stability_map_v1_3.json"
)


class PulserWienerV13TranscriptTest(unittest.TestCase):
    def test_v13_transcript_records_declared_protocol_summary(self):
        text = TRANSCRIPT.read_text(encoding="utf-8")

        self.assertIn(
            "d11a531e3dbeb71941ba0f3de58391f9ef94b860735198774572a4a153d4e79f",
            text,
        )
        self.assertEqual(
            len(re.findall(r"^\[\d{3}/048\]", text, re.MULTILINE)), 48
        )

        required_literals = [
            '"grid_cell_count": 12',
            '"replicate_run_count": 48',
            '"backend_exact_probability_executions": 1979',
            '"minimum_estimated_jacobian_singular_value": 0.002623344893051062',
            '"positive_net_recovery_fraction": 0.75',
            '"low_shot_memory_benefit_seed_fraction": 1.0',
            '"20260813":',
            '"best_positive_delay": 1',
            '"K_improvement_over_zero_delay": 0.187415753231864',
            '"20260829":',
            '"best_positive_delay": 3',
            '"K_improvement_over_zero_delay": 0.49722571107544106',
            '"agreement_fraction": 0.5',
            "-1.8939193922776065",
            "2.4447374950368252",
            '"scientific_status": "SHOT_DELAY_MEMORY_STABILITY_MAP_SUPPORTED"',
        ]
        for literal in required_literals:
            self.assertIn(literal, text)

    def test_v13_canonical_report_is_not_reconstructed_from_transcript(self):
        self.assertFalse(CANONICAL_REPORT.exists())
