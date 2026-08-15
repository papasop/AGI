#!/usr/bin/env python3
"""Verify freshly generated C4-E2b v0.3.5.1 Colab reports.

This verifier is read-only. It checks JSON structure, self-hashes, provenance
links, and the explicit Arb-outward enclosure-rigour guards. It does not create
or infer a certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def load_json(path: str) -> dict[str, Any]:
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(p)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError(f"{p} is not a JSON object")
    return data


def verify_self_hash(data: dict[str, Any], field: str) -> None:
    expected = data.get(field)
    payload = dict(data)
    payload.pop(field, None)
    actual = canonical_sha(payload)
    if expected != actual:
        raise RuntimeError(f"{field} mismatch: expected {expected}, actual {actual}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ladder", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--diagnostic", required=True)
    parser.add_argument("--handoff", required=True)
    args = parser.parse_args(argv)

    ladder = load_json(args.ladder)
    candidate = load_json(args.candidate)
    diagnostic = load_json(args.diagnostic)
    handoff = load_json(args.handoff)

    verify_self_hash(candidate, "candidate_sha256_without_self")
    verify_self_hash(diagnostic, "report_sha256_without_self")
    verify_self_hash(handoff, "report_sha256_without_self")

    if handoff.get("version") != "0.3.5.1":
        raise RuntimeError("handoff report is not v0.3.5.1")
    if handoff.get("scientific_status") != "C4_E2B_AFFINE_CORRELATED_HANDOFF_CERTIFIED":
        raise RuntimeError("handoff report is not certified")
    if handoff.get("all_gates_pass") is not True:
        raise RuntimeError("handoff gates do not pass")

    protocol = handoff.get("protocol") or {}
    rigour = protocol.get("enclosure_rigour") or {}
    required = {
        "quadratic_radius_arithmetic": "arb_outward",
        "neumann_norm_arithmetic": "arb_outward",
        "neumann_tail_arithmetic": "arb_outward",
        "binary64_used_only_for_serialization": True,
    }
    for key, value in required.items():
        if rigour.get(key) != value:
            raise RuntimeError(f"missing enclosure-rigour guard {key}={value!r}")

    gates = handoff.get("gates") or {}
    if gates.get("all_leaf_enclosure_rigour_guards_pass") is not True:
        raise RuntimeError("leaf enclosure-rigour guard did not pass")

    if candidate.get("source_checkpoint_sha256") != protocol.get("checkpoint_sha256"):
        raise RuntimeError("candidate/checkpoint provenance mismatch")
    if diagnostic.get("protocol", {}).get("candidate_sha256") != protocol.get("candidate_sha256"):
        raise RuntimeError("diagnostic/candidate provenance mismatch")

    if not (ladder.get("prerequisite_0_to_1") or {}).get("all_gates_pass"):
        raise RuntimeError("transition 0->1 prerequisite is not passing")

    print("C4-E2b v0.3.5.1 output verification: PASS")
    print("This is a verifier result, not a substitute for the generated JSON certificate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
