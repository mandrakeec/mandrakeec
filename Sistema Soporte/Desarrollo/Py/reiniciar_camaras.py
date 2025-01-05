import paramiko
import tkinter as tk
from tkinter import messagebox

# Configuración de conexión SSH
HOST = '192.168.0.113'
PORT = 22
USER = 'root'


def connect_ssh(host, port, user, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=user, password=password)
    return ssh


def verify_process(ssh):
    command_check = 'pm2 ls'  # Comando para listar los procesos
    stdin, stdout, stderr = ssh.exec_command(command_check)
    output_check = stdout.read().decode()
    return output_check


def restart_process_by_id(ssh, process_id):
    command = f'pm2 restart {process_id}'
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    if errors:
        return f'Error al reiniciar el proceso: {errors}'
    else:
        return f'Proceso con ID {process_id} reiniciado exitosamente.'


def restart_cameras(password, progress_label, output_text):
    try:
        progress_label.config(text="Conectando a SSH...")
        ssh = connect_ssh(HOST, PORT, USER, password)

        process_id = 0  # ID del proceso que quieres reiniciar
        progress_label.config(text="Reiniciando el proceso...")
        result = restart_process_by_id(ssh, process_id)

        # Verificar el estado de los procesos
        output_check = verify_process(ssh)
        output_text.delete(1.0, tk.END)  # Limpiar el área de texto
        output_text.insert(tk.END, output_check)

        if str(process_id) in output_check:
            result += "\nProceso con ID 0 está en línea."
        else:
            result += "\nEl proceso con ID 0 no está en la lista de procesos."

        ssh.close()
        progress_label.config(text=result)
        return result
    except Exception as e:
        progress_label.config(text=f"Error: {e}")
        return f'Error: {e}'


def on_reiniciar_click(progress_label, output_text, password_entry):
    password = password_entry.get()

    if not password:  # Validar si la contraseña está vacía
        messagebox.showerror(
            "Error", "Por favor, ingresa la contraseña de root.")
        return

    progress_label.config(text="Iniciando reinicio...")
    result = restart_cameras(password, progress_label, output_text)
    messagebox.showinfo("Resultado", result)


def on_mostrar_click(progress_label, output_text, password_entry):
    password = password_entry.get()

    if not password:  # Validar si la contraseña está vacía
        messagebox.showerror(
            "Error", "Por favor, ingresa la contraseña de root.")
        return

    try:
        progress_label.config(text="Conectando a SSH...")
        ssh = connect_ssh(HOST, PORT, USER, password)

        progress_label.config(text="Obteniendo lista de procesos...")
        output_check = verify_process(ssh)

        output_text.delete(1.0, tk.END)  # Limpiar el área de texto
        output_text.insert(tk.END, output_check)

        ssh.close()
        progress_label.config(text="Lista de procesos obtenida.")
    except Exception as e:
        progress_label.config(text=f"Error: {e}")
        messagebox.showerror(
            "Error", f"Error al obtener lista de procesos: {e}")


# Crear ventana de Tkinter
root = tk.Tk()
root.title("Reiniciar Cámaras")
root.geometry('1200x650')

# Deshabilitar el botón de maximizar
root.resizable(False, False)

# Etiqueta para la contraseña
password_label = tk.Label(root, text="Ingresa la contraseña de root:")
password_label.pack(pady=10)

# Caja de texto para la contraseña
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=10)
password_entry.focus()

# Etiqueta para mostrar el estado del proceso
progress_label = tk.Label(root, text="", wraplength=300)
progress_label.pack(pady=10)

# Caja de texto para mostrar el resultado de 'pm2 ls'
output_text = tk.Text(root, height=25, width=180, wrap=tk.WORD)
output_text.pack(pady=10)

# Contenedor para los botones
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Botón para reiniciar cámaras
reiniciar_button = tk.Button(
    button_frame, text="Reiniciar Cámaras", command=lambda: on_reiniciar_click(progress_label, output_text, password_entry), bg="blue", fg="white")
reiniciar_button.pack(side=tk.LEFT, padx=10)

# Botón para mostrar lista de procesos
mostrar_button = tk.Button(
    button_frame, text="Mostrar Procesos", command=lambda: on_mostrar_click(progress_label, output_text, password_entry), bg="green", fg="white")
mostrar_button.pack(side=tk.LEFT, padx=10)

# Iniciar la interfaz gráfica
root.mainloop()
