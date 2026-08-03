#!/usr/bin/env python3
"""Endpoint centre-identifiability audit for Geometric-Flow v0.9.14.

This audit prevents a reachable-radius bound from being silently promoted to
a trajectory endpoint.  It consumes the v0.9.12 summary, verifies its frozen
exhaustion certificate, and checks whether a six-component formally enclosed
endpoint centre was actually emitted.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,sys,time
from decimal import Decimal,getcontext
from pathlib import Path
from typing import Any
VERSION="0.9.14";TITLE="GEOMETRIC-FLOW TERMINAL ENDPOINT CENTRE-IDENTIFIABILITY AUDIT";getcontext().prec=80
EXPECTED_STEPS=557;EXPECTED_INNER=Decimal("1e-11")
def canonical(o:Any)->str:return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def atomic(p:Path,o:Any):p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(o,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def locate(explicit):
 candidates=[]
 if explicit:candidates.append(Path(explicit))
 candidates += [Path.cwd()/"response_fibre_transition_preflight_v0_9_12_results"/"run_summary.json",Path("/content/response_fibre_transition_preflight_v0_9_12_results/run_summary.json")]
 for p in candidates:
  if p.is_file():return p.resolve()
 raise FileNotFoundError("v0.9.12 run_summary.json not found; pass --v0912-summary PATH")
def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_endpoint_identifiability_v0_9_14_results");p.add_argument("--v0912-summary");p.add_argument("--endpoint-certificate");return p.parse_known_args()
def valid_vector(x):
 if not isinstance(x,list) or len(x)!=6:return False
 try:return all(Decimal(str(v)).is_finite() for v in x)
 except:return False
def run(args):
 st=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);sp=locate(args.v0912_summary);s=json.loads(sp.read_text())
 radius=Decimal(s["last_certified_radius"]);inner=Decimal(s["inner_domain_radius"]);n=int(s["maximum_certified_steps"])
 base={"v0912_preflight_gates_pass":s.get("all_preflight_gates_pass") is True,"maximum_step_count_matches":n==EXPECTED_STEPS,"last_radius_strictly_inside_inner_domain":radius<inner,"inner_radius_matches_frozen_protocol":inner==EXPECTED_INNER}
 cert_path=Path(args.endpoint_certificate) if args.endpoint_certificate else out/"terminal_endpoint_center_certificate.json"
 cert=json.loads(cert_path.read_text()) if cert_path.is_file() else {}
 center=cert.get("endpoint_center_midpoint");component_radii=cert.get("endpoint_component_radii");trajectory=cert.get("formal_stepwise_center_integrator")
 identity={"six_component_endpoint_center_present":valid_vector(center),"six_component_endpoint_radii_present":valid_vector(component_radii),"formal_stepwise_center_integrator_present":isinstance(trajectory,dict) and trajectory.get("formal_interval_arithmetic") is True,"endpoint_certificate_bound_to_557_steps":cert.get("step_index")==EXPECTED_STEPS,"endpoint_certificate_bound_to_v0912":cert.get("v0912_summary_sha256")==hashlib.sha256(sp.read_bytes()).hexdigest()}
 identifiable=all(identity.values())
 contract={"schema":"geometric-flow/formal-terminal-centre-integrator/v0.9.14","input_summary_sha256":hashlib.sha256(sp.read_bytes()).hexdigest(),"step_count":EXPECTED_STEPS,"dimension":6,"required_method":"validated interval ODE integrator or Taylor-model flowpipe; a scalar Gronwall radius alone is insufficient","required_outputs":["endpoint_center_midpoint[6]","endpoint_component_radii[6]","formal_stepwise_center_integrator","local_truncation_error_boxes","propagated_roundoff_boxes","endpoint_response_invariance_certificate","endpoint_L6_descent_certificate"],"acceptance_gate":"the emitted centre-radius box encloses every validated endpoint and is narrow enough for a new normal-root Krawczyk domain","forbidden_substitution":"do not set endpoint_center_midpoint=0 merely because the reachable tube was bounded around the chart origin"};atomic(out/"terminal_center_integrator_backend_contract.json",contract)
 status="FORMAL_TERMINAL_ENDPOINT_CENTRE_CERTIFIED" if identifiable and all(base.values()) else "SCALAR_REACHABLE_TUBE_CERTIFIED_ENDPOINT_CENTRE_NOT_IDENTIFIABLE"
 result={"title":TITLE,"version":VERSION,"scientific_status":status,"v0912_summary":str(sp),"v0912_summary_sha256":hashlib.sha256(sp.read_bytes()).hexdigest(),"reachable_tube":{"step_index":n,"radius":format(radius,".40E"),"inner_domain_radius":format(inner,".40E"),"scalar_radius_certified":all(base.values())},"base_gates":base,"centre_identifiability_gates":identity,"endpoint_centre_identifiable":identifiable,"same_chart_recenter_ready":identifiable,"all_scientific_gates_pass":all(base.values()) and identifiable,"backend_contract":str(out/"terminal_center_integrator_backend_contract.json"),"claim_boundary":"the scalar reachable tube is valid, but no trajectory endpoint centre is claimed unless every identifiability gate passes","next_required_step":"implement a validated six-dimensional interval/Taylor ODE integrator over the 557 steps and emit the contracted endpoint centre box","elapsed_seconds":time.time()-st,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 atomic(out/"run_summary.json",result);return result
def main():
 a,i=parse();
 if i:print(f"[notice] ignored notebook/kernel arguments: {i}")
 try:r=run(a);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if all(r["base_gates"].values()) else 2
 except Exception as e:print(json.dumps({"scientific_status":"V0914_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2
if __name__=="__main__":
 c=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(c)
