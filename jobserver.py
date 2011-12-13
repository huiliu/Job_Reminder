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

def Server(disList, pipe, port=8888):
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
        #if pipe.recv() == 'quit':
        #    s.close()
        #    break

        data = ''
        timestr = ''
        client, addr = s.accept()

        # Check Client IP
        if AckAddr(addr):
            msg = client.recv(maxData)
            client.close()
            timestr = time.ctime()
            data = eval(msg.decode(code))
        else:
            client.close()
            continue

        # Check Client Data
        if AckData(data):
            disList = AckJob(data, timestr, disList)
        else:
            continue

        pipe.send("recived message")

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

    ip = client[1][0]
    if ip == '127.0.0.1':
        msg = client.recv(maxData).decode(code)
        LocalCmd(msg, process)
        return False

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
    w = gtk.glade.XML(wFile)
    windows = w.get_widget('Notice')
    clist = w.get_widget('JobList')
    windows.connect('destroy', gtk.Window.hide)
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
    clist = []
    pWindows = None
    sendPipe, recvPipe = Pipe()
    pSocket = Process(target=Server, args=(clist, sendPipe))
    pSocket.start()
    print recvPipe.recv()
    print 'recived'
    pSocket.join()
    while True:
        try:
            msg = recvPipe.recv()
            if not pWindows:
                pWindows = Process(target=Reminder, args=(disList,))
                pWindows.start()
                pWindows.join()
            else:
                pWindows.terminate()
                pWindows = Process(target=Reminder, args=(disList,))
                pWindows.start()
                pWindows.join()
            print msg
            #Reminder(clist)
        except:
            pass
            
if __name__ == '__main__':
    main()
