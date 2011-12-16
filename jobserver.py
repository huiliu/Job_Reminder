#!/usr/bin/python2
# -*- code: utf-8 -*-

#
# Have bug:
# when someone ping me, the programe will crash
#

from socket import *
from multiprocessing import Process, Pipe
import gtk.glade
import gtk
import time
import pynotify
import sys
import os

def Server(disList, port=8888):
    """
        Startup Server and list the port
    """
    maxClient = 5
    maxData = 1024
    code = 'utf-8'

    # Create Socket list port
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', port))

    while True:
        #if pipe.recv() == 'quit':
        #    s.close()
        #    break

        data = ''
        timestr = ''
        msg, addr = s.recvfrom(maxData)

        # Check Client IP
        if AckAddr(addr):
            timestr = time.ctime()
            data = eval(msg.decode(code))
        else:
            continue

        # Check Client Data
        if AckData(data):
            print "AckJob"
            disList = AckJob(data, timestr, disList)
            #Reminder(data)
            print "new process..."
            p = Process(target = Reminder, args = (['test'],))
            p.start()
            #p.join()
        else:
            continue


def LocalCmd(cmd, p):
    """
        Excute the command come from localhost.
    """
    if cmd == 'quit':
        msg = "admin notice to shutup!"
        NotifyUnknowHost(msg)
        sys.exit(0)
    else:
        NotifyUnknowHost(cmd)

def NotifyUnknowHost(msg):
    """
        Notify user the host that is not list in whitelist or blacklist.
    """
    pynotify.init('job_notify')
    m = pynotify.Notification(msg)
    m.show()

def AckJob(revmsg, timestr, disList):
    """
        Check job's type
    """
    Running = 'Running'
    Finished = 'Finished'

    # if message represent a job has finished, delete correlated running message.
    #print revmsg
    if revmsg[1] == Finished:
        #import copy
        #tmp = copy.deepcopy(revmsg)
        tmp = revmsg[:]
        tmp[1] = Running
        #print "hello"
        # find the running message
        for i, item in enumerate(disList):
            #print "recived Data: ", revmsg
            #print "item Data: ", item
            #print "cmp Data: ", item[0:2]
            if tmp == item[0:3]:
                #print 'remove'
                #print disList
                disList.pop(i)
                #print disList
                break
    revmsg = revmsg + [timestr]
    disList.append(revmsg)

    return disList

def AckAddr(client, process=None):
    """ Check the ip of client.
    """
    #
    # TODO: Write a code wchich use to translate ip/netmask to ip list
    #
    WhiteList = ['59.77.33.200', '59.77.33.122', '59.77.33.142', '127.0.0.1']
    BlackList = []

    print client
    ip = client[0]
    if ip == '127.0.0.1':
        #msg = client.recv(maxData).decode(code)
        #LocalCmd(msg, process)
        return True

    # Default reject all request besides the client's ip in WhiteList
    try:
        WhiteList.index(ip)
        return True
    except ValueError:
        notice = "The %s want to connect me." % ip
        NotifyUnknowHost(notice)
        return False

def AckData(revdata):
    """ Check the recive Data that is correct
        [jobname, status, where]
    """
    ListLength = 3
    if type(revdata) is list and len(revdata) == ListLength:
        for item in revdata:
            if type(item) is not str:
                print "The Data structure has error!"
                return False
        return True 
    return False

def Reminder(data, wFile='windows.glade'):
    """
        Add time stamp and index to the job list
    """
    #
    # init windows
    #
    print os.getppid()
    print os.getpid()

    print data
    time.sleep(4)
    print "return"
    return
    w = gtk.glade.XML(wFile)
    windows = w.get_widget('Notice')
    clist = w.get_widget('JobList')
    windows.connect('destroy', gtk.main_quit)
    #self.windows.set_visible(False)

    #
    # Display Data in the list
    #
    # Append the data to the gtkCList
    for item in data:
        clist.append(item)

    # Display the window
    gtk.main()

def main():
    # [jobname, status, where, time]
    pass
            
if __name__ == '__main__':
    #Reminder(['test'])
    Server([])
    sys.exit(0)
    main()
