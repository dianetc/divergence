from sympy import *
from sympy.solvers import solve

# from sympy.integrals.manualintegrate import manualintegrate
from divergence import diverge


x = symbols("x")
args = [(sin(x), x), (x**2 - 1, x), "sympy.core.cache", "clear_cache"]


@diverge(args)
def test_solve(a, b):
    return solve(a, b)


test_solve()
