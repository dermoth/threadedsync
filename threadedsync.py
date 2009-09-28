#!/usr/bin/env python

import sys, os
from signal import signal, SIGTERM, SIGINT, SIGHUP, SIG_IGN
from threading import Thread
from subprocess import Popen
from collections import deque
from time import sleep

# Config
localsrcdir = '/somepath/tosync'
localdstdir = '/somepath/synced'
remotedst = 'remote.example.com/somepath/synced'
threads = 8

# Files in progress (will not be added to the queue)
inprocess = set()

# For handling shutdowns
shutdown = False

# Signal handler
def handler(signum, frame):
    global shutdown
    shutdown = True
signal(SIGHUP, SIG_IGN)
signal(SIGINT, handler)
signal(SIGTERM, handler)


def rsync(file):
    rs = Popen(['/usr/bin/rsync', '-a', '-e', '/usr/bin/ssh -i /path/to/ssh.key', '--partial', os.path.join(localsrcdir,file), os.path.join(remotedst, file)], shell=False)
    try:
        my_rc = os.waitpid(rs.pid, 0)
    except OSError, e:
        print "Execution failed:", e
        return False

    if my_rc[1] != 0:
        print 'rsync failed with error:', str(my_rc[1] >> 8)
        return False

    return True

class runsync(Thread):
    def __init__ (self, queue, num):
        Thread.__init__(self)
        self.queue = queue
        self.num = num
    def run(self):
        while True:
            # Shutdown?
            if shutdown:
                print 'Thread', self.num, 'exiting...'
                return

            try:
                file = self.queue.popleft()
            except IndexError:
                sleep(1)
                continue

            print 'Thread', self.num, 'starting file', file
            if rsync(file):
                os.rename(os.path.join(localsrcdir,file), os.path.join(localdstdir,file))
                inprocess.remove(file)
                print 'Thread', self.num, 'finished file', file
            else:
                self.queue.append(file)
                print 'Thread', self.num, 'failed on file', file

# Global queue and thread pool
globalqueue = deque()
threadpool = list(range(0, threads))

# Start the threads
for t in range(0, threads):
    threadpool[t] = runsync(globalqueue, t)
    threadpool[t].start()

# Main loop
while True:
    for f in os.listdir(localsrcdir):
        if os.path.isdir(os.path.join(localsrcdir, f)): continue
        if f in inprocess: continue
        globalqueue.append(f)
        inprocess.add(f)
    sleep(10)
    if shutdown: break

print "System shutdown, waiting for threads to exit..."

