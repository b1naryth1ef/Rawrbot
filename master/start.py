from main import Master
from multiprocessing import Process, Queue
import time


def loop():
    q = Queue()
    m = Master()
    p = Process(target=m.boot, args=(q,))
    p.start()

    while True:
        time.sleep(60)  
    p.join()

    if q.get() == 'update': return loop()
loop()

