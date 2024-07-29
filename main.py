#Licencia: Software propietario
#Autor: Fernando Alvarez Delgadillo
#Fecha: 11/12/2023
#Descripción: Software en python para la impresión de etiquetas
import barcode
from barcode.writer import ImageWriter
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import keyboard
from PIL import Image, ImageTk

class BarcodeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Aplicacin de impresión de etiquetas para almacen V0.1.1")

        # Variables para el tipo de código de barras y datos
        self.barcode_type_var = tk.StringVar(master, value='code128')
        self.data_entry = tk.Entry(self.master)

        # Lista de tipos de etiquetas
        self.label_types = ['EAN', 'UPC', 'Code 39', 'Code 128', 'ITF', 'QR']
        self.label_type_var = tk.StringVar(master, value=self.label_types[0])

        # Variables para el nombre del archivo y la extensión
        self.filename_var = tk.StringVar(master)
        self.extension_var = tk.StringVar(master, value='.png')
        self.extensions = ['.png', '.jpg', '.gif', '.tif']

        # Canvas para la previsualización del código de barras
        self.canvas = tk.Canvas(self.master, width=300, height=100)
        self.canvas.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.create_widgets()

    def create_widgets(self):
        data_label = tk.Label(self.master, text="Data:")
        data_label.grid(row=1, column=0, padx=10, pady=10)

        self.data_entry.grid(row=1, column=1, padx=10, pady=10)

        # Lista desplegable para seleccionar el tipo de etiqueta
        label_type_dropdown = ttk.Combobox(self.master, textvariable=self.label_type_var, values=self.label_types, state='readonly')
        label_type_dropdown.grid(row=1, column=2, padx=10, pady=10)
        label_type_dropdown.bind("<<ComboboxSelected>>", self.update_barcode_format)

        # Botón para previsualizar el código de barras
        preview_button = tk.Button(self.master, text="Preview Barcode", command=self.preview_barcode)
        preview_button.grid(row=2, column=2, padx=10, pady=10)

        # Botón para generar el código de barras
        generate_button = tk.Button(self.master, text="Generate Barcode", command=self.show_generate_dialog)
        generate_button.grid(row=2, column=0, padx=10, pady=10)

        # Botón para imprimir el código de barras
        print_button = tk.Button(self.master, text="Print Barcode", command=self.print_barcode)
        print_button.grid(row=2, column=1, padx=10, pady=10)

    def update_barcode_format(self, event=None):
        # Actualizar el formato del código de barras cuando se selecciona un nuevo tipo de etiqueta
        label_type = self.label_type_var.get()

        if label_type == 'EAN':
            self.barcode_type_var.set('ean13')
        elif label_type == 'UPC':
            self.barcode_type_var.set('upca')
        elif label_type == 'Code 39':
            self.barcode_type_var.set('code39')
        elif label_type == 'Code 128':
            self.barcode_type_var.set('code128')
        #Nota:El formato 'ITF' sólo soporta números enteros
        elif label_type == 'ITF':
            self.barcode_type_var.set('itf')
        elif label_type == 'QR':
            self.barcode_type_var.set('qr')

    def show_generate_dialog(self):
        # Ventana emergente para obtener el nombre del archivo y la extensión
        generate_dialog = tk.Toplevel(self.master)
        generate_dialog.title("Generate Barcode")

        # Cuadro de texto para el nombre del archivo
        filename_label = tk.Label(generate_dialog, text="File Name:")
        filename_label.grid(row=0, column=0, padx=10, pady=10)

        filename_entry = tk.Entry(generate_dialog, textvariable=self.filename_var)
        filename_entry.grid(row=0, column=1, padx=10, pady=10)

        # Combobox para seleccionar la extensión
        extension_label = tk.Label(generate_dialog, text="Extension:")
        extension_label.grid(row=1, column=0, padx=10, pady=10)

        extension_dropdown = ttk.Combobox(generate_dialog, textvariable=self.extension_var, values=self.extensions, state='readonly')
        extension_dropdown.grid(row=1, column=1, padx=10, pady=10)

        # Botón para generar el código de barras
        generate_button = tk.Button(generate_dialog, text="Generate", command=lambda: self.generate_barcode_from_dialog(generate_dialog))
        generate_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def generate_barcode_from_dialog(self, generate_dialog):
        # Obtener los valores del cuadro de texto y combobox en la ventana emergente
        filename = self.filename_var.get()
        extension = self.extension_var.get()

        # Cerrar la ventana emergente
        generate_dialog.destroy()

        # Generar el código de barras con los valores proporcionados
        self.generate_barcode(filename, extension)

    def generate_barcode(self, filename, extension):
        barcode_type = self.barcode_type_var.get()
        data = self.data_entry.get()

        if barcode_type and data and filename:
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_object = barcode_class(data, writer=ImageWriter())

            # Guardar el archivo con la extensión seleccionada
            filename_with_extension = f"{filename}{extension}"
            
            # Utilizar Pillow para salvar la imagen con la extensión correcta
            barcode_image = Image.open(barcode_object.save("temp"))
            barcode_image.save(filename_with_extension)

            print("Barcode generated and saved:", filename_with_extension)

    def scan_callback(self, event):
        barcode_type = self.barcode_type_var.get()
        data = event.name

        print("Scanned data:", data)

        barcode_class = barcode.get_barcode_class(barcode_type)
        barcode_object = barcode_class(data, writer=ImageWriter())
        filename_with_extension = f"{data}.{barcode_object.default_writer.__class__.__name__}.png"
        barcode_object.save(filename_with_extension)

        print("Barcode generated and saved:", filename_with_extension)

    def preview_barcode(self):
        barcode_type = self.barcode_type_var.get()
        data = self.data_entry.get()
        label_type = self.label_type_var.get()

        if barcode_type and data:
            if label_type == 'QR':
                self.show_qr_code(barcode_type, data)
            else:
                self.show_preview_window(barcode_type, data)
        #Ventana se abre para vista previa de la impresión
    def show_preview_window(self, barcode_type, data):
        preview_window = tk.Toplevel(self.master)
        preview_window.title("Barcode Preview")

        barcode_class = barcode.get_barcode_class(barcode_type)
        barcode_object = barcode_class(data, writer=ImageWriter())
        barcode_image = ImageTk.PhotoImage(Image.open(barcode_object.save("temp")))

        label = tk.Label(preview_window, image=barcode_image)
        label.image = barcode_image # type: ignore
        label.pack(padx=10, pady=10)

    def show_qr_code(self, barcode_type, data):
        # Lógica específica para mostrar el código QR, si es necesario
        pass

    def print_barcode(self):
        # Agregar opciones para la impresión
        print_options = self.get_print_options()

        if print_options is not None:
            # Agrega aquí la lógica para imprimir el código de barras con las opciones seleccionadas
            print("Printing barcode with options:", print_options)

    def get_print_options(self):
        # Cuadro de diálogo para obtener opciones de impresión
        print_options = simpledialog.askstring("Print Options", "Enter print options (e.g., copies, color, etc.):")

        return print_options

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeApp(root)
    root.mainloop()



