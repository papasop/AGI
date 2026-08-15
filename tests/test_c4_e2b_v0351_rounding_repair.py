import ast
import hashlib
from decimal import Decimal, getcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEW_DIR = ROOT / "archive" / "milestones" / "c4_e2b_v0_3_5_1"
PARENT = NEW_DIR / "C4_E2B_B_EIGHT_CHART_ARB_FLOWPIPE_RIGOROUS_v0_3_5_1.py"
HANDOFF = NEW_DIR / "C4_E2B_AFFINE_CORRELATED_HANDOFF_RIGOROUS_v0_3_5_1.py"
OLD_JSON = ROOT / "results" / "c4_e2b" / "c4_e2b_affine_correlated_handoff_v0_3_5.json"
OLD_JSON_SHA256 = "c8a83ffb4f1bc2e91ff33a651436a3bc3f8565cab6f8390eaa5fbf896f07f41a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_source(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = path.read_text(encoding="utf-8").splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"{name} not found in {path}")


def test_historical_v035_json_is_unchanged():
    assert sha256(OLD_JSON) == OLD_JSON_SHA256


def test_v0351_neumann_paths_do_not_convert_bounds_to_float():
    for name in ("neumann_inverse", "qneumann_inverse_near_identity"):
        source = function_source(PARENT, name)
        assert "float(" not in source
        assert "hi(abs(" not in source
        assert "exact(tail)" not in source
        assert "arb_definitely_less" in source


def test_v0351_quadratic_patch_marks_active_arb_outward_methods():
    source = PARENT.read_text(encoding="utf-8")
    assert "patch_quadratic_for_outward_arithmetic" in source
    assert 'func._arithmetic = "arb_outward"' in source
    assert '"quadratic_radius_arithmetic": "arb_outward"' in source
    assert '"neumann_norm_arithmetic": "arb_outward"' in source
    assert '"neumann_tail_arithmetic": "arb_outward"' in source


def test_v0351_rigour_guards_are_derived_not_literal_true():
    source = HANDOFF.read_text(encoding="utf-8")
    assert '"no_float_in_quadratic_radius_path": True' not in source
    assert '"no_float_in_neumann_norm_path": True' not in source
    assert '"no_float_in_neumann_tail_path": True' not in source
    assert "getattr(q_method, \"_arithmetic\", None)" in source
    assert "getattr(neumann_method, \"_norm_arithmetic\", None)" in source
    assert "getattr(neumann_method, \"_tail_arithmetic\", None)" in source


def test_v0351_default_report_path_does_not_overwrite_v035_report():
    source = HANDOFF.read_text(encoding="utf-8")
    assert 'default="/tmp/c4_e2b_affine_correlated_handoff_v0_3_5_1.json"' in source
    assert 'default="/tmp/c4_e2b_affine_correlated_handoff_v0_3_5.json"' not in source


def test_binary64_down_rounding_can_shrink_decimal_upper_bound():
    getcontext().prec = 80
    exact_upper = Decimal(1) + (Decimal(2) ** Decimal(-54)) + (Decimal(2) ** Decimal(-120))
    rounded = Decimal.from_float(float(exact_upper))
    assert rounded < exact_upper
