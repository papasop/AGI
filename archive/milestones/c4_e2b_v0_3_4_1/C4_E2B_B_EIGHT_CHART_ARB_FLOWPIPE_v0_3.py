#!/usr/bin/env python3
"""C4-E2b-B: eight-chart frozen-right-inverse Arb flowpipe v0.3.

Attempts, fail-closed, to transport a nonzero 14D initial box from the frozen
chart-0 centre through all eight certified C4-E2a overlaps, 0/1 through 7/8.
Each leg uses outward-rounded Picard slabs and the dynamically corrected
frozen-right-inverse controller.  At every handoff the complete endpoint box
is tested in the old-chart overlap coordinates, then conservatively transformed
and recentered into the new frozen orthonormal frame before continuation.

Response contraction is certified from the controller identity, rather than
from a dependency-inflated interval expansion of dV.  On every slab the
Neumann defect q = ||I-JY0|| is certified below one, so A=JY0 is invertible,
Y=Y0 A^-1 satisfies JY=I, and P=I-YJ satisfies JP=0.  Consequently
e_dot=-beta e and, for V=||e||^2/2, V_dot=-2 beta V exactly.  The direct
expanded interval bound for dV is retained in the report as a non-gating
diagnostic.

PASS is an eight-overlap validated continuation for this frozen finite chain.
It is not a positive-invariance theorem beyond the chain, a global or long-time
flow theorem, K=1 evidence, Pulser evidence, hardware evidence, or QPU evidence.

Colab: upload and run this file. Dependencies and six SHA-pinned repository
modules and the SHA-pinned E2a prerequisite are installed/fetched automatically.
"""
from __future__ import annotations

import argparse, hashlib, importlib, json, math, os, subprocess, sys, urllib.request
from pathlib import Path


COMMIT = "f391925b3219070f8f843f2043e0b265ea2eb3b9"
ROOT = f"https://raw.githubusercontent.com/papasop/Geometric-Flow/{COMMIT}/research/control_extension/c4"
REPO_ROOT = f"https://raw.githubusercontent.com/papasop/Geometric-Flow/{COMMIT}"
E2A_NAME = "c4_e2a_arb_multichart_overlap_chain_v1_0.json"
E2A_URL = f"{REPO_ROOT}/results/post_publication/control_extension/c4/{E2A_NAME}"
E2A_SHA = "b030e0ef468de09cf53ea11b1594428e47c35fd7483def27401de8776186521c"
FILES = {
 "c4_arb_recovery_core_certificate_v1_0.py": "b6a6ffe41c9025bfe24bbea8da94a42eb6c74fdef02c36e855008915049c4743",
 "c4_arb_affine_taylor_subdivision_v1_2.py": "cb31628e984b3303774fb3e4b7e34b82da849190e416bdc7697530dfd084d9f0",
 "c4_arb_quadratic_taylor_defect_v1_4.py": "7032d7bb7e97d9e946697accbe16bfbaffe3fae89e820a3d4e03d0b83dfa7b18",
 "c4_arb_defect_centered_affine_v1_3.py": "7ec54ff9830a3aaf73312705152676524c7b6fdfdfc2c8e0d0730cea54e39f9b",
 "c4_e0_moving_chart_overlap_preflight_v1_0.py": "cda327272e5b1d93da3cf5f1d846f11d19560fc8d85c1d59c2a4119186ab2d24",
 "c4_e1a_arb_first_chart_overlap_certificate_v1_0.py": "8e441c654441d632c01f10002421dcf73dd3b6f875fc867312031009309de8ed",
 "normally_attracting_response_fibre_real_model_v1_1.py": "2ba9e8739c328d97e4074f6f2ce8c0adbdf678c6f18e37bfb72cba2919b81529",
}
TITLE = "C4-E2b-B EIGHT-CHART FROZEN-RIGHT-INVERSE ARB FLOWPIPE"
VERSION = "0.3"


def bootstrap():
    try:
        import flint  # noqa
        import numpy  # noqa
    except Exception:
        if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
            raise RuntimeError("install python-flint==0.8.0 and numpy==2.0.2")
        print("[bootstrap] installing python-flint==0.8.0 numpy==2.0.2")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                               "python-flint==0.8.0", "numpy==2.0.2"])
        importlib.invalidate_caches()


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch_modules(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        path = directory / name
        if not path.exists() or digest(path) != expected:
            print("[setup] fetching", name)
            with urllib.request.urlopen(f"{ROOT}/{name}", timeout=90) as r:
                path.write_bytes(r.read())
        got = digest(path)
        if got != expected:
            raise RuntimeError(f"SHA mismatch {name}: {got} != {expected}")
    if str(directory) not in sys.path: sys.path.insert(0, str(directory))


def fetch_e2a(directory: Path):
    path = directory / E2A_NAME
    if not path.exists() or digest(path) != E2A_SHA:
        print("[setup] fetching", E2A_NAME)
        with urllib.request.urlopen(E2A_URL, timeout=90) as r:
            path.write_bytes(r.read())
    got = digest(path)
    if got != E2A_SHA:
        raise RuntimeError(f"SHA mismatch {E2A_NAME}: {got} != {E2A_SHA}")
    data = json.loads(path.read_text())
    if not data.get("all_gates_pass") or len(data.get("transition_certificates", [])) != 8:
        raise RuntimeError("frozen E2a eight-transition prerequisite does not pass")
    return data


bootstrap()
import numpy as np
from flint import arb, arb_mat, ctx


def exact(x):
    n, d = float(x).as_integer_ratio()
    return arb(n) / arb(d)


def lo(x): return float(x.lower())
def hi(x): return float(x.upper())


def finite_ball(x):
    try: return math.isfinite(lo(x)) and math.isfinite(hi(x))
    except Exception: return False


def ball_from_mid_rad(mid, rad):
    rad = max(float(rad), 0.0)
    return exact(float(mid)) + arb(0, exact(float(rad)))


def interval_mid_rad(x):
    a, b = lo(x), hi(x)
    # Outward binary64 padding protects the conversion back to exact floats.
    a = np.nextafter(a, -np.inf); b = np.nextafter(b, np.inf)
    return 0.5*(a+b), 0.5*(b-a)


def vector_to_box(v):
    mr = [interval_mid_rad(v[i, 0]) for i in range(v.nrows())]
    return np.array([x[0] for x in mr]), np.array([x[1] for x in mr])


def matrix_exact(a): return arb_mat([[exact(float(v)) for v in row] for row in a])


def neumann_inverse(B, terms=14):
    """Rigorous inverse of B close to I, with an infinity-norm tail ball."""
    n = B.nrows()
    I = arb_mat(n, n)
    for i in range(n): I[i, i] = arb(1)
    E = I - B
    q = max(sum(hi(abs(E[i, j])) for j in range(n)) for i in range(n))
    if not (math.isfinite(q) and q < 1.0):
        raise RuntimeError(f"preconditioned inverse Neumann defect not below one: {q}")
    S, power = arb_mat(I), arb_mat(I)
    for _ in range(1, terms + 1):
        power = power * E
        S = S + power
    tail = q ** (terms + 1) / (1.0 - q)
    tail_ball = arb(0, exact(tail))
    for i in range(n):
        for j in range(n): S[i, j] += tail_ball
    return S, q, tail


def canonical_sha(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def setup_objects(workdir):
    fetch_modules(workdir)
    global base, e0, e1, engine, qengine
    base = importlib.import_module("c4_arb_recovery_core_certificate_v1_0")
    engine = importlib.import_module("c4_arb_affine_taylor_subdivision_v1_2")
    qengine = importlib.import_module("c4_arb_quadratic_taylor_defect_v1_4")
    e0 = importlib.import_module("c4_e0_moving_chart_overlap_preflight_v1_0")
    e1 = importlib.import_module("c4_e1a_arb_first_chart_overlap_certificate_v1_0")
    model = e0.load_model(workdir / e0.MODEL_NAME)
    charts = e1.frozen_mixed_charts(model, windows=8, steps=4)
    if len(charts) != 9:
        raise RuntimeError(f"expected nine frozen charts, got {len(charts)}")
    return model, charts


def qreal(x):
    Q=qengine.Quadratic
    return Q(x.c.real,[v.real for v in x.a],
             [[v.real for v in row] for row in x.q],x.r)


def qimag(x):
    Q=qengine.Quadratic
    return Q(x.c.imag,[v.imag for v in x.a],
             [[v.imag for v in row] for row in x.q],x.r)


def qmatmul(A,B):
    Q=qengine.Quadratic; m,n,p=len(A),len(B),len(B[0])
    return [[sum((A[i][k]*B[k][j] for k in range(n)),Q(0))
             for j in range(p)] for i in range(m)]


def qtranspose(A): return [list(row) for row in zip(*A)]


def qinverse(A):
    """Gauss-Jordan inverse over dependency-preserving Quadratic forms."""
    Q=qengine.Quadratic; n=len(A)
    M=[[Q(A[i][j]) for j in range(n)]+[Q(1 if i==j else 0) for j in range(n)]
       for i in range(n)]
    for col in range(n):
        pivot=max(range(col,n),key=lambda r: float(base.upper(abs(M[r][col].c))))
        M[col],M[pivot]=M[pivot],M[col]
        invp=M[col][col].inv()
        M[col]=[x*invp for x in M[col]]
        for r in range(n):
            if r==col: continue
            factor=M[r][col]
            M[r]=[M[r][j]-factor*M[col][j] for j in range(2*n)]
    return [row[n:] for row in M]


def qneumann_inverse_near_identity(A, terms=3):
    """Dependency-preserving A^-1 for A close to I, with analytic tail."""
    Q=qengine.Quadratic; n=len(A)
    I=[[Q(1 if i==j else 0) for j in range(n)] for i in range(n)]
    E=[[I[i][j]-A[i][j] for j in range(n)] for i in range(n)]
    q=max(sum(float(base.upper(abs(E[i][j].enclosure()))) for j in range(n))
          for i in range(n))
    if not(math.isfinite(q) and q<1):
        raise RuntimeError(f"correlated quadratic Neumann defect not below one: {q}")
    S=[[Q(I[i][j]) for j in range(n)] for i in range(n)]
    power=[[Q(I[i][j]) for j in range(n)] for i in range(n)]
    for _ in range(terms):
        power=qmatmul(power,E)
        S=[[S[i][j]+power[i][j] for j in range(n)] for i in range(n)]
    tail=q**(terms+1)/(1-q)
    for i in range(n):
        for j in range(n): S[i][j].r += exact(tail)
    return S,q,tail


def quadratic_data(forms):
    """Retain dependencies through J J^T, its inverse, and the full field."""
    Q=qengine.Quadratic
    z,dz,den=engine.projective_affine(forms,False)
    zb,dzb,denb=engine.projective_affine(forms,True)
    J=[[Q(0) for _ in range(14)] for _ in range(8)]
    for order in range(4):
        for phase in range(14):
            J[order][phase]=qreal((dz[phase].c[order]+dzb[phase].c[order])/2)
            J[4+order][phase]=qreal((dz[phase].c[order]-dzb[phase].c[order])/base.acb(0,2))
    z0,_=base.projective_float(base.REFERENCE_PHASES,False)
    err=[]
    for order in range(4): err.append(qreal(z.c[order])-Q(exact(z0.c[order].real)))
    for order in range(4):
        err.append(qimag(z.c[order])-Q(exact(z0.c[order].imag)))
    product=z*zb; denominator=1+product; grad=[]
    for phase in range(14):
        val=(dz[phase]*zb+z*dzb[phase])/(denominator*denominator)
        grad.append(qreal(val.c[6]))
    return J,[[x] for x in grad],[[x] for x in err],den.enclosure(),denb.enclosure()


def interval_field(model, old, u_mid, u_rad, beta):
    """Dynamically corrected frozen-right-inverse field in old coordinates."""
    ambient_centre = old["centre"] + old["frame"] @ u_mid
    half = np.maximum(u_rad, 0.0)
    e1.configure_interval_engine()
    forms = e1.ambient_phase_forms(ambient_centre, old["frame"], half)
    J,g,err,den,denb=quadratic_data(forms)
    den_ok = lo(abs(den)) > 0 and lo(abs(denb)) > 0
    # Freeze the centre Moore--Penrose right inverse Y0 as controller data,
    # but correct it dynamically by A(theta)^-1, A=J(theta)Y0.  Thus
    # Y=Y0 A^-1 is an exact right inverse on the whole certified box:
    # JY=I, P=I-YJ, JP=0, and response error obeys e_dot=-beta e.
    _,J0,_,_=model.response_jacobian_gradient_loss(old["centre"])
    Y0=J0.T@np.linalg.inv(J0@J0.T)
    Y0q=[[qengine.Quadratic(exact(float(v))) for v in row] for row in Y0]
    A=qmatmul(J,Y0q)
    Ainv,inv_q,inv_tail=qneumann_inverse_near_identity(A,terms=3)
    Y=qmatmul(Y0q,Ainv)
    Jg=qmatmul(J,g); normal_grad=qmatmul(Y,Jg)
    Pgrad=[[g[i][0]-normal_grad[i][0]] for i in range(14)]
    recovery=qmatmul(Y,err)
    ftheta=[[-Pgrad[i][0]-exact(beta)*recovery[i][0]] for i in range(14)]
    frameq=[[qengine.Quadratic(exact(float(v))) for v in row] for row in old["frame"].T]
    fuq=qmatmul(frameq,ftheta)
    fu=arb_mat([[fuq[i][0].enclosure().real] for i in range(14)])
    all_finite = den_ok and all(finite_ball(fu[i, 0]) for i in range(14))
    dLq=qmatmul(qtranspose(g),ftheta)[0][0]; dL=dLq.enclosure().real
    # e-dot = J f; Vdot for V=||e||_2^2/2 is e^T J f.
    dVq=qmatmul(qtranspose(err),qmatmul(J,ftheta))[0][0]; dV=dVq.enclosure().real
    return fu, dL, dV, all_finite, inv_q, inv_tail


def hull_of_picard(xm, xr, f, h):
    mids, rads = [], []
    for i in range(14):
        fl, fh = lo(f[i, 0]), hi(f[i, 0])
        xlo, xhi = xm[i]-xr[i], xm[i]+xr[i]
        ylo = xlo + min(0.0, h*fl, h*fh)
        yhi = xhi + max(0.0, h*fl, h*fh)
        ylo = np.nextafter(ylo, -np.inf); yhi = np.nextafter(yhi, np.inf)
        mids.append(0.5*(ylo+yhi)); rads.append(0.5*(yhi-ylo))
    return np.asarray(mids), np.asarray(rads)


def endpoint_box(xm, xr, f, h):
    mids, rads = [], []
    for i in range(14):
        fl, fh = lo(f[i, 0]), hi(f[i, 0])
        yl = xm[i]-xr[i] + h*fl; yh = xm[i]+xr[i] + h*fh
        yl = np.nextafter(yl, -np.inf); yh = np.nextafter(yh, np.inf)
        mids.append(0.5*(yl+yh)); rads.append(0.5*(yh-yl))
    return np.asarray(mids), np.asarray(rads)


def contained(am, ar, bm, br):
    return bool(np.all(np.abs(am-bm)+ar < br))


def transform_box_between_frames(xm, xr, old, new):
    """Enclose an old-frame coordinate box in the new orthonormal frame."""
    u = arb_mat([[ball_from_mid_rad(xm[i], xr[i])] for i in range(len(xm))])
    old_c = arb_mat([[exact(float(v))] for v in old["centre"]])
    new_c = arb_mat([[exact(float(v))] for v in new["centre"]])
    theta = old_c + matrix_exact(old["frame"]) * u
    new_u = matrix_exact(new["frame"].T) * (theta-new_c)
    return vector_to_box(new_u)


def picard_step(model, old, xm, xr, h, beta, max_iter=18):
    # First enclosure is intentionally generous and then tightened/expanded
    # monotonically until the Picard image is strictly inside it.
    f0, _, _, ok0, q0, tail0 = interval_field(model, old, xm, xr, beta)
    bm, br = hull_of_picard(xm, xr, f0, h)
    br += 64*np.finfo(float).eps*np.maximum(1.0, np.abs(bm))
    best = None
    for iteration in range(1, max_iter+1):
        f, dL, dV, ok, iq, itail = interval_field(model, old, bm, br, beta)
        pm, pr = hull_of_picard(xm, xr, f, h)
        if contained(pm, pr, bm, br):
            ym, yr = endpoint_box(xm, xr, f, h)
            return ym, yr, {"iterations": iteration, "dL_upper": hi(dL),
                            "dV_upper": hi(dV), "regular": bool(ok and ok0),
                            "inverse_neumann_defect_upper": max(q0,iq),
                            "inverse_series_tail_upper": max(tail0,itail),
                            "tube_max_radius": float(br.max())}
        # Monotone hull plus small outward cushion.
        blo, bhi = bm-br, bm+br; plo, phi = pm-pr, pm+pr
        nl, nh = np.minimum(blo, plo), np.maximum(bhi, phi)
        bm, br = 0.5*(nl+nh), 0.5*(nh-nl)
        br += 64*np.finfo(float).eps*np.maximum(1.0, np.abs(bm))
        best = (pm, pr)
    raise RuntimeError("Picard self-map not certified within iteration limit")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-substeps", type=int, default=8)
    ap.add_argument("--later-substeps", type=int, default=16)
    ap.add_argument("--initial-half", type=float, default=1e-12)
    ap.add_argument("--first-leg-time", type=float, default=1.25e-5)
    ap.add_argument("--later-leg-time", type=float, default=2.5e-5)
    ap.add_argument("--beta", type=float, default=100.0)
    ap.add_argument("--report", default="/tmp/c4_e2b_b_eight_chart_flowpipe_v0_3.json")
    args, unknown = ap.parse_known_args(argv)
    if unknown: print("# [notice] ignored notebook/kernel arguments:", unknown)
    if min(args.first_substeps, args.later_substeps) < 1:
        raise ValueError("substep counts must be positive")
    if min(args.initial_half, args.first_leg_time, args.later_leg_time, args.beta) <= 0:
        raise ValueError("initial-half, leg times, and beta must be positive")
    ctx.prec = 256
    workdir = Path("/tmp/c4_e2ba_modules")
    model, charts = setup_objects(workdir)
    e2a_data = fetch_e2a(workdir)
    certificates = e2a_data["transition_certificates"]
    centre_errors=[]
    for i, cert in enumerate(certificates):
        co=np.asarray(cert["frozen_centres"]["old"],float)
        cn=np.asarray(cert["frozen_centres"]["new"],float)
        centre_errors.extend([float(np.max(np.abs(charts[i]["centre"]-co))),
                              float(np.max(np.abs(charts[i+1]["centre"]-cn)))])
    max_centre_error=max(centre_errors)
    if max_centre_error > 5e-14:
        raise RuntimeError(f"generated charts disagree with frozen E2a centres: {max_centre_error}")
    protocol = {"version": VERSION, "commit": COMMIT, "precision_bits": 256,
                "transitions": [[i,i+1] for i in range(8)],
                "e2a_sha256": E2A_SHA,
                "first_substeps": args.first_substeps,
                "later_substeps": args.later_substeps,
                "initial_coordinate_half": args.initial_half,
                "first_leg_time": args.first_leg_time,
                "later_leg_time": args.later_leg_time,
                "beta": args.beta,
                "controller": "Y=Y0[J(theta)Y0]^-1; P=I-YJ; theta_dot=-P gradL-beta Y e",
                "integrator": "outward-rounded Picard slabs; correlated quadratic forms",
                "handoff": "strict overlap inclusion then absolute-matrix box transform into new frozen frame",
                "response_contraction_proof":
                    "q=||I-JY0||<1 => JY=I and JP=0 => e_dot=-beta e => V_dot=-2 beta V"}
    print("="*100); print(TITLE, "v"+VERSION); print("="*100)
    print("protocol_sha256:", canonical_sha(protocol))
    print("boundary: frozen eight-overlap finite continuation; not global/long-time/K=1/Pulser/QPU")
    print("response gate: certified inverse + exact controller identity; expanded dV is diagnostic only")
    xm, xr = np.zeros(14), np.full(14, args.initial_half)
    transitions=[]
    try:
        for t in range(8):
            old,new=charts[t],charts[t+1]
            cert=certificates[t]
            midpoint=np.asarray(cert["frozen_centres"]["overlap_midpoint"],float)
            overlap_c=old["frame"].T@(midpoint-old["centre"])
            tr=float(cert["overlap_box"]["tangent_coordinate_half_width"])
            nr=float(cert["overlap_box"]["normal_coordinate_half_width"])
            overlap_r=np.r_[np.full(6,tr),np.full(8,nr)]
            nsteps=args.first_substeps if t==0 else args.later_substeps
            leg_time=args.first_leg_time if t==0 else args.later_leg_time
            h=leg_time/nsteps; steps=[]
            for k in range(nsteps):
                xm,xr,rec=picard_step(model,old,xm,xr,h,args.beta)
                rec.update(step=k+1,endpoint_max_radius=float(xr.max()))
                steps.append(rec)
            used=np.abs(xm-overlap_c)+xr; margin=overlap_r-used
            chart_half=np.r_[np.full(6,0.02),np.full(8,1e-4)]
            inverse_ok=all(x["regular"] and x["inverse_neumann_defect_upper"]<1 for x in steps)
            tgates={
              "all_picard_slabs_self_map":len(steps)==nsteps,
              "all_corrected_right_inverses_and_denominators_regular":all(x["regular"] for x in steps),
              "complete_endpoint_box_strictly_inside_overlap":bool(np.all(margin>0)),
              "endpoint_inside_old_chart":bool(np.all(np.abs(xm)+xr<chart_half)),
              "objective_descent_on_every_slab":all(x["dL_upper"]<0 for x in steps),
              "certified_inverse_neumann_defect_below_one":inverse_ok,
              "exact_response_law_by_controller_identity":inverse_ok and args.beta>0,
              "response_lyapunov_exponential_contraction":inverse_ok and args.beta>0,
            }
            transition_pass=all(tgates.values())
            record={"transition":[t,t+1],"substeps":nsteps,"leg_time":leg_time,
              "steps":steps,"bounds":{
                "minimum_overlap_coordinate_margin":float(margin.min()),
                "maximum_endpoint_coordinate_radius":float(xr.max()),
                "maximum_endpoint_normalized_overlap_use":float((used/overlap_r).max()),
                "maximum_dL_upper":max(x["dL_upper"] for x in steps),
                "maximum_inverse_neumann_defect_upper":max(x["inverse_neumann_defect_upper"] for x in steps),
                "maximum_expanded_interval_dV_upper_diagnostic":max(x["dV_upper"] for x in steps)},
              "gates":tgates,"all_gates_pass":transition_pass}
            transitions.append(record)
            print(f"[{t}->{t+1}] slabs={nsteps} pass={transition_pass} "
                  f"margin={margin.min():.3e} use={(used/overlap_r).max():.3f} "
                  f"rad={xr.max():.3e} q={record['bounds']['maximum_inverse_neumann_defect_upper']:.3e} "
                  f"dL+={record['bounds']['maximum_dL_upper']:.3e}")
            if not transition_pass:
                raise RuntimeError(f"transition {t}->{t+1} failed a certificate gate")
            xm,xr=transform_box_between_frames(xm,xr,old,new)
            record["handoff_to_new_frame"]={
                "coordinate_midpoint_inf":float(np.max(np.abs(xm))),
                "coordinate_radius_inf":float(np.max(xr))}
        all_steps=[s for trn in transitions for s in trn["steps"]]
        inverse_certified=all(s["regular"] and s["inverse_neumann_defect_upper"]<1 for s in all_steps)
        gates={
          "frozen_e2a_prerequisite_passes":True,
          "generated_chart_centres_match_frozen_e2a":max_centre_error<=5e-14,
          "all_eight_transitions_completed":len(transitions)==8,
          "all_eight_complete_endpoint_boxes_strictly_inside_overlaps":all(
              x["gates"]["complete_endpoint_box_strictly_inside_overlap"] for x in transitions),
          "all_picard_slabs_self_map":all(s["iterations"]>=1 for s in all_steps),
          "objective_descent_on_every_slab":all(s["dL_upper"]<0 for s in all_steps),
          "certified_inverse_neumann_defect_below_one":inverse_certified,
          "exact_response_and_lyapunov_laws_on_entire_chain":inverse_certified and args.beta>0,
        }
        passed=all(gates.values())
        status="C4_E2B_EIGHT_CHART_FLOWPIPE_CERTIFIED" if passed else "C4_E2B_B_INCONCLUSIVE"
        result={"title":TITLE,"version":VERSION,"protocol":protocol,
          "protocol_sha256":canonical_sha(protocol),"transition_certificates":transitions,
          "bounds":{"maximum_generated_chart_centre_error":max_centre_error,
                    "minimum_overlap_coordinate_margin":min(
                        x["bounds"]["minimum_overlap_coordinate_margin"] for x in transitions),
                    "maximum_endpoint_normalized_overlap_use":max(
                        x["bounds"]["maximum_endpoint_normalized_overlap_use"] for x in transitions),
                    "maximum_endpoint_coordinate_radius":max(
                        x["bounds"]["maximum_endpoint_coordinate_radius"] for x in transitions),
                    "maximum_dL_upper":max(s["dL_upper"] for s in all_steps),
                    "maximum_inverse_neumann_defect_upper":max(s["inverse_neumann_defect_upper"] for s in all_steps),
                    "certified_response_error_exponent":-float(args.beta),
                    "certified_lyapunov_exponent":-2.0*float(args.beta),
                    "maximum_expanded_interval_dV_upper_diagnostic":max(
                        s["dV_upper"] for s in all_steps)},
          "response_contraction_certificate":{
                    "premise":"A=JY0 is invertible on every slab, certified by q<1",
                    "identities":["Y=Y0 A^-1", "JY=I", "P=I-YJ", "JP=0"],
                    "response_law":"e_dot=-beta e",
                    "lyapunov_law":"V_dot=-2 beta V for V=||e||^2/2",
                    "expanded_interval_dV_is_gate":False},
          "gates":gates,"all_gates_pass":passed,"scientific_status":status,
          "claim_boundary":"256-bit Arb/Picard transport plus exact conditional controller identity across the frozen finite eight-overlap chain only; no positive invariance beyond the chain, global or long-time flow, K=1, Pulser, hardware, or QPU claim.",
          "required_next_step":"If PASS, freeze the script/report and perform an independent verifier replay before repository integration."}
    except Exception as exc:
        result={"title":TITLE,"version":VERSION,"protocol":protocol,
          "protocol_sha256":canonical_sha(protocol),"transition_certificates":transitions,"gates":{},
          "all_gates_pass":False,"scientific_status":"C4_E2B_B_INCONCLUSIVE",
          "error_type":type(exc).__name__,"error":str(exc),
          "failed_transition":len(transitions)-1 if transitions and not transitions[-1]["all_gates_pass"] else len(transitions),
          "claim_boundary":"A failed or incomplete transition emitted no eight-chart continuation certificate; completed transition records remain local evidence only."}
    Path(args.report).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result.get(k) for k in ("bounds","gates","all_gates_pass","scientific_status","error_type","error") if k in result},indent=2))
    print("report:",args.report)
    return 0 if result["all_gates_pass"] else 2


if __name__=="__main__":
    code=main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
