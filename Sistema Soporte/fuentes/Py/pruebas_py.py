import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import paramiko


def execute_ssh_command(ip, user, password, commands, sudo_password=None):
    """
    Ejecuta comandos SSH en el servidor remoto, usando `sudo -i` si es necesario.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=user, password=password)

        for command in commands:
            # Ejecutar comandos dentro de un entorno sudo -i
            if sudo_password:
                command = f"echo {sudo_password} | sudo -S -i {command}"

            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            output = stdout.read().decode()
            errors = stderr.read().decode()

            if errors:
                messagebox.showerror('Error', errors)
                print(f'Error: {errors}')
            else:
                print(f'Output: {output}')
                messagebox.showinfo('Resultado', output)

        ssh.close()
    except Exception as e:
        messagebox.showerror('Error', str(e))
        print(f'Exception: {e}')


def prompt_sudo_password():
    """
    Solicita la contraseña sudo al usuario.
    """
    return simpledialog.askstring(
        'Contraseña sudo', 'Ingresa la contraseña de sudo:', show='*'
    )


def borrar_logs():
    """
    Borra los logs del servidor remoto utilizando sudo -i.
    """
    ip = ip_entry.get()
    user = user_entry.get()
    password = password_entry.get()

    if not ip or not user or not password:
        messagebox.showerror("Error", "Debes completar todos los campos.")
        return

    sudo_password = prompt_sudo_password()
    if sudo_password:
        commands = [
            'rm -Rf /var/www/wstpg_notifications_fcm/storage/logs/*'
        ]
        execute_ssh_command(ip, user, password, commands, sudo_password)
    else:
        messagebox.showerror("Error", "No se ingresó la contraseña sudo.")


# Configuración de la ventana principal
root = tk.Tk()
root.title('*** LOG_CHOFERES ***')
root.geometry('320x300')
root.resizable(False, False)

# Estilo
style = ttk.Style()
style.configure('TButton', font=('Arial', 10))
style.configure('TLabel', font=('Arial', 10))

# Etiquetas y campos de entrada
ttk.Label(root, text="IP del Servidor:").grid(
    row=0, column=0, padx=10, pady=5, sticky="w")
ip_entry = ttk.Entry(root, width=30)
ip_entry.grid(row=0, column=1, padx=10, pady=5)
ip_entry.insert(0, "192.168.0.203")
ip_entry.focus()

ttk.Label(root, text="Usuario:").grid(
    row=1, column=0, padx=10, pady=5, sticky="w")
user_entry = ttk.Entry(root, width=30)
user_entry.grid(row=1, column=1, padx=10, pady=5)
user_entry.insert(0, "support")

ttk.Label(root, text="Contraseña:").grid(
    row=2, column=0, padx=10, pady=5, sticky="w")
password_entry = ttk.Entry(root, width=30, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5)

# Botones para las operaciones
ttk.Button(root, text='Borrar Logs con sudo', command=borrar_logs).grid(
    row=3, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

# Iniciar la aplicación
root.mainloop()
