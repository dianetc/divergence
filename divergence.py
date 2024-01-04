import trace
import sys
from columnar import columnar
from click import style


class bcolors:
    OKGREEN = "\033[92m"
    ENDC = "\033[0m"


class Trace(trace.Trace):
    def __init__(self):
        super().__init__(countfuncs=True, ignoredirs=[sys.prefix, sys.exec_prefix])


def diverge(arguments):
    def decorator(func):
        def wrapper():
            stack_traces = {}
            inputs = {k: arguments[k] for k in ("arg1", "arg2")}
            need_clearance = "function" in arguments.keys()
            tracer = Trace()
            if need_clearance:
                module = arguments["module"]
                cache = importing(module)
                clear = getattr(cache, arguments["function"])
            for k, v in inputs.items():
                tracer.runfunc(func, *v)
                r = tracer.results()
                stack_traces[k] = r.calledfuncs
                if need_clearance:
                    clear()
            comparison(
                (arguments["arg1"], stack_traces["arg1"]),
                (arguments["arg2"], stack_traces["arg2"]),
            )
            return None

        return wrapper

    return decorator


# import necessary module for clearing the cache
def importing(name):
    mod = __import__(name)
    components = name.split(".")
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# compare traces.
def comparison(tup1, tup2):
    input1, trace1 = tup1[0], tup1[1]
    input2, trace2 = tup2[0], tup2[1]
    keys1 = list(trace1.keys())
    keys2 = list(trace2.keys())
    for k1, k2 in zip(keys1, keys2):
        if k1 != k2:
            return terminalFormatting(0, keys1, keys2, keys1.index(k1), input1, input2)
    if len(keys1) < len(keys2):
        return terminalFormatting(1, keys1, keys2, input1, input2)
    elif len(keys1) > len(keys2):
        return terminalFormatting(2, keys1, keys2, input1, input2)
    return terminalFormatting(3, input1, input2)


# construct the terminal formatting
def terminalFormatting(instance, *args):
    keys1 = args[0]
    keys2 = args[1]
    match instance:
        case 0:
            index = args[2]
            input1 = args[3]
            input2 = args[4]
            headers = [str(input1), str(input2)]
            data, patterns = [], []
            for i, j in zip(keys1[index - 2 : index + 3], keys2[index - 2 : index + 3]):
                s_i = refineString(i)
                s_j = refineString(j)
                data.append([s_i, s_j])
                if s_i == refineString(keys1[index]):
                    patterns.append((s_i, lambda text: style(text, fg="red")))
                    patterns.append((s_j, lambda text: style(text, fg="red")))
            table = columnar(data, headers=headers, patterns=patterns)
            print(table)
        case 1:
            index = len(keys1) - 1
            input1 = args[2]
            input2 = args[3]
            headers = [str(input1), str(input2)]
            data, patterns = [], []
            for i, j in zip(keys1[index - 2 : index + 1], keys2[index - 2 : index + 1]):
                s_i = refineString(i)
                s_j = refineString(j)
                data.append([s_i, s_j])
                if s_i == refineString(keys1[index]):
                    patterns.append((s_i, lambda text: style(text, fg="green")))
                    patterns.append((s_j, lambda text: style(text, fg="green")))
            for k in keys2[index + 1 : index + 3]:
                s_k = refineString(k)
                data.append(["", s_k])
            table = columnar(data, headers=headers, patterns=patterns)
            print(table)

        case 2:
            index = len(keys2) - 1
            input1 = args[2]
            input2 = args[3]
            headers = [str(input1), str(input2)]
            data, patterns = [], []
            for i, j in zip(keys1[index - 2 : index + 1], keys2[index - 2 : index + 1]):
                s_i = refineString(i)
                s_j = refineString(j)
                data.append([s_i, s_j])
                if s_i == refineString(keys1[index]):
                    patterns.append((s_i, lambda text: style(text, fg="green")))
                    patterns.append((s_j, lambda text: style(text, fg="green")))
            for k in keys1[index + 1 : index + 3]:
                s_k = refineString(k)
                data.append([s_k, ""])
            table = columnar(data, headers=headers, patterns=patterns)
            print(table)
        case 3:
            input1 = args[0]
            input2 = args[1]
            print(
                f"{bcolors.OKGREEN}{input1} and {input2} do not diverge{bcolors.ENDC}"
            )


# process ouputs from collectfunc by removing unneccesary jargon
def refineString(string):
    string = list(string)
    directory = string[0].split("/")
    refined = "/".join(directory[-2:])
    string[0] = refined
    s = " ".join(str(l) for l in string)
    return s
