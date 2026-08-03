#!/usr/bin/env python3
"""Preview a safe archive migration for frozen milestone scripts.

The default mode is read-only.  It writes a migration report but does not move
or rewrite any frozen proof artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "ARCHIVE_MIGRATION_PLAN.json"
DEFAULT_MD = ROOT / "docs" / "ARCHIVE_MIGRATION_PLAN.md"


@dataclass(frozen=True)
class MovePlan:
    source: str
    target: str
    classification: str
    status: str


PLANS = [
    MovePlan(
        "response_fibre_validated_continuation_v0_9_4_1_oneclick.py",
        "archive/frozen_milestones/01_local_foundation/response_fibre_validated_continuation_v0_9_4_1_oneclick.py",
        "01_local_foundation",
        "audit_history",
    ),
    MovePlan(
        "response_fibre_two_step_continuation_v0_9_5_oneclick.py",
        "archive/frozen_milestones/01_local_foundation/response_fibre_two_step_continuation_v0_9_5_oneclick.py",
        "01_local_foundation",
        "finite_continuation_input",
    ),
    MovePlan(
        "response_fibre_recenter_preflight_v0_9_6_oneclick.py",
        "archive/frozen_milestones/01_local_foundation/response_fibre_recenter_preflight_v0_9_6_oneclick.py",
        "01_local_foundation",
        "normal_root_preflight",
    ),
    MovePlan(
        "response_fibre_normal_root_v0_9_7_oneclick.py",
        "archive/frozen_milestones/01_local_foundation/response_fibre_normal_root_v0_9_7_oneclick.py",
        "01_local_foundation",
        "normal_root_setup",
    ),
    MovePlan(
        "response_fibre_arb_normal_root_v0_9_8_oneclick.py",
        "archive/frozen_milestones/01_local_foundation/response_fibre_arb_normal_root_v0_9_8_oneclick.py",
        "01_local_foundation",
        "normal_root_setup",
    ),
    MovePlan(
        "response_fibre_recentered_frame_v0_9_9_oneclick.py",
        "archive/frozen_milestones/02_second_chart/response_fibre_recentered_frame_v0_9_9_oneclick.py",
        "02_second_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_second_chart_v0_9_10_oneclick.py",
        "archive/frozen_milestones/02_second_chart/response_fibre_second_chart_v0_9_10_oneclick.py",
        "02_second_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_finite_continuation_v0_9_11_oneclick.py",
        "archive/frozen_milestones/02_second_chart/response_fibre_finite_continuation_v0_9_11_oneclick.py",
        "02_second_chart",
        "finite_continuation_input",
    ),
    MovePlan(
        "response_fibre_transition_preflight_v0_9_12_oneclick.py",
        "archive/frozen_milestones/02_second_chart/response_fibre_transition_preflight_v0_9_12_oneclick.py",
        "02_second_chart",
        "diagnostic",
    ),
    MovePlan(
        "response_fibre_route_correction_v0_9_13_oneclick.py",
        "archive/frozen_milestones/02_second_chart/response_fibre_route_correction_v0_9_13_oneclick.py",
        "02_second_chart",
        "scope_correction",
    ),
    MovePlan(
        "response_fibre_endpoint_identifiability_v0_9_14_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_endpoint_identifiability_v0_9_14_oneclick.py",
        "03_endpoint_enclosure",
        "endpoint_diagnostic",
    ),
    MovePlan(
        "response_fibre_validated_lohner_v0_9_15_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_validated_lohner_v0_9_15_oneclick.py",
        "03_endpoint_enclosure",
        "adapter_exploration",
    ),
    MovePlan(
        "response_fibre_adapter_hardening_v0_9_16_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_adapter_hardening_v0_9_16_oneclick.py",
        "03_endpoint_enclosure",
        "adapter_hardening",
    ),
    MovePlan(
        "response_fibre_executable_adapter_v0_9_17_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_executable_adapter_v0_9_17_oneclick.py",
        "03_endpoint_enclosure",
        "adapter_hardening",
    ),
    MovePlan(
        "response_fibre_lohner_stress_v0_9_18_oneclick.py",
        "archive/frozen_milestones/superseded/v0_9_18/response_fibre_lohner_stress_v0_9_18_oneclick.py",
        "superseded/v0_9_18",
        "superseded_by_v0_9_20",
    ),
    MovePlan(
        "response_fibre_local_dx_target_v0_9_19_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_local_dx_target_v0_9_19_oneclick.py",
        "03_endpoint_enclosure",
        "norm_diagnostic",
    ),
    MovePlan(
        "response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py",
        "03_endpoint_enclosure",
        "norm_correction",
    ),
    MovePlan(
        "response_fibre_six_component_endpoint_v0_9_21_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_six_component_endpoint_v0_9_21_oneclick.py",
        "03_endpoint_enclosure",
        "endpoint_enclosure",
    ),
    MovePlan(
        "response_fibre_signed_field_export_v0_9_22_oneclick.py",
        "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_signed_field_export_v0_9_22_oneclick.py",
        "03_endpoint_enclosure",
        "signed_field_export",
    ),
    MovePlan(
        "response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py",
        "04_third_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_third_frame_v0_9_24_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_frame_v0_9_24_oneclick.py",
        "04_third_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_third_frame_backend_v0_9_25_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_frame_backend_v0_9_25_oneclick.py",
        "04_third_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_third_picard_v0_9_26_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_picard_v0_9_26_oneclick.py",
        "04_third_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_third_chart_finite_continuation_v0_9_27_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_chart_finite_continuation_v0_9_27_oneclick.py",
        "04_third_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py",
        "archive/frozen_milestones/04_third_chart/response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py",
        "04_third_chart",
        "endpoint_enclosure",
    ),
    MovePlan(
        "response_fibre_fourth_frame_v0_9_29_oneclick.py",
        "archive/frozen_milestones/05_fourth_chart/response_fibre_fourth_frame_v0_9_29_oneclick.py",
        "05_fourth_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_fourth_picard_v0_9_30_oneclick.py",
        "archive/frozen_milestones/05_fourth_chart/response_fibre_fourth_picard_v0_9_30_oneclick.py",
        "05_fourth_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_fourth_chart_finite_v0_9_31_oneclick.py",
        "archive/frozen_milestones/05_fourth_chart/response_fibre_fourth_chart_finite_v0_9_31_oneclick.py",
        "05_fourth_chart",
        "valid_milestone",
    ),
    MovePlan(
        "response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py",
        "archive/frozen_milestones/05_fourth_chart/response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py",
        "05_fourth_chart",
        "valid_input_to_v0_10_chain",
    ),
    MovePlan(
        "src/geometric_flow_active_backend_export_v0_10_1_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_active_backend_export_v0_10_1_oneclick.py",
        "06_taylor_lohner",
        "valid_chain_component",
    ),
    MovePlan(
        "src/geometric_flow_scalar_primitives_extract_v0_10_2_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_scalar_primitives_extract_v0_10_2_oneclick.py",
        "06_taylor_lohner",
        "valid_chain_component",
    ),
    MovePlan(
        "src/geometric_flow_six_variable_jet_lift_v0_10_3_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_six_variable_jet_lift_v0_10_3_oneclick.py",
        "06_taylor_lohner",
        "current_effective_chain",
    ),
    MovePlan(
        "src/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py",
        "06_taylor_lohner",
        "current_effective_chain",
    ),
    MovePlan(
        "src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
        "06_taylor_lohner",
        "current_effective_chain",
    ),
    MovePlan(
        "src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
        "06_taylor_lohner",
        "latest_reference_certificate",
    ),
    MovePlan(
        "src/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py",
        "06_taylor_lohner",
        "source_certified_packaging_pending",
    ),
    MovePlan(
        "src/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py",
        "06_taylor_lohner",
        "fifth_frame_contract_open",
    ),
    MovePlan(
        "src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py",
        "archive/frozen_milestones/06_taylor_lohner/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py",
        "06_taylor_lohner",
        "implementation_open_fail_closed",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tracked_text_files() -> list[Path]:
    excluded = {DEFAULT_JSON.resolve(), DEFAULT_MD.resolve()}
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.resolve() in excluded:
            continue
        if path.suffix.lower() in {".zip", ".json", ".ipynb", ".pyc"}:
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def references_for(source: str, files: list[Path]) -> list[str]:
    refs: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if source in text:
            refs.append(str(path.relative_to(ROOT)))
    return refs


def build_report() -> dict[str, object]:
    text_files = tracked_text_files()
    entries = []
    for plan in PLANS:
        source_path = ROOT / plan.source
        target_path = ROOT / plan.target
        entries.append(
            {
                "source": plan.source,
                "target": plan.target,
                "classification": plan.classification,
                "status": plan.status,
                "source_exists": source_path.is_file(),
                "target_exists": target_path.exists(),
                "sha256": sha256(source_path) if source_path.is_file() else None,
                "references": references_for(plan.source, text_files),
            }
        )
    return {
        "mode": "preview_only",
        "moves_planned": len(entries),
        "content_rewrite_planned": False,
        "scientific_claim_change_planned": False,
        "apply_policy": "do not move files until a dedicated migration PR updates wrappers, manifests, references, and CI",
        "entries": entries,
    }


def write_markdown(report: dict[str, object], path: Path) -> None:
    lines = [
        "# Archive Migration Plan",
        "",
        "Mode: preview only.",
        "",
        "No theorem-producing expression is modified, no certificate is promoted,",
        "and no frozen file is moved by this report generator.",
        "",
        "| Source | Target | Status | References |",
        "| --- | --- | --- | --- |",
    ]
    for entry in report["entries"]:
        refs = ", ".join(entry["references"]) if entry["references"] else "-"
        lines.append(
            f"| `{entry['source']}` | `{entry['target']}` | "
            f"{entry['status']} | {refs} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default=str(DEFAULT_JSON), help="JSON report path")
    parser.add_argument("--markdown", default=str(DEFAULT_MD), help="Markdown report path")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="reserved for a dedicated migration PR; always fails closed here",
    )
    args = parser.parse_args()
    if args.apply:
        raise SystemExit("--apply is intentionally disabled in this safety package")
    report = build_report()
    json_path = Path(args.json)
    md_path = Path(args.markdown)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, md_path)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print("mode: preview_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
