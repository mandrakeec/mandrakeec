import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ActasApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Actas")
        self.master.geometry("800x600")

        # Frame principal
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Agregar logotipo
        self.agregar_logotipo()

        # Menú principal
        self.crear_menu()

    def crear_menu(self):
        # Crear botones de menú
        btn_actas = ttk.Button(
            self.main_frame, text="Actas", command=self.abrir_actas)
        btn_actas.pack(pady=10)

        btn_opciones = ttk.Button(
            self.main_frame, text="Opciones", command=self.abrir_opciones)
        btn_opciones.pack(pady=10)

    def abrir_actas(self):
        print("Abriendo Actas...")

    def abrir_opciones(self):
        print("Abriendo Opciones...")

    def agregar_logotipo(self):
        # Ruta de la imagen
        ruta_logo = r"C:\Sistemas Soporte\Imagenes\tpg.png"

        # Cargar la imagen con PIL
        img = Image.open(ruta_logo)
        # Cambiar el tamaño si es necesario
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)

        # Crear Label con la imagen
        logo_label = tk.Label(self.main_frame, image=self.logo, bg="white")
        logo_label.pack(pady=20)  # Espaciado alrededor del logotipo


if __name__ == "__main__":
    root = tk.Tk()
    app = ActasApp(root)
    root.mainloop()
