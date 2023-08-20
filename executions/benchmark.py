import psutil
from asyncExecution import afunction
import asyncio
from testThreads import thfunction

def benchmark_resource_usage(approach_function):
    process = psutil.Process()
    start_cpu_usage = process.cpu_percent()
    start_memory_usage = process.memory_info().rss

    approach_function()
    

    end_cpu_usage = process.cpu_percent()
    end_memory_usage = process.memory_info().rss

    cpu_usage = end_cpu_usage - start_cpu_usage
    memory_usage = end_memory_usage - start_memory_usage

    return cpu_usage, memory_usage

# cpu_usage_async, memory_usage_async = benchmark_resource_usage(afunction)
cpu_usage_threaded, memory_usage_threaded = benchmark_resource_usage(thfunction)
# print(cpu_usage_async,memory_usage_async)
print(cpu_usage_threaded,memory_usage_threaded)