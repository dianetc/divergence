This is meant to be a decorator called `diverge`, that returns the first instance where two inputs have divergent stack traces for a specific function (or if they agree up to the length of the smaller stack trace, it returns the starting point where the larger stack trace continues). So it would look something like:

```
from divergence import diverge

arguments = {"arg1": <argument 1>, "arg2": <argument 2>}

@diverge(arguments)
def test_problem_function(arg)
    return problem_function(arg)

test_problem_function()
```

And that should return some information on where the stack traces diverge. Currently, it returns the
two initial function calls that were different in the traces (*which in hindsight, isn't too useful*).

The output of the current `test.py` file is below:

![test_example](https://github.com/dianetc/divergence/assets/46408633/b1971789-4927-4aa4-a40e-e977bde8115b)


The right hand stack trace was larger and they agreed for the entirety of the stack trace of the left hand column. Consequently,
it shows when the right hand side continues. 

The `test.py` file is testing  SymPy's `solve` function, which caches certain function results for efficiency. Consequenty, I needed to `clear_cache()` in `divergence.py`. So, if you're testing a function that might have this issue you will need to pass in the associated clear cache function and corresponding library. I can't think of a better way to do this for the moment.   

As a remark, truly capturing trace similarity is a nontrivial task: [example](https://arxiv.org/pdf/2009.12590.pdf).

NOTE: This works on Python>=3.10.0. I recommend using pyenv to manage python versions!
