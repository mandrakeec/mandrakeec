import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_agg import FigureCanvasAgg
from fpdf import FPDF
import os


# --- Configuración de Directorios ---
BASE_DIR = r"Y:\Base_Datos"

# Crear directorios si no existen
os.makedirs(BASE_DIR, exist_ok=True)

# Ruta de la base de datos
DB_PATH = os.path.join(BASE_DIR, "soporte_desa.db")


class DashboardWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard e Informes")
        self.master.geometry("1100x700")

        # Crear el canvas con scrollbar
        self.canvas = tk.Canvas(self.master)
        self.scroll_y = ttk.Scrollbar(
            self.master, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(
            self.master, orient="horizontal", command=self.canvas.xview)

        self.frame_graficos = ttk.Frame(self.canvas)

        self.frame_graficos.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.frame_graficos, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set,
                              xscrollcommand=self.scroll_x.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")

        # Configurar el evento de scroll para desplazar el canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Botón para generar informe
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Generar Informe",
                   command=self.generar_informe).pack(side=tk.RIGHT)

        self.crear_graficos()

     # Método para hacer scroll usando el mouse.
    def on_mouse_wheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def crear_graficos(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Estadísticas para los gráficos
        cursor.execute(
            "SELECT Estado, COUNT(*) FROM inventario GROUP BY Estado")
        estado_data = cursor.fetchall()

        cursor.execute("SELECT Marca, COUNT(*) FROM inventario GROUP BY Marca")
        marca_data = cursor.fetchall()

        cursor.execute(
            "SELECT Departamento, COUNT(*) FROM inventario GROUP BY Departamento")
        departamento_data = cursor.fetchall()

        conn.close()

        # Configuración de gráficos
        self.fig_estado, _ = self.crear_pie_chart(
            estado_data, "Equipos por Estado")
        self.fig_marca, _ = self.crear_bar_chart(
            marca_data, "Equipos por Marca", "Marcas", "Cantidad", rotar_x=True)
        self.fig_departamento, _ = self.crear_horizontal_bar_chart(
            departamento_data, "Equipos por Departamento", "Cantidad", "Departamentos"
        )

        # Agregar gráficos al canvas
        self.agregar_canvas(self.fig_estado, 0, 0)
        self.agregar_canvas(self.fig_marca, 1, 0)
        self.agregar_canvas(self.fig_departamento, 2, 0, colspan=2)

    def crear_pie_chart(self, data, title):
        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=["#10477d", "#02f502", "#db1276", "#ab6618"])
        ax.set_title(title, fontsize=14, fontweight="bold")
        return fig, ax

    def crear_bar_chart(self, data, title, xlabel, ylabel, rotar_x=False):
        labels = [row[0] for row in data]
        values = [row[1] for row in data]

        # Lista de colores para las barras
        colores = ['#42a5f5', '#66bb6a', '#7b2a91', '#e04d0d',
                   '#ffd700', '#2110e3', '#32cd32', '#b01a47']

        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Asignar colores a las barras
        bars = ax.bar(labels, values, color=colores[:len(labels)])

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        if rotar_x:
            ax.tick_params(axis='x', rotation=45)

        # Agregar etiquetas con los valores encima de las barras
        for bar in bars:
            ax.annotate(f'{bar.get_height()}',  # Texto (valor de la barra)
                        xy=(bar.get_x() + bar.get_width() / \
                            2, bar.get_height()),  # Posición
                        xytext=(0, 5),  # Desplazamiento (en píxeles)
                        textcoords="offset points",  # Coordenadas relativas
                        ha='center', va='bottom', fontsize=10)

        # Ajustar diseño para evitar recortes
        fig.tight_layout()
        return fig, ax

    def crear_horizontal_bar_chart(self, data, title, xlabel, ylabel):
        labels = [row[0] for row in data]
        values = [row[1] for row in data]

        # Lista de colores para las barras
        colores = ['#42a5f5', '#66bb6a', '#ff7043', '#ab47bc',
                   '#123654', '#ffee58', '#d1400d', '#a8080b']

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Asignar colores a las barras
        bars = ax.barh(labels, values, color=colores[:len(labels)])

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        # Agregar etiquetas con los valores al final de las barras
        for bar in bars:
            ax.annotate(f'{bar.get_width()}',  # Texto (valor de la barra)
                        xy=(bar.get_width(), bar.get_y() + \
                            bar.get_height() / 2),  # Posición
                        xytext=(5, 0),  # Desplazamiento (en píxeles)
                        textcoords="offset points",  # Coordenadas relativas
                        ha='left', va='center', fontsize=10)

        # Ajustar diseño para evitar recortes
        fig.tight_layout()
        return fig, ax

    def agregar_canvas(self, fig, row, column, colspan=1):
        canvas = FigureCanvasTkAgg(fig, self.frame_graficos)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=row, column=column,
                           padx=10, pady=10, sticky="nsew")
        self.frame_graficos.grid_rowconfigure(row, weight=1)
        self.frame_graficos.grid_columnconfigure(
            column, weight=1, minsize=400 * colspan)

    def generar_informe(self):
        """Generar informe en PDF con gráficos, cada uno en una página nueva."""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Generar y agregar gráfico de "Estado" en una página nueva
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Informe de Inventario - Dashboard",
                     ln=True, align="C")
            self.agregar_grafica_al_pdf(pdf, self.fig_estado, "", "estado.png")

            # Generar y agregar gráfico de "Marca" en una página nueva
            pdf.add_page()
            self.agregar_grafica_al_pdf(pdf, self.fig_marca, "", "marca.png")

            # Generar y agregar gráfico de "Departamento" en una página nueva
            pdf.add_page()
            self.agregar_grafica_al_pdf(
                pdf, self.fig_departamento, "", "departamento.png")

            # Guardar PDF en Descargas
            download_path = os.path.join(os.path.expanduser(
                "~"), "Downloads", "Informe_Dashboard.pdf")
            pdf.output(download_path)
            messagebox.showinfo("Informe Generado",
                                f"Informe guardado en {download_path}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo generar el informe: {e}")

    def agregar_grafica_al_pdf(self, pdf, figure, titulo, nombre_imagen):
        """Convertir una gráfica en imagen y agregarla al PDF."""
        # Guardar la imagen de la figura como archivo temporal
        temp_img_path = os.path.join(BASE_DIR, nombre_imagen)
        canvas = FigureCanvasAgg(figure)
        canvas.print_png(temp_img_path)

        # Agregar la imagen al PDF
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=titulo, ln=True, align="C")
        pdf.image(temp_img_path, x=10, y=pdf.get_y() + 10, w=200)
        os.remove(temp_img_path)  # Eliminar archivo temporal de la imagen


# --- Ejecutar Aplicación ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardWindow(root)
    root.mainloop()
