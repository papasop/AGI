#!/usr/bin/env python3
"""Repository-native recentering preflight for Geometric-Flow v0.9.6.

The program downloads and hash-verifies the frozen v0.9.3 generator, v0.7.4
Arb backend and v0.6.2 input archive from papasop/Geometric-Flow. It applies a
small auditable instrumentation patch that exposes the six component intervals
of the intrinsic field at the certified centre, reruns the formal v0.9.3 audit,
and constructs an outward guarded candidate recenter/endpoint enclosure.

It intentionally does not claim a recentered fibre-chart theorem until a new
normal-root Krawczyk solve and a new tangent/normal frame pass at that centre.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Dict, List, Tuple

VERSION="0.9.6"
TITLE="GEOMETRIC-FLOW REPOSITORY-NATIVE RECENTERED FIBRE-CHART PREFLIGHT"
REPO="https://github.com/papasop/Geometric-Flow"
RAW="https://raw.githubusercontent.com/papasop/Geometric-Flow/main"
FILES={
 "v093_source":("src/response_fibre_intrinsic_picard_microstep_v0_9_3.py","3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"),
 "v074_source":("src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py","1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"),
 "inputs_zip":("inputs/response_fibre_v0_6_2_backend_inputs.zip","2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"),
}
FROZEN_ATLAS_SHA256="c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
getcontext().prec=80


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def canonical_hash(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def atomic_json(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8");tmp.replace(path)


def ensure_flint()->str:
    try:
        import flint
        return getattr(flint,"__version__","installed")
    except ModuleNotFoundError:
        notebook="ipykernel" in sys.modules or "google.colab" in sys.modules
        if not notebook:raise RuntimeError("Install the formal backend with: python -m pip install python-flint==0.8.0")
        print("[setup] installing frozen formal backend python-flint==0.8.0")
        subprocess.check_call([sys.executable,"-m","pip","install","-q","python-flint==0.8.0"])
        importlib.invalidate_caches();import flint
        return getattr(flint,"__version__","0.8.0")


def acquire(out:Path)->Dict[str,Any]:
    root=out/"frozen_repository_inputs";root.mkdir(parents=True,exist_ok=True);records={}
    for key,(rel,expected) in FILES.items():
        path=root/Path(rel).name
        if not path.is_file():
            print(f"[repository] downloading {rel}");urllib.request.urlretrieve(f"{RAW}/{rel}",path)
        digest=sha256_file(path);ok=digest==expected
        records[key]={"repository":REPO,"repository_path":rel,"local_path":str(path),
          "sha256":digest,"expected_sha256":expected,"hash_match":ok}
        if not ok:raise RuntimeError(f"frozen repository hash mismatch for {rel}: {digest}")
    return records


def instrument(source:Path,destination:Path)->Dict[str,Any]:
    text=source.read_text(encoding="utf-8")
    needle='''    field_sup = max((upper_point(value) for value in field), default=arb(0))'''
    injected='''    # v0.9.6 instrumentation: expose the centre-field component disks.\n    # This changes reporting only; every v0.9.3 proof gate remains untouched.\n    v096_field_component_midpoints = []\n    v096_field_component_radii = []\n    for v096_value in field:\n        v096_mid = midpoint_radius(v096_value.real)[0]\n        v096_rad = upper_point(v096_value - acb(ap(v096_mid)))\n        v096_field_component_midpoints.append(float(v096_mid))\n        v096_field_component_radii.append(upper_float(v096_rad))\n\n'''+needle
    if text.count(needle)!=1:raise RuntimeError(f"expected exactly one v0.9.3 field-sup hook, found {text.count(needle)}")
    text=text.replace(needle,injected,1)
    result_needle='''        "intrinsic_field_sup_norm_upper": upper_float(field_sup),'''
    result_injected=result_needle+'''\n        "v096_intrinsic_field_component_midpoints": v096_field_component_midpoints,\n        "v096_intrinsic_field_component_radii": v096_field_component_radii,'''
    if text.count(result_needle)!=1:raise RuntimeError("v0.9.3 result hook not uniquely found")
    text=text.replace(result_needle,result_injected,1)
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(text,encoding="utf-8")
    return {"base_source_sha256":sha256_file(source),"instrumented_source_sha256":sha256_file(destination),
      "patch_scope":"report centre-field component midpoint/radius disks only","proof_gate_logic_modified":False}


def decimal(x:Any)->Decimal:return Decimal(str(x))


def run(args:argparse.Namespace)->Dict[str,Any]:
    started=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    flint_version=ensure_flint();records=acquire(out)
    patched=out/"instrumented_response_fibre_v0_9_3_for_v0_9_6.py"
    patch_record=instrument(Path(records["v093_source"]["local_path"]),patched)
    base_out=out/"formal_base_rerun"
    cmd=[sys.executable,str(patched),"--inputs-zip",records["inputs_zip"]["local_path"],
      "--v074-source",records["v074_source"]["local_path"],"--no-download","--output",str(base_out)]
    completed=subprocess.run(cmd,text=True,capture_output=True)
    (out/"formal_backend_stdout.txt").write_text(completed.stdout,encoding="utf-8")
    (out/"formal_backend_stderr.txt").write_text(completed.stderr,encoding="utf-8")
    cert_path=base_out/"intrinsic_picard_microstep_certificate.json"
    if not cert_path.is_file():raise RuntimeError(f"instrumented formal backend exit={completed.returncode}; certificate missing; inspect logs")
    cert=json.loads(cert_path.read_text(encoding="utf-8"))
    mids=cert.get("v096_intrinsic_field_component_midpoints")
    radii=cert.get("v096_intrinsic_field_component_radii")
    if not isinstance(mids,list) or not isinstance(radii,list) or len(mids)!=6 or len(radii)!=6:
        raise RuntimeError("instrumented backend did not emit six field component disks")
    h=decimal(cert["certified_time_step"]);L=decimal(cert["cauchy_lipschitz_upper"])
    M=decimal(cert["intrinsic_field_sup_norm_upper"]);r=decimal(cert["inner_real_picard_radius"])
    guard=Decimal("1.000000000000001");d=h*M*guard
    # For a(t)=integral X(a(s)) ds, the deviation from Euler centre h X(0)
    # is bounded by h*L*sup|a(s)| <= h*L*d. Component disk uncertainty is added.
    nonlinear=h*L*d*guard
    centre=[];endpoint_lower=[];endpoint_upper=[];component_radii=[]
    for m,rad in zip(mids,radii):
        c=h*decimal(m);rr=h*decimal(rad)*guard+nonlinear
        centre.append(c);component_radii.append(rr);endpoint_lower.append(c-rr);endpoint_upper.append(c+rr)
    max_endpoint=max(max(abs(x) for x in endpoint_lower),max(abs(x) for x in endpoint_upper))
    proposed_new_radius=decimal(str(args.recenter_radius))
    endpoint_in_proposed=all(-proposed_new_radius<=lo and hi<=proposed_new_radius for lo,hi in zip(endpoint_lower,endpoint_upper))
    base_gates={
      "all_repository_hashes_match":all(x["hash_match"] for x in records.values()),
      "instrumentation_did_not_modify_proof_gates":not patch_record["proof_gate_logic_modified"],
      "formal_v093_rerun_exit_zero":completed.returncode==0,
      "formal_v093_all_gates_pass":cert.get("all_gates_pass") is True,
      "six_field_component_disks_emitted":len(mids)==len(radii)==6,
      "candidate_endpoint_inside_original_inner_domain":max_endpoint<r,
      "candidate_endpoint_inside_proposed_recenter_box":endpoint_in_proposed,
    }
    # These are deliberately false until a new Arb normal-root/frame audit is implemented.
    theorem_gates={
      **base_gates,
      "recentered_normal_root_krawczyk_certified":False,
      "recentered_response_exactly_matches_frozen_response":False,
      "recentered_tangent_normal_frame_certified":False,
      "recentered_pullback_metric_and_picard_certified":False,
      "old_endpoint_in_new_formal_fibre_graph_domain":False,
    }
    candidate={
      "coordinate_system":"v0.9.3-child-15-intrinsic-tangent-a",
      "euler_recenter_midpoint":[format(x,".40E") for x in centre],
      "guarded_endpoint_lower":[format(x,".40E") for x in endpoint_lower],
      "guarded_endpoint_upper":[format(x,".40E") for x in endpoint_upper],
      "guarded_component_radius":[format(x,".40E") for x in component_radii],
      "nonlinear_lipschitz_remainder_per_component":format(nonlinear,".40E"),
      "maximum_endpoint_absolute_coordinate":format(max_endpoint,".40E"),
      "proposed_recenter_box_radius":format(proposed_new_radius,".40E"),
    }
    protocol={"version":VERSION,"repository":REPO,"repository_default_branch":"main",
      "frozen_atlas_sha256":FROZEN_ATLAS_SHA256,"v093_source_sha256":FILES["v093_source"][1],
      "v074_source_sha256":FILES["v074_source"][1],"inputs_zip_sha256":FILES["inputs_zip"][1],
      "recenter_radius":str(args.recenter_radius),"roundoff_guard":str(guard),
      "claim_boundary":"target extraction/preflight only; no recentered fibre-chart theorem before all theorem gates pass"}
    protocol_hash=canonical_hash(protocol);atomic_json(out/"protocol.json",protocol);atomic_json(out/"recenter_candidate.json",candidate)
    status=("RECENTERED_FIBRE_CHART_CONTINUATION_CERTIFIED" if all(theorem_gates.values()) else
      "REPOSITORY_NATIVE_RECENTER_TARGET_EXTRACTED_FORMAL_NORMAL_ROOT_OPEN" if all(base_gates.values()) else
      "RECENTER_PREFLIGHT_INCONCLUSIVE_FAIL_CLOSED")
    result={"title":TITLE,"version":VERSION,"scientific_status":status,
      "repository_dependency":{"repository":REPO,"files":records,"explicitly_calls_user_geometric_flow_repository":True},
      "python_flint_version":flint_version,"instrumentation":patch_record,
      "formal_base_certificate":str(cert_path),"formal_base_certificate_sha256":sha256_file(cert_path),
      "formal_base_scientific_status":cert.get("scientific_status"),"recenter_candidate":candidate,
      "base_gates":base_gates,"theorem_gates":theorem_gates,
      "all_scientific_gates_pass":all(theorem_gates.values()),"recentered_theorem_claimed":all(theorem_gates.values()),
      "protocol_sha256":protocol_hash,"next_required_backend_work":[
        "solve B(R(theta0+T*a_c+N*b)-c)=0 for a formal normal-root box b_c",
        "construct a new Jacobian SVD tangent/normal frame at the corrected centre",
        "certify the new complex fibre graph and overlap with the old endpoint enclosure",
        "recompute pullback metric, normalization branch, Picard contraction and strict L6 descent"
      ],
      "claim_boundary":"A formally bounded recenter target is extracted from repository-native Arb code; no recentered continuation is claimed yet.",
      "elapsed_seconds":time.time()-started,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
    result["report_sha256_before_self_field"]=canonical_hash(result);atomic_json(out/"run_summary.json",result)
    return result


def parse_args()->Tuple[argparse.Namespace,List[str]]:
    p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_recenter_v0_9_6_results")
    p.add_argument("--recenter-radius",default="2e-14")
    return p.parse_known_args()


def main()->int:
    args,ignored=parse_args()
    if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    try:
        result=run(args);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(result,indent=2))
        # The expected preflight status is a successful run even though the theorem remains open.
        return 0 if result["scientific_status"]=="REPOSITORY_NATIVE_RECENTER_TARGET_EXTRACTED_FORMAL_NORMAL_ROOT_OPEN" else (0 if result["all_scientific_gates_pass"] else 2)
    except Exception as exc:
        print(json.dumps({"scientific_status":"V096_FAILED_CLOSED","error_type":type(exc).__name__,"error":str(exc)},indent=2));return 2


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
