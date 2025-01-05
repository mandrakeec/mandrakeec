import os
import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
import openpyxl
from openpyxl.styles import Font  # Importar Font para aplicar estilo de negrita

# Configuración inicial de la base de datos


def create_database():
    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Inventario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Equipo TEXT, Marca TEXT, Modelo TEXT, Caracteristicas TEXT,
                        Serie TEXT, Estado TEXT, Usuario TEXT, Departamento TEXT,
                        Jefe_Area TEXT, Ubicacion TEXT)''')
    conn.commit()
    conn.close()

# Función para mostrar los datos en la tabla


def fetch_data():
    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inventario")
    rows = cursor.fetchall()
    inventory_table.delete(*inventory_table.get_children())
    for row in rows:
        inventory_table.insert('', END, values=row)
    conn.close()

# Función para agregar un registro


def add_record():
    if equipo_var.get() == "" or marca_var.get() == "" or estado_var.get() == "":
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    data = (equipo_var.get(), marca_var.get(), modelo_var.get(), caracteristicas_var.get(),
            serie_var.get(), estado_var.get(), usuario_var.get(), departamento_var.get(),
            jefe_area_var.get(), ubicacion_var.get())
    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Inventario (Equipo, Marca, Modelo, Caracteristicas, Serie, Estado, Usuario, Departamento, Jefe_Area, Ubicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    fetch_data()
    clear_form()

# Función para actualizar un registro


def update_record():
    if selected_id is None:
        messagebox.showerror("Error", "Selecciona un registro para actualizar")
        return
    data = (equipo_var.get(), marca_var.get(), modelo_var.get(), caracteristicas_var.get(),
            serie_var.get(), estado_var.get(), usuario_var.get(), departamento_var.get(),
            jefe_area_var.get(), ubicacion_var.get(), selected_id)
    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE Inventario SET Equipo=?, Marca=?, Modelo=?, Caracteristicas=?, 
                      Serie=?, Estado=?, Usuario=?, Departamento=?, Jefe_Area=?, Ubicacion=? 
                      WHERE id=?''', data)
    conn.commit()
    conn.close()
    fetch_data()
    clear_form()

# Función para eliminar un registro


def delete_record():
    global selected_id
    if selected_id is None:
        messagebox.showerror("Error", "Selecciona un registro para eliminar")
        return
    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Inventario WHERE id=?", (selected_id,))
    conn.commit()
    conn.close()
    fetch_data()
    clear_form()

# Función para limpiar el formulario


def clear_form():
    global selected_id
    selected_id = None
    equipo_var.set("")
    marca_var.set("")
    modelo_var.set("")
    caracteristicas_var.set("")
    serie_var.set("")
    estado_var.set("")
    usuario_var.set("")
    departamento_var.set("")
    jefe_area_var.set("")
    ubicacion_var.set("")

# Función para exportar a Excel


def export_to_excel():
    # Obtener la ruta de Descargas del usuario
    download_path = os.path.join(os.path.expanduser(
        "~"), "Downloads", "Inventario_Exportado.xlsx")

    conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inventario")
    records = cursor.fetchall()

    # Crear y rellenar el archivo de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    headers = ["ID", "Equipo", "Marca", "Modelo", "Características",
               "Serie", "Estado", "Usuario", "Departamento", "Jefe Área", "Ubicación"]
    sheet.append(headers)

    # Aplicar negrita a los encabezados
    # La fila de encabezado es la primera fila (sheet[1])
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    # Insertar los registros
    for row in records:
        sheet.append(row)

    # Guardar el archivo en la carpeta de Descargas
    workbook.save(download_path)
    messagebox.showinfo("Exportación", f"Datos exportados a {
                        download_path} con éxito.")

    conn.close()

# def export_to_excel():
#     conn = sqlite3.connect(r'C:\Sistemas Soporte\Base_Datos\soporte.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Inventario")
#     records = cursor.fetchall()
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active
#     headers = ["ID", "Equipo", "Marca", "Modelo", "Características",
#                "Serie", "Estado", "Usuario", "Departamento", "Jefe Área", "Ubicación"]
#     sheet.append(headers)
#     for row in records:
#         sheet.append(row)
#     workbook.save("C:/inventario/Inventario_Exportado.xlsx")
#     messagebox.showinfo(
#         "Exportación", "Datos exportados a Inventario_Exportado.xlsx con éxito.")
#     conn.close()

# Función para cargar datos en el formulario al hacer doble clic en un registro


def load_data(event):
    global selected_id
    selected = inventory_table.focus()
    values = inventory_table.item(selected, 'values')
    if values:
        selected_id = values[0]
        equipo_var.set(values[1])
        marca_var.set(values[2])
        modelo_var.set(values[3])
        caracteristicas_var.set(values[4])
        serie_var.set(values[5])
        estado_var.set(values[6])
        usuario_var.set(values[7])
        departamento_var.set(values[8])
        jefe_area_var.set(values[9])
        ubicacion_var.set(values[10])


# Crear GUI con Tkinterf
root = Tk()
root.title("Inventario de Equipos Informáticos")
root.geometry("1100x650")
root.resizable(False, False)
root.config(bg="#f5f5f5")  # Fondo gris claro para una apariencia limpia

# Variables de entrada
equipo_var = StringVar()
marca_var = StringVar()
modelo_var = StringVar()
caracteristicas_var = StringVar()
serie_var = StringVar()
estado_var = StringVar()
usuario_var = StringVar()
departamento_var = StringVar()
jefe_area_var = StringVar()
ubicacion_var = StringVar()

# Variable para guardar el ID del registro seleccionado
selected_id = None

# Colores y estilo
estilo_boton = {'font': ('Arial', 10, 'bold'),
                'bg': '#4CAF50', 'fg': 'white', 'width': 15}
estilo_label = {'bg': '#f5f5f5', 'font': ('Arial', 10, 'bold')}
estilo_entry = {'width': 25, 'font': ('Arial', 10)}

# Layout del formulario
Label(root, text="Equipo", **estilo_label).grid(row=0, column=0, padx=10, pady=10)
Entry(root, textvariable=equipo_var, **estilo_entry).grid(row=0, column=1)
Label(root, text="Marca", **estilo_label).grid(row=0, column=2, padx=10, pady=10)
Entry(root, textvariable=marca_var, **estilo_entry).grid(row=0, column=3)
Label(root, text="Modelo", **estilo_label).grid(row=1, column=0, padx=10, pady=10)
Entry(root, textvariable=modelo_var, **estilo_entry).grid(row=1, column=1)
Label(root, text="Características", **
      estilo_label).grid(row=1, column=2, padx=10, pady=10)
Entry(root, textvariable=caracteristicas_var,
      **estilo_entry).grid(row=1, column=3)
Label(root, text="Serie", **estilo_label).grid(row=2, column=0, padx=10, pady=10)
Entry(root, textvariable=serie_var, **estilo_entry).grid(row=2, column=1)
Label(root, text="Estado", **estilo_label).grid(row=2, column=2, padx=10, pady=10)
estado_listbox = ttk.Combobox(root, textvariable=estado_var, values=[
                              "Activo", "Bodega", "Dado de Baja", "Reparación", "Traspaso", "Backup"], width=23)
estado_listbox.grid(row=2, column=3)
Label(root, text="Usuario", **estilo_label).grid(row=3, column=0, padx=10, pady=10)
Entry(root, textvariable=usuario_var, **estilo_entry).grid(row=3, column=1)
Label(root, text="Departamento", **
      estilo_label).grid(row=3, column=2, padx=10, pady=10)
Entry(root, textvariable=departamento_var,
      **estilo_entry).grid(row=3, column=3)
Label(root, text="Jefe Área", **estilo_label).grid(row=4,
                                                   column=0, padx=10, pady=10)
Entry(root, textvariable=jefe_area_var, **estilo_entry).grid(row=4, column=1)
Label(root, text="Ubicación", **estilo_label).grid(row=4,
                                                   column=2, padx=10, pady=10)
Entry(root, textvariable=ubicacion_var, **estilo_entry).grid(row=4, column=3)

# Botones
Button(root, text="Agregar", command=add_record, **
       estilo_boton).grid(row=5, column=0, pady=20)
Button(root, text="Actualizar", command=update_record,
       **estilo_boton).grid(row=5, column=1)
Button(root, text="Eliminar", command=delete_record,
       **estilo_boton).grid(row=5, column=2)
Button(root, text="Exportar a Excel", command=export_to_excel,
       **estilo_boton).grid(row=5, column=3)

# Configuración de las barras de desplazamiento
frame_table = Frame(root)
frame_table.grid(row=6, column=0, columnspan=4, pady=10)
scroll_x = Scrollbar(frame_table, orient=HORIZONTAL)
scroll_y = Scrollbar(frame_table, orient=VERTICAL)
inventory_table = ttk.Treeview(frame_table, columns=("ID", "Equipo", "Marca", "Modelo", "Características", "Serie", "Estado",
                               "Usuario", "Departamento", "Jefe Área", "Ubicación"), xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.config(command=inventory_table.xview)
scroll_y.config(command=inventory_table.yview)

# Configuración de las columnas de la tabla
inventory_table.heading("ID", text="ID")
inventory_table.heading("Equipo", text="Equipo")
inventory_table.heading("Marca", text="Marca")
inventory_table.heading("Modelo", text="Modelo")
inventory_table.heading("Características", text="Características")
inventory_table.heading("Serie", text="Serie")
inventory_table.heading("Estado", text="Estado")
inventory_table.heading("Usuario", text="Usuario")
inventory_table.heading("Departamento", text="Departamento")
inventory_table.heading("Jefe Área", text="Jefe Área")
inventory_table.heading("Ubicación", text="Ubicación")
inventory_table['show'] = 'headings'

for col in inventory_table["columns"]:
    inventory_table.column(col, width=100)

inventory_table.pack(fill=BOTH, expand=True)
inventory_table.bind("<Double-1>", load_data)

# Crear la base de datos y cargar los datos iniciales
create_database()
fetch_data()

root.mainloop()
