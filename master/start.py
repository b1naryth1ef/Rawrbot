import main
from multiprocessing import Process, Queue
import time, os


def loop():
    global main
    q = Queue()
    m = main.Master()
    p = Process(target=m.boot, args=(q,))
    p.start()

    while True:
        i = q.get(True, None)
        if i == 'update':
            p.terminate()
            del sys.modules['main']
            os.popen('git pull origin deploy')
            os.wait()
            import main
            return loop()
loop()

