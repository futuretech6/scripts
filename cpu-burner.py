#!/usr/bin/env python
import multiprocessing
import sys


def cpu_task():
    while True:
        pass


num_processes = int(sys.argv[1]) if len(sys.argv) == 2 else multiprocessing.cpu_count()
processes = [multiprocessing.Process(target=cpu_task) for _ in range(num_processes)]
for process in processes:
    process.start()
for process in processes:
    process.join()
