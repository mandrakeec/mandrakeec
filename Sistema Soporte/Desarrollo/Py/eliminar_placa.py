import tkinter as tk
from tkinter import messagebox
import socket
import json


def enviar_datos():
    accion = entry_accion.get()
    placa = entry_placa.get()

    if not accion or not placa:
        messagebox.showwarning(
            "Campos vacíos", "Por favor, rellena todos los campos.")
        return

    # Crear el JSON
    data = {
        "accion": accion,
        "placa": placa
    }
    json_data = json.dumps(data).encode('utf-8')

    try:
        # Conectar al servidor y enviar los datos
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('192.168.0.113', 9697))
            s.sendall(json_data)
            response = s.recv(1024)
            messagebox.showinfo("Respuesta del servidor",
                                response.decode('utf-8'))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")


# Configurar la ventana de Tkinter
root = tk.Tk()
root.title("Eliminar Placa")
root.geometry('250x100')

# Etiquetas y campos de entrada
tk.Label(root, text="Acción:").grid(row=0, column=0, padx=10, pady=5)
entry_accion = tk.Entry(root)
entry_accion.grid(row=0, column=1, padx=10, pady=5)
entry_accion.insert(0, "BORRA")

tk.Label(root, text="Placa:").grid(row=1, column=0, padx=10, pady=5)
entry_placa = tk.Entry(root)
entry_placa.grid(row=1, column=1, padx=10, pady=5)
entry_placa.focus()  # Aquí se establece el Focus automáticamente

# Botón para enviar datos
btn_enviar = tk.Button(root, text="Enviar",
                       command=enviar_datos, bg="blue", fg="white")
btn_enviar.grid(row=2, column=1, columnspan=2, pady=10)

# Ejecutar la aplicación
root.mainloop()
