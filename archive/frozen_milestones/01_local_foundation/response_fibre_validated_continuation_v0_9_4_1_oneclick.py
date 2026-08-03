#!/usr/bin/env python3
"""Fail-closed validated response-fibre continuation auditor v0.9.4.

This is the next theorem-infrastructure step after Geometric-Flow v0.9.3.
It does NOT turn the v0.9.3 microstep into a global theorem. Instead it defines
and audits the missing chain contract:

    certified endpoint box of step k
        subset of
    certified start domain of step k+1.

It additionally checks time contiguity, frozen response identity, strict L6
descent, atlas/protocol identity, chart transitions and declared coverage.

Examples
--------
  python response_fibre_validated_continuation_v0_9_4.py --self-test
  python response_fibre_validated_continuation_v0_9_4.py \
      --certificates 'certificates/step_*.json'
  python response_fibre_validated_continuation_v0_9_4.py \
      --inspect-v093 results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json
  python response_fibre_validated_continuation_v0_9_4.py --write-template step_template.json

Certificate boxes use coordinate-wise closed intervals:
  {"lower": [..], "upper": [..], "coordinate_system": "chart-9-tangent-a"}
All numeric comparisons are structural checks on outward-rounded endpoints
already produced by a formal backend; this auditor is not itself interval
arithmetic and never upgrades nonformal input to a formal proof.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import platform
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "0.9.4.1"
TITLE = "VALIDATED RESPONSE-FIBRE ENDPOINT-INCLUSION CONTINUATION AUDIT"
V093_CERTIFICATE_URL = (
    "https://raw.githubusercontent.com/papasop/Geometric-Flow/main/"
    "results/v0_9_3_reference/intrinsic_picard_microstep_certificate.json"
)
V093_CERTIFICATE_SHA256 = "96cd24d34d1b426eef74696c83441510890b50902ae6cbe60fed3fc741bfbf3c"
V093_REQUIRED_ADDITIONS = [
    "atlas_sha256", "continuation_protocol_sha256", "step_index",
    "chart_index", "time_interval", "start_domain_box", "endpoint_box",
    "response_box", "L6_start_interval", "L6_end_interval",
]


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def finite_number(x: Any, name: str) -> float:
    if isinstance(x, bool): raise TypeError(f"{name} cannot be boolean")
    y = float(x)
    if not math.isfinite(y): raise ValueError(f"{name} must be finite")
    return y


def interval(value: Any, name: str) -> Tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{name} must be [lower, upper]")
    lo, hi = finite_number(value[0], name+".lower"), finite_number(value[1], name+".upper")
    if lo > hi: raise ValueError(f"{name} has lower > upper")
    return lo, hi


def box(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict): raise TypeError(f"{name} must be an object")
    lower, upper = value.get("lower"), value.get("upper")
    system = value.get("coordinate_system")
    if not isinstance(lower, list) or not isinstance(upper, list) or not lower:
        raise ValueError(f"{name} requires nonempty lower/upper arrays")
    if len(lower) != len(upper): raise ValueError(f"{name} lower/upper dimension mismatch")
    lo = [finite_number(x, f"{name}.lower[{i}]") for i,x in enumerate(lower)]
    hi = [finite_number(x, f"{name}.upper[{i}]") for i,x in enumerate(upper)]
    if any(a>b for a,b in zip(lo,hi)): raise ValueError(f"{name} contains reversed interval")
    if not isinstance(system,str) or not system: raise ValueError(f"{name} requires coordinate_system")
    return {"lower":lo,"upper":hi,"coordinate_system":system}


def subset(inner: Dict[str, Any], outer: Dict[str, Any], tolerance: float=0.0) -> bool:
    if inner["coordinate_system"] != outer["coordinate_system"]: return False
    if len(inner["lower"]) != len(outer["lower"]): return False
    return all(o0-tolerance <= i0 and i1 <= o1+tolerance
               for i0,i1,o0,o1 in zip(inner["lower"],inner["upper"],outer["lower"],outer["upper"]))


def intersection_nonempty(a: Tuple[float,float], b: Tuple[float,float]) -> bool:
    return max(a[0],b[0]) <= min(a[1],b[1])


def template() -> Dict[str, Any]:
    zeros=[0.0]*6; eps=[1e-12]*6
    return {
      "schema":"geometric-flow-continuation-step-v0.9.4",
      "scientific_status":"FORMAL_ENDPOINT_ENCLOSURE_STEP_CERTIFIED",
      "formal_interval_arithmetic":True,"arb_precision_bits":192,
      "all_step_gates_pass":True,"atlas_sha256":"REPLACE_FROZEN_ATLAS_SHA256",
      "continuation_protocol_sha256":"REPLACE_FROZEN_CONTINUATION_PROTOCOL_SHA256",
      "response_id_sha256":"REPLACE_FROZEN_RESPONSE_VALUE_SHA256",
      "step_index":0,"chart_index":9,"child_index":15,"time_interval":[0.0,1e-14],
      "start_domain_box":{"lower":[-x for x in eps],"upper":eps,"coordinate_system":"chart-9-tangent-a"},
      "endpoint_box":{"lower":zeros,"upper":[5.9e-15]*6,"coordinate_system":"chart-9-tangent-a"},
      "response_box":[-1e-30,1e-30],
      "L6_start_interval":[1.0,1.0],"L6_end_interval":[0.99999999999999,0.999999999999995],
      "endpoint_enclosure_formal":True,"exact_response_preservation_certified":True,
      "ODE_existence_certified":True,"ODE_uniqueness_certified":True,
      "uniform_L6_descent_certified":True,"transition_to_next":None,
      "coverage":{"chart_parameter_interval":[0.0,1.0],"covered_interval":[0.0,1e-14]},
      "source_certificate_sha256":"REPLACE_SHA256_OF_FORMAL_BACKEND_CERTIFICATE"
    }


def validate_step(raw: Dict[str,Any], source: str) -> Dict[str,Any]:
    required=set(V093_REQUIRED_ADDITIONS)|{
      "schema","scientific_status","formal_interval_arithmetic","arb_precision_bits",
      "all_step_gates_pass","response_id_sha256","endpoint_enclosure_formal",
      "exact_response_preservation_certified","ODE_existence_certified",
      "ODE_uniqueness_certified","uniform_L6_descent_certified"
    }
    missing=sorted(required-set(raw))
    errors=[]
    if missing: errors.append("missing fields: "+", ".join(missing))
    parsed={}
    if not missing:
        try:
            parsed={
              "source":source,"raw":raw,"step_index":int(raw["step_index"]),
              "chart_index":int(raw["chart_index"]),"child_index":int(raw.get("child_index",-1)),
              "time_interval":interval(raw["time_interval"],source+".time_interval"),
              "start":box(raw["start_domain_box"],source+".start_domain_box"),
              "end":box(raw["endpoint_box"],source+".endpoint_box"),
              "response":interval(raw["response_box"],source+".response_box"),
              "L6_start":interval(raw["L6_start_interval"],source+".L6_start_interval"),
              "L6_end":interval(raw["L6_end_interval"],source+".L6_end_interval"),
            }
            if parsed["time_interval"][0] >= parsed["time_interval"][1]: errors.append("time interval is not positive")
            truth_fields=["formal_interval_arithmetic","all_step_gates_pass","endpoint_enclosure_formal",
              "exact_response_preservation_certified","ODE_existence_certified",
              "ODE_uniqueness_certified","uniform_L6_descent_certified"]
            false_fields=[k for k in truth_fields if raw.get(k) is not True]
            if false_fields: errors.append("required true fields failed: "+", ".join(false_fields))
            if raw.get("schema")!="geometric-flow-continuation-step-v0.9.4": errors.append("wrong schema")
            if int(raw["arb_precision_bits"])<192: errors.append("precision below 192 bits")
            if parsed["L6_end"][1] >= parsed["L6_start"][0]: errors.append("strict interval L6 descent not certified")
        except Exception as exc:
            errors.append(f"parse error: {type(exc).__name__}: {exc}")
    return {"valid":not errors,"errors":errors,"parsed":parsed,"sha256":sha256_obj(raw),"source":source}


def transition_inclusion(left: Dict[str,Any], right: Dict[str,Any]) -> Dict[str,Any]:
    a,b=left["parsed"],right["parsed"]
    raw=left["parsed"]["raw"]
    same_chart=a["chart_index"]==b["chart_index"]
    if same_chart:
        included=subset(a["end"],b["start"])
        mode="same-chart direct inclusion"
        transition_ok=True
    else:
        tr=raw.get("transition_to_next")
        transition_ok=isinstance(tr,dict) and tr.get("formal") is True and tr.get("target_chart_index")==b["chart_index"]
        mode="cross-chart formal transition"
        included=False
        if transition_ok:
            try:
                image=box(tr["endpoint_image_box"],"transition.endpoint_image_box")
                included=subset(image,b["start"])
            except Exception:
                transition_ok=False
    time_ok=math.isclose(a["time_interval"][1],b["time_interval"][0],rel_tol=0.0,abs_tol=0.0)
    protocol_ok=raw["continuation_protocol_sha256"]==right["parsed"]["raw"]["continuation_protocol_sha256"]
    atlas_ok=raw["atlas_sha256"]==right["parsed"]["raw"]["atlas_sha256"]
    response_id_ok=raw["response_id_sha256"]==right["parsed"]["raw"]["response_id_sha256"]
    response_overlap=intersection_nonempty(a["response"],b["response"])
    L6_chain=a["L6_end"][1] <= b["L6_start"][0]
    gates={"endpoint_in_next_domain":included,"time_contiguous":time_ok,
      "transition_certificate_valid":transition_ok,"same_protocol":protocol_ok,
      "same_atlas":atlas_ok,"same_response_id":response_id_ok,
      "response_enclosures_compatible":response_overlap,"L6_chain_nonincreasing":L6_chain}
    return {"from_step":a["step_index"],"to_step":b["step_index"],"mode":mode,
      "gates":gates,"pass":all(gates.values())}


def audit(raw_steps: Sequence[Tuple[str,Dict[str,Any]]], output: Path) -> Dict[str,Any]:
    checked=[validate_step(raw,source) for source,raw in raw_steps]
    valid=sorted((x for x in checked if x["valid"]),key=lambda x:x["parsed"]["step_index"])
    indices=[x["parsed"]["step_index"] for x in valid]
    unique_indices=len(indices)==len(set(indices))
    consecutive=bool(indices) and indices==list(range(indices[0],indices[0]+len(indices)))
    transitions=[transition_inclusion(a,b) for a,b in zip(valid,valid[1:])]
    all_steps_valid=len(valid)==len(checked) and bool(valid)
    all_transitions=bool(transitions) and all(x["pass"] for x in transitions)
    charts=sorted({x["parsed"]["chart_index"] for x in valid})
    full_child=False; full_atlas=False
    # Coverage claims are accepted only when every step has a formal coverage object and
    # the aggregate declared intervals close without gaps. This structural auditor still
    # reports, rather than creates, the backend's interval proof.
    coverage=[]
    for x in valid:
        c=x["parsed"]["raw"].get("coverage")
        if isinstance(c,dict):
            try: coverage.append((x["parsed"]["chart_index"],interval(c["chart_parameter_interval"],"chart"),interval(c["covered_interval"],"covered")))
            except Exception: pass
    if valid and len(coverage)==len(valid):
        by_chart:Dict[int,List[Tuple[float,float]]]={}
        targets:Dict[int,Tuple[float,float]]={}
        for chart,target,cov in coverage: by_chart.setdefault(chart,[]).append(cov);targets[chart]=target
        chart_pass=[]
        for chart,parts in by_chart.items():
            parts.sort(); cursor=targets[chart][0]
            ok=True
            for lo,hi in parts:
                if lo>cursor: ok=False;break
                cursor=max(cursor,hi)
            chart_pass.append(ok and cursor>=targets[chart][1])
        full_child=all(chart_pass) and len(charts)==1
        full_atlas=all(chart_pass) and charts==list(range(10)) and all_transitions
    gates={"at_least_two_steps":len(valid)>=2,"all_step_certificates_valid":all_steps_valid,
      "unique_step_indices":unique_indices,"consecutive_step_indices":consecutive,
      "all_endpoint_inclusions_and_transitions":all_transitions}
    chain_pass=all(gates.values())
    status=("VALIDATED_TEN_CHART_CONTINUATION_CERTIFIED" if chain_pass and full_atlas else
      "VALIDATED_COMPLETE_CHILD_CONTINUATION_CERTIFIED" if chain_pass and full_child else
      "VALIDATED_MULTI_MICROSTEP_CHAIN_CERTIFIED" if chain_pass else
      "CONTINUATION_AUDIT_INCONCLUSIVE_FAIL_CLOSED")
    result={"title":TITLE,"version":VERSION,"scientific_status":status,
      "formal_backend_claim_preserved_not_created_by_auditor":True,
      "input_certificates":len(checked),"valid_steps":len(valid),"step_indices":indices,
      "charts_covered":charts,"step_results":[{"source":x["source"],"sha256":x["sha256"],"valid":x["valid"],"errors":x["errors"]} for x in checked],
      "transitions":transitions,"gates":gates,"multi_microstep_chain_certified":chain_pass,
      "complete_child_certified":bool(chain_pass and full_child),
      "ten_chart_continuation_certified":bool(chain_pass and full_atlas),
      "arbitrary_endpoint_connection_claimed":False,"global_fibre_connectedness_claimed":False,
      "next_required_step":("Supply formal endpoint/start-domain boxes from a modified Arb backend."
        if not chain_pass else "Extend certified coverage while preserving endpoint inclusion; do not infer arbitrary fibre connectedness."),
      "elapsed_seconds":time.time()-START,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
    result["audit_sha256_before_self_field"]=sha256_obj(result)
    atomic_json(output,result)
    return result


def inspect_v093(path: str, output: Path) -> Dict[str,Any]:
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    missing=sorted(set(V093_REQUIRED_ADDITIONS)-set(raw))
    result={"title":TITLE,"version":VERSION,"scientific_status":"V093_CERTIFICATE_NOT_CHAINABLE_AS_IS",
      "input":str(path),"input_sha256":sha256_obj(raw),"v093_all_gates_pass":raw.get("all_gates_pass"),
      "missing_continuation_fields":missing,"endpoint_inclusion_certified":False,
      "explanation":"v0.9.3 proves one local ODE microstep but does not enclose its endpoint in coordinates accepted by a next-step domain.",
      "next_required_step":"Modify the Arb backend to emit start_domain_box and endpoint_box, then certify endpoint_box subset next start_domain_box."}
    atomic_json(output,result);return result


def sha256_file(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""):digest.update(chunk)
    return digest.hexdigest()


def one_click(outdir: Path, explicit_v093: Optional[str]=None) -> Dict[str,Any]:
    """Run the safe default workflow without requiring notebook arguments."""
    outdir.mkdir(parents=True,exist_ok=True)
    self_result=self_test()
    cert=Path(explicit_v093) if explicit_v093 else outdir/"intrinsic_picard_microstep_certificate_v0_9_3.json"
    acquisition={"source":"explicit local file" if explicit_v093 else V093_CERTIFICATE_URL,"path":str(cert)}
    if not cert.is_file():
        try:
            urllib.request.urlretrieve(V093_CERTIFICATE_URL,cert)
            acquisition["downloaded"]=True
        except Exception as exc:
            acquisition.update({"downloaded":False,"error":f"{type(exc).__name__}: {exc}"})
    certificate_check=None
    if cert.is_file():
        digest=sha256_file(cert)
        acquisition["sha256"]=digest
        acquisition["frozen_hash_match"]=digest==V093_CERTIFICATE_SHA256
        if digest!=V093_CERTIFICATE_SHA256:
            acquisition["error"]="v0.9.3 certificate hash mismatch; inspection refused"
        else:
            certificate_check=inspect_v093(str(cert),outdir/"v093_chainability_report.json")
    step_template=outdir/"continuation_step_template.json"
    atomic_json(step_template,template())
    ready=bool(self_result["all_self_tests_pass"] and certificate_check is not None and acquisition.get("frozen_hash_match"))
    result={
      "title":TITLE,"version":VERSION,
      "scientific_status":("ONE_CLICK_CONTINUATION_PREFLIGHT_COMPLETE_BACKEND_UPGRADE_REQUIRED" if ready
        else "ONE_CLICK_CONTINUATION_PREFLIGHT_INCOMPLETE"),
      "self_test":self_result,"v093_acquisition":acquisition,
      "v093_chainability":certificate_check,
      "continuation_step_template":str(step_template),
      "formal_continuation_certified":False,
      "why_not_yet":("The frozen v0.9.3 theorem is valid but its certificate has no formal endpoint box in next-step coordinates."
        if certificate_check else "The frozen v0.9.3 certificate could not be verified locally."),
      "backend_requirements":[
        "emit an outward-rounded start_domain_box",
        "integrate one formal microstep and emit endpoint_box",
        "prove endpoint_box subset next start_domain_box",
        "repeat with frozen atlas/protocol/response hashes",
        "emit a formal chart transition image box at every chart boundary"
      ],
      "next_command_after_backend_outputs":(
        "python archive/frozen_milestones/01_local_foundation/response_fibre_validated_continuation_v0_9_4_1_oneclick.py "
        "--certificates 'certificates/step_*.json'"),
      "claim_boundary":"This preflight defines and tests the continuation proof contract; it is not a multi-step or global-flow certificate."
    }
    result["report_sha256_before_self_field"]=sha256_obj(result)
    atomic_json(outdir/"oneclick_report.json",result)
    return result


def self_test() -> Dict[str,Any]:
    base=template();base.update({"atlas_sha256":"a"*64,"continuation_protocol_sha256":"b"*64,
      "response_id_sha256":"c"*64,"source_certificate_sha256":"d"*64})
    a=json.loads(json.dumps(base));b=json.loads(json.dumps(base))
    a["step_index"]=0;a["time_interval"]=[0.0,1e-14]
    a["endpoint_box"]={"lower":[1e-15]*6,"upper":[2e-15]*6,"coordinate_system":"chart-9-tangent-a"}
    a["L6_start_interval"]=[1.0,1.0];a["L6_end_interval"]=[0.9,0.91]
    b["step_index"]=1;b["time_interval"]=[1e-14,2e-14]
    b["start_domain_box"]={"lower":[0.0]*6,"upper":[3e-15]*6,"coordinate_system":"chart-9-tangent-a"}
    b["L6_start_interval"]=[0.91,0.92];b["L6_end_interval"]=[0.8,0.81]
    ca,cb=validate_step(a,"self-a"),validate_step(b,"self-b")
    good=ca["valid"] and cb["valid"] and transition_inclusion(ca,cb)["pass"]
    bad=json.loads(json.dumps(b));bad["start_domain_box"]["upper"]=[1.5e-15]*6
    cbad=validate_step(bad,"self-bad")
    rejection=cbad["valid"] and not transition_inclusion(ca,cbad)["pass"]
    return {"good_chain_accepted":good,"broken_inclusion_rejected":rejection,"all_self_tests_pass":good and rejection}


def parse_args() -> Tuple[argparse.Namespace,List[str]]:
    p=argparse.ArgumentParser()
    p.add_argument("--certificates",help="Glob for ordered JSON step certificates")
    p.add_argument("--inspect-v093")
    p.add_argument("--write-template")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--one-click",action="store_true",help="default when no mode is supplied")
    p.add_argument("--v093-certificate",help="optional local frozen v0.9.3 certificate")
    p.add_argument("--outdir",default="response_fibre_continuation_v0_9_4_1_results")
    p.add_argument("--output",default="response_fibre_continuation_v0_9_4_results/report.json")
    return p.parse_known_args()


START=time.time()


def main() -> int:
    args,ignored=parse_args()
    if ignored: print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    try:
        no_explicit_mode=not any((args.write_template,args.self_test,args.inspect_v093,args.certificates))
        if args.one_click or no_explicit_mode:
            result=one_click(Path(args.outdir),args.v093_certificate)
            print("="*112);print(f"{TITLE} v{VERSION} — ONE CLICK");print("="*112)
            print(json.dumps(result,indent=2))
            return 0 if result["scientific_status"]=="ONE_CLICK_CONTINUATION_PREFLIGHT_COMPLETE_BACKEND_UPGRADE_REQUIRED" else 2
        if args.write_template:
            atomic_json(Path(args.write_template),template());print(args.write_template);return 0
        if args.self_test:
            result=self_test();print(json.dumps(result,indent=2));return 0 if result["all_self_tests_pass"] else 2
        output=Path(args.output)
        if args.inspect_v093:
            result=inspect_v093(args.inspect_v093,output)
        elif args.certificates:
            paths=sorted(glob.glob(args.certificates))
            if not paths: raise FileNotFoundError(f"No files match {args.certificates!r}")
            result=audit([(p,json.loads(Path(p).read_text(encoding="utf-8"))) for p in paths],output)
        else:
            raise ValueError("Choose --self-test, --inspect-v093, --write-template, or --certificates")
        print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(result,indent=2))
        return 0 if result.get("multi_microstep_chain_certified",False) else 2
    except Exception as exc:
        result={"scientific_status":"CONTINUATION_AUDIT_FAILED_CLOSED","error_type":type(exc).__name__,"error":str(exc)}
        print(json.dumps(result,indent=2));return 2


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
