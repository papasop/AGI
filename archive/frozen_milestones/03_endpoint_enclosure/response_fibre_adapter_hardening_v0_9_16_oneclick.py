#!/usr/bin/env python3
"""Executable Geometric-Flow formal-adapter hardening audit v0.9.16."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,platform,sys,time
from pathlib import Path
VERSION="0.9.16";TITLE="GEOMETRIC-FLOW EXECUTABLE FORMAL-ADAPTER HARDENING AUDIT"
HASHES={"v093_source":"3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c","v074_source":"1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8","inputs_zip":"2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"}
REQUIRED=["formal_vector_field_X","formal_jacobian_DX","implicit_fibre_root_solver","adapter_metadata"]
TEMPLATE='''"""Implement against repository-native python-flint/Arb objects."""\nFROZEN_HASHES=%r\n\ndef adapter_metadata():\n    return {"dimension":6,"formal_backend":"python-flint/Arb","precision_bits":192,"frozen_repository_hashes":FROZEN_HASHES,"response_invariance_certified":False,"L6_descent_certified":False}\n\ndef formal_vector_field_X(a_box):\n    raise NotImplementedError("bind the v0.9.10 intrinsic field evaluator")\n\ndef formal_jacobian_DX(a_box):\n    raise NotImplementedError("bind the Arb derivative/Taylor evaluator")\n\ndef implicit_fibre_root_solver(a_box):\n    raise NotImplementedError("bind the normal-root Krawczyk solver")\n''' % HASHES
def atomic(p,o):p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(o,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_adapter_hardening_v0_9_16_results");p.add_argument("--adapter-module");return p.parse_known_args()
def load(path):
 spec=importlib.util.spec_from_file_location("gf_formal_adapter",path)
 if spec is None or spec.loader is None:raise ImportError("cannot load adapter module")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def arb_like(x):
 return hasattr(x,"contains") and hasattr(x,"mid")
def run(args):
 st=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);template=out/"geometric_flow_formal_adapter_template.py";template.write_text(TEMPLATE)
 path=Path(args.adapter_module) if args.adapter_module else template;module=None;errors=[]
 try:module=load(path)
 except Exception as e:errors.append(f"module_load:{type(e).__name__}:{e}")
 symbols={name:bool(module and callable(getattr(module,name,None))) for name in REQUIRED}
 metadata={}
 if symbols["adapter_metadata"]:
  try:metadata=module.adapter_metadata()
  except Exception as e:errors.append(f"metadata:{type(e).__name__}:{e}")
 meta_gates={"dimension_six":metadata.get("dimension")==6,"formal_backend_arb":metadata.get("formal_backend")=="python-flint/Arb","precision_at_least_192":int(metadata.get("precision_bits",0))>=192,"frozen_hashes_exact":metadata.get("frozen_repository_hashes")==HASHES,"response_invariance_certified":metadata.get("response_invariance_certified") is True,"L6_descent_certified":metadata.get("L6_descent_certified") is True}
 probes={"X_returns_six_Arb_values":False,"DX_returns_6x6_Arb_matrix":False,"root_solver_returns_certified_box":False,"invalid_dimension_rejected":False}
 if all(symbols.values()) and all(meta_gates.values()):
  try:
   import flint;flint.ctx.prec=192;a=[flint.arb(0) for _ in range(6)];x=module.formal_vector_field_X(a);dx=module.formal_jacobian_DX(a);root=module.implicit_fibre_root_solver(a)
   probes["X_returns_six_Arb_values"]=isinstance(x,(list,tuple)) and len(x)==6 and all(arb_like(v) for v in x)
   probes["DX_returns_6x6_Arb_matrix"]=isinstance(dx,(list,tuple)) and len(dx)==6 and all(isinstance(r,(list,tuple)) and len(r)==6 and all(arb_like(v) for v in r) for r in dx)
   probes["root_solver_returns_certified_box"]=isinstance(root,dict) and root.get("krawczyk_strict_inclusion") is True and isinstance(root.get("normal_root_box"),list)
   try:module.formal_vector_field_X([flint.arb(0)]*5)
   except Exception:probes["invalid_dimension_rejected"]=True
  except Exception as e:errors.append(f"probe:{type(e).__name__}:{e}")
 ready=all(symbols.values()) and all(meta_gates.values()) and all(probes.values())
 # Demonstrate why v0.9.15's truthiness-only JSON gate was insufficient.
 sham={k:"not-an-executable-formal-proof" for k in ["formal_vector_field_X","formal_jacobian_DX","implicit_fibre_root_solver","response_invariance_gate","L6_descent_gate","v0912_summary_sha256"]};old_truthiness=all(bool(v) for v in sham.values());hardened_rejects=not ready if path==template else True
 gates={"required_symbols_callable":all(symbols.values()),**meta_gates,**probes,"sham_truthy_JSON_would_pass_old_gate":old_truthiness,"hardened_verifier_rejects_unimplemented_template":hardened_rejects}
 result={"title":TITLE,"version":VERSION,"scientific_status":"EXECUTABLE_GEOMETRIC_FLOW_FORMAL_ADAPTER_CERTIFIED" if ready else "HARDENED_EXECUTABLE_ADAPTER_CONTRACT_READY_IMPLEMENTATION_OPEN","adapter_module":str(path),"generated_template":str(template),"required_symbols":symbols,"metadata":metadata,"probe_gates":probes,"errors":errors,"adapter_ready":ready,"geometric_flow_endpoint_certified":False,"all_scientific_gates_pass":ready,"gates":gates,"correction_to_v0915":"truthy JSON fields are not proof-producing callables and must not satisfy the adapter gate","claim_boundary":"adapter interface verification only; no 557-step endpoint until the executable repository-native adapter passes","next_required_step":"replace the generated NotImplemented template with bindings to the v0.9.10 Arb field, derivative, and normal-root backend","elapsed_seconds":time.time()-st,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 atomic(out/"run_summary.json",result);return result
def main():
 a,i=parse();
 if i:print(f"[notice] ignored notebook/kernel arguments: {i}")
 try:r=run(a);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0
 except Exception as e:print(json.dumps({"scientific_status":"V0916_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2
if __name__=="__main__":
 c=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(c)
