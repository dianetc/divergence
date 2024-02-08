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
            need_clearance = "clear_function" in arguments.keys()
            tracer = Trace()
            if need_clearance:
                module = arguments["module"]
                cache = importing(module)
                clear = getattr(cache, arguments["clear_function"])
            for k, v in inputs.items():
                if not isinstance(v, tuple):
                    v = (v,)
                tracer.runfunc(func, *v)
                r = tracer.results()
                stack_traces[k] = r.calledfuncs
                if need_clearance:
                    clear()
            comparison(
                {
                    "info1": {
                        "arg1": arguments["arg1"],
                        "trace1": stack_traces["arg1"],
                    },
                    "info2": {
                        "arg2": arguments["arg2"],
                        "trace2": stack_traces["arg2"],
                    },
                }
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


# compare function traces.
def comparison(info_dict):
    arg1, trace1 = info_dict["info1"]["arg1"], info_dict["info1"]["trace1"]
    arg2, trace2 = info_dict["info2"]["arg2"], info_dict["info2"]["trace2"]
    keys1 = list(trace1.keys())
    keys2 = list(trace2.keys())
    for k1, k2 in zip(keys1, keys2):
        if k1 != k2:
            return terminalFormatting(
                occurrence.DIFFERENT_KEYS,
                {"arg1": arg1, "arg2": arg2},
                {"keys1": keys1, "keys2": keys2},
                {"index": keys1.index(k1)},
            )
    if len(keys1) != len(keys2):
        return terminalFormatting(
            occurrence.DIFFERENT_LENGTHS,
            {"arg1": arg1, "arg2": arg2},
            {"keys1": keys1, "keys2": keys2},
            {"index": min(len(keys1) - 1, len(keys2) - 1)},
        )
    return terminalFormatting(occurrence.NO_DIVERGENCE, {"arg1": arg1, "arg2": arg2})


# construct the terminal formatting
def terminalFormatting(instance, *args):
    arg1 = args[0]["arg1"]
    arg2 = args[0]["arg2"]

    match instance:
        case occurrence.DIFFERENT_KEYS:
            keys1 = args[1]["keys1"]
            keys2 = args[1]["keys2"]
            index = args[2]["index"]
            headers = [str(arg1), str(arg2)]
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
        case occurrence.DIFFERENT_LENGTHS:
            keys1 = args[1]["keys1"]
            keys2 = args[1]["keys2"]
            index = args[2]["index"]
            bigger_list = keys2 if len(keys1) < len(keys2) else keys1
            headers = [str(arg1), str(arg2)]
            data, patterns = [], []
            for i, j in zip(keys1[index - 2 : index + 1], keys2[index - 2 : index + 1]):
                s_i = refineString(i)
                s_j = refineString(j)
                data.append([s_i, s_j])
                if s_i == refineString(bigger_list[index]):
                    patterns.append((s_i, lambda text: style(text, fg="green")))
                    patterns.append((s_j, lambda text: style(text, fg="green")))
            for k in bigger_list[index + 1 : index + 3]:
                s_k = refineString(k)
                data.append(["", s_k]) if bigger_list == keys2 else data.append(
                    [s_k, ""]
                )
            table = columnar(data, headers=headers, patterns=patterns)
            print(table)
        case occurrence.NO_DIVERGENCE:
            print(f"{bcolors.OKGREEN}{arg1} and {arg2} do not diverge{bcolors.ENDC}")

class occurrence:
    DIFFERENT_KEYS = 0
    DIFFERENT_LENGTHS = 1
    NO_DIVERGENCE = 2

# process ouputs from collectfunc by removing unneccesary jargon
def refineString(string):
    string = list(string)
    directory = string[0].split("/")
    refined = "/".join(directory[-2:])
    string[0] = refined
    s = " ".join(str(l) for l in string)
    return s
