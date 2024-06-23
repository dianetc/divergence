from sympy import *
from sympy.solvers import solve
from divergence import diverge, DivergenceConfig

x = symbols("x")

@diverge(DivergenceConfig(
    arg1=(sin(x), x),
    arg2=(x ** 2 - 1, x),
    module="sympy.core.cache",
    clear_function="clear_cache"
))
def test_solve(a, b):
    return solve(a, b)

test_solve()
