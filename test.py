from sympy import *
from sympy.solvers import solve

# from sympy.integrals.manualintegrate import manualintegrate
from divergence import diverge


x = symbols("x")
args = {
    "arg1": (sin(x), x),
    "arg2": (x**2 - 1, x),
    "module": "sympy.core.cache",
    "clear_function": "clear_cache",
}


@diverge(args)
def test_solve(a, b):
    return solve(a, b)


test_solve()
