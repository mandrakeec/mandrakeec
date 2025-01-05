import os
import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import ast
import logging
##################### SE AGREGO PARA PROBAR PONER EN NEGRITA RECIBE: ENTREGA:###############
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from tkinter import Checkbutton, IntVar, Text
from tkinter import Menu
import subprocess
#####################


################ PROGRAMA REALIZADO POR: MANDRAKE.EC, CON AYUDA DE CHATGPT################
# --- Configuración de Directorios ---
# BASE_DIR = r"C:\Sistemas Soporte\Base_Datos"
# PDF_DIR = r"C:\Sistemas Soporte\Pdf"
# PY_DIR = r"C:\Sistemas Soporte\Py"
# # En esta Carpeta debe ir la imagen de membrete con nombre membrete.png
# IMAGES_DIR = r"C:\Sistemas Soporte\Imagenes"

# --- Configuración de Directorios ---
BASE_DIR = r"Y:\Base_Datos"
PDF_DIR = r"Y:\Pdf"
PY_DIR = r"Y:\Py"
# En esta Carpeta debe ir la imagen de membrete con nombre membrete.png
IMAGES_DIR = r"Y:\Imagenes"

# # Crear directorios si no existen
# os.makedirs(BASE_DIR, exist_ok=True)
# os.makedirs(PDF_DIR, exist_ok=True)
# os.makedirs(PY_DIR, exist_ok=True)
# os.makedirs(IMAGES_DIR, exist_ok=True)

# --- Configuración de la Base de Datos ---
# DB_PATH = os.path.join(BASE_DIR, "soporte.db")
DB_PATH = r'Y:\Base_Datos\soporte.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crea Tabla de Actas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            fecha TEXT,
            recibe TEXT,
            entrega TEXT,
            descripcion TEXT,
            items TEXT,
            firma_entrega TEXT,
            firma_recibe TEXT,
            departamento_entrega TEXT,
            departamento_recibe TEXT,
            nota TEXT
        )
    ''')
    # Tabla para el historial de borrado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Historial_Actas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Acta_ID INTEGER NOT NULL,
            Usuario TEXT NOT NULL,
            Hora_Ingreso TEXT NOT NULL,
            Hora_Borrado TEXT NOT NULL,
            FOREIGN KEY (Acta_ID) REFERENCES Actas(ID)
        )
    ''')

    # Tabla de Usuarios para Autenticación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Crear un usuario por defecto si no existe
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))

    conn.commit()
    conn.close()


init_db()

# --- Ventana de Inicio de Sesión ---


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Inicio de Sesión")
        self.master.geometry("300x200")
        self.master.resizable(False, False)

        # Etiquetas y Campos de Entrada
        Label(master, text="Nombre de Usuario:",
              font=("Arial", 12)).pack(pady=10)
        self.username_entry = Entry(master, width=30)
        self.username_entry.pack()
        self.username_entry.focus()  # Aquí se establece el Focus automáticamente

        # Etiqueta y entrada para la contraseña
        Label(master, text="Contraseña:", font=("Arial", 12)).pack(pady=10)
        self.password_entry = Entry(master, width=30, show="*")
        self.password_entry.pack()

        # Botón de Inicio de Sesión
        Button(master, text="Iniciar Sesión", command=self.login,
               bg="blue", fg="white", font=("Arial", 12)).pack(pady=20)
        # Vincular la tecla Enter al método login
        master.bind('<Return>', lambda event: self.login())

    ############# SE MODIFICO PARA QUE APAREZCA MENSAJE DE BIENVENIDA #####################
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Error", "Por favor, ingrese usuario y contraseña.")
            return

        # Usar función de verificación de usuario
        if self.verify_user(username, password):
            # Mensaje de bienvenida antes de abrir la aplicación principal
            messagebox.showinfo("Bienvenida", f"¡Bienvenido/a, {username}!")
            self.master.destroy()  # Cierra la ventana de login
            root = Tk()
            # Aquí carga tu aplicación principal
            app = ActasApp(root, username)
            # Vincular la tecla Enter al botón de iniciar sesión
            root.bind('<Return>', lambda event: login_app())
            root.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def verify_user(self, username, password):
        """Verifica el usuario contra la base de datos"""

        try:
            # Usar "with" para asegurarte de que la conexión se cierre automáticamente
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                # Verifica las credenciales en la base de datos (sin cifrado de contraseña)
                cursor.execute(
                    "SELECT password FROM users WHERE username = ?", (username,))
                # "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                user = cursor.fetchone()
                return user is not None  # Retorna True si el usuario es válido

        except sqlite3.Error as e:
            # Manejamos posibles errores de conexión con la base de datos
            messagebox.showerror("Error de base de datos",
                                 f"Se produjo un error: {e}")
            return False
    ############# FIN APAREZCA MENSAJE DE BIENVENIDA Y FOCUS PROMPT #####################


# --- Aplicación Principal ---


class ActasApp:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual  # Guarda el usuario que inició sesión
        self.root.title("Sistemas de Soporte TPG")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Menú Principal
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        ######## FUNCION PARA ABRIR OTROS .py  ###########

        def abrir_notas():
            # notas_script = r"C:\Sistemas Soporte\Py\notas.py"
            notas_script = r"Y:\\Py\\notas.py"
    # Ejecutar notas.py en segundo plano sin mostrar consola
            subprocess.Popen(
                ["python", notas_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
    # Ejecutar borrar_log_DISV.py en segundo plano sin mostrar consola

        def eliminar_logs_disv():
            # pass
            # eliminar_logs_disv_script = r"C:\Sistemas Soporte\Py\borrar_log_disv.py"
            eliminar_logs_disv_script = r"Y:\\Py\\borrar_log_disv.py"
            subprocess.Popen(
                ["python", eliminar_logs_disv_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
    # Ejecutar borrar_log_transp.py en segundo plano sin mostrar consola

        def eliminar_logs_transp():
            # pass
            # eliminar_logs_transp_script = r"C:\Sistemas Soporte\Py\borrar_log_transp.py"
            eliminar_logs_transp_script = r"Y:\\Py\\borrar_log_transp.py"
            subprocess.Popen(
                ["python", eliminar_logs_transp_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

    # Ejecutar eliminar_placa.py en segundo plano sin mostrar consola
        def eliminar_placa():
            # pass
            # eliminar_placa_script = r"C:\Sistemas Soporte\Py\eliminar_placa.py"
            eliminar_placa_script = r"Y:\\Py\\eliminar_placa.py"
            subprocess.Popen(
                ["python", eliminar_placa_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

    # Ejecutar reiniciar_camaras.py en segundo plano sin mostrar consola
        def reiniciar_camaras():
            # pass
            # reiniciar_camaras_script = r"C:\Sistemas Soporte\Py\reiniciar_camaras.py"
            reiniciar_camaras_script = r"Y:\\Py\\reiniciar_camaras.py"
            subprocess.Popen(
                ["python", reiniciar_camaras_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

    # Ejecutar inventario.py en segundo plano sin mostrar consola
        def inventario():
            # pass
            # inventario_script = r"C:\Sistemas Soporte\Py\inventario.py"
            inventario_script = r"Y:\\Py\\inventario.py"
            subprocess.Popen(
                ["python", inventario_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

    # Ejecutar informes.py en segundo plano sin mostrar consola
        def informes():
            # pass
            # informes_script = r"C:\Sistemas Soporte\Py\informes.py"
            informes_script = r"Y:\\Py\\informes.py"
            subprocess.Popen(
                ["python", informes_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        ######## FIN NOTAS ##########
        # MENU ACTAS
        acta_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actas", menu=acta_menu)
        acta_menu.add_command(label="Ingresar Nueva Acta",
                              command=self.ingresar_acta)
        acta_menu.add_command(label="Consultar Actas",
                              command=self.consultar_actas)
        acta_menu.add_command(label="Modificar Acta",
                              command=self.modificar_acta)  # Nueva opción
        acta_menu.add_command(label="Eliminar Actas",
                              command=self.eliminar_actas)
        acta_menu.add_command(label="Imprimir Actas",
                              command=self.imprimir_actas)

        ######### Menú de Opciones #############
        # Menú "Opciones" dentro del menú de Actas
        menu_opciones = Menu(menubar, tearoff=0)
        # Agregar "Opciones" al menú principal
        menubar.add_cascade(label="Opciones", menu=menu_opciones)
        menu_opciones.add_command(label="Notas", command=abrir_notas)
        menu_opciones.add_command(
            label="Eliminar Logs DISV", command=eliminar_logs_disv)
        menu_opciones.add_command(
            label="Eliminar Logs Transp", command=eliminar_logs_transp)
        menu_opciones.add_command(
            label="Eliminar Placa", command=eliminar_placa)
        menu_opciones.add_command(
            label="Reiniciar Camaras", command=reiniciar_camaras)
        menu_opciones.add_command(
            label="Inventario", command=inventario)
        menu_opciones.add_command(
            label="Informes", command=informes)

        # Configurar el menú en la ventana principal
        root.config(menu=menubar)
        ##########################################

    def ingresar_acta(self):
        IngresarActaWindow(self.root)

    def consultar_actas(self):
        ConsultarActasWindow(self.root)

    def modificar_acta(self):
        ModificarActasWindow(self.root)  # Llamar a la nueva ventana

    def eliminar_actas(self):
        EliminarActasWindow(self.root, self.usuario_actual)

    def imprimir_actas(self):
        ImprimirActasWindow(self.root)

# --- Ventana para Ingresar Nueva Acta ---


class IngresarActaWindow:
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Ingresar Nueva Acta")
        self.top.geometry("1200x700")
        self.top.resizable(False, False)

        # En la configuración de tu ventana principal
        self.incluir_nota_var = IntVar()

        # Campos de Acta
        Label(self.top, text="Recibe:", font=("Arial", 12)).grid(
            row=0, column=0, padx=10, pady=5, sticky=E)
        self.recibe_entry = Entry(self.top, width=50)
        self.recibe_entry.grid(row=0, column=1, padx=10, pady=5)
        self.recibe_entry.focus()  # Aquí se establece el Focus automáticamente

        Label(self.top, text="Entrega:", font=("Arial", 12)).grid(
            row=1, column=0, padx=10, pady=5, sticky=E)
        self.entrega_entry = Entry(self.top, width=50)
        self.entrega_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(self.top, text="Descripción:", font=("Arial", 12)).grid(
            row=2, column=0, padx=10, pady=5, sticky=NE)
        self.descripcion_text = Text(self.top, width=38, height=4)
        self.descripcion_text.grid(row=2, column=1, padx=10, pady=5)

        ############ AGREGANDO CAMPOS DPTO.##########################
        # Dentro del formulario de ingreso
        Label(self.top, text="Departamento Entrega:", font=("Arial", 12)).grid(
            row=0, column=2, padx=10, pady=5, sticky=E)
        self.departamento_entrega_entry = Entry(self.top, width=30)
        self.departamento_entrega_entry.grid(row=0, column=3, padx=10, pady=5)

        Label(self.top, text="Departamento Recibe:", font=("Arial", 12)).grid(
            row=1, column=2, padx=10, pady=5, sticky=E)
        self.departamento_recibe_entry = Entry(self.top, width=30)
        self.departamento_recibe_entry.grid(row=1, column=3, padx=10, pady=5)

        #############################################################
        # Tabla de Items
        columns = ("Item", "Tipo", "Marca", "Modelo", "Serie", "Estado")
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        # Botones para agregar y eliminar items
        btn_frame = Frame(self.top)
        btn_frame.grid(row=4, column=1, columnspan=2, pady=5)

        Button(btn_frame, text="Agregar Item", command=self.agregar_item,
               bg="blue", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Eliminar Item", command=self.eliminar_item,
               bg="red", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)

        # Firmas
        Label(self.top, text="Firma Entrega (opcional):", font=("Arial", 12)).grid(
            row=5, column=1, padx=10, pady=5, sticky=E)
        self.firma_entrega_path = StringVar()
        Entry(self.top, textvariable=self.firma_entrega_path, width=40).grid(
            row=5, column=2, padx=10, pady=5, sticky=W)
        Button(self.top, text="Cargar Firma", command=self.cargar_firma_entrega, bg="gray",
               fg="white", font=("Arial", 10)).grid(row=5, column=2, padx=10, pady=5, sticky=E)

        Label(self.top, text="Firma Recibe (opcional):", font=("Arial", 12)).grid(
            row=6, column=1, padx=10, pady=5, sticky=E)
        self.firma_recibe_path = StringVar()
        Entry(self.top, textvariable=self.firma_recibe_path, width=40).grid(
            row=6, column=2, padx=10, pady=5, sticky=W)
        Button(self.top, text="Cargar Firma", command=self.cargar_firma_recibe, bg="gray",
               fg="white", font=("Arial", 10)).grid(row=6, column=2, padx=10, pady=5, sticky=E)

        # Botón para guardar acta
        Button(self.top, text="Guardar Acta", command=self.guardar_acta, bg="green",
               fg="white", font=("Arial", 12)).grid(row=7, column=1, columnspan=2, pady=20)
########################### AGREGANDO NOTAS #################################
        # Checkbutton para activar/desactivar la inclusión de la nota
        self.nota_check = Checkbutton(
            self.top, text="Incluir Nota u Observación",
            variable=self.incluir_nota_var, command=self.toggle_nota
        )
        self.nota_check.grid(row=4, column=3, padx=10,
                             pady=5, sticky="w")

        Label(self.top, text="Observación:", font=("Arial", 12)).grid(
            row=2, column=2, padx=10, pady=5, sticky=NE)
        self.nota_text = Text(self.top, width=38, height=4, state='disabled')
        self.nota_text.grid(row=2, column=3, padx=10, pady=5)

    def toggle_nota(self):
        # Habilitar o deshabilitar el cuadro de texto según el estado del Checkbutton
        if self.incluir_nota_var.get() == 1:
            self.nota_text.config(state='normal')
        else:
            self.nota_text.config(state='disabled')

######################## AGREGANDO NOTAS #################################

    def agregar_item(self):
        AgregarItemWindow(self)

    def eliminar_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
        else:
            messagebox.showwarning(
                "Advertencia", "Selecciona un item para eliminar.")

    def cargar_firma_entrega(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Firma Entrega",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            self.firma_entrega_path.set(file_path)

    def cargar_firma_recibe(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Firma Recibe",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            self.firma_recibe_path.set(file_path)

    def guardar_acta(self):
        recibe = self.recibe_entry.get().strip()
        entrega = self.entrega_entry.get().strip()
        descripcion = self.descripcion_text.get("1.0", END).strip()
        #############################################
        departamento_entrega = self.departamento_entrega_entry.get().strip()
        departamento_recibe = self.departamento_recibe_entry.get().strip()
        nota = self.nota_text.get("1.0", END).strip(
        ) if self.incluir_nota_var.get() == 1 else ""
        #############################################

        items = []
        for child in self.tree.get_children():
            items.append(self.tree.item(child)["values"])

        if not recibe or not entrega or not descripcion or not items:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Generar numeración única
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM actas WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (year, month))
            count = cursor.fetchone()[0] + 1
            numero = f"{year}-{month}-{str(count).zfill(3)}"

    # Obtener fecha actual
            fecha = now.strftime("%Y-%m-%d  %H:%M:%S")

            # Guardar firmas
            firma_entrega = ""
            firma_recibe = ""
            if self.firma_entrega_path.get():
                firma_entrega = self.guardar_imagen(
                    self.firma_entrega_path.get())

            if self.firma_recibe_path.get():
                firma_recibe = self.guardar_imagen(
                    self.firma_recibe_path.get())

            # Guardar en base de datos
            cursor.execute('''
                INSERT INTO actas (numero, fecha, recibe, entrega, descripcion, items, firma_entrega, firma_recibe, departamento_entrega, departamento_recibe,nota)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            ''', (
                numero,
                fecha,
                recibe,
                entrega,
                descripcion,
                str(items),
                firma_entrega,
                firma_recibe,
                departamento_entrega,
                departamento_recibe,
                nota
            ))
            conn.commit()
            messagebox.showinfo(
                "Éxito", f"Acta {numero} guardada exitosamente.")
            self.top.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error", "El número de acta generado ya existe. Intenta guardar nuevamente.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al guardar el acta: {e}")
        finally:
            conn.close()

    def guardar_imagen(self, path):
        filename = os.path.basename(path)
        dest_path = os.path.join(IMAGES_DIR, filename)
        try:
            with open(path, 'rb') as fsrc:
                with open(dest_path, 'wb') as fdst:
                    fdst.write(fsrc.read())
            return dest_path
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")
            return ""

# --- Ventana para Agregar Items ---


class AgregarItemWindow:
    def __init__(self, parent):
        self.parent = parent
        self.top = Toplevel(parent.top)
        self.top.title("Agregar Item")
        self.top.geometry("400x350")
        self.top.resizable(False, False)

        Label(self.top, text="Item:", font=("Arial", 12)).grid(
            row=0, column=0, padx=20, pady=5, sticky=E)
        self.item_entry = Entry(self.top, width=40)
        self.item_entry.grid(row=0, column=1, padx=10, pady=5)
        self.item_entry.focus()  # Aquí se establece el Focus automáticamente

        Label(self.top, text="Tipo:", font=("Arial", 12)).grid(
            row=1, column=0, padx=10, pady=5, sticky=E)
        self.tipo_entry = Entry(self.top, width=40)
        self.tipo_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(self.top, text="Marca:", font=("Arial", 12)).grid(
            row=2, column=0, padx=10, pady=5, sticky=E)
        self.marca_entry = Entry(self.top, width=40)
        self.marca_entry.grid(row=2, column=1, padx=10, pady=5)

        Label(self.top, text="Modelo:", font=("Arial", 12)).grid(
            row=3, column=0, padx=10, pady=5, sticky=E)
        self.modelo_entry = Entry(self.top, width=40)
        self.modelo_entry.grid(row=3, column=1, padx=10, pady=5)

        Label(self.top, text="Serie:", font=("Arial", 12)).grid(
            row=4, column=0, padx=10, pady=5, sticky=E)
        self.serie_entry = Entry(self.top, width=40)
        self.serie_entry.grid(row=4, column=1, padx=10, pady=5)

        Label(self.top, text="Estado:", font=("Arial", 12)).grid(
            row=5, column=0, padx=10, pady=5, sticky=E)
        self.estado_entry = Entry(self.top, width=40)
        self.estado_entry.grid(row=5, column=1, padx=10, pady=5)

        Button(self.top, text="Agregar", command=self.agregar, bg="blue", fg="white", font=(
            "Arial", 12)).grid(row=6, column=1, columnspan=2, pady=20)

    def agregar(self):
        item = self.item_entry.get().strip()
        tipo = self.tipo_entry.get().strip()
        marca = self.marca_entry.get().strip()
        modelo = self.modelo_entry.get().strip()
        serie = self.serie_entry.get().strip()
        estado = self.estado_entry.get().strip()

        if not all([item, tipo, marca, modelo, serie, estado]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        self.parent.tree.insert('', END, values=(
            item, tipo, marca, modelo, serie, estado))
        self.top.destroy()

# --- Ventana para Consultar Actas ---


class ConsultarActasWindow:
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Consultar Actas")
        self.top.geometry("900x600")
        self.top.resizable(False, False)

        # Barra de búsqueda
        search_frame = Frame(self.top)
        search_frame.pack(pady=10)

        Label(search_frame, text="Buscar por Número:",
              font=("Arial", 12)).pack(side=LEFT, padx=5)
        self.search_var = StringVar()

        Entry(search_frame, textvariable=self.search_var,
              width=30).pack(side=LEFT, padx=5)
        Button(search_frame, text="Buscar", command=self.buscar_actas,
               bg="orange", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)
        Button(search_frame, text="Mostrar Todas", command=self.cargar_actas,
               bg="gray", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)

        # Tabla de Actas
        columns = ("Número", "Fecha", "Recibe", "Entrega", "Descripción")
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.tree, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.cargar_actas()

    def cargar_actas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT numero, fecha, recibe, entrega, descripcion, departamento_entrega, departamento_recibe, nota FROM actas")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert('', END, values=row)
        conn.close()

    def buscar_actas(self):
        numero = self.search_var.get().strip()
        if not numero:
            messagebox.showwarning(
                "Advertencia", "Ingrese un número para buscar.")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT numero, fecha, recibe, entrega, descripcion FROM actas WHERE numero LIKE ?", ('%' + numero + '%',))
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                self.tree.insert('', END, values=row)
        else:
            messagebox.showinfo(
                "Información", "No se encontraron actas con ese número.")
        conn.close()

# --- Ventana para Modificar Actas ---


class ModificarActasWindow:
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Modificar Acta")
        self.top.geometry("800x800")
        self.top.resizable(False, False)

        # Estilos de fuentes
        LabelFont = ("Arial", 12, "bold")
        EntryFont = ("Arial", 12)

        # Frame para buscar acta
        buscar_frame = Frame(self.top, padx=20, pady=20)
        buscar_frame.pack(fill=X)

        Label(buscar_frame, text="Número de Acta:", font=LabelFont).grid(
            row=0, column=0, sticky=W, pady=5)
        self.numero_entry = Entry(buscar_frame, font=EntryFont, width=30)
        self.numero_entry.grid(row=0, column=1, pady=5, padx=10)
        self.numero_entry.focus()  # Aquí se establece el Focus automáticamente

        Button(buscar_frame, text="Buscar", command=self.buscar_acta, bg="#4CAF50",
               fg="white", font=("Arial", 12)).grid(row=0, column=2, pady=5, padx=10)

        # Frame para mostrar y editar detalles
        self.detalles_frame = Frame(self.top, padx=20, pady=20)
        self.detalles_frame.pack(fill=BOTH, expand=True)
        self.detalles_frame.pack_forget()  # Ocultar inicialmente

    def buscar_acta(self):
        numero = self.numero_entry.get().strip()

        if not numero:
            messagebox.showwarning(
                "Advertencia", "Por favor, ingresa un número de acta.")
            return

        # Obtener datos de la acta
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actas WHERE numero = ?", (numero,))
        acta = cursor.fetchone()
        conn.close()

        if not acta:
            messagebox.showerror("Error", "Acta no encontrada.")
            return

        # Mostrar los campos para editar
        self.detalles_frame.pack(fill=BOTH, expand=True)

        # Limpiar el frame si ya tenía widgets
        for widget in self.detalles_frame.winfo_children():
            widget.destroy()

        # Crear Labels y Entrys organizados en grid
        fields = ["Fecha (YYYY-MM-DD):", "Recibe:", "Entrega:", "Descripción:"]
        self.entries = {}

        for idx, field in enumerate(fields):
            Label(self.detalles_frame, text=field, font=("Arial", 12, "bold")).grid(
                row=idx, column=0, sticky=W, pady=10)
            if field.startswith("Descripción"):
                text_widget = Text(self.detalles_frame,
                                   height=5, width=50, font=("Arial", 12))
                text_widget.insert(END, acta[5])
                text_widget.grid(row=idx, column=1, pady=10, padx=10, sticky=W)
                self.entries[field] = text_widget
            else:
                entry = Entry(self.detalles_frame,
                              font=("Arial", 12), width=30)
                if field.startswith("Fecha"):
                    entry.insert(0, acta[2])
                elif field.startswith("Recibe"):
                    entry.insert(0, acta[3])
                elif field.startswith("Entrega"):
                    entry.insert(0, acta[4])
                elif field.startswith("departamento_entrega"):
                    entry.insert(0, acta[9])
                elif field.startswith("departamento_recibe"):
                    entry.insert(0, acta[10])
                elif field.startswith("nota"):
                    entry.insert(0, acta[11])
                entry.grid(row=idx, column=1, pady=10, padx=10, sticky=W)
                self.entries[field] = entry

        # Frame para gestionar los items
        items_label = Label(self.detalles_frame,
                            text="Items:", font=("Arial", 12, "bold"))
        items_label.grid(row=4, column=0, sticky=W, pady=10)

        # Frame que contiene la tabla y los botones
        items_frame = Frame(self.detalles_frame)
        items_frame.grid(row=4, column=1, pady=10, padx=10, sticky=W)

        # Crear la tabla (Treeview)
        columns = ("Item", "Tipo", "Marca", "Modelo", "Serie", "Estado")
        self.tree = ttk.Treeview(
            items_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=CENTER)
        self.tree.pack(side=LEFT)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(
            items_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=LEFT, fill=Y)

        # Botones para agregar, editar y eliminar items
        buttons_frame = Frame(self.detalles_frame)
        buttons_frame.grid(row=5, column=1, pady=10, padx=110, sticky=W)

        Button(buttons_frame, text="Agregar Item", command=self.agregar_item,
               bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Editar Item", command=self.editar_item,
               bg="#FFC107", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Eliminar Item", command=self.eliminar_item,
               bg="#F44336", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)

        # Cargar los items existentes en la tabla
        try:
            # Convertir de string a lista de Python
            items = ast.literal_eval(acta[6])
            if not isinstance(items, list):
                raise ValueError
        except:
            items = []
            messagebox.showwarning(
                "Advertencia", "No se pudieron cargar los items de la acta.")

        for item in items:
            if isinstance(item, list) and len(item) == 6:
                self.tree.insert('', END, values=item)
            else:
                messagebox.showwarning(
                    "Advertencia", f"Item con formato incorrecto: {item}")

        # Botón para guardar cambios
        Button(self.detalles_frame, text="Guardar Cambios", command=lambda: self.guardar_cambios(
            acta[1]), bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).grid(row=6, column=1, columnspan=2, pady=20)

    def agregar_item(self):
        self.abrir_dialogo_item()

    def editar_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Advertencia", "Selecciona un item para editar.")
            return
        item_values = self.tree.item(selected_item)['values']
        self.abrir_dialogo_item(item_values, selected_item)

    def eliminar_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Advertencia", "Selecciona un item para eliminar.")
            return
        self.tree.delete(selected_item)

    def abrir_dialogo_item(self, item_values=None, item_id=None):
        dialog = Toplevel(self.top)
        dialog.title("Agregar/Editar Item")
        dialog.geometry("450x400")
        dialog.resizable(False, False)

        # ESTE LABELFONT ES PARA FUENTE-TAMAÑO-TIPO
        LabelFont = ("Arial", 12)  # LabelFont = ("Arial", 12,"bold")
        EntryFont = ("Arial", 12)

        fields = ["Item", "Tipo", "Marca", "Modelo", "Serie", "Estado"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(dialog, text=f"{field}:", font=LabelFont).grid(
                row=idx, column=0, sticky=W, pady=10, padx=20)
            entry = Entry(dialog, font=EntryFont, width=30)
            entry.grid(row=idx, column=1, pady=10, padx=20)
            entries[field] = entry

        if item_values:
            for idx, field in enumerate(fields):
                entries[fields[idx]].insert(0, item_values[idx])

        def guardar():
            new_item = [entries[field].get().strip() for field in fields]
            if any(not value for value in new_item):
                messagebox.showwarning(
                    "Advertencia", "Por favor, completa todos los campos del item.")
                return
            if item_values and item_id:
                self.tree.item(item_id, values=new_item)
            else:
                self.tree.insert('', END, values=new_item)
            dialog.destroy()

        Button(dialog, text="Guardar", command=guardar, bg="#4CAF50", fg="white", font=(
            "Arial", 12)).grid(row=len(fields), column=1, columnspan=2, pady=20)

    def guardar_cambios(self, numero_original):
        fecha = self.entries["Fecha (YYYY-MM-DD):"].get().strip()
        recibe = self.entries["Recibe:"].get().strip()
        entrega = self.entries["Entrega:"].get().strip()
        descripcion = self.entries["Descripción:"].get("1.0", END).strip()
        items = []

        for child in self.tree.get_children():
            item = self.tree.item(child)['values']
            if len(item) != 6:
                messagebox.showwarning(
                    "Advertencia", f"Item con formato incorrecto: {item}")
                continue
            items.append(item)

        # Validación de campos
        if not fecha or not recibe or not entrega or not descripcion:
            messagebox.showwarning(
                "Advertencia", "Por favor, completa todos los campos obligatorios.")
            return

        # Validar formato de fecha
        try:
            # fecha = now.strftime("%Y-%m-%d  %H:%M:%S")
            datetime.strptime(fecha, '%Y-%m-%d  %H:%M:%S')
        except ValueError:
            messagebox.showerror(
                "Error", "El formato de la fecha es inválido. Usa YYYY-MM-DD.")
            return

        # Actualizar en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE actas
                SET fecha = ?, recibe = ?, entrega = ?, descripcion = ?, items = ?
                WHERE numero = ?
            """, (fecha, recibe, entrega, descripcion, str(items), numero_original))
            conn.commit()
            messagebox.showinfo("Éxito", "Acta actualizada exitosamente.")
            self.top.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al actualizar el acta: {e}")
        finally:
            conn.close()


# --- Ventana para Eliminar Actas ---

class EliminarActasWindow:
    def __init__(self, master, usuario_actual):
        self.usuario_actual = usuario_actual  # Almacena el usuario actual
        self.top = Toplevel(master)
        self.top.title("Eliminar Actas")
        self.top.geometry("900x600")
        self.top.resizable(False, False)

        # Tabla de Actas
        columns = ("ID", "Número", "Fecha", "Recibe", "Entrega")
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.top, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Botón Eliminar
        Button(
            self.top,
            text="Eliminar Seleccionado",
            command=self.eliminar_acta,
            bg="red",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=10)

        self.cargar_actas()

    def cargar_actas(self):
        """Carga todas las actas desde la base de datos en el TreeView."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero, fecha, recibe, entrega FROM actas")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert('', END, values=row)
        conn.close()

    def eliminar_acta(self):
        """Elimina el acta seleccionada y registra en Historial_Actas."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Advertencia", "Selecciona un acta para eliminar.")
            return

        item = self.tree.item(selected_item)
        acta_id = item['values'][0]
        numero = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirmar", f"¿Estás seguro de eliminar la acta {numero}?")
        if confirm:
            # Reemplazar con la lógica para obtener el usuario actual.
            # usuario_actual = "Usuario_Actual"
            hora_borrado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Obtener la hora de ingreso del acta antes de eliminarla
            cursor.execute("SELECT fecha FROM actas WHERE id = ?", (acta_id,))
            hora_ingreso = cursor.fetchone()

            if hora_ingreso:
                hora_ingreso = hora_ingreso[0]  # Obtener la fecha como string

                # Registrar en la tabla Historial_Actas
                cursor.execute('''
                   INSERT INTO historial_actas (acta_id, Usuario, hora_ingreso, hora_borrado)
                    VALUES (?, ?, ?, ?)
                ''', (acta_id, self.usuario_actual, hora_ingreso, hora_borrado))

                #     INSERT INTO Historial_Actas (Acta_ID, Usuario, Hora_Ingreso, Hora_Borrado)
                #     VALUES (?, ?, ?, ?)
                # ''', (acta_id, usuario_actual, hora_ingreso, hora_borrado))

            # Eliminar el acta
            cursor.execute("DELETE FROM actas WHERE id = ?", (acta_id,))
            conn.commit()
            conn.close()

            # Eliminar del TreeView
            self.tree.delete(selected_item)
            messagebox.showinfo(
                "Éxito", f"Acta {numero} eliminada exitosamente.")
            self.cargar_actas()


# --- Ventana para Imprimir Actas ---


class ImprimirActasWindow:
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Imprimir Actas")
        self.top.geometry("900x600")
        self.top.resizable(False, False)
        self.incluir_nota_var = IntVar()

        # Tabla de Actas
        columns = ("Número", "Fecha", "Recibe", "Entrega")
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.tree, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.cargar_actas()

        Button(self.top, text="Imprimir Seleccionado", command=self.imprimir_acta,
               bg="purple", fg="white", font=("Arial", 12)).pack(pady=10)

    def cargar_actas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT numero, fecha, recibe, entrega, descripcion, items, firma_entrega, firma_recibe FROM actas")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert('', END, values=(row[0], row[1], row[2], row[3]))
        conn.close()

    def imprimir_acta(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Advertencia", "Selecciona una acta para imprimir.")
            return
        item = self.tree.item(selected_item)
        numero = item['values'][0]

        # Obtener datos de la acta
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actas WHERE numero = ?", (numero,))
        acta = cursor.fetchone()
        conn.close()

        if not acta:
            messagebox.showerror("Error", "Acta no encontrada.")
            return

        # Generar PDF
        pdf_path = os.path.join(PDF_DIR, f"Acta_Entrega {numero}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        nota = ""
        # Definir estilos para Paragraph
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleJ = ParagraphStyle(
            name='Justify',
            parent=styleN,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            fontSize=12,
            leading=15
        )
        # Verificar si se debe incluir la Nota *********** REVISAR EN CASA ESTE BLOQUE *********

        # Verificar si se debe incluir la Nota
        if self.incluir_nota_var.get() == 1:
            # Obtener el texto de la Nota
            nota = self.nota_text.get("1.0", "end").strip()
            if nota:  # Asegurarse de que la Nota no esté vacía
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "Nota u Observación:")
                y_position -= 20  # Mover hacia abajo para el texto
                c.setFont("Helvetica", 10)

                # Crear un objeto de texto para la Nota
                text_object = c.beginText(50, y_position)
                text_object.setFont("Helvetica", 10)
                text_object.setTextOrigin(50, y_position)

                # Añadir el texto de la Nota al PDF
                text_object.textLines(nota)

                # Dibujar el texto en el PDF
                c.drawText(text_object)

                # Ajustar la posición de y después de agregar el texto
                # Aproximación al espacio ocupado por las líneas
                y_position -= len(nota.split('\n')) * 12

        # if self.incluir_nota_var.get() == 1:
        #     # Obtener el texto de la Nota
        #     nota = self.nota_text.get("1.0", "end").strip()
        # if nota:
        #     c.setFont("Helvetica-Bold", 12)
        #     c.drawString(50, y_position, "Nota u Observación:")
        #     y_position -= 20
        #     c.setFont("Helvetica", 10)
        #     text_object = c.beginText(50, y_position)
        #     text_object.textLines(nota)  # Añadir el texto de la Nota al PDF
        #     c.drawText(text_object)

        ####################
        # Membrete
        membrete_path = os.path.join(IMAGES_DIR, "membrete.png")
        if os.path.exists(membrete_path):
            try:
                c.drawImage(membrete_path, 50, height - 150,
                            width=500, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo cargar el membrete: {e}")

        # Numeración y Fecha
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 150, f"Número: {acta[1]}")
        c.drawString(400, height - 150, f"Fecha: {acta[2]}")

        ####### CAMBIO EN CODIGO PARA PONER NEGRITA A RECIBE: ENTREGA: ########
        # Recibe y Entrega (Entrega debajo de Recibe)
        # Recibe en negrita y su texto normal
        c.setFont("Helvetica-Bold", 12)  # Negrita para "Recibe:"
        c.drawString(50, height - 170, "Recibe:")  # Texto "Recibe:" en negrita
        c.setFont("Helvetica", 12)  # Normal para el nombre que recibe
        c.drawString(110, height - 170, acta[3])  # El nombre del que recibe

        # Entrega en negrita y su texto normal
        c.setFont("Helvetica-Bold", 12)  # Negrita para "Entrega:"
        # Texto "Entrega:" en negrita
        c.drawString(50, height - 185, "Entrega:")
        c.setFont("Helvetica", 12)  # Normal para el nombre que entrega
        c.drawString(110, height - 185, acta[4])  # El nombre del que entrega
        ##############################################################################################

        # Descripción Negrita
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 210, "Descripción:")

        # Crear el objeto Paragraph para la descripción
        descripcion_para_pdf = Paragraph(
            acta[5].replace('\n', '<br/>'), styleJ)

        # Definir el ancho y la altura disponibles para el texto
        descripcion_width = 500  # Ancho de la caja de texto
        # Altura máxima (puedes ajustarlo dinámicamente si es necesario)
        descripcion_height = 150

        # Calcular la posición y dibujar el Paragraph
        descripcion_para_pdf.wrap(descripcion_width, descripcion_height)
        descripcion_para_pdf.drawOn(
            c, 50, height - 215 - descripcion_para_pdf.height)
        # ############### NOTA JUSTIFICADA INICIO ##################
        # Nota en Negrita
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 620, "Nota:")

        # Crear el objeto Paragraph para la Nota
        nota_para_pdf = Paragraph(
            acta[11].replace('\n', '<br/>'), styleJ)

        # Definir el ancho y la altura disponibles para el texto
        nota_width = 500  # Ancho de la caja de texto
        # Altura máxima (puedes ajustarlo dinámicamente si es necesario)
        nota_height = 150

        # Calcular la posición y dibujar el Paragraph texto de la nota
        nota_para_pdf.wrap(nota_width, nota_height)
        nota_para_pdf.drawOn(
            c, 50, height - 630 - nota_para_pdf.height)

        ############### NOTA JUSTIFICADA FIN ##################
        # Tabla de Items
        c.drawString(50, height - 270, "Items:")
        data = [["Item", "Tipo", "Marca", "Modelo", "Serie", "Estado"]]
        import ast
        try:
            items = ast.literal_eval(acta[6])
            for itm in items:
                data.append(itm)
        except:
            items = []
            messagebox.showwarning(
                "Advertencia", "No se pudieron cargar los items de la acta.")

        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors

        table = Table(data, colWidths=[30, 100, 80, 80, 140, 80])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        table.wrapOn(c, width, height)
        table_height = 20 * len(data)
        table.drawOn(c, 50, height - 280 - table_height)

        ################## SECCION FIRMAS ########################################
        # Posición fija para la firma en la parte inferior de la página
        y_position = 100  # Ajusta este valor según tu necesidad
        firma_width = 150  # Ancho de la firma para calcular el centro

        # Firma Entrega
        if acta[7]:
            try:
                c.drawImage(acta[7], 50, y_position - 150,
                            width=firma_width, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo cargar la firma de entrega: {e}")

        # Centrar el texto de "Firma Entrega", nombre y departamento
        c.setFont("Helvetica-Bold", 12)
        centro_entrega = 50 + (firma_width / 2)
        c.drawCentredString(centro_entrega, height - 730,
                            "Firma Entrega")  # Título centrado
        c.setFont("Helvetica", 12)
        c.drawCentredString(centro_entrega, height - 750,
                            acta[4])  # Nombre centrado
        c.drawCentredString(centro_entrega, height - 765,
                            acta[9])  # Departamento centrado

        # Firma Recibe
        if acta[8]:
            try:
                c.drawImage(acta[8], 380, y_position - 150,
                            width=firma_width, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo cargar la firma de recibe: {e}")

        # Centrar el texto de "Firma Recibe", nombre y departamento
        c.setFont("Helvetica-Bold", 12)
        centro_recibe = 380 + (firma_width / 2)
        c.drawCentredString(centro_recibe, height - 730,
                            "Firma Recibe")  # Título centrado
        c.setFont("Helvetica", 12)
        c.drawCentredString(centro_recibe, height - 750,
                            acta[3])  # Nombre centrado
        c.drawCentredString(centro_recibe, height - 765,
                            acta[10])  # Departamento centrado

        c.save()

        # Abrir automáticamente el PDF generado
        try:
            os.startfile(pdf_path)  # Funciona en Windows
        except AttributeError:
            # Para sistemas que no son Windows, se puede usar otro método
            import webbrowser
            webbrowser.open_new(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {e}")

        messagebox.showinfo(
            "Éxito", f"Acta {numero} impresa exitosamente en {pdf_path}.")


# --- Iniciar la Aplicación con la Ventana de Login ---
if __name__ == "__main__":
    login_root = Tk()
    login_app = LoginWindow(login_root)
    login_root.mainloop()
