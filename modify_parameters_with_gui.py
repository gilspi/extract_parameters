import os
import subprocess
import shutil
import matplotlib.pyplot as plt
import pandas as pd

# установленные библиотеки
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# пользовательские библиотеки
from config import PROJECT_PATH, OSDILIBS_PATH
from utils import find_file, modify_parameters

import plot_simulation

# TODO: нужно выполнять поиск файла с помощью os
# TODO: в дальнейшем пользователь должен просто подгружать модель из окна GUI
FOLDER_NAME = "mextram"  # FIXME: пока что код работает только с mextram

PARAMETERS_FILE= os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/parameters.inc")
VAMODEL_PATH = os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/")
VAMODEL_NAME = "bjt505.va"
OSDIMODEL_NAME = "bjt505.osdi"
EXAMPLES_PATH = os.path.join(PROJECT_PATH, f"examples/{FOLDER_NAME}/ngspice/")
SPICE_FILE = "npn_ic_ib_is_vb.sp"  # FIXME: нужно сделать так чтобы можно было пользователь мог подгружать схему
####################################################################################

spice_file = None  # find_file(SPICE_FILE)
# print(spice_file)


def rebuild_osdi(vamodel_name: str = VAMODEL_NAME, vamodel_path: str = VAMODEL_PATH):
    """
    Функция пересобирает osdi-модель.
    Использует vamodel_name указанную в параметрах функции
    Пример: ./openvaf bjt505.va -> bjt505.osdi
    """
    subprocess.run(["./openvaf", vamodel_name], cwd=vamodel_path)


def move_osdi_file(src: str = VAMODEL_PATH, osdi_model: str = OSDIMODEL_NAME):
    """
    Перемещает файл bjt505.osdi из src в dst
    src - директория, в которой создалась модель osdi
    Файл osdi перемещается в osdilibs
    """
    source_path = find_file(osdi_model, search_path=src)
    # print(source_path)
    dst = os.path.join(OSDILIBS_PATH, osdi_model)
    if os.path.exists(dst):
        os.remove(dst)

    shutil.move(source_path, OSDILIBS_PATH)


def run_ngspice_interactive(spice_file: str, canvas, fig):
    process = subprocess.Popen(["ngspice", "-b", spice_file])
    process.wait()
    
    try:
        process.terminate()
    except Exception as e:
        print(f"Ошибка завершения ngspice: {e}")

    plot_simulation.plot_simulation_data(canvas, fig)


def choose_spice_file():
    """Выбор SPICE-файла для симуляции."""
    return filedialog.askopenfilename(
        initialdir=EXAMPLES_PATH, title="Выберите SPICE-файл",
        filetypes=(("SPICE files", "*.sp *.cir"), ("All files", "*.*"))
    )


def select_spice_file():
    global spice_file
    spice_file = choose_spice_file()
    if spice_file:
        messagebox.showinfo("Файл выбран", f"Выбранный файл: {spice_file}")



def start_simulation(canvas, fig, spice_file):
    """
    TODO: запускает симуляцию в NGSPICE и проверяем ошибки
    """
    if not spice_file:
        messagebox.showwarning("Ошибка",
                               "Пожалуйста, выберите SPICE файл")
        return
    
    is_value = entry_is.get() or "1.0e-15"
    nff_value = entry_nff.get() or "1.0"
    nfr_value = entry_nfr.get() or "1.0"
    
    params_to_modify = {
        "is": is_value,
        "nff": nff_value,
        "nfr": nfr_value
    }
    
    modify_parameters(PARAMETERS_FILE, params_to_modify)
    
    rebuild_osdi()
    
    move_osdi_file()
    
    try:
        run_ngspice_interactive(spice_file, canvas, fig)
        messagebox.showinfo("Успех", "Симуляция завершена успешно.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка симуляции: {e}")



root = tk.Tk()
root.title("NGSPICE Симулятор")

tk.Label(root, text="is:").grid(row=0, column=0, padx=5, pady=5)
entry_is = tk.Entry(root)
entry_is.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="nff:").grid(row=1, column=0, padx=5, pady=5)
entry_nff = tk.Entry(root)
entry_nff.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="nfr:").grid(row=2, column=0, padx=5, pady=5)
entry_nfr = tk.Entry(root)
entry_nfr.grid(row=2, column=1, padx=5, pady=5)

run_button = tk.Button(root, text="Запустить симуляцию",
                       command=lambda:start_simulation(canvas, fig, spice_file))
run_button.grid(row=3, column=0, columnspan=2)

choose_button = tk.Button(root, text="Выбрать схему",
                          command=select_spice_file)
choose_button.grid(row=4, column=0, columnspan=2)

exit_button = tk.Button(root, text="Выход", command=root.quit)
exit_button.grid(row=5, column=0, columnspan=2)

fig = plt.Figure(figsize=(6,4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=2, rowspan=6, padx=10, pady=5)

root.mainloop()

