#!/usr/bin/env python3
"""Standalone formal recentered-frame audit for Geometric-Flow v0.9.9.

Embeds the frozen, tested v0.9.8 driver, adds an Arb frame audit at its
Krawczyk-certified root box, and reruns the repository-native proof chain.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,os,platform,subprocess,sys,time,zlib
from pathlib import Path

VERSION="0.9.9"
TITLE="GEOMETRIC-FLOW FORMAL RECENTERED TANGENT-NORMAL FRAME AUDIT"
EMBEDDED_SHA="666fad44e9d370466f43860cd4e04ebb48769fc1d92f88bbf3fc139c8e6a1cdb"
EMBEDDED='''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'''

FRAME_CODE=r'''
    # v0.9.9: construct a new midpoint-SVD frame and certify it uniformly
    # over the complete v0.9.8 Krawczyk root box.
    jc,_=response_jacobian_and_gradient(theta_b,True)
    jc_mid=np.asarray([[midpoint_radius(jc[r][c].real)[0]
                       for c in range(CONTROL_DIMENSION)]
                      for r in range(RESPONSE_DIMENSION)],dtype=float)
    left9,svals9,rt9=np.linalg.svd(jc_mid,full_matrices=True)
    n9f=rt9[:RESPONSE_DIMENSION,:].T
    t9f=rt9[RESPONSE_DIMENSION:,:].T
    b9f=np.diag(1.0/svals9)@left9.T
    n9=[[acb(ap(float(n9f[r,c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)]
    t9=[[acb(ap(float(t9f[r,c]))) for c in range(tangent_dimension)]
        for r in range(CONTROL_DIMENSION)]
    b9=[[acb(ap(float(b9f[r,c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)]
    q9=[n9[r]+t9[r] for r in range(CONTROL_DIMENSION)]
    qtq=v093_matmul(v093_transpose(q9),q9)
    orth9=v093_inf_matrix([[acb(int(r==c))-qtq[r][c]
                            for c in range(CONTROL_DIMENSION)]
                           for r in range(CONTROL_DIMENSION)])
    jbox9,_=response_jacobian_and_gradient(theta_box,True)
    bj9=v093_matmul(b9,jbox9)
    nd9=v093_matmul(bj9,n9)
    td9=v093_matmul(bj9,t9)
    ndef9=v093_inf_matrix([[acb(int(r==c))-nd9[r][c]
                            for c in range(RESPONSE_DIMENSION)]
                           for r in range(RESPONSE_DIMENSION)])
    tres9=v093_inf_matrix(td9)
    frame_pass=bool(orth9<ap("1e-12") and ndef9<ap("0.8") and svals9[-1]>0)
    v098_cert.update({
      "v099_frame_schema":"geometric-flow/recentered-frame/v0.9.9",
      "recentered_response_jacobian_singular_values":[float(x) for x in svals9],
      "recentered_response_minimum_singular_value":float(svals9[-1]),
      "frame_orthogonal_completeness_defect_upper":v098_up(orth9),
      "root_box_normal_identity_defect_upper":v098_up(ndef9),
      "root_box_tangent_response_residual_upper":v098_up(tres9),
      "recentered_response_full_row_rank_certified":bool(ndef9<arb(1)),
      "recentered_frame_orthogonal_complete_certified":bool(orth9<ap("1e-12")),
      "recentered_normal_derivative_invertible_certified":bool(ndef9<arb(1)),
      "recentered_tangent_normal_frame_certified":frame_pass,
      "v099_all_frame_gates_pass":frame_pass
    })
'''

def materialize_and_patch(out:Path)->Path:
 raw=zlib.decompress(base64.b64decode(EMBEDDED))
 if hashlib.sha256(raw).hexdigest()!=EMBEDDED_SHA:raise RuntimeError("embedded v0.9.8 hash mismatch")
 text=raw.decode();needle='''    v098_certificate_path.parent.mkdir(parents=True,exist_ok=True)'''
 if text.count(needle)!=1:raise RuntimeError("v0.9.8 certificate hook not unique")
 text=text.replace(needle,FRAME_CODE+"\n"+needle,1)
 path=out/"embedded_instrumented_v0_9_8_for_v0_9_9.py";path.write_text(text);return path

def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_recentered_frame_v0_9_9_results");p.add_argument("--root-radius",default="2e-18")
 return p.parse_known_args()

def run(args):
 start=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);child=out/"v098_formal_backend";script=materialize_and_patch(out)
 done=subprocess.run([sys.executable,str(script),"--outdir",str(child),"--root-radius",str(args.root_radius)],text=True,capture_output=True)
 (out/"stdout.txt").write_text(done.stdout);(out/"stderr.txt").write_text(done.stderr)
 cert=child/"normal_root_arb_certificate.json"
 if not cert.is_file():raise RuntimeError(f"instrumented backend exit={done.returncode}; frame certificate missing; inspect logs")
 c=json.loads(cert.read_text());g={
  "v098_unique_normal_root_certified":c.get("unique_normal_root_certified") is True,
  "recentered_response_full_row_rank":c.get("recentered_response_full_row_rank_certified") is True,
  "frame_orthogonal_complete":c.get("recentered_frame_orthogonal_complete_certified") is True,
  "recentered_normal_derivative_invertible":c.get("recentered_normal_derivative_invertible_certified") is True,
  "recentered_tangent_normal_frame":c.get("recentered_tangent_normal_frame_certified") is True}
 passed=done.returncode==0 and all(g.values())
 r={"title":TITLE,"version":VERSION,"scientific_status":"VALIDATED_RECENTERED_TANGENT_NORMAL_FRAME_CERTIFIED" if passed else "RECENTERED_FRAME_INCONCLUSIVE_FAIL_CLOSED",
    "repository":"https://github.com/papasop/Geometric-Flow","formal_backend":"python-flint/Arb 192-bit","frame_certificate":str(cert),
    "frame_metrics":{k:c.get(k) for k in ["recentered_response_jacobian_singular_values","recentered_response_minimum_singular_value","frame_orthogonal_completeness_defect_upper","root_box_normal_identity_defect_upper","root_box_tangent_response_residual_upper"]},
    "gates":g,"all_scientific_gates_pass":passed,"second_local_picard_chart_certified":False,"old_endpoint_in_new_chart_domain_certified":False,"global_flow_claimed":False,
    "next_required_step":"certify a new complex fibre graph, endpoint overlap, pullback metric and Picard microstep at this frame",
    "claim_boundary":"new frame is uniform on the certified root box; no second Picard chart or global continuation yet", "elapsed_seconds":time.time()-start,
    "environment":{"python":platform.python_version(),"platform":platform.platform()}}
 tmp=out/"run_summary.json.tmp";tmp.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");tmp.replace(out/"run_summary.json");return r

def main():
 args,ignored=parse();
 if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
 try:
  r=run(args);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["all_scientific_gates_pass"] else 2
 except Exception as e:print(json.dumps({"scientific_status":"V099_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2

if __name__=="__main__":
 code=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
