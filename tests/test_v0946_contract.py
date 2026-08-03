import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "src" / "geometric_flow_native_point_field_candidate_v0_9_46.py"


def test_required_callbacks_exist():
    tree = ast.parse(CANDIDATE.read_text())
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert {
        "implicit_fibre_root_solver",
        "pullback_metric",
        "projected_gradient",
        "formal_vector_field_X",
    } <= names


def test_unimplemented_candidate_is_explicitly_fail_closed():
    tree = ast.parse(CANDIDATE.read_text())
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "NotImplementedError"
    ]
    # This assertion is intentionally true for the update scaffold.  Replace
    # it with `assert not calls` only in the implementation commit, then run
    # the executable harness before making a scientific claim.
    assert calls


def test_no_fixed_field_constant_shortcut():
    text = CANDIDATE.read_text()
    assert "FIELD_MIDPOINTS" not in text
    assert "FIELD_RADII" not in text
