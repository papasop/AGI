#!/usr/bin/env python3
"""One-click two-microstep same-chart continuation certificate v0.9.5.

This program derives a finite continuation chain from the uniform formal Arb
bounds already certified in Geometric-Flow v0.9.3.  If, on the same intrinsic
chart domain D, ||X||_inf <= M, Lip(X) <= L, hL < 1, and the reachable boxes

    E_k = [-k h M, k h M]^6

remain inside the real Picard domain, the local solutions concatenate uniquely.
The v0.9.3 identity DR3 W = 0 and its uniform negative Lyapunov derivative are
then inherited along the concatenated solution.

Default output is exactly two certified microsteps.  This is not a complete
child, chart-overlap, arbitrary-endpoint or global-fibre theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
import urllib.request
from decimal import Decimal, getcontext, ROUND_FLOOR
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION="0.9.5"
TITLE="RESPONSE-FIBRE VALIDATED TWO-MICROSTEP SAME-CHART CONTINUATION"
CERT_URL=("https://raw.githubusercontent.com/papasop/Geometric-Flow/main/"
          "results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json")
CERT_SHA256="96cd24d34d1b426eef74696c83441510890b50902ae6cbe60fed3fc741bfbf3c"
ATLAS_SHA256="c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
V093_PROTOCOL_SHA256="6d0aaefabd71f1d2986515ed84673f0083ae90d0344b9a1e92d7697ac08d061a"
getcontext().prec=80


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def canonical_hash(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def atomic_json(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    tmp.replace(path)


def ds(x:Decimal)->str:
    return format(x,".40E")


def decimal_json(path:Path)->Dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"),parse_float=Decimal,parse_int=int)


def acquire(explicit:Optional[str],out:Path)->Tuple[Path,Dict[str,Any]]:
    path=Path(explicit) if explicit else out/"intrinsic_picard_microstep_certificate_v0_9_3.json"
    meta={"path":str(path),"source":"explicit" if explicit else CERT_URL,"downloaded":False}
    if not path.is_file():
        path.parent.mkdir(parents=True,exist_ok=True)
        urllib.request.urlretrieve(CERT_URL,path);meta["downloaded"]=True
    digest=sha256_file(path);meta.update({"sha256":digest,"frozen_hash_match":digest==CERT_SHA256})
    if digest!=CERT_SHA256:raise RuntimeError(f"frozen v0.9.3 certificate hash mismatch: {digest}")
    return path,meta


def require_v093(raw:Dict[str,Any])->None:
    truth=["all_gates_pass","formal_interval_arithmetic","ODE_existence_certified",
      "ODE_uniqueness_certified","exact_response_preservation_certified",
      "uniform_L6_descent_certified_for_validated_solution"]
    failed=[k for k in truth if raw.get(k) is not True]
    if failed:raise RuntimeError("v0.9.3 prerequisite gates failed: "+", ".join(failed))
    if raw.get("scientific_status")!="VALIDATED_INTRINSIC_RESPONSE_FIBRE_ODE_MICROSTEP_CERTIFIED":
        raise RuntimeError("unexpected v0.9.3 scientific status")
    if int(raw.get("tangent_dimension",-1))!=6:raise RuntimeError("expected six tangent dimensions")


def make_box(radius:Decimal)->Dict[str,Any]:
    return {"lower":[ds(-radius)]*6,"upper":[ds(radius)]*6,
      "coordinate_system":"v0.9.3-child-15-intrinsic-tangent-a"}


def run(args:argparse.Namespace)->Dict[str,Any]:
    started=time.time();out=Path(args.outdir);cert_dir=out/"certificates";cert_dir.mkdir(parents=True,exist_ok=True)
    path,acquisition=acquire(args.v093_certificate,out)
    raw=decimal_json(path);require_v093(raw)
    h=Decimal(raw["certified_time_step"])
    M=Decimal(raw["intrinsic_field_sup_norm_upper"])
    L=Decimal(raw["cauchy_lipschitz_upper"])
    r=Decimal(raw["inner_real_picard_radius"])
    R=Decimal(raw["outer_complex_tangent_radius"])
    descent=Decimal(raw["intrinsic_projected_gradient_norm_lower"])
    reported_contraction=Decimal(raw["picard_contraction_factor"])
    reported_displacement=Decimal(raw["picard_displacement_upper"])
    # Decimal recomputation is deliberately rounded outward by a tiny rational
    # guard that dominates decimal serialization roundoff of the frozen bounds.
    guard=Decimal("1.000000000000001")
    q=h*L*guard;d=h*M*guard
    per_step_drop=h*descent/guard
    safety=Decimal(str(args.domain_utilization_limit))
    if not Decimal(0)<safety<Decimal(1):raise ValueError("domain utilization limit must lie in (0,1)")
    max_steps=int(((safety*r)/d).to_integral_value(rounding=ROUND_FLOOR))
    gates={
      "frozen_certificate_hash":acquisition["frozen_hash_match"],
      "v093_all_formal_gates":True,
      "decimal_recomputed_contraction_below_half":q<Decimal("0.5"),
      "decimal_recomputed_displacement_consistent":d>=reported_displacement,
      "reported_contraction_consistent":q>=reported_contraction,
      "requested_steps_at_least_two":args.steps>=2,
      "requested_steps_within_uniform_domain":args.steps<=max_steps,
      "strict_uniform_L6_descent":descent>Decimal(0),
    }
    protocol={
      "title":TITLE,"version":VERSION,"steps":args.steps,"chart_index":9,"child_index":15,
      "source_certificate_sha256":CERT_SHA256,"source_atlas_sha256":ATLAS_SHA256,
      "source_v093_protocol_sha256":V093_PROTOCOL_SHA256,"time_step":ds(h),
      "field_sup_norm_upper_guarded":ds(M*guard),"lipschitz_upper_guarded":ds(L*guard),
      "inner_domain_radius":ds(r),"outer_complex_radius":ds(R),
      "domain_utilization_limit":ds(safety),"roundoff_guard":ds(guard),
      "continuation_lemma":("If X is uniformly Lipschitz on D, E_k is a reachable enclosure, "
        "and E_k + h[-M,M]^6 is contained in D, Picard uniqueness concatenates the next solution segment."),
      "claim_boundary":["same child and same intrinsic chart only","no complete-child coverage",
        "no chart transition","no arbitrary endpoint connection","no global fibre connectedness"]
    }
    protocol_hash=canonical_hash(protocol);atomic_json(out/"protocol.json",protocol)
    steps:List[Dict[str,Any]]=[]
    for k in range(args.steps):
        start_radius=Decimal(k)*d;end_radius=Decimal(k+1)*d
        start_time=Decimal(k)*h;end_time=Decimal(k+1)*h
        step_gates={
          "source_formal_Arb_domain":True,"picard_contraction":q<Decimal("0.5"),
          "start_reachable_box_inside_domain":start_radius<=safety*r,
          "endpoint_box_inside_domain":end_radius<=safety*r,
          "endpoint_in_next_admissible_start_domain":end_radius+d<=r if k+1<args.steps else True,
          "exact_response_preservation_inherited":True,"uniform_strict_L6_descent_inherited":True,
          "ODE_existence_inherited_on_uniform_domain":True,"ODE_uniqueness_enables_concatenation":True,
        }
        step={
          "schema":"geometric-flow-same-chart-continuation-step-v0.9.5",
          "scientific_status":("FORMAL_BOUND_DERIVED_SAME_CHART_CONTINUATION_STEP_CERTIFIED"
            if all(step_gates.values()) else "SAME_CHART_CONTINUATION_STEP_INCONCLUSIVE"),
          "step_index":k,"chart_index":9,"child_index":15,"tangent_dimension":6,
          "time_interval":[ds(start_time),ds(end_time)],"start_reachable_box":make_box(start_radius),
          "endpoint_box":make_box(end_radius),"uniform_domain_box":make_box(r),
          "endpoint_radius":ds(end_radius),"domain_utilization":ds(end_radius/r),
          "picard_contraction_upper_guarded":ds(q),"field_displacement_upper_guarded":ds(d),
          "L6_drop_lower_this_step":ds(per_step_drop),
          "L6_drop_lower_cumulative":ds(Decimal(k+1)*per_step_drop),
          "exact_response_preservation_certified":True,"ODE_existence_certified":True,
          "ODE_uniqueness_certified":True,"uniform_L6_descent_certified":True,
          "formal_interval_arithmetic_source":True,"derived_from_uniform_outward_bounds":True,
          "source_certificate_sha256":CERT_SHA256,"atlas_sha256":ATLAS_SHA256,
          "continuation_protocol_sha256":protocol_hash,"gates":step_gates,
          "all_step_gates_pass":all(step_gates.values())
        }
        step["certificate_sha256_before_self_field"]=canonical_hash(step)
        atomic_json(cert_dir/f"step_{k:04d}.json",step);steps.append(step)
    inclusions=[]
    for a,b in zip(steps,steps[1:]):
        ar=Decimal(a["endpoint_radius"]);br=Decimal(b["start_reachable_box"]["upper"][0])
        inc={"from_step":a["step_index"],"to_step":b["step_index"],
          "endpoint_equals_next_reachable_start":ar==br,
          "endpoint_inside_uniform_domain":ar<=r,"time_contiguous":a["time_interval"][1]==b["time_interval"][0]}
        inc["pass"]=all(inc[x] for x in ("endpoint_equals_next_reachable_start","endpoint_inside_uniform_domain","time_contiguous"));inclusions.append(inc)
    all_pass=all(gates.values()) and all(s["all_step_gates_pass"] for s in steps) and all(x["pass"] for x in inclusions)
    status=("VALIDATED_TWO_MICROSTEP_SAME_CHART_CONTINUATION_CERTIFIED" if all_pass and args.steps==2 else
      "VALIDATED_FINITE_MULTI_MICROSTEP_SAME_CHART_CONTINUATION_CERTIFIED" if all_pass else
      "SAME_CHART_CONTINUATION_INCONCLUSIVE_FAIL_CLOSED")
    result={"title":TITLE,"version":VERSION,"scientific_status":status,
      "all_scientific_gates_pass":all_pass,"requested_steps":args.steps,"maximum_steps_under_frozen_uniform_bound":max_steps,
      "total_certified_time":ds(Decimal(args.steps)*h),"final_reachable_radius":ds(Decimal(args.steps)*d),
      "minimum_cumulative_L6_drop":ds(Decimal(args.steps)*per_step_drop),
      "acquisition":acquisition,"protocol_sha256":protocol_hash,"gates":gates,
      "step_certificates":[str(cert_dir/f"step_{k:04d}.json") for k in range(args.steps)],
      "endpoint_inclusions":inclusions,"same_chart_only":True,"complete_child_certified":False,
      "ten_chart_continuation_certified":False,"global_flow_claimed":False,
      "mathematical_basis":("finite continuation by uniform Picard bounds on one already Arb-certified intrinsic chart domain; "
        "reachable boxes are accumulated with guarded outward scalar bounds"),
      "next_required_step":"Recenter/reframe the Arb fibre graph or certify coverage to the child boundary before claiming complete-child traversal.",
      "elapsed_seconds":time.time()-started,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
    result["report_sha256_before_self_field"]=canonical_hash(result);atomic_json(out/"run_summary.json",result)
    return result


def parse_args()->Tuple[argparse.Namespace,List[str]]:
    p=argparse.ArgumentParser();p.add_argument("--steps",type=int,default=2)
    p.add_argument("--outdir",default="response_fibre_two_step_v0_9_5_results")
    p.add_argument("--v093-certificate");p.add_argument("--domain-utilization-limit",type=float,default=0.95)
    return p.parse_known_args()


def main()->int:
    args,ignored=parse_args()
    if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    try:
        result=run(args);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(result,indent=2))
        return 0 if result["all_scientific_gates_pass"] else 2
    except Exception as exc:
        print(json.dumps({"scientific_status":"V095_FAILED_CLOSED","error_type":type(exc).__name__,"error":str(exc)},indent=2));return 2


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
