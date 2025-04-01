import os
import gettext

from graphics import create_app, run_app


localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
lang = gettext.translation('loc', localedir=localedir, languages=['en'], fallback=True)
lang.install()


def main():
    """
    Основная функция для запуска приложения NGSPICE Simulator.
    Автоматически выбирает GUI-фреймворк в зависимости от операционной системы:
    - Windows: PyQt6
    - Linux/MacOS: GTK
    """
    app, window = create_app()
    run_app(app, window)

if __name__ == "__main__":
    main() 