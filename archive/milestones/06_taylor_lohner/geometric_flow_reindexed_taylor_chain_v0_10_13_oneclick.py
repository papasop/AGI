#!/usr/bin/env python3
"""Reindex Hessian parents to the ten true propagation input boxes."""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, sys
from pathlib import Path

TITLE="GEOMETRIC-FLOW REINDEXED INPUT-PARENT TAYLOR / AFFINE LOHNER CHAIN"
VERSION="0.10.13.1"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def clean(a):
 o=[];ignored=[];i=0
 while i<len(a):
  if a[i]=='-f' and i+1<len(a):ignored+=a[i:i+2];i+=2
  else:o.append(a[i]);i+=1
 if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
 return o
def locate(x,c,msg):
 for p in ([Path(x)] if x else [])+[Path(q) for q in c]:
  if p.is_file():return p.resolve()
 raise FileNotFoundError(msg)
def locate_or_recover_script(explicit,candidates,markers,destination,message):
 try:return locate(explicit,candidates,message)
 except FileNotFoundError:
  pass
 try:
  ip=get_ipython()
  history=list(ip.history_manager.input_hist_raw)
 except Exception:
  history=[]
 for cell in reversed(history):
  if 'VERSION="0.10.13.1"' in cell:
   continue
  if cell and all(marker in cell for marker in markers) and 'def main' in cell:
   destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(cell)
   try:compile(cell,str(destination),'exec')
   except Exception as exc:raise RuntimeError(f'recovered notebook source for {destination.name} does not compile: {exc}')
   print(f'[embedded] recovered {destination.name} from notebook history')
   return destination.resolve()
 raise FileNotFoundError(message+'; it was also not found in notebook history')
def run_checked(cmd,label):
 print(f'[chain] {label}')
 r=subprocess.run(cmd,text=True,capture_output=True)
 if r.returncode!=0:
  raise RuntimeError(f'{label} failed (exit={r.returncode})\nSTDOUT tail:\n{r.stdout[-1600:]}\nSTDERR tail:\n{r.stderr[-1600:]}')
 return r

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--v0109-script');ap.add_argument('--v01011-script');ap.add_argument('--v01012-script');ap.add_argument('--v0106-records');ap.add_argument('--v0106-certificate');ap.add_argument('--v0108-summary');ap.add_argument('--frame-certificate');ap.add_argument('--picard-certificate');ap.add_argument('--six-jet');ap.add_argument('--v0104-certificate');ap.add_argument('--v0105-source');ap.add_argument('--outdir',default='geometric_flow_reindexed_taylor_v0_10_13_results');args,_=ap.parse_known_args(clean(sys.argv[1:]));out=Path(args.outdir).resolve();out.mkdir(parents=True,exist_ok=True)
 recovered=out/'recovered_notebook_sources';s109=locate_or_recover_script(args.v0109_script,['geometric_flow_mean_value_normal_krawczyk_v0_10_9_1_oneclick.py','/content/geometric_flow_mean_value_normal_krawczyk_v0_10_9_1_oneclick.py'],['VERSION = "0.10.9.1"','MEAN-VALUE PARAMETRIC'],recovered/'geometric_flow_mean_value_normal_krawczyk_v0_10_9_1_oneclick.py','v0.10.9.1 script missing');s111=locate_or_recover_script(args.v01011_script,['geometric_flow_second_order_taylor_dx_v0_10_11_oneclick.py','/content/geometric_flow_second_order_taylor_dx_v0_10_11_oneclick.py'],['VERSION="0.10.11.1"','SECOND-ORDER SAME-EXPRESSION'],recovered/'geometric_flow_second_order_taylor_dx_v0_10_11_oneclick.py','v0.10.11.1 script missing');s112=locate_or_recover_script(args.v01012_script,['geometric_flow_taylor_affine_lohner_v0_10_12_oneclick.py','/content/geometric_flow_taylor_affine_lohner_v0_10_12_oneclick.py'],['VERSION="0.10.12"','CENTRED TAYLOR DX'],recovered/'geometric_flow_taylor_affine_lohner_v0_10_12_oneclick.py','v0.10.12 script missing');r6p=locate(args.v0106_records,['geometric_flow_qr_lohner_v0_10_6_results/qr_lohner_step_records.json','/content/geometric_flow_qr_lohner_v0_10_6_results/qr_lohner_step_records.json'],'v0.10.6 records missing');c6p=locate(args.v0106_certificate,['geometric_flow_qr_lohner_v0_10_6_results/fourth_chart_qr_lohner_support_certificate.json','/content/geometric_flow_qr_lohner_v0_10_6_results/fourth_chart_qr_lohner_support_certificate.json'],'v0.10.6 certificate missing');s8=locate(args.v0108_summary,['geometric_flow_adaptive_normal_graph_v0_10_8_results/run_summary.json','/content/geometric_flow_adaptive_normal_graph_v0_10_8_results/run_summary.json'],'v0.10.8 summary missing');fp=locate(args.frame_certificate,['geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json','/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json'],'frame missing');pp=locate(args.picard_certificate,['geometric_flow_native_source_v0_10_1_results/v0930_reproduction/formal_fourth_picard_backend/formal_base/intrinsic_picard_microstep_certificate.json','/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/formal_fourth_picard_backend/formal_base/intrinsic_picard_microstep_certificate.json'],'picard missing');six=locate(args.six_jet,['geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py','/content/geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py'],'six-Jet missing');v104=locate(args.v0104_certificate,['geometric_flow_qr_lohner_v0_10_6_results/corrected_v0104_dependency/parametric_normal_graph_jet_arb_certificate.json','/content/geometric_flow_qr_lohner_v0_10_6_results/corrected_v0104_dependency/parametric_normal_graph_jet_arb_certificate.json'],'v0.10.4 certificate missing')
 r6=json.loads(r6p.read_text());frame=json.loads(fp.read_text());
 if len(r6)!=10:raise RuntimeError('v0.10.6 does not contain ten records')
 initial=frame['transformed_endpoint_box'];center=[(float(lo)+float(hi))/2 for lo,hi in zip(initial['lower'],initial['upper'])];radii=[math.nextafter((float(hi)-float(lo))/2,math.inf)+1e-27 for lo,hi in zip(initial['lower'],initial['upper'])];shape=[[0.0]*6 for _ in range(6)]
 for i,x in enumerate(radii):shape[i][i]=x
 initial_record={'step':0,'time_upper':0.0,'center':center,'shape_matrix':shape,'qr_Q':[[1.0 if i==j else 0.0 for j in range(6)] for i in range(6)],'qr_R':shape,'interval_remainder_upper':[0.0]*6,'formal_coordinate_support_upper':[abs(center[i])+radii[i] for i in range(6)],'strictly_inside_real_inner_domain':True,'strictly_inside_complex_outer_domain':True}
 inputs=[initial_record]+r6[:9]
 for i,r in enumerate(inputs,1):r['step']=i
 input_path=out/'reindexed_ten_input_parent_records.json';input_path.write_text(json.dumps(inputs,indent=2)+'\n')
 mapping={'propagation_step_1':'initial transformed endpoint box'}
 for k in range(2,11):mapping[f'propagation_step_{k}']=f'v0.10.6 output record {k-1}'
 (out/'parent_reindexing_map.json').write_text(json.dumps(mapping,indent=2)+'\n')

 rootout=out/'reindexed_local_roots';cmd=[sys.executable,str(s109),'--v0108-summary',str(s8),'--v0106-records',str(input_path),'--six-jet',str(six),'--frame-certificate',str(fp),'--picard-certificate',str(pp),'--outdir',str(rootout)];run_checked(cmd,'recompute ten input-parent Krawczyk roots')
 rootsum=rootout/'run_summary.json';rootrec=rootout/'ten_step_local_normal_root_records.json'
 if not rootsum.is_file() or not json.loads(rootsum.read_text()).get('all_scientific_gates_pass'):raise RuntimeError('reindexed local-root chain did not certify')

 hessout=out/'reindexed_second_order';cmd=[sys.executable,str(s111),'--v0109-summary',str(rootsum),'--v0109-records',str(rootrec),'--v0106-records',str(input_path),'--six-jet',str(six),'--v0104-certificate',str(v104),'--frame-certificate',str(fp),'--picard-certificate',str(pp),'--outdir',str(hessout)]
 if args.v0105_source:cmd+=['--v0105-source',args.v0105_source]
 run_checked(cmd,'recompute ten input-parent centre DX and full Hessians')
 hsum=hessout/'run_summary.json';hrec=hessout/'second_order_taylor_dx_records.json'
 if not hsum.is_file() or not json.loads(hsum.read_text()).get('all_scientific_gates_pass'):raise RuntimeError('reindexed second-order chain did not certify')

 propout=out/'reindexed_taylor_propagation';cmd=[sys.executable,str(s112),'--v01011-summary',str(hsum),'--v01011-records',str(hrec),'--v01011-results-dir',str(hessout),'--v0106-certificate',str(c6p),'--v0106-records',str(input_path),'--frame-certificate',str(fp),'--picard-certificate',str(pp),'--outdir',str(propout)];run_checked(cmd,'assemble reindexed Taylor DX and propagate correlated affine tube')
 psum=propout/'run_summary.json'
 if not psum.is_file():raise RuntimeError('v0.10.12 reindexed summary missing')
 p=json.loads(psum.read_text());parent_gate=p.get('gates',{}).get('every_propagated_input_inside_its_Hessian_parent_box',False)
 gates={'ten_input_parents_reindexed':len(inputs)==10,'first_parent_is_initial_endpoint_box':inputs[0]['time_upper']==0.0,'steps_2_to_10_use_previous_v0106_outputs':True,'reindexed_local_roots_certified':json.loads(rootsum.read_text()).get('all_scientific_gates_pass',False),'reindexed_second_order_certified':json.loads(hsum.read_text()).get('all_scientific_gates_pass',False),'propagated_inputs_inside_reindexed_Hessian_parents':parent_gate,'reindexed_Taylor_affine_flowpipe_certified':p.get('all_scientific_gates_pass',False)};passed=all(gates.values())
 report={'title':TITLE,'version':VERSION,'scientific_status':'VALIDATED_REINDEXED_TAYLOR_DIRECTIONAL_AFFINE_LOHNER_CERTIFIED' if passed else 'REINDEXED_TAYLOR_CHAIN_INCONCLUSIVE_FAIL_CLOSED','reindexing':mapping,'metrics':p.get('metrics',{}),'gates':gates,'all_scientific_gates_pass':passed,'directional_affine_lohner_certified':passed,'terminal_correlated_set_certified':passed,'fifth_frame_certified':False,'complete_child_certified':False,'global_flow_claimed':False,'artifacts':{'input_parent_records':str(input_path),'local_root_summary':str(rootsum),'second_order_summary':str(hsum),'propagation_summary':str(psum)},'next_required_step':'map the certified terminal correlated set into the actual fifth SVD frame' if passed else 'inspect the first failed parent-containment record and rebuild that parent from the actual propagated set','claim_boundary':'reindexed ten-step local-root, second-order Taylor and correlated affine/Lohner chain only; no fifth frame, complete child, or global flow'};(out/'run_summary.json').write_text(json.dumps(report,indent=2)+'\n');print('='*112);print(f'{TITLE} v{VERSION}');print('='*112);print(json.dumps(report,indent=2));return 0 if passed else 2
if __name__=='__main__':
 code=main()
 if 'ipykernel' not in sys.modules and 'IPython' not in sys.modules and 'google.colab' not in sys.modules:raise SystemExit(code)
