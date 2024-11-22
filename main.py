from tkinter import Tk
from gui import NGSPICESimulatorApp


def main():
    root = Tk()  # Создаем корневое окно Tkinter
    app = NGSPICESimulatorApp(root)  # Передаем root в приложение
    root.mainloop()  # Запускаем главный цикл


if __name__ == "__main__":
    main()
