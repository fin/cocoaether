#
#  AeDetailWindow.py
#  aethercocoa
#
#  Created by fin on 6/21/10.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#

from Foundation import *
import Cocoa
import objc
from twisted.internet import reactor
from aether.client.main import send

class AeDetailView(Cocoa.NSView):
    name = objc.IBOutlet()
    controller = objc.IBOutlet()
    collectionviewitem = objc.IBOutlet()

    def awakeFromNib(self):
        self.registerForDraggedTypes_([Cocoa.NSFilenamesPboardType])

    def draggingEntered_(self,sender):
        pboard = sender.draggingPasteboard()
        types = pboard.types()
        opType = Cocoa.NSDragOperationNone
        if Cocoa.NSFilenamesPboardType in types:
            opType = Cocoa.NSDragOperationCopy
        return opType

    def performDragOperation_(self,sender):
        print sender
        pboard = sender.draggingPasteboard()
        successful = False
        if Cocoa.NSFilenamesPboardType in pboard.types():
            print "lolwtf"
            print self.collectionviewitem.representedObject.name
            print spboard.propertyListForType_(Cocoa.NSFilenamesPboardType)[0]
            # reactor.callInThread(send, self.collectionviewitem.representedObject.name, pboard.propertyListForType_(Cocoa.NSFilenamesPboardType)[0], self.done)
            successful = True
        return successful

    def done(self):
        print 'ohlol'
