import tkinter as tk
from tkinter import messagebox, ttk
import paramiko


def connect_to_server(ip, user, password):
    """
    Conecta al servidor remoto usando paramiko.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=password)
        return client
    except Exception as e:
        messagebox.showerror("Error de Conexión",
                             f"No se pudo conectar al servidor:\n{e}")
        return None


def execute_command(ip, user, password, command, success_msg, error_msg):
    """
    Ejecuta un comando remoto y muestra el resultado o un error.
    """
    client = connect_to_server(ip, user, password)
    if not client:
        return

    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            messagebox.showinfo(success_msg, output)
        elif errors:
            messagebox.showerror("Error", errors)
        else:
            messagebox.showinfo(success_msg, "Comando ejecutado con éxito.")
    finally:
        client.close()


def check_disk_space():
    """
    Verifica el espacio en disco en el servidor remoto.
    """
    ip = ip_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    command = "df -h"
    execute_command(ip, user, password, command, "Espacio en Disco",
                    "No se pudo obtener el espacio en disco.")


def list_logs():
    """
    Lista los archivos de logs en el servidor remoto.
    """
    ip = ip_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    command = "ls -lah /var/log/httpd/"
    execute_command(ip, user, password, command, "Archivos de Logs",
                    "No se pudo listar los archivos de logs.")


def delete_old_logs():
    """
    Elimina logs antiguos del servidor remoto.
    """
    ip = ip_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    command = "find /var/log/httpd/ -type f -name '*.log-*' -mtime +2 -exec rm -f {} \\;"
    execute_command(ip, user, password, command, "Eliminar Logs Antiguos",
                    "No se pudieron eliminar los logs antiguos.")


def delete_all_logs_and_restart_apache():
    """
    Elimina todos los logs y reinicia Apache en el servidor remoto.
    """
    ip = ip_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    command = "rm -f /var/log/httpd/* && service httpd restart"
    execute_command(ip, user, password, command, "Logs Eliminados y Apache Reiniciado",
                    "No se pudo realizar la operación.")


# Crear la ventana principal
root = tk.Tk()
root.title("***Log_DISV***")
root.geometry("320x300")
root.resizable(False, False)

# Estilo
style = ttk.Style()
style.configure("TButton", font=("Arial", 10))
style.configure("TLabel", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))

# Crear los widgets (etiquetas, campos de entrada y botones)
ttk.Label(root, text="IP del Servidor:").grid(
    row=0, column=0, padx=10, pady=5, sticky="w")
ip_entry = ttk.Entry(root, width=30)
ip_entry.grid(row=0, column=1, padx=10, pady=5)
ip_entry.insert(0, "192.168.0.222")
ip_entry.focus()

ttk.Label(root, text="Usuario:").grid(
    row=1, column=0, padx=10, pady=5, sticky="w")
user_entry = ttk.Entry(root, width=30)
user_entry.grid(row=1, column=1, padx=10, pady=5)
user_entry.insert(0, "root")

ttk.Label(root, text="Contraseña:").grid(
    row=2, column=0, padx=10, pady=5, sticky="w")
password_entry = ttk.Entry(root, width=30, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5)

# Botones para las operaciones
ttk.Button(root, text="Verificar Espacio en Disco", command=check_disk_space).grid(
    row=3, column=0, columnspan=2, padx=10, pady=10)

ttk.Button(root, text="Listar Archivos de Logs", command=list_logs).grid(
    row=4, column=0, columnspan=2, padx=10, pady=10)

ttk.Button(root, text="Eliminar Logs Antiguos", command=delete_old_logs).grid(
    row=5, column=0, columnspan=2, padx=10, pady=10)

ttk.Button(root, text="Eliminar Todos los Logs y Reiniciar Apache", command=delete_all_logs_and_restart_apache).grid(
    row=6, column=0, columnspan=2, padx=10, pady=10)

# Iniciar el bucle de eventos de Tkinter
root.mainloop()
