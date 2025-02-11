import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gui import NGSPICESimulatorApp  # Импортируем ваш главный класс интерфейса

def main():
    """
    Основная функция для запуска приложения NGSPICE Simulator с использованием GTK.
    """
    # Создаем окно приложения
    app = NGSPICESimulatorApp()
    app.connect("destroy", Gtk.main_quit)  # Завершаем приложение при закрытии окна
    app.show_all()  # Отображаем все элементы интерфейса
    Gtk.main()  # Запускаем главный цикл GTK для обработки событий

if __name__ == "__main__":
    main()