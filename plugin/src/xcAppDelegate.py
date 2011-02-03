#
#  xcPROJECTNAMEASIDENTIFIERxcAppDelegate.py
#  xcPROJECTNAMExc
#
#  Created by xcFULLUSERNAMExc on xcDATExc.
#  Copyright xcORGANIZATIONNAMExc xcYEARxc. All rights reserved.
#

from Foundation import *
from AppKit import *
from threading import Thread
from twisted.internet import reactor
import sys

from aether.server.main import Service
from aether.client.main import browse, send
import FoundComputer
from PyObjCTools import AppHelper
from threading import Lock

try:
    import Growl
    n = Growl.GrowlNotifier('aether', ['done'])
    n.register()
except ImportError, e:
    n = None

class ReceiveHandler(object):
    def __init__(self):
        self.last_received = 0
        self.transfers = {}

    def cb(self, client, name, received, total):
        promille = total / 1000
        if promille < 4096:
            promille = 4096
        if self.last_received + promille < received:
            self.last_received = received
        if received==total:
            if n:
                n.notify('done', name, '%d kb received' % total)




rh = ReceiveHandler()
service = Service('finui@finkbook', '/Users/fin/Downloads', rh.cb)


class ReactorLoop(Thread):
    def __init__(self):
        self.pool = NSAutoreleasePool.alloc().init()
        Thread.__init__(self)
    def run(self):
        service.listen()
        print 'listen'
        reactor.run(installSignalHandlers=0)

    def stop(self):
        print 'stopping'
        pool.release()
        reactor.stop()

class BrowseLoop(Thread):
    def __init__(self, controller):
        self.pool = NSAutoreleasePool.alloc().init()
        Thread.__init__(self)
        self.controller = controller
        self.status = []
        self.indexes = {}
        self.add_lock = Lock()

    def run(self):
        browse('_at_nomin_aether._tcp', self.added, self.removed, lambda: self.status)


    def added(self, serviceName, *args, **kwargs):
        self.add_lock.acquire()
        if serviceName in self.indexes:
            return
        index = self.controller.computers.content().count()
        fc = FoundComputer.FoundComputer.alloc().init()
        fc.name = serviceName
        AppHelper.callAfter(self.controller.computers.addObject_, fc)
        self.indexes[serviceName]=index
        self.add_lock.release()

    def removed(self, serviceName, *args, **kwargs):
        self.add_lock.acquire()
        AppHelper.callAfter(self.controller.computers.remove_, self.indexes[serviceName])
        del self.indexes[serviceName]
        self.add_lock.release()

    def stop(self):
        self.status.append('stop')
        pool.release()

class xcAppDelegate(NSObject):
    controller = objc.IBOutlet()

    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
        self.reactorthread = ReactorLoop()
        self.reactorthread.start()
        self.browsethread = BrowseLoop(self.controller)
        self.browsethread.start()

    def applicationWillTerminate_(self, sender):
        self.reactorthread.stop()
        self.browsethread.stop()
        print 'stopped'

