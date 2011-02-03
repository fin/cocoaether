#
#  FoundComputer.py
#  aethercocoa
#
#  Created by fin on 6/21/10.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#

from Foundation import *
import objc
import urllib
import os.path
import aether.client.main as client
from twisted.internet import reactor


class Transfer(NSObject):
    peer = None
    uri = None
    cancelled = False
    sender = False

    controller = None
    lastfraction = None

    def __init__(self):
        NSObject.__init__(self)

    def isSelectorExcludedFromWebScript_(self, wso):
        return False

    def progress(self, done, full):
        fraction = float(done)/float(full)
        if self.lastfraction and self.lastfraction+0.01>fraction and not fraction == 1:
            return
        self.controller.call('progress', [self, self.peer.element, self.uri, fraction])
        self.lastfraction = fraction

    def failed(self):
        self.controller.call('progress', [self, self.peer.element, self.uri, 1])

    def cancel(self):
        self.controller.log("cancelling")
        self.cancelled = True
        if self.sender:
            self.sender.cancel()

class FoundComputer(NSObject):
    name = objc.IBOutlet()
    element = objc.IBOutlet()
    transfers = []
    controller = None
    ip = None
    
    def __init__(self):
        NSObject.__init__()
        self.element = None
    
    def isSelectorExcludedFromWebScript_(self, wso):
        return False

    def getName_(self, rofl=None):
        return self.name

    def send_(self, uri):
        try:
            t = Transfer.alloc().init()
            t.peer = self
            t.uri = uri
            t.controller = self.controller
            self.transfers.append(t)
            
            def send_actual(*args, **kwargs):
                try:
                    self.controller.log_('sending')
                    t.sender = client.send(*args, **kwargs)
                except Exception, e:
                    self.controller.log_(e)
            reactor.callFromThread(send_actual, self.name, urllib.urlopen(uri).url.replace("file://",""), lambda *x,**y: t.failed(), '', t.progress)
            #send_actual(self.name, urllib.urlopen(uri).url.replace("file://",""), lambda *x,**y: t.failed(), '', t.progress)
        except Exception, e:
            return e
        return urllib.urlopen(uri).url.replace("file://","")


    def setElement_(self, elem):
        self.element = elem
        if elem:
            self.element.retain()
        print 'set element', self.element

    def getElement_(self, x=None):
        if self.element:
            self.element.retain()
        return self.element

