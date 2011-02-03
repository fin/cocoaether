from Foundation import *
from AppKit import *
from WebKit import *

class WebViewDelegate(NSObject):
    webView = objc.IBOutlet()

    def log_(self, log):
        print log

    def isSelectorExcludedFromWebScript_(self, wso):
        return False

    def setDataSource_(self, data):
        self.data = data
        self.data.addObserver_forKeyPath_options_context_(self, "arrangedObjects", 0, None)
        self.data.addObserver_forKeyPath_options_context_(self, "selectionIndexes", 0, None)
        self.webView.windowScriptObject().setValue_forKeyPath_(self, "objc")

    def selectObject_(self, name):
        for i in self.data.arrangedObjects:
            if i.name.isEqual_(name):
                self.data.setSelectionIndex_indexOfObject_(self.data.arrangedObjects, 1)
                break

    def call(self, method, arg):
        return self.webView.windowScriptObject().callWebScriptMethod_withArguments_(method, [arg])

    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, object, change, context):
        if keyPath == "arrangedObjects":
            self.observeValueForArrangedObjects_change_context_(object,change,context)
        if keyPath == "selectionIndexes":
            for i in self.data.arrangedObjects():
                self.call("unselect", i)
            i = self.data.arrangedObjects().objectAtIndex_(self.data.selectionIndex())
            self.call("select", i)
        if keyPath == "state":
            if object.state:
                self.call("enable", object)
            else:
                self.call("disable", object)

    def observeValueForArrangedObjects_change_context_(self, object, change, context):
        obj = object.arrangedObjects()[object.selectionIndex()]
        print 'valueChanged', obj, obj.element, obj.name
        if obj.element:
            self.call("remove", obj)
        else:
            self.call("add", obj)

    def keyDown_(self, theEvent):
        pass

    def contextMenuItemsForElement_defaultMenuItems_(self, element, defaultMenuItems):
        return False

    def webView_shouldChangeSelectedDOMRange_toDOMRange_affinity_stillSelecting_(self, webView, currentRange, proposedRange, affinity, flag):
        return False

    def webView_dragDestinationActionMaskForDraggingInfo_(self, webView, draggingInfo):
        return WebDragDestinationActionDHTML;


