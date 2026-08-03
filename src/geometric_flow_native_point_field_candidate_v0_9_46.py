"""v0.9.46 candidate backend: replace every NotImplementedError."""
from flint import arb, ctx
ctx.prec=192
DIMENSION=6
DOMAIN_RADIUS=arb("1.5e-11")
FROZEN_HASHES={'v0930': '426b55e5f8d2b37f2d62a597fbc8f82dc9bba42cc46903c35c553905699b4e52', 'v09433': 'ef8cc30b3cde528a6cd94d1192ce7a4a360c4635c5e675e2166dd198b969fe46', 'v0944': '94317c561661ec55663b64f9968084546ad05bf24cdebaa311a1c0977643dae8', 'v0945': 'c366f40df59bf528a04c9bbee9ee2d620facff72012e2494264e0d206b7131db'}

def _validate(a_box):
    if not isinstance(a_box,(list,tuple)) or len(a_box)!=6:
        raise ValueError("expected six Arb coordinates")
    if not all(isinstance(x,arb) for x in a_box):
        raise TypeError("coordinates must be Arb")
    if not all(abs(x)<DOMAIN_RADIUS for x in a_box):
        raise ValueError("outside fourth-chart domain")

def implicit_fibre_root_solver(a_box):
    _validate(a_box)
    # MUST evaluate the repository response at theta_c + T*a_box + N*b.
    raise NotImplementedError("bind parametric Arb Krawczyk root")

def pullback_metric(a_box,root_box):
    _validate(a_box)
    # MUST use the derivative of the same implicit graph at a_box.
    raise NotImplementedError("bind repository-native pullback metric")

def projected_gradient(a_box,root_box,metric_box):
    _validate(a_box)
    # MUST evaluate response Jacobian and L6 gradient at the same phase box.
    raise NotImplementedError("bind repository-native projected gradient")

def formal_vector_field_X(a_box):
    _validate(a_box)
    root=implicit_fibre_root_solver(a_box)
    metric=pullback_metric(a_box,root)
    grad=projected_gradient(a_box,root,metric)
    # MUST use the certified analytic normalization branch.
    raise NotImplementedError("bind normalized repository-native field")
