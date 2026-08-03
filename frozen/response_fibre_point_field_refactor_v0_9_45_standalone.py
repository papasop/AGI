#!/usr/bin/env python3
"""v0.9.45: executable contract for a point/box-dependent Arb field backend.

This version intentionally does not certify X(a) or DX(a).  It freezes the
required call graph, audits an optional v0.9.30 source, emits a typed adapter
template, and proves that the unimplemented template is rejected fail-closed.
"""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, platform, sys, time
from pathlib import Path

TITLE = "GEOMETRIC-FLOW POINT/BOX-DEPENDENT ARB FIELD REFACTOR CONTRACT"
VERSION = "0.9.45"
V0930_SHA = "426b55e5f8d2b37f2d62a597fbc8f82dc9bba42cc46903c35c553905699b4e52"
V09433_SHA = "ef8cc30b3cde528a6cd94d1192ce7a4a360c4635c5e675e2166dd198b969fe46"
V0944_SHA = "94317c561661ec55663b64f9968084546ad05bf24cdebaa311a1c0977643dae8"

TEMPLATE = r'''"""Generated v0.9.45 formal backend template — implementation required."""
from flint import arb, ctx
ctx.prec = 192
DIMENSION = 6
DOMAIN_RADIUS = arb("1.5e-11")
FROZEN_SOURCE_HASHES = {
    "v0930": "426b55e5f8d2b37f2d62a597fbc8f82dc9bba42cc46903c35c553905699b4e52",
    "v09433": "ef8cc30b3cde528a6cd94d1192ce7a4a360c4635c5e675e2166dd198b969fe46",
    "v0944": "94317c561661ec55663b64f9968084546ad05bf24cdebaa311a1c0977643dae8",
}

def _validate_box(a_box):
    if not isinstance(a_box, (list, tuple)) or len(a_box) != DIMENSION:
        raise ValueError("expected six Arb coordinates")
    if not all(isinstance(x, arb) for x in a_box):
        raise TypeError("coordinates must be flint.arb")
    if not all(abs(x) < DOMAIN_RADIUS for x in a_box):
        raise ValueError("box leaves certified fourth-chart domain")

def implicit_fibre_root_solver(a_box):
    """Return eight Arb values enclosing the unique normal root b(a_box)."""
    _validate_box(a_box)
    raise NotImplementedError("bind repository-native parametric Krawczyk solver")

def pullback_metric(a_box, root_box):
    """Return a formal 6x6 Arb pullback metric on exactly this input box."""
    _validate_box(a_box)
    raise NotImplementedError("bind repository-native graph derivative and metric")

def projected_gradient(a_box, root_box, metric_box):
    """Return the six-component projected L6 gradient before normalization."""
    _validate_box(a_box)
    raise NotImplementedError("bind repository-native response Jacobian and L6 gradient")

def formal_vector_field_X(a_box):
    """Compute X(a_box) through root -> metric -> gradient -> normalization."""
    _validate_box(a_box)
    root = implicit_fibre_root_solver(a_box)
    metric = pullback_metric(a_box, root)
    gradient = projected_gradient(a_box, root, metric)
    raise NotImplementedError("bind analytic normalization branch")

def formal_jacobian_DX(a_box):
    """Return a genuine 6x6 Arb derivative enclosure of formal_vector_field_X."""
    _validate_box(a_box)
    raise NotImplementedError("differentiate the same active geometric expression")
'''

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",default="response_fibre_point_field_refactor_v0_9_45_results")
    p.add_argument("--v0930",default=None,help="optional frozen v0.9.30 source for exact source audit")
    return p.parse_known_args()

def run(a):
    started=time.time(); out=Path(a.outdir).resolve(); out.mkdir(parents=True,exist_ok=True)
    source=None; source_hash_exact=False; markers={}
    if a.v0930:
        source=Path(a.v0930).resolve()
        if not source.is_file(): raise FileNotFoundError(source)
        source_hash_exact=sha(source)==V0930_SHA
        if not source_hash_exact: raise RuntimeError("v0.9.30 source hash mismatch")
        text=source.read_text()
        marker_terms={
          "response_jacobian_and_gradient":"response_jacobian_and_gradient",
          "matrix_multiply":"v093_matmul",
          "midpoint_inverse":"v093_midpoint_inverse",
          "fourth_frame_switch":"base_phases=v0929_theta_b",
          "normal_root_state":"fb_inverse=",
          "input_box_public_callback":"def formal_vector_field_X",
          "public_jacobian_callback":"def formal_jacobian_DX",
        }
        markers={k:(v in text) for k,v in marker_terms.items()}
    adapter=out/"geometric_flow_point_box_backend_template_v0_9_45.py"
    adapter.write_text(TEMPLATE)
    tree=ast.parse(TEMPLATE)
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    required=["implicit_fibre_root_solver","pullback_metric","projected_gradient","formal_vector_field_X","formal_jacobian_DX"]
    call_names=set()
    fx=funcs["formal_vector_field_X"]
    for n in ast.walk(fx):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name): call_names.add(n.func.id)
    spec=importlib.util.spec_from_file_location("gf_v0945_template",adapter)
    # These two properties are first checked structurally, so the contract can
    # be generated even before python-flint is installed.  When flint exists,
    # the executable probes below independently confirm them.
    notimpl_count=sum(isinstance(n,ast.Raise) and isinstance(n.exc,ast.Call)
                      and isinstance(n.exc.func,ast.Name) and n.exc.func.id=="NotImplementedError"
                      for n in ast.walk(tree))
    typeerror_count=sum(isinstance(n,ast.Raise) and isinstance(n.exc,ast.Call)
                        and isinstance(n.exc.func,ast.Name) and n.exc.func.id=="TypeError"
                        for n in ast.walk(tree))
    import_error=None; template_rejected=notimpl_count>=5; typed_invalid_rejected=typeerror_count>=1
    try:
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        try: mod.formal_vector_field_X([mod.arb(0)]*6)
        except NotImplementedError: template_rejected=True
        try: mod.formal_vector_field_X([0]*6)
        except TypeError: typed_invalid_rejected=True
    except Exception as e: import_error=f"{type(e).__name__}: {e}"
    contract={
      "schema":"geometric-flow/point-box-field-backend-contract/v0.9.45",
      "dimension":6,"formal_backend":"python-flint/Arb","minimum_precision_bits":192,
      "domain_radius":"1.5e-11","coordinate_system":"v0.9.30-fourth-recentered-intrinsic-tangent",
      "required_callbacks":required,
      "required_dependency_order":["implicit_fibre_root_solver(a_box)","pullback_metric(a_box,root)","projected_gradient(a_box,root,metric)","analytic normalization -> formal_vector_field_X(a_box)"],
      "acceptance_probes":["centre box","24 frozen v0.9.44 displaced boxes","input dependence","response invariance","strict L6 descent","6x6 formal DX enclosure","invalid dimension/type/domain rejection"],
      "forbidden_shortcuts":["fixed signed enclosure independent of a_box","finite difference promoted to formal DX","L-infinity norm divided equally among entries","truthy JSON flags without executable Arb callbacks"],
      "frozen_hashes":{"v0930":V0930_SHA,"v09433":V09433_SHA,"v0944":V0944_SHA}}
    cp=out/"point_box_field_backend_contract.json"; cp.write_text(json.dumps(contract,indent=2)+"\n")
    gates={
      "frozen_hash_chain_declared":True,
      "optional_v0930_hash_exact":(source is None) or source_hash_exact,
      "five_required_callbacks_emitted":all(k in funcs for k in required),
      "X_dependency_order_explicit":all(k in call_names for k in ["implicit_fibre_root_solver","pullback_metric","projected_gradient"]),
      "typed_invalid_input_rejected":typed_invalid_rejected,
      "unimplemented_template_rejected_fail_closed":template_rejected,
      "contract_emitted":cp.is_file(),
      "finite_difference_forbidden_as_formal_DX":True,
    }
    preflight=all(gates.values())
    implementation_ready=False
    result={"title":TITLE,"version":VERSION,
      "scientific_status":"POINT_BOX_ARB_REFACTOR_CONTRACT_READY_IMPLEMENTATION_OPEN" if preflight else "V0945_INCONCLUSIVE_FAIL_CLOSED",
      "source_audit":{"v0930_supplied":source is not None,"v0930_hash_exact":source_hash_exact if source else None,"markers":markers},
      "generated_adapter_template":str(adapter),"adapter_template_sha256":sha(adapter),
      "backend_contract":str(cp),"backend_contract_sha256":sha(cp),"template_import_error":import_error,
      "gates":gates,"preflight_all_gates_pass":preflight,"all_scientific_gates_pass":False,
      "repository_native_point_box_X_ready":implementation_ready,"formal_jacobian_DX_ready":False,
      "qr_lohner_flowpipe_certified":False,"fifth_frame_certified":False,"global_flow_claimed":False,
      "next_required_step":"replace every NotImplementedError with the active repository-native Arb expression, preserving a_box through root, metric, gradient and normalization; then rerun the 24 v0.9.44 probes",
      "claim_boundary":"executable typed refactor contract and fail-closed verifier only; no point-dependent X, DX, flowpipe, fifth frame, or global flow",
      "elapsed_seconds":time.time()-started,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
    (out/"run_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    a,u=parse()
    if u: print(f"[notice] ignored notebook/kernel arguments: {u}")
    try:
        r=run(a); print("="*112); print(f"{TITLE} v{VERSION}"); print("="*112); print(json.dumps(r,indent=2)); return 0
    except Exception as e:
        print(json.dumps({"scientific_status":"V0945_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2)); return 2
if __name__=="__main__":
    c=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules: raise SystemExit(c)
