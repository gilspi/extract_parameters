import platform
import os
import sys
from typing import Tuple, Any


try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False
    
    
def create_app() -> Tuple[Any, Any]:
    """
    Создает экземпляр приложения и главное окно
    """
    if sys.platform == "win32":
        from graphics.qt.app import QtApp
        app = QtApp()
        return app.initialize()
    else:
        from graphics.gtk.app import GtkApp
        app = GtkApp()
        return app.initialize()

def run_app(app, window):
    """
    Запускает приложение с учетом особенностей разных фреймворков
    """
    system = platform.system().lower()
    
    if system == 'windows':
        from graphics.qt.app import QtApp
        qt_app = QtApp()
        qt_app.app = app
        qt_app.window = window
        qt_app.run()
    elif GTK_AVAILABLE:
        from graphics.gtk.app import GtkApp
        gtk_app = GtkApp()
        gtk_app.app = app
        gtk_app.window = window
        gtk_app.run()
    else:
        raise ImportError("GTK не установлен") 