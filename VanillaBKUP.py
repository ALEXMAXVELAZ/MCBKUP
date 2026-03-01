import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog

minecraft_path = os.path.expanduser("~\\AppData\\Roaming\\.minecraft\\saves")
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")

BG = "#1e1e1e"
ACCENT = "#cd173f"
FG = "#ffffff"
BTN_HOVER = "#a01030"

# --- Config ---
def load_backup_folder():
    if not os.path.exists(config_file):
        return ask_and_save_folder(first_time=True)
    with open(config_file, "r") as f:
        path = f.read().strip()
    if not path or not os.path.exists(path):
        messagebox.showwarning("Aviso", "La ruta guardada no existe, selecciona una nueva.")
        return ask_and_save_folder()
    return path

def ask_and_save_folder(first_time=False):
    if first_time:
        messagebox.showinfo("Bienvenido", "Primera vez que abres el programa.\nSelecciona la carpeta donde se guardarán los backups.")
    folder = filedialog.askdirectory(title="Selecciona carpeta de backups")
    if not folder:
        exit()
    with open(config_file, "w") as f:
        f.write(folder)
    return folder

def update_folder():
    global backup_folder
    new_folder = ask_and_save_folder()
    backup_folder = new_folder
    folder_label.config(text=f"Ruta de la carpeta del Backup:\n{backup_folder}")

def get_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return round(total / (1024*1024), 2)

# --- Validaciones ---
if not os.path.exists(minecraft_path):
    messagebox.showerror("Error", "No se encontró la carpeta de mundos.")
    exit()

worlds = [f for f in os.listdir(minecraft_path) if os.path.isdir(os.path.join(minecraft_path, f))]

if not worlds:
    messagebox.showerror("Error", "No hay mundos disponibles.")
    exit()

selected_world = None

def select_world(world):
    global selected_world
    selected_world = world
    root.destroy()

def on_enter(e): e.widget.config(bg=BTN_HOVER)
def on_leave(e): e.widget.config(bg=ACCENT)

def on_mousewheel(e):
    canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

# --- Ventana ---
root = tk.Tk()
root.title("Minecraft Backup")
root.resizable(False, False)
root.configure(bg=BG)

backup_folder = load_backup_folder()

# --- Ruta actual + botón actualizar ---
footer_frame = tk.Frame(root, bg=BG, relief="sunken", border=1)
footer_frame.pack(pady=(0, 6), fill="x")

folder_label = tk.Label(
    footer_frame,
    text=f"Ruta de la carpeta del Backup:\n{backup_folder}",
    font=("Arial", 8),
    bg=BG, fg="#aaaaaa",
    anchor="w",
    wraplength=340
)
folder_label.pack(side="left", fill="x", expand=True)

btn_update = tk.Button(
    footer_frame,
    text="Cambiar ruta",
    font=("Arial", 8),
    bg=ACCENT, fg=FG,
    activebackground=BTN_HOVER,
    activeforeground=FG,
    overrelief="sunken",
    cursor="hand2",
    command=update_folder
)
btn_update.pack(side="right", padx=(8, 0), ipady=2)

tk.Label(
    root,
    text="Selecciona un mundo para hacer backup",
    font=("nsolas", 15, "bold"),
    bg=BG, fg=ACCENT,
    pady=14
).pack()

# --- Contenedor con scroll ---
container = tk.Frame(root, bg=BG)
container.pack(pady=(0, 5))

canvas = tk.Canvas(container, bg=BG, highlightthickness=0, width=370, height=300)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

frame = tk.Frame(canvas, bg=BG)
frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

def on_frame_configure(e):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_canvas_configure(e):
    canvas.itemconfig(frame_window, width=e.width)

frame.bind("<Configure>", on_frame_configure)
canvas.bind("<Configure>", on_canvas_configure)
canvas.bind("<MouseWheel>", on_mousewheel)

# --- Botones de mundos ---
for world in worlds:
    size = get_size(os.path.join(minecraft_path, world))
    btn = tk.Button(
        frame,
        text=f"{world}  —  {size} MB",
        anchor="w",
        font=("Arial", 10),
        bg=ACCENT, fg=FG,
        activebackground=BTN_HOVER,
        activeforeground=FG,
        overrelief="sunken",
        cursor="hand2",
        command=lambda w=world: select_world(w)
    )
    btn.pack(pady=3, ipady=4, fill="x", padx=5)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<MouseWheel>", on_mousewheel)

root.mainloop()

if not selected_world:
    exit()

# --- Hacer el backup ---
date_str = datetime.now().strftime("%Y-%m-%d")
source_path = os.path.join(minecraft_path, selected_world)
dest_path = os.path.join(backup_folder, f"{selected_world}_{date_str}")

try:
    shutil.copytree(source_path, dest_path)
    messagebox.showinfo("Éxito", f"Backup creado en:\n{dest_path}")
except Exception as e:
    messagebox.showerror("Error", f"No se pudo crear el backup:\n{e}")