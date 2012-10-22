import main
from multiprocessing import Process, Queue
import time, os

def loop():
    q = Queue()
    m = main.Master()
    p = Process(target=m.boot, args=(q,))
    p.start()

    while True: 
        if q.get(True, None) == 'update': 
            p.terminate()
            os.popen('git pull')
            reload(main)
            return loop()
loop()