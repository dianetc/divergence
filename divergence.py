import trace
import sys
from typing import Any, Callable, Dict, Tuple, Optional
from dataclasses import dataclass
from columnar import columnar
from click import style

@dataclass
class DivergenceConfig:
    arg1: Tuple[Any, ...]
    arg2: Tuple[Any, ...]
    module: Optional[str] = None
    clear_function: Optional[str] = None

class Trace(trace.Trace):
    def __init__(self):
        super().__init__(countfuncs=True, ignoredirs=[sys.prefix, sys.exec_prefix])

def diverge(config: DivergenceConfig):
    def decorator(func: Callable):
        def wrapper():
            try:
                stack_traces = get_stack_traces(func, config)
                compare_stack_traces(stack_traces, config)
            except Exception as e:
                print(f"An error occurred: {e}")
            return None
        return wrapper
    return decorator

def get_stack_traces(func: Callable, config: DivergenceConfig) -> Dict[str, Dict]:
    stack_traces = {}
    tracer = Trace()
    
    for key, args in [("arg1", config.arg1), ("arg2", config.arg2)]:
        if config.module and config.clear_function:
            clear_cache(config.module, config.clear_function)
        
        tracer.runfunc(func, *args)
        stack_traces[key] = {"args": args, "trace": tracer.results().calledfuncs}
    
    return stack_traces

def clear_cache(module: str, clear_function: str):
    try:
        mod = __import__(module)
        for comp in module.split(".")[1:]:
            mod = getattr(mod, comp)
        clear = getattr(mod, clear_function)
        clear()
    except (ImportError, AttributeError) as e:
        print(f"Error clearing cache: {e}")

def compare_stack_traces(stack_traces: Dict[str, Dict], config: DivergenceConfig):
    trace1, trace2 = stack_traces["arg1"]["trace"], stack_traces["arg2"]["trace"]
    keys1, keys2 = list(trace1.keys()), list(trace2.keys())

    for i, (k1, k2) in enumerate(zip(keys1, keys2)):
        if k1 != k2:
            display_table(keys1, keys2, i, config, "red")
            return

    if len(keys1) != len(keys2):
        if len(keys1) > len(keys2):
            longer_trace = keys1
            shorter_trace = keys2
            longer_arg = config.arg1
            shorter_arg = config.arg2
        else:
            longer_trace = keys2
            shorter_trace = keys1
            longer_arg = config.arg2
            shorter_arg = config.arg1
        display_length_difference(longer_trace, shorter_trace, longer_arg, shorter_arg)
    else:
        print("Traces are identical")

def display_length_difference(longer_trace, shorter_trace, longer_arg, shorter_arg):
    divergence_index = len(shorter_trace)
    
    headers = [f"{shorter_arg}", f"{longer_arg}"]
    data = []
    
    for i in range(max(0, divergence_index - 2), divergence_index):
        data.append([refine_string(shorter_trace[i]), refine_string(longer_trace[i])])
    
    for i in range(divergence_index, min(divergence_index + 3, len(longer_trace))):
        data.append(["", refine_string(longer_trace[i])])
    
    patterns = [(refine_string(longer_trace[divergence_index]), lambda text: style(text, fg="green"))]
    
    table = columnar(data, headers=headers, patterns=patterns)
    print(table)

def display_table(keys1: list, keys2: list, index: int, config: DivergenceConfig, color: str):
    headers = [str(config.arg1), str(config.arg2)]
    data, patterns = [], []
    
    for i in range(max(0, index-2), min(len(keys1), len(keys2), index+3)):
        row = [refine_string(keys1[i]) if i < len(keys1) else "",
               refine_string(keys2[i]) if i < len(keys2) else ""]
        data.append(row)
        if i == index:
            patterns.extend((cell, lambda text: style(text, fg=color)) for cell in row if cell)

    try:
        table = columnar(data, headers=headers, patterns=patterns)
        print(table)
    except Exception as e:
        print(f"Error creating table: {e}")
    

def refine_string(item: Any) -> str:
    if isinstance(item, str):
        parts = item.split()
        if parts:
            directory = parts[0].split("/")
            refined = "/".join(directory[-2:])
            return f"{refined} {' '.join(parts[1:])}"
        return item
    elif isinstance(item, tuple):
        return ' '.join(str(x) for x in item)
    else:
        return str(item)
