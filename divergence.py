import trace
import sys
from columnar import columnar
from click import style


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Trace(trace.Trace):
    def __init__(self):
        super().__init__(countfuncs=True, ignoredirs=[sys.prefix, sys.exec_prefix])


def diverge(arguments):
    def decorator(func):
        def wrapper():
            stack_traces = []
            inputs = arguments[0:2]
            need_clearance = clearance(arguments)
            tracer = Trace()
            if need_clearance:
                module_name = arguments[2]
                cache = importing(module_name)
                clear = getattr(cache, arguments[3])
            for input in inputs:
                tracer.runfunc(func, *input)
                r = tracer.results()
                stack_traces.append(r.calledfuncs)
                if need_clearance:
                    clear()
            comparison((inputs[0], stack_traces[0]), (inputs[1], stack_traces[1]))
            return None

        return wrapper

    return decorator


# will need to clear cache?
def clearance(arguments):
    if len(arguments) > 2:
        if len(arguments) > 4:
            raise Exception("you need to have the module AND function name")
        else:
            return True
    else:
        return False


# import necessary module for clearing the cache
def importing(name):
    mod = __import__(name)
    components = name.split(".")
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# inputting the same argument to diverge might return slightly different size
# for callfuncs. Normalization is difficult. so for the moment we leave it as is.
def comparison(arg1, arg2):
    input1, trace1 = arg1[0], arg1[1]
    input2, trace2 = arg2[0], arg2[1]
    keys1 = list(trace1.keys())
    keys2 = list(trace2.keys())
    for k1, k2 in zip(keys1, keys2):
        if k1 != k2:
            return niceOutput(0, keys1, keys2, keys1.index(k1), input1, input2)
    if len(keys1) < len(keys2):
        return niceOutput(1, keys1, keys2, input1, input2)
    elif len(keys1) > len(keys2):
        return niceOutput(2, keys1, keys2, input1, input2)
    return niceOutput(3, input1, input2)


# construct the terminal formatting for proper formatting
def niceOutput(instance, *args):
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
                    patterns.append((s_i, lambda text: style(text, fg="red")))
                    patterns.append((s_j, lambda text: style(text, fg="red")))
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
                    patterns.append((s_i, lambda text: style(text, fg="red")))
                    patterns.append((s_j, lambda text: style(text, fg="red")))
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
