import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "audit_repo.py"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class AuditRepoTests(unittest.TestCase):
    def make_repo(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        write(root / "data" / "input.json", '{"all_gates_pass": true, "scientific_status": "OK"}\n')
        write(root / "scripts" / "producer.py", "VALUE = 2.0\n")
        artifact = {
            "schema_version": "1.0",
            "artifacts": [
                {
                    "id": "producer",
                    "path": "scripts/producer.py",
                    "sha256": sha(root / "scripts" / "producer.py"),
                    "type": "script",
                    "status": "frozen",
                    "producer": "test",
                    "inputs": [],
                    "scientific_scope": "test",
                },
                {
                    "id": "cert",
                    "path": "data/input.json",
                    "sha256": sha(root / "data" / "input.json"),
                    "type": "certificate",
                    "status": "frozen",
                    "producer": "producer",
                    "inputs": ["producer"],
                    "scientific_scope": "test",
                },
            ],
        }
        claims = {
            "schema_version": "1.0",
            "claims": {
                "test_claim": {
                    "status": "certified",
                    "description": "test",
                    "producer": "scripts/producer.py",
                    "protocol": "data/input.json",
                    "inputs": ["scripts/producer.py"],
                    "certificate": "data/input.json",
                    "required_certificate_fields": {
                        "all_gates_pass": True,
                        "scientific_status": "OK",
                    },
                    "scope_boundary": "test only",
                }
            },
        }
        write(root / "audit" / "artifact_manifest.json", json.dumps(artifact, indent=2) + "\n")
        write(root / "audit" / "claims_manifest.yaml", json.dumps(claims, indent=2) + "\n")
        sums = {
            "audit/artifact_manifest.json": sha(root / "audit" / "artifact_manifest.json"),
            "audit/claims_manifest.yaml": sha(root / "audit" / "claims_manifest.yaml"),
            "data/input.json": sha(root / "data" / "input.json"),
            "scripts/producer.py": sha(root / "scripts" / "producer.py"),
        }
        write(root / "SHA256SUMS.txt", "".join(f"{digest}  {rel}\n" for rel, digest in sorted(sums.items())))
        return tmp, root

    def run_audit(self, root, report=True, strict=True):
        report_path = root / "audit_report.json"
        cmd = [sys.executable, str(AUDIT), "--root", str(root)]
        if strict:
            cmd.append("--strict")
        if report:
            cmd += ["--report", str(report_path)]
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        payload = json.loads(report_path.read_text()) if report_path.exists() else None
        return proc, payload

    def test_normal_manifest_passes(self):
        tmp, root = self.make_repo()
        with tmp:
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(payload["all_audit_gates_pass"])

    def test_missing_file_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            (root / "data" / "input.json").unlink()
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(payload["all_audit_gates_pass"])

    def test_non_strict_reports_failures_without_failing_exit_code(self):
        tmp, root = self.make_repo()
        with tmp:
            (root / "data" / "input.json").unlink()
            proc, payload = self.run_audit(root, strict=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(payload["all_audit_gates_pass"])
            self.assertGreater(payload["summary"]["FAIL"], 0)

    def test_hash_mismatch_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "data" / "input.json", '{"all_gates_pass": false, "scientific_status": "OK"}\n')
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            names = [c["name"] for c in payload["checks"] if c["status"] == "FAIL"]
            self.assertIn("artifact_sha256", names)

    def test_absolute_path_is_found(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "scripts" / "producer.py", 'DEFAULT = "/Users/example/input.json"\n')
            # Refresh only the SHA so this isolates the absolute-path gate.
            manifest = json.loads((root / "audit" / "artifact_manifest.json").read_text())
            manifest["artifacts"][0]["sha256"] = sha(root / "scripts" / "producer.py")
            write(root / "audit" / "artifact_manifest.json", json.dumps(manifest, indent=2) + "\n")
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("absolute_runtime_paths", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_missing_certificate_has_no_fallback(self):
        tmp, root = self.make_repo()
        with tmp:
            claims = json.loads((root / "audit" / "claims_manifest.yaml").read_text())
            claims["claims"]["test_claim"]["certificate"] = "data/missing.json"
            write(root / "audit" / "claims_manifest.yaml", json.dumps(claims, indent=2) + "\n")
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("claim_certificate_exists", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_hardcoded_all_gates_pass_is_flagged(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "scripts" / "extra.py", "all_gates_pass = True\n")
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            hardcoded = [c for c in payload["checks"] if c["name"] == "hardcoded_result_screen"][0]
            self.assertEqual(hardcoded["status"], "WARNING")

    def test_multiline_hardcoded_all_gates_pass_is_flagged_by_ast(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "scripts" / "extra.py", "result = {\n    'all_gates_pass':\n        True,\n}\n")
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            hardcoded = [c for c in payload["checks"] if c["name"] == "hardcoded_result_screen"][0]
            self.assertEqual(hardcoded["status"], "WARNING")
            self.assertTrue(any("hardcoded_all_gates_pass_true" in item for item in hardcoded["evidence"]))

    def test_generic_audit_allow_does_not_hide_static_risk(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "scripts" / "extra.py", "all_gates_pass = True  # audit: allow\n")
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            hardcoded = [c for c in payload["checks"] if c["name"] == "hardcoded_result_screen"][0]
            self.assertEqual(hardcoded["status"], "WARNING")

    def test_structured_audit_allow_hides_line_regex_static_risk(self):
        tmp, root = self.make_repo()
        with tmp:
            write(
                root / "docs" / "note.md",
                "candidate margin is 1.25e-4  # audit: allow hardcoded_result_screen; reason=test fixture\n",
            )
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            hardcoded = [c for c in payload["checks"] if c["name"] == "hardcoded_result_screen"][0]
            self.assertEqual(hardcoded["status"], "PASS")

    def test_artifact_dependency_self_cycle_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            manifest = json.loads((root / "audit" / "artifact_manifest.json").read_text())
            manifest["artifacts"][0]["inputs"] = ["producer"]
            write(root / "audit" / "artifact_manifest.json", json.dumps(manifest, indent=2) + "\n")
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("artifact_dependency_cycle", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_artifact_dependency_indirect_cycle_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            manifest = json.loads((root / "audit" / "artifact_manifest.json").read_text())
            manifest["artifacts"][0]["inputs"] = ["cert"]
            manifest["artifacts"][1]["inputs"] = ["producer"]
            write(root / "audit" / "artifact_manifest.json", json.dumps(manifest, indent=2) + "\n")
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("artifact_dependency_cycle", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_claim_nonexistent_input_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            claims = json.loads((root / "audit" / "claims_manifest.yaml").read_text())
            claims["claims"]["test_claim"]["inputs"].append("data/absent.json")
            write(root / "audit" / "claims_manifest.yaml", json.dumps(claims, indent=2) + "\n")
            write(root / "SHA256SUMS.txt", (root / "SHA256SUMS.txt").read_text().replace(
                sha(root / "audit" / "claims_manifest.yaml"),
                sha(root / "audit" / "claims_manifest.yaml"),
            ))
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("claim_input_resolves", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_audit_status_is_not_scientific_status(self):
        tmp, root = self.make_repo()
        with tmp:
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("all_audit_gates_pass", payload)
            self.assertNotIn("all_gates_pass", payload)

    def test_malformed_json_fails(self):
        tmp, root = self.make_repo()
        with tmp:
            write(root / "data" / "input.json", "{bad json\n")
            manifest = json.loads((root / "audit" / "artifact_manifest.json").read_text())
            manifest["artifacts"][1]["sha256"] = sha(root / "data" / "input.json")
            write(root / "audit" / "artifact_manifest.json", json.dumps(manifest, indent=2) + "\n")
            lines = []
            for rel in ["audit/artifact_manifest.json", "audit/claims_manifest.yaml", "data/input.json", "scripts/producer.py"]:
                lines.append(f"{sha(root / rel)}  {rel}\n")
            write(root / "SHA256SUMS.txt", "".join(lines))
            proc, payload = self.run_audit(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("artifact_json_parse", [c["name"] for c in payload["checks"] if c["status"] == "FAIL"])

    def test_dirty_worktree_is_reported(self):
        tmp, root = self.make_repo()
        with tmp:
            subprocess.run(["git", "-C", str(root), "init"], check=True, stdout=subprocess.PIPE)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True, stdout=subprocess.PIPE)
            subprocess.run(
                ["git", "-C", str(root), "-c", "user.name=Audit", "-c", "user.email=audit@example.test", "commit", "-m", "init"],
                check=True,
                stdout=subprocess.PIPE,
            )
            write(root / "untracked.txt", "dirty\n")
            proc, payload = self.run_audit(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(payload["dirty_status"])


if __name__ == "__main__":
    unittest.main()
