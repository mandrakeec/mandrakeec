import json
import os
import tkinter as tk
from tkinter import messagebox

# Ruta para el archivo JSON que almacenará las notas
NOTES_FILE = r"C:\Sistemas Soporte\Py\notas.json"


class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tablero de Notas Adhesivas")
        self.root.geometry("300x100")
        self.root.configure(bg="gray")

        self.notes = []  # Lista para almacenar las referencias de las notas
        self.load_notes()

        # Crear un frame contenedor centrado para los botones
        button_frame = tk.Frame(root, bg="gray")
        button_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Botón para añadir una nueva nota
        add_note_button = tk.Button(
            button_frame, text="Agregar Nota", command=self.add_note, bg="blue", fg="white"
        )
        add_note_button.grid(row=0, column=0, padx=5)

        # Botón para anclar/desanclar la ventana principal
        self.pin_button = tk.Button(
            button_frame, text="Anclar Ventana", command=self.toggle_main_pin, bg="blue", fg="white"
        )
        self.pin_button.grid(row=0, column=1, padx=5)

    def load_notes(self):
        """Carga las notas desde el archivo JSON."""
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r") as file:
                    notes_data = json.load(file)
                    for note_data in notes_data:
                        if (
                            isinstance(note_data, dict)
                            and "text" in note_data
                            and "geometry" in note_data
                            and "pinned" in note_data
                        ):
                            self.create_note(
                                note_data["text"], note_data["geometry"], bool(note_data["pinned"]), save=False
                            )
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Error", "El archivo JSON está corrupto. Se cargará una lista vacía."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Ocurrió un error al cargar notas: {e}"
                )

    def save_notes(self):
        """Guarda el estado actual de todas las notas."""
        try:
            notes_data = []
            for note in self.notes:
                text_content = note["text"].get("1.0", tk.END).strip()
                geometry = note["frame"].geometry()
                pinned = bool(note["frame"].attributes(
                    "-topmost"))  # Convertir a booleano
                notes_data.append(
                    {"text": text_content, "geometry": geometry, "pinned": pinned}
                )

            with open(NOTES_FILE, "w") as file:
                # Guardar con formato legible
                json.dump(notes_data, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar las notas: {e}")

    def add_note(self):
        """Crea una nueva nota con valores predeterminados."""
        self.create_note("Nueva Nota")

    def create_note(self, text="Nueva Nota", geometry="200x200+100+100", pinned=False, save=True):
        """Crea una nota adhesiva con texto y configuración opcionales."""
        frame = tk.Toplevel(self.root)
        frame.geometry(geometry)
        frame.configure(bg="deep sky blue")
        frame.attributes("-topmost", pinned)

        text_widget = tk.Text(frame, wrap="word",
                              bg="lightyellow", height=10, width=20)
        text_widget.insert("1.0", text)
        text_widget.pack(expand=True, fill="both")

        # Botón para anclar/desanclar la nota
        pin_button = tk.Button(
            frame, text="Anclar", command=lambda: self.toggle_pin(frame, pin_button)
        )
        pin_button.pack(side="left", padx=5, pady=5)
        pin_button.config(text="Desanclar" if pinned else "Anclar")

        # Botón para eliminar la nota
        delete_button = tk.Button(
            frame, text="Eliminar", command=lambda: self.delete_note(frame), bg="gold", fg="white"
        )
        delete_button.pack(side="right", padx=5, pady=5)

        # Habilitar cambio de tamaño
        frame.resizable(True, True)

        # Guardar referencia de la nota
        self.notes.append({"frame": frame, "text": text_widget})

        # Actualizar automáticamente al mover o editar
        frame.bind("<Configure>", lambda e: self.save_notes())
        text_widget.bind("<KeyRelease>", lambda e: self.save_notes())

        # Guardar notas si es necesario
        if save:
            self.save_notes()

    def toggle_pin(self, frame, pin_button):
        """Alterna entre anclar y desanclar la ventana de nota."""
        try:
            is_pinned = frame.attributes("-topmost")
            frame.attributes("-topmost", not is_pinned)
            pin_button.config(text="Desanclar" if not is_pinned else "Anclar")
            self.save_notes()
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo anclar/desanclar la nota: {e}")

    def toggle_main_pin(self):
        """Alterna entre anclar y desanclar la ventana principal."""
        try:
            is_pinned = self.root.attributes("-topmost")
            self.root.attributes("-topmost", not is_pinned)
            self.pin_button.config(
                text="Desanclar Ventana" if not is_pinned else "Anclar Ventana"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo anclar/desanclar: {e}")

    def delete_note(self, frame):
        """Elimina una nota de la interfaz y de la lista."""
        for note in self.notes:
            if note["frame"] == frame:
                self.notes.remove(note)
                frame.destroy()
                break
        self.save_notes()


# Crear la ventana principal y ejecutar la aplicación
root = tk.Tk()
app = StickyNotesApp(root)
root.mainloop()
