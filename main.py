import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gui import NGSPICESimulatorApp
import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
lang = gettext.translation('loc', localedir=localedir, languages=['en'], fallback=True)
lang.install()

def main():
    """
    Основная функция для запуска приложения NGSPICE Simulator с использованием GTK.
    """

    app = NGSPICESimulatorApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()  # Запускаем главный цикл GTK для обработки событий

if __name__ == "__main__":
    main()