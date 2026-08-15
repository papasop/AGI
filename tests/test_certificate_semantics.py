import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_certificate_semantics.py"
AUDIT = ROOT / "audit" / "audit_repo.py"


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


class CertificateSemanticTests(unittest.TestCase):
    def make_semantic_root(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        for rel in [
            "results/reference/protocol.json",
            "results/reference/certificate.json",
            "results/reference/report.json",
            "results/reference_run_summary.json",
            "results/v0_9_3_reference/protocol.json",
            "results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json",
            "results/v0_9_3_reference/report.json",
        ]:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        return tmp, root

    def run_verifier(self, root: Path):
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--root", str(root)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def mutate_v093_certificate(self, root: Path, mutator) -> None:
        path = root / "results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutator(payload)
        write_json(path, payload)

    def mutate_v093_report(self, root: Path, mutator) -> None:
        path = root / "results/v0_9_3_reference/report.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutator(payload)
        write_json(path, payload)

    def test_real_frozen_values_pass(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("single-instance semantic certificate verifier", proc.stdout)
            self.assertIn("v0.9.3.uniform_strict_L6_descent", proc.stdout)

    def test_g1_mutated_descent_value_fails_semantically(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("uniform_dL6_dt_upper", -0.1))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("v0.9.3.uniform_strict_L6_descent", proc.stdout)
            self.assertIn("result=FAIL", proc.stdout)

    def test_g3_inconsistent_gates_and_aggregate_fail(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            def mutate(cert):
                cert["gates"]["picard_contraction"] = False
                cert["all_gates_pass"] = True

            self.mutate_v093_certificate(root, mutate)
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("v0.9.3.gates.picard_contraction", proc.stdout)
            self.assertIn("v0.9.3.all_gates_pass_equals_all_gates", proc.stdout)

    def test_missing_field_is_schema_error(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.pop("picard_contraction_factor"))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("missing required field: picard_contraction_factor", proc.stderr)

    def test_nan_is_schema_error(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("picard_contraction_factor", float("nan")))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("must be finite", proc.stderr)

    def test_infinity_is_schema_error(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("picard_contraction_factor", float("inf")))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("must be finite", proc.stderr)

    def test_string_numeric_is_schema_error_for_certificate_value(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("picard_contraction_factor", "0.003"))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("must be a finite numeric value, got str", proc.stderr)

    def test_bool_as_number_is_schema_error(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("picard_contraction_factor", True))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("must be a finite numeric value, got bool", proc.stderr)

    def test_strict_equality_threshold_is_enforced(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("certified_time_step", 2e-14))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("v0.9.3.certified_time_step", proc.stdout)

    def test_report_certificate_inconsistency_fails(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_report(root, lambda r: r.__setitem__("picard_contraction_factor", 0.25))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("v0.9.3.report_consistency.picard_contraction_factor", proc.stdout)

    def test_threshold_missing_is_schema_error(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            path = root / "results/v0_9_3_reference/protocol.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            del payload["gates"]["maximum_picard_contraction"]
            write_json(path, payload)
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("missing required field: gates.maximum_picard_contraction", proc.stderr)

    def test_all_gates_pass_false_fails_for_v093(self):
        tmp, root = self.make_semantic_root()
        with tmp:
            self.mutate_v093_certificate(root, lambda c: c.__setitem__("all_gates_pass", False))
            proc = self.run_verifier(root)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("v0.9.3.all_gates_pass_equals_all_gates", proc.stdout)


class StrictClosureTests(unittest.TestCase):
    def make_audit_root(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "results/reference").mkdir(parents=True)
        (root / "audit").mkdir()
        cert = root / "results/reference/certificate.json"
        cert.write_text('{"all_gates_pass": true, "scientific_status": "OK"}\n', encoding="utf-8")
        artifact = {
            "schema_version": "1.0",
            "artifacts": [
                {
                    "id": "cert",
                    "path": "results/reference/certificate.json",
                    "sha256": sha(cert),
                    "type": "certificate",
                    "status": "frozen",
                    "producer": "test",
                    "inputs": [],
                    "scientific_scope": "test",
                }
            ],
        }
        claims = {
            "schema_version": "1.0",
            "claims": {
                "claim": {
                    "status": "certified",
                    "description": "test",
                    "producer": "results/reference/certificate.json",
                    "protocol": "results/reference/certificate.json",
                    "inputs": ["results/reference/certificate.json"],
                    "certificate": "results/reference/certificate.json",
                    "required_certificate_fields": {"all_gates_pass": True},
                    "scope_boundary": "test",
                }
            },
        }
        write_json(root / "audit/artifact_manifest.json", artifact)
        write_json(root / "audit/claims_manifest.yaml", claims)
        rels = [
            "audit/artifact_manifest.json",
            "audit/claims_manifest.yaml",
            "results/reference/certificate.json",
        ]
        (root / "SHA256SUMS.txt").write_text("".join(f"{sha(root / rel)}  {rel}\n" for rel in sorted(rels)), encoding="utf-8")
        return tmp, root

    def run_audit(self, root: Path):
        report = root / "audit-report.json"
        proc = subprocess.run(
            [sys.executable, str(AUDIT), "--root", str(root), "--strict", "--report", str(report)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))
        return proc, payload

    def test_g4_unregistered_protected_result_file_fails_strict_audit(self):
        tmp, root = self.make_audit_root()
        with tmp:
            (root / "results/reference/unregistered.json").write_text("{}\n", encoding="utf-8")
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            failed = [c for c in payload["checks"] if c["status"] == "FAIL"]
            self.assertTrue(any(c["name"] == "protected_result_closure" for c in failed))

    @unittest.skipIf(not hasattr(os, "symlink"), "symlink unavailable")
    def test_symlink_in_protected_results_fails(self):
        tmp, root = self.make_audit_root()
        with tmp:
            os.symlink(root / "results/reference/certificate.json", root / "results/reference/link.json")
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            failed = [c for c in payload["checks"] if c["status"] == "FAIL"]
            self.assertTrue(any(c["name"] == "protected_result_closure" for c in failed))

    def test_allowed_non_science_file_outside_results_does_not_false_positive(self):
        tmp, root = self.make_audit_root()
        with tmp:
            (root / "notes").mkdir()
            (root / "notes/local.txt").write_text("not a result\n", encoding="utf-8")
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            closure = [c for c in payload["checks"] if c["name"] == "protected_result_closure"][0]
            self.assertEqual(closure["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
