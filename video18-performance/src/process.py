import time
from os import getpid
from multiprocessing import Process

def hold(sec):
    pid = getpid()
    print(f'Running for {sec} seconds in process {pid}')
    time.sleep(sec)
    return

if __name__ == "__main__":
    start = time.time()
    processes = []
    for seconds in [2, 3, 4]:
        proc = Process(target=hold, args=(seconds,)) 
        processes.append(proc)

    for process in processes:
        process.start()
    
    for process in processes:
        process.join()

    print("Execution time:", time.time() - start)

