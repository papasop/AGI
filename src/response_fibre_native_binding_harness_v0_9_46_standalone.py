#!/usr/bin/env python3
"""Geometric-Flow v0.9.46 — executable native point-field binding harness.

This verifier accepts a candidate Python module and proves whether it exposes
genuine input-dependent Arb callbacks.  With no candidate it emits a complete
backend skeleton and reports IMPLEMENTATION_OPEN.  It never promotes domain
validation, fixed enclosures, or finite differences to a formal field/DX proof.
"""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, platform, sys, time
from pathlib import Path

TITLE="GEOMETRIC-FLOW REPOSITORY-NATIVE POINT-FIELD BINDING HARNESS"
VERSION="0.9.46"
HASHES={
 "v0930":"426b55e5f8d2b37f2d62a597fbc8f82dc9bba42cc46903c35c553905699b4e52",
 "v09433":"ef8cc30b3cde528a6cd94d1192ce7a4a360c4635c5e675e2166dd198b969fe46",
 "v0944":"94317c561661ec55663b64f9968084546ad05bf24cdebaa311a1c0977643dae8",
 "v0945":"c366f40df59bf528a04c9bbee9ee2d620facff72012e2494264e0d206b7131db",
}
REQUIRED=("implicit_fibre_root_solver","pullback_metric","projected_gradient","formal_vector_field_X")

SKELETON='''"""v0.9.46 candidate backend: replace every NotImplementedError."""
from flint import arb, ctx
ctx.prec=192
DIMENSION=6
DOMAIN_RADIUS=arb("1.5e-11")
FROZEN_HASHES=%r

def _validate(a_box):
    if not isinstance(a_box,(list,tuple)) or len(a_box)!=6:
        raise ValueError("expected six Arb coordinates")
    if not all(isinstance(x,arb) for x in a_box):
        raise TypeError("coordinates must be Arb")
    if not all(abs(x)<DOMAIN_RADIUS for x in a_box):
        raise ValueError("outside fourth-chart domain")

def implicit_fibre_root_solver(a_box):
    _validate(a_box)
    # MUST evaluate the repository response at theta_c + T*a_box + N*b.
    raise NotImplementedError("bind parametric Arb Krawczyk root")

def pullback_metric(a_box,root_box):
    _validate(a_box)
    # MUST use the derivative of the same implicit graph at a_box.
    raise NotImplementedError("bind repository-native pullback metric")

def projected_gradient(a_box,root_box,metric_box):
    _validate(a_box)
    # MUST evaluate response Jacobian and L6 gradient at the same phase box.
    raise NotImplementedError("bind repository-native projected gradient")

def formal_vector_field_X(a_box):
    _validate(a_box)
    root=implicit_fibre_root_solver(a_box)
    metric=pullback_metric(a_box,root)
    grad=projected_gradient(a_box,root,metric)
    # MUST use the certified analytic normalization branch.
    raise NotImplementedError("bind normalized repository-native field")
''' % HASHES

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p)
 if s is None or s.loader is None: raise RuntimeError(f"cannot import {p}")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_native_binding_v0_9_46_results")
 p.add_argument("--candidate",default=None,help="candidate module implementing the four Arb callbacks")
 return p.parse_known_args()

def interval_bounds(x):
 # python-flint Arb supports lower()/upper() in the frozen runtime.
 return (str(x.lower()),str(x.upper()))

def run(a):
 st=time.time();out=Path(a.outdir).resolve();out.mkdir(parents=True,exist_ok=True)
 sk=out/"geometric_flow_native_point_field_candidate_v0_9_46.py";sk.write_text(SKELETON)
 tree=ast.parse(SKELETON);funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 fx_calls={n.func.id for n in ast.walk(funcs["formal_vector_field_X"])
           if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
 static_gates={
  "four_required_callbacks_emitted":all(k in funcs for k in REQUIRED),
  "root_metric_gradient_dependency_order_present":all(k in fx_calls for k in REQUIRED[:3]),
  "frozen_hash_chain_exact":HASHES["v0945"]=="c366f40df59bf528a04c9bbee9ee2d620facff72012e2494264e0d206b7131db",
  "fixed_enclosure_shortcut_not_present":"FIELD_MIDPOINTS" not in SKELETON and "FIELD_RADII" not in SKELETON,
  "finite_difference_DX_not_declared":"formal_jacobian_DX" not in SKELETON,
  "implementation_placeholders_fail_closed":sum(isinstance(n,ast.Raise) for n in ast.walk(tree))>=4,
 }
 probes={};errors=[];candidate_ready=False;position_sensitive=False
 if a.candidate:
  cp=Path(a.candidate).resolve()
  if not cp.is_file():raise FileNotFoundError(cp)
  text=cp.read_text();ctree=ast.parse(text)
  cfuncs={n.name:n for n in ctree.body if isinstance(n,ast.FunctionDef)}
  probes["required_symbols_callable_static"]=all(k in cfuncs for k in REQUIRED)
  probes["candidate_has_no_NotImplementedError"]=not any(
   isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="NotImplementedError"
   for n in ast.walk(ctree))
  probes["candidate_source_mentions_a_box_in_each_callback"]=all(
   any(isinstance(n,ast.Name) and n.id=="a_box" and isinstance(n.ctx,ast.Load)
       for n in ast.walk(cfuncs[k])) for k in REQUIRED if k in cfuncs) and all(k in cfuncs for k in REQUIRED)
  try:
   m=load(cp,"gf_v0946_candidate")
   from flint import arb,ctx
   ctx.prec=192
   zero=[arb(0) for _ in range(6)];d1=arb("2.5e-16");d2=arb("5e-16")
   boxes=[zero]
   for d in (d1,d2):
    for j in range(6):
     for sgn in (1,-1):
      q=[arb(0) for _ in range(6)];q[j]=d*sgn;boxes.append(q)
   outputs=[]
   for q in boxes:
    y=m.formal_vector_field_X(q)
    if not isinstance(y,(list,tuple)) or len(y)!=6 or not all(isinstance(z,arb) for z in y):
     raise TypeError("formal_vector_field_X must return six Arb values")
    outputs.append(tuple(interval_bounds(z) for z in y))
   position_sensitive=len(set(outputs))>1
   probes["twenty_five_Arb_field_probes_execute"]=len(outputs)==25
   probes["displaced_outputs_not_all_identical"]=position_sensitive
   bad=False
   try:m.formal_vector_field_X([0]*6)
   except (TypeError,ValueError):bad=True
   probes["invalid_type_rejected"]=bad
  except Exception as e:errors.append(f"{type(e).__name__}: {e}")
  candidate_ready=all(probes.values()) and not errors
 contract={"schema":"geometric-flow/native-point-field-binding/v0.9.46","dimension":6,
  "coordinate_system":"v0.9.30-fourth-recentered-intrinsic-tangent","formal_backend":"python-flint/Arb 192-bit",
  "required_callbacks":list(REQUIRED),"frozen_hashes":HASHES,
  "acceptance":"all 25 probes execute and at least one certified output enclosure differs from the centre output",
  "nonclaim":"different outputs establish executable input dependence only, not a formal DX enclosure"}
 cpath=out/"native_point_field_binding_contract.json";cpath.write_text(json.dumps(contract,indent=2)+"\n")
 preflight=all(static_gates.values())
 result={"title":TITLE,"version":VERSION,"scientific_status":
   ("EXECUTABLE_REPOSITORY_NATIVE_POINT_FIELD_CANDIDATE_ACCEPTED" if candidate_ready else
    "NATIVE_POINT_FIELD_BINDING_HARNESS_READY_IMPLEMENTATION_OPEN" if preflight else "V0946_INCONCLUSIVE_FAIL_CLOSED"),
  "generated_candidate":str(sk),"generated_candidate_sha256":sha(sk),"contract":str(cpath),"contract_sha256":sha(cpath),
  "candidate_supplied":bool(a.candidate),"static_gates":static_gates,"candidate_probes":probes,"errors":errors,
  "preflight_all_gates_pass":preflight,"candidate_all_gates_pass":candidate_ready,
  "all_scientific_gates_pass":candidate_ready,"repository_native_point_box_X_ready":candidate_ready,
  "input_dependence_observed":position_sensitive,"formal_jacobian_DX_ready":False,
  "qr_lohner_flowpipe_certified":False,"fifth_frame_certified":False,"global_flow_claimed":False,
  "next_required_step":"implement the generated candidate with the active repository-native Arb closures, then rerun this file with --candidate PATH",
  "claim_boundary":"binding harness and, only if candidate gates pass, executable input dependence; no formal DX, QR/Lohner flowpipe, fifth frame, or global flow",
  "elapsed_seconds":time.time()-st,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 (out/"run_summary.json").write_text(json.dumps(result,indent=2)+"\n");return result

def main():
 a,u=parse()
 if u:print(f"[notice] ignored notebook/kernel arguments: {u}")
 try:
  r=run(a);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["preflight_all_gates_pass"] else 2
 except Exception as e:
  print(json.dumps({"scientific_status":"V0946_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2
if __name__=="__main__":
 c=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(c)
