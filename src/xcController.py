#
#  xcController.py
#  aethercocoa
#
#  Created by fin on 6/21/10.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *
import Cocoa
import objc

class xcController(NSWindowController):
    computers = objc.IBOutlet()
    computers_view = objc.IBOutlet()
    webview = objc.IBOutlet()
    webViewDelegate = objc.IBOutlet()
    
    def awakeFromNib(self):
        resourcePath = NSBundle.mainBundle().resourcePath().replace('/','//').replace(' ', '%20')
        self.webview.mainFrame().loadHTMLString_baseURL_(
            NSString.stringWithContentsOfFile_(
                NSBundle.mainBundle().pathForResource_ofType_("webview", "html")
            ),
            NSURL.URLWithString_("file://%s/" % resourcePath)
        )
        print dir(self)
        self.webview.setUIDelegate_(self.webViewDelegate);
        self.webview.setEditingDelegate_(self.webViewDelegate)
        self.webViewDelegate.setDataSource_(self.computers);

