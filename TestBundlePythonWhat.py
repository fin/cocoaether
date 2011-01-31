x = open('/tmp/testbundle.log', 'w')
x.write('iniitload')
x.close()

import site

site.addsitedir('/System/Library/Frameworks/Python.framework/Versions/Current/Extras/lib/python/')

import objc
from Foundation import *
from AppKit import *
from WebKit import *

objc.setVerbose(1)
NSLog(u'ProgressViewPalette.py loaded')

x = open('/tmp/testbundle.log', 'w')
x.write('load')
x.close()

class TestBundlePythonWhat(NSObject):
    def test(self):
        return "this too seems to work"

    def isSelectorExcludedFromWebScript_(self, wso):
        return False

    def keyDown_(self, theEvent):
        pass

    def contextMenuItemsForElement_defaultMenuItems_(self, element, defaultMenuItems):
        return False

    def webView_shouldChangeSelectedDOMRange_toDOMRange_affinity_stillSelecting_(self, webView, currentRange, proposedRange, affinity, flag):
        return False

    def webView_dragDestinationActionMaskForDraggingInfo_(self, webView, draggingInfo):
        return WebDragDestinationActionDHTML;

    def windowScriptObjectAvailable_(self, scriptObject):
        y = open('/tmp/testbundle.log', 'a')
        y.write('lol')
        y.close()

        scriptObject.setValue_forKey_(self, "TestBundle")

    def initWithWebView_(self, webView):
        self = super(TestBundlePythonWhat, self).init()
        return self

