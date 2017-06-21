#!/usr/bin/python

"""
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2017/06/13 9:56:12 $"


Multicast Client, Server and Observer

"""

import threading, time, datetime
import string, os, sys
import struct, socket
import random

import wx
from PythonCard import model, dialog

def discover(message, addr, port, ttlval=10):
    """
        Send discover message to all servers from
        multicast group and return a list
        of servers with services
    """
    multicast_group = (addr, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    #People have the misconception that binding is only for listening on a socket,
    #but this is also true for connecting, and its just that in normal usage the binding is chosen for you.
    sock.bind(('', 0))

    sock.settimeout(0.010) #short timeout, but 30 times recv
    ttl = struct.pack("b", ttlval)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    sent = sock.sendto(message, multicast_group)
    sent = sock.sendto(message, multicast_group)
    sent = sock.sendto(message, multicast_group)
    time.sleep(0.5)
    D={}
    for i in range(30):
        try:
            data, server = sock.recvfrom(1024)
            if D.has_key(data):
                D[data][0] += 1
                D[data][1] = datetime.datetime.now()
                D[data][2] = server
            else:
                D[data] = [1, datetime.datetime.now(), server]
        except:
            pass
    return D


def getPropsDict(filename, sep, comment = ";#"):
    #
    # sep = separator and may be :, =, etc.
    # comment = a list of chars which define starting of comment
    #
    ret = {}
    f = open(filename,"rt")
    accumulator = ''
    flag = False
    while True:
        line = f.readline()
        if not line:
            #line must have at least '\r\n' (Windows) or '\n' (Unix)
            break
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.lstrip()
        if not line:
            #line is empty
            continue
        if line[0] in comment:
            #line starts with a comment
            continue
        for c in comment:
            #remove commented section
            ix = line.find(c)
            if -1 != ix:
                line = line[:line.find(c)]
        if line[-1] == '\\':
            #current line will continue on next line
            line = line[:-1]
            if flag:
                #add to accumulator
                accumulator = string.join((accumulator, line), ' ')
            else:
                #set
                accumulator = line
            flag = True
            continue
        if flag:
            #add last part of line to accumulator
            accumulator = string.join((accumulator, line), ' ')
            line = accumulator
            accumulator = ''
            flag = False
        #split line to key and value
        ix = line.find(sep)
        if ix > 0:
            key = line[:ix].rstrip()
            value = line[ix+1:].lstrip().rstrip()
            if ret.has_key(key):
                old = ret[key]
                if type(old) == type([]):
                    #already a list
                    ret[key].append(value)
                else:
                    ret[key] = [old, value]
            else:
                ret[key] = value
    f.close()
    return ret

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data, EVT_ID):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_ID)
        self.data = data #on receiver func message is in event.data

class MyBackground(model.Background):

    def on_close(self,evt):
        self.Destroy()

    def on_initialize(self, event):
        #
        # config
        #
        configFile = "config.ini"
        self.DATAFOLDER = os.getcwd()
        configFilename = string.join((self.DATAFOLDER, configFile), os.sep)
        if not os.path.isfile(configFilename):
            self.DATAFOLDER = string.join((os.getcwd(),'..'),os.sep)
            configFilename = string.join((self.DATAFOLDER, configFile), os.sep)

        #if getattr(sys, 'frozen', False):
        #    self.DATAFOLDER = string.join((os.getcwd(),'..'),os.sep)
        #else:
        #    self.DATAFOLDER = os.getcwd()
        #configFilename = string.join((self.DATAFOLDER, "config.ini"), os.sep)
        self.config = getPropsDict(configFilename, '=')
        self.title = self.config.get('TITLE','UDP Multicast Observer')
        self.multicast_addr = self.config.get('multicast_addr', '224.3.4.5')
        self.multicast_port = int(self.config.get('multicast_port', 45566))
        nodename = self.config.get('nodename','node{}'.format(random.randint(1,100)))
        self.remove_timeout = int(self.config.get('remove_timeout', 7))
        #
        # components
        #
        self.components.enablebroadcast.checked = False
        self.components.mynodename.text = nodename
        hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(socket.gethostname())
        ipaddrlist.append('127.0.0.1')
        ipaddrlist.append('0.0.0.0')
        self.components.selectedInterface.items = ipaddrlist
        self.components.selectedInterface.selection = 0
        self.components.nodelist.columnHeadings = ('#','Server reply','Replys','Server IP','Last seen','Inactive [sec]')

        # Set up event handler for any worker thread results
        #
        self.EVT_CLOCK = wx.NewId()
        self.Connect(-1, -1, self.EVT_CLOCK, self.OnResultClock)
        self.EVT_NODELIST = wx.NewId()
        self.Connect(-1, -1, self.EVT_NODELIST, self.OnResultNodeList)
        #
        # Threads
        #
        self.task1 = threading.Thread(target=self.task_ceas, kwargs=dict())
        self.task1.daemon = True
        self.task1.start()
        self.task2 = threading.Thread(target=self.task_nodelist, kwargs=dict())
        self.task2.daemon = True
        self.task2.start()
        self.task3 = threading.Thread(target=self.task_broadcast, kwargs=dict())
        self.task3.daemon = True
        self.task3.start()

    def OnResultClock(self, event):
        self.components.textclock.text = event.data

    def OnResultNodeList(self, event):
        self.components.nodelist.items = event.data
        if 1:
            self.components.nodelist.SetColumnWidth(0,30)   #ix
            self.components.nodelist.SetColumnWidth(1,160)  #Node Name
            self.components.nodelist.SetColumnWidth(2,70)   #Replys
            self.components.nodelist.SetColumnWidth(3,100)   #Server IP
            self.components.nodelist.SetColumnWidth(4,90)   #Last seen
            #self.components.nodelist.SetColumnWidth(5,50)  #Inactive [sec]

    def on_selectedInterface_select(self, evt):
        self.TaskBroadcastEnabled = False
        #print "Stop thread:"
        while self.TaskBroadcastRunning:
            time.sleep(1)
        self.task3 = threading.Thread(target=self.task_broadcast, kwargs=dict())
        self.task3.daemon = True;self.task3.start()


    def task_ceas(self):
        flag_secunde = True
        while True:
            flag_secunde = not flag_secunde
            ch = ' '
            if flag_secunde:
                ch = ':'
            format = "%%H:%%M%c%%S" % (ch,)
            s = time.strftime(format,time.localtime())
            wx.PostEvent(self, ResultEvent(s, self.EVT_CLOCK))
            time.sleep(0.5)
        return

    def task_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ix = self.components.selectedInterface.selection
        bind_interface = self.components.selectedInterface.items[ix]
        #print "bind_interface=",bind_interface
        sock.bind((bind_interface, self.multicast_port))
        group = socket.inet_aton(self.multicast_addr)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(0.1)
        self.TaskBroadcastEnabled = True
        self.TaskBroadcastRunning = True
        while self.TaskBroadcastEnabled:
            if self.components.enablebroadcast.checked:
                while True:
                    try:
                        data, address = sock.recvfrom(1024)
                        #it doesn't matter the data received, send always the service list
                        #now the service list is nodename
                        sock.sendto(self.components.mynodename.text, address)
                    except socket.timeout:
                        break
                    except Exception as ex:
                        #print "err task_broadcast:",ex
                        break
            else:
                time.sleep(1)
        sock.close()
        self.TaskBroadcastRunning = False
    #end task_broadcast


    def task_nodelist(self):
        self.d_nodes = {}
        while True:
            time.sleep(1)
            L = []
            d = discover("discover", self.multicast_addr, self.multicast_port, ttlval=10)
            self.d_nodes.update(d)
            d = {}
            for ix,node in enumerate(sorted(self.d_nodes.keys())):
                node_name = node
                number_of_replys = self.d_nodes[node][0]
                ip, port = self.d_nodes[node][2]
                server = '{}'.format(ip)
                last_seen = self.d_nodes[node][1]
                inactive = (datetime.datetime.now() - last_seen).seconds
                if inactive < self.remove_timeout:
                    l = (str(ix), node_name, str(number_of_replys),
                         server, last_seen.strftime("%H:%M:%S"), str(inactive))
                    L.append(l)
                    d[node] = self.d_nodes[node]
            self.d_nodes = d
            wx.PostEvent(self, ResultEvent(L, self.EVT_NODELIST))
    #end task_nodelist

    def on_about_command(self, event):
        result = dialog.messageDialog(self, '''{}

(C) 2017 Ioan Coman
http://rainbowheart.ro/

Config folder:
{}

wx version: {}

Python version:
{}

'''.format(self.title, self.DATAFOLDER, wx.version(), sys.version), 'About', wx.ICON_INFORMATION | wx.OK) #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL)



def fix_frozen_apps():
    #
    #fix import for py2exe, cx_freeze, pyinstaller, ...
    #
    #import here whatever fail to import when application is frozen
    #
    #import pyodbc, pymssql, _mssql
    from PythonCard.components import slider
    #from PythonCard.components import radiogroup
    from PythonCard.components import button
    #from PythonCard.components import list
    from PythonCard.components import choice
    from PythonCard.components import statictext
    from PythonCard.components import checkbox
    #from PythonCard.components import gauge
    from PythonCard.components import multicolumnlist
    #from PythonCard.components import passwordfield
    from PythonCard.components import textarea
    from PythonCard.components import combobox
    #from PythonCard.components import calendar



if __name__ == '__main__':
    app = model.Application(MyBackground)
    app.MainLoop()
