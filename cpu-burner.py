#!/usr/bin/python
import multiprocessing


def cpu_task():
    while True:
        pass


def main():
    processes = [
        multiprocessing.Process(target=cpu_task)
        for _ in range(multiprocessing.cpu_count())
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
