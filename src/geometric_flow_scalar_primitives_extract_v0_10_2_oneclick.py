#!/usr/bin/env python3
"""Extract dependency-closed scalar Arb primitives from retained v0.9.30 source."""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, sys, textwrap
from pathlib import Path

TITLE="GEOMETRIC-FLOW DEPENDENCY-CLOSED SCALAR ARB PRIMITIVE EXTRACTION"
VERSION="0.10.2"
EXPECTED_ACTIVE_SHA="d0ef55e1361f2c92d41dcdde0a9b3066e400d3d675d85a68ad69e6498620435d"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def clean(argv):
 out=[];ignored=[];i=0
 while i<len(argv):
  if argv[i]=="-f" and i+1<len(argv):ignored+=argv[i:i+2];i+=2
  else:out.append(argv[i]);i+=1
 if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
 return out

def locate(explicit):
 c=[]
 if explicit:c.append(Path(explicit))
 c += [Path("geometric_flow_native_source_v0_10_1_results/active_repository_native_arb_backend_v0_9_30.py"),
       Path("/content/geometric_flow_native_source_v0_10_1_results/active_repository_native_arb_backend_v0_9_30.py")]
 for p in c:
  if p.is_file():return p.resolve()
 raise FileNotFoundError("Run v0.10.1 first or pass --active-backend PATH")

def source_segment(src,node):
 lines=src.splitlines()
 return textwrap.dedent("\n".join(lines[node.lineno-1:node.end_lineno]))

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--active-backend");ap.add_argument("--outdir",default="geometric_flow_scalar_primitives_v0_10_2_results")
 args,_=ap.parse_known_args(clean(sys.argv[1:]));active=locate(args.active_backend)
 if sha(active)!=EXPECTED_ACTIVE_SHA:raise RuntimeError(f"active backend hash mismatch: {sha(active)}")
 src=active.read_text();tree=ast.parse(src);mainfn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="main"),None)
 if mainfn is None:raise RuntimeError("main closure not found")
 wanted_defs={"ap","upper_point","ball","upper_float","DeltaJet","jet_matvec","nominal_state","projective_jet_and_derivatives","response_jacobian_and_gradient"}
 wanted_assign={"I","target_state","target_norm","target","orthogonal"}
 selected=[]
 for n in mainfn.body:
  name=getattr(n,"name",None)
  if name in wanted_defs:selected.append(n);continue
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   targets=n.targets if isinstance(n,ast.Assign) else [n.target]
   names={t.id for t in targets if isinstance(t,ast.Name)}
   if names & wanted_assign:selected.append(n)
 missing=wanted_defs-{getattr(n,"name",None) for n in selected}
 if missing:raise RuntimeError(f"missing closure definitions: {sorted(missing)}")
 constants={}
 for n in tree.body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {"OMEGA","TAU","CONTROL_DIMENSION","RESPONSE_ORDER","RESPONSE_DIMENSION","DELTA_ORDER","PRECISION_BITS","REFERENCE_PHASES"}:
   constants[n.targets[0].id]=source_segment(src,n)
 req={"OMEGA","TAU","CONTROL_DIMENSION","RESPONSE_ORDER","RESPONSE_DIMENSION","DELTA_ORDER","PRECISION_BITS","REFERENCE_PHASES"}
 if set(constants)!=req:raise RuntimeError(f"missing constants: {sorted(req-set(constants))}")
 out=Path(args.outdir).resolve();out.mkdir(parents=True,exist_ok=True);candidate=out/"geometric_flow_native_scalar_primitives_v0_10_2.py"
 body=["#!/usr/bin/env python3","from __future__ import annotations","import math","import numpy as np","from flint import acb, arb, ctx",""]
 body += [constants[k] for k in ["PRECISION_BITS","OMEGA","TAU","CONTROL_DIMENSION","RESPONSE_ORDER","RESPONSE_DIMENSION","DELTA_ORDER","REFERENCE_PHASES"]]
 body += ["ctx.prec=PRECISION_BITS",""]+[source_segment(src,n) for n in selected]
 body += ['''
def response_map(phases, analytic_output=True):
    z,_=projective_jet_and_derivatives(phases,mirror=False)
    zb,_=projective_jet_and_derivatives(phases,mirror=True)
    vals=[]
    for order in range(RESPONSE_ORDER+1): vals.append((z.c[order]+zb.c[order])/2)
    for order in range(RESPONSE_ORDER+1): vals.append((z.c[order]-zb.c[order])/(2*I))
    return vals if analytic_output else [v.real for v in vals]

def l6_gradient(phases, analytic_output=True):
    return response_jacobian_and_gradient(phases,analytic_output)[1]

SCALAR_PRIMITIVE_METADATA={
 "schema":"geometric-flow/native-scalar-primitives/v0.10.2",
 "source_active_backend_sha256":"'''+EXPECTED_ACTIVE_SHA+'''",
 "formal_backend":"python-flint/Arb","precision_bits":192,
 "input_dependent":True,"fixed_interval_shortcut":False,
 "scalar_arb_primitives_ready":True,"six_variable_jet_ready":False,
 "same_expression_DX_ready":False}
''']
 candidate.write_text("\n\n".join(body)+"\n")
 compile(candidate.read_text(),str(candidate),"exec")
 spec=importlib.util.spec_from_file_location("gf_scalar",candidate);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 phases=[mod.ap(x) for x in mod.REFERENCE_PHASES]
 response=mod.response_map(phases);jac,grad=mod.response_jacobian_and_gradient(phases,True)
 gates={"active_hash_exact":True,"dependency_definitions_complete":not missing,"candidate_compiles":True,"candidate_imports":True,"response_dimension_eight":len(response)==8,"jacobian_shape_8x14":len(jac)==8 and all(len(r)==14 for r in jac),"gradient_dimension_14":len(grad)==14,"no_fixed_interval_shortcut":"FIELD_MIDPOINTS" not in candidate.read_text() and "FIELD_RADII" not in candidate.read_text()}
 passed=all(gates.values());report={"title":TITLE,"version":VERSION,"scientific_status":"DEPENDENCY_CLOSED_NATIVE_SCALAR_ARB_PRIMITIVES_EXTRACTED" if passed else "V0102_FAILED_CLOSED","active_backend":str(active),"active_backend_sha256":sha(active),"candidate":str(candidate),"candidate_sha256":sha(candidate),"gates":gates,"scalar_arb_primitives_ready":passed,"six_variable_jet_ready":False,"same_expression_DX_ready":False,"all_scientific_gates_pass":False,"next_required_step":"lift acb phase arithmetic through the v0.10.0 six-variable Jet so response, implicit graph, L6 gradient, X and DX share one expression","claim_boundary":"input-dependent scalar Arb response/Jacobian/L6-gradient primitives only; no six-variable DX, QR/Lohner flowpipe, fifth frame, or global flow"}
 (out/"run_summary.json").write_text(json.dumps(report,indent=2)+"\n");print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(report,indent=2));return 0 if passed else 2

if __name__=="__main__":
 code=main()
 if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
