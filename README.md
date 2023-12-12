This is meant to be a decorator called `diverge`, that returns the first instance where two inputs have divergent stack traces for a specific function (or if they agree up to the length of the smaller stack trace, it returns the starting point where the larger stack trace continues). So it would look something like:

```
import divergence

arguments = [arg1, arg2]
@divergence.diverge(arguments)
def test_problem_function(arg)
    return problem_function(arg)

test_problem_function()
```
And that should return some information on where the stack traces diverge. Currently, it returns the
two initial function calls that were different in the traces (*which in hindsight, isn't too useful*).

The `test.py` file has a test case, I'm currently using to check my code. Since the function being tested is `solve` in sympy, I need to `clear_cache()` in `divergence.py`.Consequently, if you're testing a function that might have this issue you will need to pass in the associated clear cache function and corresponding library. I can't think of a better way to do this for the moment.   

As a remark, truly capturing trace similarity is a nontrivial task: [example](https://arxiv.org/pdf/2009.12590.pdf).

This is a tool i've always wanted when debugging in `sympy` or any math heavy libraries where inputs to the same function might send you into wildly different areas of the code base (but that is not clear apriori). Usually, the thing to do in this case, is to run both input instances simultaneously then step through each in parallel, but this can be arduous (and super easy to miss the diverging point). I need to rethink the experience I'm trying to recreate and if side-by-side differences in stack truly captures it. 


NOTE: This will crap the bed on testing recursive functions.
