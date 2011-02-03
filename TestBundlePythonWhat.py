import site

site.addsitedir('/System/Library/Frameworks/Python.framework/Versions/Current/Extras/lib/python/')
#won't find objc otherwise


import objc
from Foundation import *
from AppKit import *
from WebKit import *

from threading import Thread, Lock
import os.path

from PyObjCTools import AppHelper

from aether.server.main import Service
from aether.client.main import browse, send

import FoundComputer

from twisted.internet import reactor

log = NSLog

objc.setVerbose(1)
log(u'ProgressViewPalette.py loaded')

notifier = None

import socket
import getpass

SERVICENAME = u'%s@%s' % (getpass.getuser(), socket.gethostname().replace('.local',''),)

class Autoflush:
    def __init__(self, stream): 
        self.stream = stream 

    def write(self, text): 
        self.stream.write(text)
        self.stream.flush() 

import sys
f = open("/tmp/plugin-stderr.log", "w")
original_stderr = sys.stderr
sys.stderr = Autoflush(f)
f = open("/tmp/plugin-stdout.log", "w")
original_stdout = sys.stdout
sys.stdout = Autoflush(f)

print 'hi'
print >>sys.stderr, "hi"

try:
    import Growl
    notifier = Growl.GrowlNotifier('aether', ['done'])
    notifier.register()
except ImportError, e:
    log("no notifications!")

class ReceiveHandler(object):
    def __init__(self, controller):
        self.last_received = 0
        self.controller = controller

    def cb(self, client, name, received, total, failed=False, server=None):
        service = None
        for computer in self.controller.computers.content():
            if computer.ip == client[0]:
                service = computer

        transfer = None
        for candidate_transfer in service.transfers:
            if candidate_transfer.uri == name and candidate_transfer.peer == computer:
                transfer = candidate_transfer

        if not transfer:
            transfer = FoundComputer.Transfer.alloc().init()
            transfer.peer = computer
            transfer.uri = name
            transfer.controller = self.controller

        if transfer.cancelled:
            server.transport.loseConnection()
            transfer.failed()
            return

        if failed:
            transfer.failed()
            return
        
        transfer.progress(received, total)

class ReactorLoop(Thread):
    def __init__(self, controller):
        self.pool = NSAutoreleasePool.alloc().init()
        self.receivehandler = ReceiveHandler(controller)
        self.service = Service(SERVICENAME, os.path.expanduser('~/Downloads'), self.receivehandler.cb)
        Thread.__init__(self)

    def run(self):
        print 'listen'
        reactor.run(installSignalHandlers=0)

    def listen(self):
        reactor.callFromThread(self.service.listen)

    def stop(self):
        log("ReactorLoop stopping")
        self.service.stop()
        self.pool.release()
        log("ReactorLoop stopped")

class BrowseLoop(Thread):
    def __init__(self, controller):
        Thread.__init__(self)
        self.controller = controller
        self.status = []
        self.indexes = {}
        self.add_lock = Lock()

    def run(self):
        browse('_at_nomin_aether._tcp', self.added, self.removed, lambda: self.status)
        self.pool = NSAutoreleasePool.alloc().init()


    def added(self, serviceName, regtype, replyDomain, hosttarget, *args, **kwargs):
        self.add_lock.acquire()
        if serviceName in self.indexes:
            return
        index = self.controller.computers.content().count()
        fc = FoundComputer.FoundComputer.alloc().init()
        fc.controller = self.controller
        fc.name = serviceName
        print serviceName
        fc.ip = socket.gethostbyname(hosttarget)
        AppHelper.callAfter(self.controller.computers.addObject_, fc)
        self.indexes[serviceName]=index
        self.add_lock.release()
        print self.controller.computers

    def removed(self, serviceName, *args, **kwargs):
        self.add_lock.acquire()
        AppHelper.callAfter(self.controller.computers.remove_, self.indexes[serviceName])
        del self.indexes[serviceName]
        self.add_lock.release()

    def stop(self):
        log("BrowseLoop stopping")
        self.status.append('stop')
        del self.pool
        log("BrowseLoop stopped")

class TestBundlePythonWhat(NSObject):
    reactorthread = None
    browsethread = None
    computers = None
    wso = None
    webview = None

    def log_(self, text):
        log(text)

    def test(self):
        return "this too seems to work"

    def test1(self):
        log("test");
        return "wait, what?"

    def startit(self):
        if not self.computers:
            self.computers = NSArrayController.alloc().init()
            self.setDataSource_(self.computers)
            log("got computers")
        log("starting threads.")
        try:
            if not self.reactorthread:
                self.reactorthread = ReactorLoop(self)
                self.reactorthread.start()
            self.reactorthread.listen()
            self.browsethread = BrowseLoop(self)
            self.browsethread.start()
        except Exception, e:
            try:
                log(e)
            except Exception, ex:
                print e

        return "okay"
    
    def stopit(self):
        log("stopping threads")
        self.reactorthread.stop()
        self.browsethread.stop()
        log("stopped")
        return "okay"

    def quitit(self):
        log("quitting")
        reactor.callFromThread(reactor.stop)
        log("quitted")

    def isSelectorExcludedFromWebScript_(self, wso):
        return False

    def windowScriptObjectAvailable_(self, scriptObject):
        global log

        log = lambda x: AppHelper.callAfter(scriptObject.callWebScriptMethod_withArguments_, 'log', [x])
        scriptObject.setValue_forKey_("yes", "TestBundleLoaded")
        scriptObject.setValue_forKey_(self, "TestBundle")
        AppHelper.callLater(1, scriptObject.callWebScriptMethod_withArguments_, 'initialize_threads', [])
        #log("hi!");
        self.wso = scriptObject
        #scriptObject.setValue_forKey_(self, "TestBundle")
        #scriptObject.callWebScriptMethod_withArguments_('log', ["hiii!"])

    def setDataSource_(self, data):
        if not self.wso:
            return
        self.data = data
        self.data.addObserver_forKeyPath_options_context_(self, "arrangedObjects", 0, None)
        self.data.addObserver_forKeyPath_options_context_(self, "selectionIndexes", 0, None)
        self.wso.setValue_forKeyPath_(self, "objc")
    
    def selectObject_(self, name):
        for i in self.data.arrangedObjects:
            if i.name.isEqual_(name):
                self.data.setSelectionIndex_indexOfObject_(self.data.arrangedObjects, 1)
                break
    
    def call(self, method, args):
        return AppHelper.callAfter(self.wso.callWebScriptMethod_withArguments_, method, args)

    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, object, change, context):
        if keyPath == "arrangedObjects":
            self.observeValueForArrangedObjects_change_context_(object,change,context)
        if keyPath == "selectionIndexes":
            for i in self.data.arrangedObjects():
                self.call("unselect", [i])
            i = self.data.arrangedObjects().objectAtIndex_(self.data.selectionIndex())
            self.call("select", [i])
        if keyPath == "state":
            if object.state:
                self.call("enable", [object])
            else:
                self.call("disable", [object])

    def observeValueForArrangedObjects_change_context_(self, object, change, context):
        obj = object.arrangedObjects()[object.selectionIndex()]
        print 'valueChanged', obj, obj.element, obj.name
        if obj.element:
            self.call("remove", [obj])
        else:
            self.call("add", [obj])

    def initWithWebView_(self, webview):
        self.webview = webview
        return self

    def send_(self, uri):
        log('send: %s' % uri)
