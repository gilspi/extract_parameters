from tkinter import Tk
from gui import NGSPICESimulatorApp


def main():
    """
    Основная функция для запуска приложения NGSPICE Simulator. 
    Эта функция создает корневое окно Tkinter, инициализирует приложение NGSPICESimulatorApp, 
    и запускает главный цикл Tkinter для обработки событий.
    """
    root = Tk()
    app = NGSPICESimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
