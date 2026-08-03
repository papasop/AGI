#!/usr/bin/env python3
"""Lift v0.10.2 native scalar Arb formulas to six-variable complex Arb jets."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, sys
from pathlib import Path

TITLE="GEOMETRIC-FLOW NATIVE SIX-VARIABLE COMPLEX ARB JET LIFT"
VERSION="0.10.3"
EXPECTED_SCALAR_SHA="16e153347068b9f412fc01e2bb9eadf1aa4091b8dc4e3a62d6c7e691d960e417"

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

def first_existing(explicit,candidates,label):
 paths=([Path(explicit)] if explicit else[])+[Path(x) for x in candidates]
 for p in paths:
  if p.is_file():return p.resolve()
 raise FileNotFoundError(label)

CJET=r'''
JET_DIMENSION=6
class CJet:
    __slots__=("v","d")
    def __init__(self,value=0,derivatives=None):
        if isinstance(value,CJet):
            self.v=value.v;self.d=value.d[:];return
        self.v=value if isinstance(value,acb) else acb(value)
        self.d=[acb(0) for _ in range(JET_DIMENSION)] if derivatives is None else [x if isinstance(x,acb) else acb(x) for x in derivatives]
        if len(self.d)!=JET_DIMENSION:raise ValueError("CJet derivative dimension")
    @classmethod
    def variable(cls,value,index):
        d=[acb(0) for _ in range(JET_DIMENSION)];d[index]=acb(1);return cls(value,d)
    def __add__(self,o):
        o=CJet(o);return CJet(self.v+o.v,[self.d[i]+o.d[i] for i in range(JET_DIMENSION)])
    __radd__=__add__
    def __neg__(self):return CJet(-self.v,[-x for x in self.d])
    def __sub__(self,o):return self+(-CJet(o))
    def __rsub__(self,o):return CJet(o)-self
    def __mul__(self,o):
        o=CJet(o);return CJet(self.v*o.v,[self.d[i]*o.v+self.v*o.d[i] for i in range(JET_DIMENSION)])
    __rmul__=__mul__
    def inv(self):
        if self.v.contains(0):raise ArithmeticError("CJet inverse contains zero")
        return CJet(1/self.v,[-x/(self.v*self.v) for x in self.d])
    def __truediv__(self,o):return self*CJet(o).inv()
    def __rtruediv__(self,o):return CJet(o)/self
    def exp(self):
        v=self.v.exp();return CJet(v,[v*x for x in self.d])
    def sqrt(self):
        v=self.v.sqrt()
        if v.contains(0):raise ArithmeticError("CJet sqrt contains zero")
        return CJet(v,[x/(2*v) for x in self.d])
    def sin(self):
        v=self.v.sin();c=self.v.cos();return CJet(v,[c*x for x in self.d])
    def cos(self):
        v=self.v.cos();s=self.v.sin();return CJet(v,[-s*x for x in self.d])
    def conjugate(self):return CJet(self.v.conjugate(),[x.conjugate() for x in self.d])
    def contains(self,x):return self.v.contains(x)
    @property
    def real(self):return self.v.real
    @property
    def imag(self):return self.v.imag
def cjet(value=0):return value if isinstance(value,CJet) else CJet(value)
'''

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--scalar");ap.add_argument("--frame-certificate");ap.add_argument("--outdir",default="geometric_flow_six_variable_jet_v0_10_3_results")
 args,_=ap.parse_known_args(clean(sys.argv[1:]));scalar=first_existing(args.scalar,["geometric_flow_scalar_primitives_v0_10_2_results/geometric_flow_native_scalar_primitives_v0_10_2.py","/content/geometric_flow_scalar_primitives_v0_10_2_results/geometric_flow_native_scalar_primitives_v0_10_2.py"],"Run v0.10.2 first or pass --scalar")
 if sha(scalar)!=EXPECTED_SCALAR_SHA:raise RuntimeError(f"scalar primitive hash mismatch: {sha(scalar)}")
 frame=first_existing(args.frame_certificate,["geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json","/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json"],"fourth frame certificate not found")
 fc=json.loads(frame.read_text());T=fc["tangent_frame_midpoint"]
 if len(T)!=14 or any(len(r)!=6 for r in T):raise RuntimeError("fourth tangent frame is not 14x6")
 box=fc["corrected_phase_center_box"];lo=box["lower"];hi=box["upper"]
 if len(lo)!=14 or len(hi)!=14:raise RuntimeError("fourth phase centre box missing")
 src=scalar.read_text()
 # Preserve scalar Arb and replace only coercions that must accept derivative-carrying values.
 src=src.replace("from flint import acb, arb, ctx","from flint import acb, arb, ctx\n"+CJET,1)
 src=src.replace("self.c = [acb(item) for item in coefficients]","self.c = [cjet(item) for item in coefficients]",1)
 src=src.replace("self.c = [acb(coefficients)] + [acb(0)] * self.order","self.c = [cjet(coefficients)] + [cjet(0)] * self.order",1)
 src=src.replace("self.c += [acb(0)] * (self.order + 1 - len(self.c))","self.c += [cjet(0)] * (self.order + 1 - len(self.c))",1)
 src=src.replace("phase = acb(phase_value)","phase = cjet(phase_value)")
 # Scalar target construction remains valid as constant CJets; expose tangent seeding.
 append='''
TANGENT_FRAME = %s
THETA_CENTER_LOWER = %s
THETA_CENTER_UPPER = %s
def fourth_chart_phase_jets(a_values=None):
    a_values=[arb(0) for _ in range(6)] if a_values is None else list(a_values)
    if len(a_values)!=6:raise ValueError("six tangent values required")
    av=[CJet.variable(a_values[j],j) for j in range(6)]
    out=[]
    for i in range(14):
        mid=(arb(THETA_CENTER_LOWER[i])+arb(THETA_CENTER_UPPER[i]))/2
        x=CJet(acb(mid))
        for j in range(6):x=x+arb(TANGENT_FRAME[i][j])*av[j]
        out.append(x)
    return out
def response_map_six_jet(a_values=None):return response_map(fourth_chart_phase_jets(a_values),True)
def response_jacobian_gradient_six_jet(a_values=None):return response_jacobian_and_gradient(fourth_chart_phase_jets(a_values),True)
SIX_JET_METADATA={"schema":"geometric-flow/native-six-complex-jet/v0.10.3","source_scalar_sha256":"%s","frame_certificate_sha256":"%s","six_variable_jet_ready":True,"finite_difference":False,"same_expression_response_derivative":True,"same_expression_DX_ready":False}
'''%(repr(T),repr(lo),repr(hi),EXPECTED_SCALAR_SHA,sha(frame))
 candidate=Path(args.outdir).resolve()/"geometric_flow_native_six_jet_primitives_v0_10_3.py";candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(src+append)
 compile(candidate.read_text(),str(candidate),"exec");spec=importlib.util.spec_from_file_location("gf6",candidate);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 r=m.response_map_six_jet();j,g=m.response_jacobian_gradient_six_jet()
 flat=list(r)+[x for row in j for x in row]+list(g)
 gates={"scalar_hash_exact":True,"frame_14x6":True,"candidate_compiles":True,"candidate_imports":True,"response_eight_cjets":len(r)==8 and all(isinstance(x,m.CJet) for x in r),"jacobian_8x14_cjets":len(j)==8 and all(len(row)==14 for row in j) and all(isinstance(x,m.CJet) for row in j for x in row),"gradient_14_cjets":len(g)==14 and all(isinstance(x,m.CJet) for x in g),"six_derivatives_each":all(len(x.d)==6 for x in flat),"nonzero_tangent_derivative_observed":any(any(not z.contains(0) for z in x.d) for x in list(r)+list(g)),"no_finite_difference":"finite_difference_DX" not in candidate.read_text()}
 passed=all(gates.values());report={"title":TITLE,"version":VERSION,"scientific_status":"NATIVE_SIX_VARIABLE_COMPLEX_ARB_JET_PRIMITIVES_CERTIFIED" if passed else "V0103_FAILED_CLOSED","scalar_source":str(scalar),"frame_certificate":str(frame),"candidate":str(candidate),"candidate_sha256":sha(candidate),"gates":gates,"six_variable_jet_ready":passed,"same_expression_response_derivative_ready":passed,"same_expression_DX_ready":False,"implicit_normal_graph_jet_ready":False,"all_scientific_gates_pass":False,"next_required_step":"differentiate the parametric Krawczyk normal solve to obtain psi(a) and Dpsi(a), then assemble W,H,X and DX","claim_boundary":"six-variable complex Arb jets for native response/Jacobian/L6-gradient formulas only; no implicit graph jet, X/DX, QR/Lohner flowpipe, fifth frame, or global flow"}
 (candidate.parent/"run_summary.json").write_text(json.dumps(report,indent=2)+"\n");print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(report,indent=2));return 0 if passed else 2

if __name__=="__main__":
 code=main()
 if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
