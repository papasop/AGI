#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "archive/frozen_milestones/06_taylor_lohner/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py",
    ROOT / "archive/frozen_milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
    ROOT / "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
    ROOT / "results/v0_10_4/run_summary.json",
    ROOT / "results/v0_10_5/run_summary.json",
    ROOT / "results/v0_10_6/run_summary.json",
    ROOT / "SHA256SUMS.txt",
]

for path in required:
    if not path.is_file():
        raise SystemExit(f"missing: {path.relative_to(ROOT)}")

v104 = json.loads((ROOT / "results/v0_10_4/run_summary.json").read_text())
if "1.500000000000000" not in json.dumps(v104):
    raise SystemExit("v0_10_4 is not visibly bound to the full fourth domain")
v105 = json.loads((ROOT / "results/v0_10_5/run_summary.json").read_text())
if not v105.get("gates", {}).get("complete_fourth_graph_box_used"):
    raise SystemExit("v0_10_5 full fourth graph-box gate is false")

report = json.loads((ROOT / "results/v0_10_6/run_summary.json").read_text())
if not report.get("qr_lohner_support_flowpipe_certified"):
    raise SystemExit("v0.10.6 support-flowpipe gate is false")
if report.get("directional_qr_tightening_certified"):
    raise SystemExit("unexpected directional QR claim")

for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
    digest, rel = line.split("  ", 1)
    path = ROOT / rel
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f"hash mismatch: {rel}")

print("v0.10.6 update verified")
