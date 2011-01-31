from distutils.core import setup
import py2app
setup(
    plugin = ['TestBundlePythonWhat.py'],
    data_files = ['../pyaethercocoa/', '../aether/'],
    options=dict(py2app=dict(
        extension='.widgetplugin',
    )),
)
