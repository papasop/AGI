#!/usr/bin/env python3
"""Repository-native continuation-route correction audit v0.9.13.

Determines whether exhaustion of the v0.9.10 intrinsic Picard ball authorizes
an atlas transition.  It intentionally distinguishes intrinsic tangent
coordinates from atlas arclength coordinates and fails closed on any attempted
comparison without a certified coordinate map.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,sys,time,urllib.request,zipfile
from pathlib import Path
from typing import Any

VERSION="0.9.13"
TITLE="GEOMETRIC-FLOW CONTINUATION-ROUTE CORRECTION AUDIT"
REPO="https://github.com/papasop/Geometric-Flow"
URL="https://raw.githubusercontent.com/papasop/Geometric-Flow/main/inputs/response_fibre_v0_6_2_backend_inputs.zip"
ZIP_SHA="2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
ATLAS_SHA="c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
CURRENT_ATLAS_CHART=9
CURRENT_CHILD_INDEX=15
INTRINSIC_INNER_RADIUS="1e-11"

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def canonical(o:Any)->bytes:return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def atomic(p:Path,o:Any)->None:
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(o,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def acquire(out:Path)->Path:
 p=out/"frozen_repository_inputs"/"response_fibre_v0_6_2_backend_inputs.zip";p.parent.mkdir(parents=True,exist_ok=True)
 if not p.is_file():print("[repository] downloading frozen atlas inputs");urllib.request.urlretrieve(URL,p)
 got=sha_file(p)
 if got!=ZIP_SHA:raise RuntimeError(f"frozen input ZIP hash mismatch: {got}")
 return p
def read_zip(p:Path,name:str):
 with zipfile.ZipFile(p) as z:return json.loads(z.read("response_fibre_v0_6_2_backend_inputs/"+name))
def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_route_correction_v0_9_13_results");return p.parse_known_args()
def run(args):
 st=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);zp=acquire(out)
 atlas=read_zip(zp,"corrected_atlas.json");geometry=read_zip(zp,"chart_geometry.json");overlaps=read_zip(zp,"endpoint_overlaps.json");manifest=read_zip(zp,"manifest.json")
 atlas_digest=sha_bytes(canonical(atlas));charts=atlas.get("charts",[]);ids=[int(x.get("chart",i)) for i,x in enumerate(geometry)]
 successors=[o for o in overlaps if int(o.get("left_chart",-1))==CURRENT_ATLAS_CHART and o.get("declared_tubes_overlap") is True]
 incoming=[o for o in overlaps if int(o.get("right_chart",-1))==CURRENT_ATLAS_CHART and o.get("declared_tubes_overlap") is True]
 coordinate_map_present=any(k in atlas for k in ["intrinsic_to_arclength_map","intrinsic_chart_transition_map","tangent_to_atlas_map"])
 gates={"frozen_input_zip_hash_match":sha_file(zp)==ZIP_SHA,"corrected_atlas_canonical_hash_match":atlas_digest==ATLAS_SHA,"ten_atlas_charts_present":ids==list(range(10)),"current_chart_is_terminal_atlas_chart":CURRENT_ATLAS_CHART==max(ids),"incoming_8_to_9_overlap_present":any(int(x["left_chart"])==8 for x in incoming),"no_declared_successor_after_chart_9":len(successors)==0,"intrinsic_radius_not_compared_to_atlas_arclength_without_map":not coordinate_map_present}
 passed=all(gates.values())
 route="SAME_CHART_RECENTER_REQUIRED" if passed else "ROUTE_UNRESOLVED_FAIL_CLOSED"
 contract={"schema":"geometric-flow/same-chart-recenter/v0.9.13","repository":REPO,"frozen_input_zip_sha256":ZIP_SHA,"corrected_atlas_sha256":ATLAS_SHA,"atlas_chart_index":CURRENT_ATLAS_CHART,"child_index":CURRENT_CHILD_INDEX,"source_coordinate_system":"v0.9.10 six-dimensional intrinsic tangent coordinates","source_inner_radius":INTRINSIC_INNER_RADIUS,"required_backend_outputs":["terminal_reachable_box_in_intrinsic_coordinates","new_tangent_target_box","new_normal_root_krawczyk_certificate","new_frame_certificate","old_terminal_box_in_new_intrinsic_coordinates","new_complex_fibre_graph_certificate","new_picard_certificate"],"forbidden_inference":"do not compare intrinsic radius 1e-11 with atlas arclength without a certified coordinate map","completion_gate":"terminal reachable box subset interior(new same-chart start domain)"};atomic(out/"same_chart_recenter_backend_contract.json",contract)
 result={"title":TITLE,"version":VERSION,"scientific_status":"TERMINAL_ATLAS_CHART_CONFIRMED_SAME_CHART_RECENTER_REQUIRED" if passed else "CONTINUATION_ROUTE_INCONCLUSIVE_FAIL_CLOSED","repository":REPO,"frozen_inputs":{"zip":str(zp),"zip_sha256":sha_file(zp),"corrected_atlas_canonical_sha256":atlas_digest,"manifest_version":manifest.get("version")},"atlas_structure":{"chart_ids":ids,"current_chart":CURRENT_ATLAS_CHART,"current_child":CURRENT_CHILD_INDEX,"declared_successors":successors,"declared_incoming_overlaps":incoming,"intrinsic_to_atlas_coordinate_map_present":coordinate_map_present},"route_decision":route,"gates":gates,"all_scientific_gates_pass":passed,"same_chart_recenter_certified":False,"atlas_transition_certified":False,"complete_child_certified":False,"global_flow_claimed":False,"contract":str(out/"same_chart_recenter_backend_contract.json"),"correction_to_v0912":"uniform intrinsic-domain exhaustion does not imply arrival at an atlas chart boundary; chart 9 has no declared successor in the frozen atlas","next_required_step":"implement a second same-chart recenter at the terminal reachable tube, then rerun root/frame/graph/Picard gates","claim_boundary":"route classification and backend contract only; no additional continuation step is claimed","elapsed_seconds":time.time()-st,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 atomic(out/"run_summary.json",result);return result
def main():
 a,i=parse()
 if i:print(f"[notice] ignored notebook/kernel arguments: {i}")
 try:r=run(a);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["all_scientific_gates_pass"] else 2
 except Exception as e:print(json.dumps({"scientific_status":"V0913_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2
if __name__=="__main__":
 c=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(c)
