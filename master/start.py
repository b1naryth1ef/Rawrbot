import main
import time, os, sys

while True:
    o = os.popen('python main.py')
    os.wait()
    o = o.readlines()
    print o
    if not o[-1].startswith('update'): break
    else:
        os.popen('git pull origin deploy')
        

