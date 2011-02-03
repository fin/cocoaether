from distutils.core import setup
import py2app
setup(
    plugin = ['TestBundlePythonWhat.py'],
    data_files = ['./src/', '../aether/',
        #'/Library/Python/2.6/site-packages/pybonjour-1.1.1-py2.6.egg/pybonjour.py',
        #'/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/twisted',
        ],
    install_requires = ['twisted', 'pybonjour', ],
    options=dict(py2app=dict(
        extension='.widgetplugin',
        includes = ['pybonjour', ],
        packages = ['twisted.internet', 'twisted.protocols', ],
    )),
)
