import main
from multiprocessing import Process, Queue
import time, os


def loop():
    q = Queue()
    m = main.Master()
    p = Process(target=m.boot, args=(q,))
    p.start()

    while True:
        time.sleep(60)  
    p.join()

    if q.get() == 'update': 
        os.popen('git pull')
        reload(main)
        return loop()
loop()

