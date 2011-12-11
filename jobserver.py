#!/usr/bin/python2
# -*- code: utf-8 -*-

#
# Have bug:
# when someone ping me, the programe will crash
#

from socket import *
import threading
import gtk.glade
import gtk
import time
import pynotify
import sys

def Server(disList, port=8888):
    """
        Startup Server and list the port
    """
    maxClient = 5
    maxData = 1024
    code = 'utf-8'

    # Create Socket list port
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(maxClient)

    while True:
        client, addr = s.accept()
        msg = ''
        if addr[0] == '127.0.0.1':
            msg = client.recv(maxData).decode(code)
            LocalCmd(msg)
            continue
        elif AckAddr(addr):
            msg = client.recv(maxData)
        else:
            notice = "The %s want to connect me." % str(addr[0])
            NotifyUnknowHost(notice)
            continue
        client.close()

        timestr = time.ctime()
        data = eval(msg.decode(code))

        if AckData(data):
            disList = AckJob(data, timestr, disList)
        else:
            continue

        # Display disList on windows
        #t = threading.Thread(target=w.Display, args=((disList,)))
        #t.daemon = True
        #t.start
        w = Minder(disList)
        w.Display(disList)
        #print disList

def LocalCmd(cmd):
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

class Minder:
    """
        Add time stamp and index to the job list
    """
    def __init__(self, data, wFile='windows.glade'):
        """
            init windows
        """
        wFile = '/home/liuhui/code/python/windows.glade'
        self.w = gtk.glade.XML(wFile)
        self.clist = self.w.get_widget('JobList')
        self.windows = self.w.get_widget('Notice')
        self.windows.connect('destroy', gtk.main_quit)
        #self.Display(data)

    def Display(self, data):
        """
            Display Data in the list
        """
        i = 1
        #print type(self.clist)
        for item in data:
            #tmp = [str(i)] + item
            #self.clist.append(tmp)
            self.clist.append(item)
            i += 1
        # Display the window
        gtk.main()
        # print "display data!"

def AckAddr(addr):
    """
        Check the ip of client.
    """
    #
    # TODO: Write a code wchich use to translate ip/netmask to ip list
    #
    WhiteList = [
                    '59.77.33.200',
                    '59.77.33.122',
                    '59.77.33.142',
                    '127.0.0.1'
                ]
    BlackList = []
    # Default reject all request besides the client's ip in WhiteList
    try:
        WhiteList.index(addr[0])
        return True
    except ValueError:
        return False

def AckData(revdata):
    """
        Check the recive Data that is correct
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

def main():
    # [jobname, status, where, time]
    clist = []
    Server(clist)

if __name__ == '__main__':
    main()
