#!/usr/bin/env python3
"""Read-only repository audit entrypoint.

This tool verifies repository integrity and provenance metadata. It does not
run Arb, Picard, Krawczyk, Lohner, or any other scientific computation.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


VERSION = "1.0"
ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("PASS", "WARNING", "FAIL", "NOT CHECKED")
ABSOLUTE_RUNTIME_RE = re.compile(r"(/Users/|/content(?:/|\b)|/private/tmp(?:/|\b)|/tmp(?:/|\b)|[A-Za-z]:\\\\)")
ALLOW_COMMENT_RE = re.compile(r"audit:\s*allow", re.IGNORECASE)
HARDCODE_PATTERNS = [
    ("hardcoded_all_gates_pass_true", re.compile(r"all_gates_pass\s*[=:]\s*True\b")),
    ("hardcoded_certified_status", re.compile(r"scientific_status\s*[=:].*CERTIFIED")),
    ("float_json_to_interval_boundary", re.compile(r"float\s*\(\s*json|arb\s*\(\s*float\s*\(")),
    ("binary64_linear_algebra_boundary", re.compile(r"\b(expm|pinv|lstsq|svd|eig|roots?)\b.*\b(float|np\.|numpy\.)")),
    ("candidate_or_margin_constant", re.compile(r"\b(candidate|endpoint|margin|radius|rank|gate|PASS)\b.*[-+]?\d+\.\d+(?:e[-+]?\d+)?", re.IGNORECASE)),
]


@dataclass
class Check:
    name: str
    status: str
    message: str
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "evidence": self.evidence,
        }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_claims(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "claims_manifest.yaml is intentionally JSON-compatible YAML; "
            f"parse failed at line {exc.lineno}: {exc.msg}"
        ) from exc


def git_text(root: Path, args: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return 127, "git executable not found"
    output = completed.stdout.strip() or completed.stderr.strip()
    return completed.returncode, output


def relpath_ok(path: str) -> bool:
    p = Path(path)
    return not p.is_absolute() and ".." not in p.parts and path not in ("", ".")


def read_sha_manifest(path: Path) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    errors: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        if "  " not in line:
            errors.append(f"line {lineno}: missing double-space separator")
            continue
        digest, rel = line.split("  ", 1)
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"line {lineno}: invalid SHA-256 digest for {rel}")
            continue
        if rel in entries and entries[rel] != digest:
            errors.append(f"line {lineno}: conflicting duplicate path {rel}")
        entries[rel] = digest
    return entries, errors


def load_artifacts(root: Path) -> tuple[list[dict[str, Any]], list[Check]]:
    path = root / "audit" / "artifact_manifest.json"
    checks: list[Check] = []
    if not path.is_file():
        checks.append(Check("artifact_manifest_exists", "FAIL", "audit/artifact_manifest.json is missing"))
        return [], checks
    try:
        manifest = read_json(path)
    except Exception as exc:  # noqa: BLE001 - report parse failure
        checks.append(Check("artifact_manifest_parse", "FAIL", str(exc), [str(path)]))
        return [], checks
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        checks.append(Check("artifact_manifest_schema", "FAIL", "artifacts must be a list", [str(path)]))
        return [], checks
    checks.append(Check("artifact_manifest_parse", "PASS", f"loaded {len(artifacts)} artifacts", [str(path)]))
    return artifacts, checks


def check_artifact_files(root: Path, artifacts: list[dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    ids: set[str] = set()
    paths_seen: dict[str, str] = {}
    for artifact in artifacts:
        aid = str(artifact.get("id", ""))
        rel = str(artifact.get("path", ""))
        status = artifact.get("status")
        if not aid:
            checks.append(Check("artifact_id_present", "FAIL", "artifact without id", [rel]))
        elif aid in ids:
            checks.append(Check("artifact_id_unique", "FAIL", f"duplicate artifact id {aid}", [rel]))
        ids.add(aid)
        if not relpath_ok(rel):
            checks.append(Check("artifact_path_is_repository_relative", "FAIL", f"invalid artifact path {rel}", [aid]))
            continue
        if rel in paths_seen and paths_seen[rel] != aid:
            checks.append(Check("artifact_path_unique", "FAIL", f"path {rel} used by multiple artifacts", [paths_seen[rel], aid]))
        paths_seen[rel] = aid
        path = root / rel
        if status == "missing":
            if path.exists():
                checks.append(Check("missing_artifact_absent", "FAIL", "artifact marked missing exists", [rel]))
            else:
                checks.append(Check("missing_artifact_absent", "PASS", "missing artifact is explicitly absent", [rel]))
            continue
        if not path.is_file():
            checks.append(Check("artifact_exists", "FAIL", "declared artifact missing", [rel]))
            continue
        expected = artifact.get("sha256")
        actual = sha256_file(path)
        if expected != actual:
            checks.append(Check("artifact_sha256", "FAIL", f"SHA mismatch for {rel}", [f"expected={expected}", f"actual={actual}"]))
        else:
            checks.append(Check("artifact_sha256", "PASS", "SHA matches", [rel]))
        if artifact.get("type") in {"certificate", "diagnostic", "protocol"} or rel.endswith(".json"):
            try:
                read_json(path)
                checks.append(Check("artifact_json_parse", "PASS", "JSON parses without rewriting values", [rel]))
            except Exception as exc:  # noqa: BLE001
                checks.append(Check("artifact_json_parse", "FAIL", f"malformed JSON: {exc}", [rel]))
    id_or_path = ids | set(paths_seen)
    for artifact in artifacts:
        rel = str(artifact.get("path", ""))
        for dep in artifact.get("inputs", []) or []:
            dep_text = str(dep)
            if dep_text not in id_or_path:
                checks.append(Check("artifact_dependency_resolves", "FAIL", f"unresolved dependency {dep_text}", [rel]))
            else:
                checks.append(Check("artifact_dependency_resolves", "PASS", f"dependency {dep_text} resolves", [rel]))
    return checks


def check_certificate_fields(root: Path, claims: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    for claim_id, claim in (claims.get("claims") or {}).items():
        certificate = claim.get("certificate")
        if not certificate:
            if claim.get("status") == "open":
                checks.append(Check("claim_certificate_optional", "PASS", "open claim has no certificate", [claim_id]))
            else:
                checks.append(Check("claim_certificate_present", "FAIL", "non-open claim lacks certificate", [claim_id]))
            continue
        if not relpath_ok(str(certificate)):
            checks.append(Check("claim_certificate_path", "FAIL", "certificate path is not repository-relative", [claim_id, str(certificate)]))
            continue
        path = root / certificate
        if not path.is_file():
            checks.append(Check("claim_certificate_exists", "FAIL", "claim certificate is missing; no fallback allowed", [claim_id, str(certificate)]))
            continue
        try:
            data = read_json(path)
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("claim_certificate_json_parse", "FAIL", f"malformed certificate JSON: {exc}", [claim_id, str(certificate)]))
            continue
        required = claim.get("required_certificate_fields") or {}
        for key, expected in required.items():
            cursor: Any = data
            for part in key.split("."):
                if isinstance(cursor, dict) and part in cursor:
                    cursor = cursor[part]
                else:
                    checks.append(Check("claim_required_certificate_field", "FAIL", f"missing field {key}", [claim_id, str(certificate)]))
                    break
            else:
                if expected == "__present__" or cursor == expected:
                    checks.append(Check("claim_required_certificate_field", "PASS", f"{key} verified from certificate", [claim_id, str(certificate)]))
                else:
                    checks.append(Check("claim_required_certificate_field", "FAIL", f"{key} value mismatch", [claim_id, f"expected={expected!r}", f"actual={cursor!r}"]))
    return checks


def check_claim_paths(root: Path, claims: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    for claim_id, claim in (claims.get("claims") or {}).items():
        for field_name in ("producer", "protocol", "certificate"):
            value = claim.get(field_name)
            if value:
                if not relpath_ok(str(value)):
                    checks.append(Check("claim_path_is_repository_relative", "FAIL", f"{field_name} is not repository-relative", [claim_id, str(value)]))
                elif not (root / str(value)).is_file():
                    if claim.get("status") == "open" and field_name == "certificate":
                        checks.append(Check("claim_path_resolves", "PASS", "open claim certificate intentionally absent", [claim_id]))
                    else:
                        checks.append(Check("claim_path_resolves", "FAIL", f"{field_name} path missing", [claim_id, str(value)]))
                else:
                    checks.append(Check("claim_path_resolves", "PASS", f"{field_name} path exists", [claim_id, str(value)]))
        for input_path in claim.get("inputs", []) or []:
            if not relpath_ok(str(input_path)) or not (root / str(input_path)).is_file():
                checks.append(Check("claim_input_resolves", "FAIL", "claim input missing or non-relative", [claim_id, str(input_path)]))
            else:
                checks.append(Check("claim_input_resolves", "PASS", "claim input exists", [claim_id, str(input_path)]))
    return checks


def check_sha256sums(root: Path) -> list[Check]:
    checks: list[Check] = []
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        return [Check("sha256sums_exists", "FAIL", "SHA256SUMS.txt is missing")]
    entries, errors = read_sha_manifest(manifest)
    if errors:
        checks.append(Check("sha256sums_unique_paths", "FAIL", "manifest has malformed or conflicting entries", errors))
    else:
        checks.append(Check("sha256sums_unique_paths", "PASS", f"{len(entries)} unique paths"))
    missing: list[str] = []
    mismatched: list[str] = []
    for rel, expected in entries.items():
        path = root / rel
        if not path.is_file():
            missing.append(rel)
        elif sha256_file(path) != expected:
            mismatched.append(rel)
    if missing or mismatched:
        checks.append(Check("sha256sums_match_files", "FAIL", "repository SHA manifest mismatch", missing[:20] + mismatched[:20]))
    else:
        checks.append(Check("sha256sums_match_files", "PASS", "all SHA256SUMS.txt entries match"))
    return checks


def source_files(root: Path) -> list[Path]:
    excluded = {".git"}
    out: list[Path] = []
    for path in root.rglob("*"):
        if any(part in excluded for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".json", ".yaml", ".yml"}:
            out.append(path)
    return out


def check_absolute_paths(root: Path, artifacts: list[dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    for artifact in artifacts:
        if artifact.get("status") == "missing":
            continue
        rel = str(artifact.get("path", ""))
        path = root / rel
        if not path.is_file() or path.suffix not in {".py", ".md", ".json", ".yaml", ".yml"}:
            continue
        hits: list[str] = []
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if ABSOLUTE_RUNTIME_RE.search(line) and not ALLOW_COMMENT_RE.search(line):
                hits.append(f"{rel}:{lineno}:{line.strip()[:160]}")
        if hits and artifact.get("allow_absolute_runtime_paths"):
            checks.append(Check("absolute_runtime_paths", "WARNING", "absolute runtime paths are documented legacy/Colab behaviour", hits[:10]))
        elif hits:
            checks.append(Check("absolute_runtime_paths", "FAIL", "forbidden absolute runtime paths found", hits[:10]))
        else:
            checks.append(Check("absolute_runtime_paths", "PASS", "no forbidden absolute runtime paths", [rel]))
    return checks


def check_static_risks(root: Path) -> list[Check]:
    findings: list[str] = []
    fallback_findings: list[str] = []
    overwrite_findings: list[str] = []
    for path in source_files(root):
        rel = str(path.relative_to(root))
        if rel.startswith("audit/") or rel.startswith("tests/audit/"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if ALLOW_COMMENT_RE.search(line):
                continue
            for name, pattern in HARDCODE_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{name}:{rel}:{lineno}:{line.strip()[:180]}")
                    break
            if re.search(r"Path\(\"/(content|tmp)|glob\(|rglob\(|download|urlretrieve|locate\(", line):
                fallback_findings.append(f"{rel}:{lineno}:{line.strip()[:180]}")
            if re.search(r"add_argument\(\"--report\".*default=.*results/|write_text\(|open\(.+[\"']w", line):
                overwrite_findings.append(f"{rel}:{lineno}:{line.strip()[:180]}")
    checks = [
        Check(
            "hardcoded_result_screen",
            "WARNING" if findings else "PASS",
            "static candidates found; classify before treating as scientific risk" if findings else "no hard-coded result candidates found",
            findings[:50],
        ),
        Check(
            "silent_fallback_screen",
            "WARNING" if fallback_findings else "PASS",
            "fallback/default discovery patterns found; audit does not use them" if fallback_findings else "no fallback patterns found",
            fallback_findings[:50],
        ),
        Check(
            "output_overwrite_screen",
            "WARNING" if overwrite_findings else "PASS",
            "output-writing patterns found; audit does not execute them" if overwrite_findings else "no output overwrite candidates found",
            overwrite_findings[:50],
        ),
    ]
    return checks


def check_git(root: Path) -> tuple[list[Check], dict[str, Any]]:
    checks: list[Check] = []
    code, commit = git_text(root, ["rev-parse", "HEAD"])
    code_status, status = git_text(root, ["status", "--porcelain"])
    metadata = {
        "commit": commit if code == 0 else None,
        "dirty": bool(status) if code_status == 0 else None,
        "status_porcelain": status,
    }
    if code == 0:
        checks.append(Check("git_commit_recorded", "PASS", "repository commit recorded", [commit]))
    else:
        checks.append(Check("git_commit_recorded", "WARNING", "git commit unavailable", [commit]))
    if code_status == 0:
        checks.append(Check("git_dirty_status_recorded", "WARNING" if status else "PASS", "working tree dirty" if status else "working tree clean", status.splitlines()[:20]))
    else:
        checks.append(Check("git_dirty_status_recorded", "WARNING", "git status unavailable", [status]))
    return checks, metadata


def run_audit(root: Path, strict: bool) -> dict[str, Any]:
    checks: list[Check] = []
    git_checks, git_meta = check_git(root)
    checks.extend(git_checks)
    artifacts, artifact_checks = load_artifacts(root)
    checks.extend(artifact_checks)
    checks.extend(check_artifact_files(root, artifacts))
    claims_path = root / "audit" / "claims_manifest.yaml"
    if claims_path.is_file():
        try:
            claims = load_claims(claims_path)
            checks.append(Check("claims_manifest_parse", "PASS", "claims manifest parsed", [str(claims_path.relative_to(root))]))
            checks.extend(check_claim_paths(root, claims))
            checks.extend(check_certificate_fields(root, claims))
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("claims_manifest_parse", "FAIL", str(exc), [str(claims_path.relative_to(root))]))
    else:
        checks.append(Check("claims_manifest_exists", "FAIL", "audit/claims_manifest.yaml is missing"))
    checks.extend(check_sha256sums(root))
    checks.extend(check_absolute_paths(root, artifacts))
    checks.extend(check_static_risks(root))

    counts = {status: sum(1 for c in checks if c.status == status) for status in STATUSES}
    all_pass = counts["FAIL"] == 0
    return {
        "audit_tool_version": VERSION,
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "repository_root": str(root),
        "repository_commit_sha": git_meta.get("commit"),
        "dirty_status": git_meta.get("dirty"),
        "strict": strict,
        "checks": [c.as_dict() for c in checks],
        "summary": counts,
        "all_audit_gates_pass": all_pass,
        "note": "all_audit_gates_pass is a repository audit result, not a scientific certificate all_gates_pass field.",
    }


def print_summary(report: dict[str, Any]) -> None:
    print("Geometric-Flow repository audit")
    print(f"commit: {report.get('repository_commit_sha')}")
    print(f"dirty: {report.get('dirty_status')}")
    for status in STATUSES:
        print(f"{status}: {report['summary'].get(status, 0)}")
    for item in report["checks"]:
        if item["status"] in {"FAIL", "WARNING", "NOT CHECKED"}:
            print(f"[{item['status']}] {item['name']}: {item['message']}")
            for evidence in item.get("evidence", [])[:5]:
                print(f"  - {evidence}")
    print("PASS" if report["all_audit_gates_pass"] else "FAIL")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail closed on mandatory audit failures")
    parser.add_argument("--report", help="write machine-readable JSON report")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    report = run_audit(root, strict=args.strict)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_summary(report)
    return 0 if report["all_audit_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
