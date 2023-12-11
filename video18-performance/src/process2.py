import time
from os import getpid
from multiprocessing import Process, Queue

def hold(sec, queue):
    pid = getpid()
    print(f'Running for {sec} seconds in process {pid}')
    queue.put("Hello from process " + str(pid))
    time.sleep(sec)
    return 

if __name__ == "__main__":
    start = time.time()
    processes = []
    queues = []
    for seconds in [2, 3, 4]:
        q = Queue()
        queues.append(q)
        proc = Process(target=hold, args=(seconds,q)) 
        processes.append(proc)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    for queue in queues:
        print(queue.get())
    
    print("Execution time:", time.time() - start)

