import customtkinter as ctk
from tkinter import filedialog
import os
import threading

class ConvertPage(ctk.CTkFrame):
    def __init__(self, master, converter_logic, config):
        super().__init__(master, fg_color="transparent")
        self.converter_logic = converter_logic
        self.config = config
        
        self.grid_columnconfigure(0, weight=1)
        
        # --- Cabecera ---
        self.label_title = ctk.CTkLabel(self, text="Convertidor de Video", font=("Roboto", 24, "bold"))
        self.label_title.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # --- Selección de Archivos ---
        self.frame_select = ctk.CTkFrame(self)
        self.frame_select.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.frame_select.grid_columnconfigure(0, weight=1)
        
        self.btn_select = ctk.CTkButton(self.frame_select, text="Seleccionar Archivos", height=45, command=self.select_files)
        self.btn_select.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # --- Lista de Archivos (Cola) ---
        self.queue_frame = ctk.CTkScrollableFrame(self, height=200, label_text="Cola de Conversión")
        self.queue_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.queue_frame.grid_columnconfigure(0, weight=1)
        
        self.file_list = []
        self.queue_items = []
        
        # --- Configuración Destino ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.frame_config.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame_config, text="Formato de Salida:").grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.combo_format = ctk.CTkComboBox(self.frame_config, values=["AVI", "MP4", "MP3", "GIF"])
        self.combo_format.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.combo_format.set("AVI")
        
        # --- Botón Convertir ---
        self.btn_convert = self.create_glow_button("INICIAR CONVERSIÓN", self.start_batch_conversion)
        self.btn_convert.grid(row=4, column=0, pady=20, sticky="ew")
        
        # --- Estado ---
        self.status_label = ctk.CTkLabel(self, text="Selecciona videos para empezar", text_color="gray60")
        self.status_label.grid(row=5, column=0)

    def create_glow_button(self, text, command):
        return ctk.CTkButton(self, text=text, height=50, font=("Roboto", 18, "bold"),
                           fg_color="#3B8ED0", hover_color="#36719F", command=command)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Archivos de video", "*.mp4 *.avi *.mkv *.webm *.mov")])
        if files:
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
                    self.add_to_queue_ui(f)
            self.status_label.configure(text=f"{len(self.file_list)} archivos en cola")

    def add_to_queue_ui(self, file_path):
        item = ctk.CTkFrame(self.queue_frame, fg_color=("gray85", "gray20"))
        item.grid(row=len(self.queue_items), column=0, sticky="ew", pady=2, padx=5)
        item.grid_columnconfigure(0, weight=1)
        
        name = os.path.basename(file_path)
        ctk.CTkLabel(item, text=name).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        btn_del = ctk.CTkButton(item, text="X", width=30, height=25, fg_color="#D14545", hover_color="#A83232",
                                command=lambda f=file_path, i=item: self.remove_from_queue(f, i))
        btn_del.grid(row=0, column=1, padx=5, pady=5)
        
        self.queue_items.append({"path": file_path, "frame": item})

    def remove_from_queue(self, path, frame):
        self.file_list.remove(path)
        frame.destroy()
        self.queue_items = [i for i in self.queue_items if i["path"] != path]
        self.status_label.configure(text=f"{len(self.file_list)} archivos en cola")

    def start_batch_conversion(self):
        if not self.file_list: return
        
        target_fmt = self.combo_format.get()
        self.btn_convert.configure(state="disabled", text="CONVIRTIENDO...")
        
        def run():
            total = len(self.file_list)
            for idx, path in enumerate(list(self.file_list)):
                self.after(0, lambda i=idx+1: self.status_label.configure(text=f"Procesando {i}/{total}: {os.path.basename(path)}"))
                # Sincrónico dentro del hilo worker para procesar uno a uno
                self.converter_logic.convert(path, target_fmt)
                # Opcional: remover de la cola al terminar
                # self.after(0, lambda p=path: self.remove_finished(p))
            
            self.after(0, self.on_batch_complete)

        threading.Thread(target=run).start()

    def on_batch_complete(self):
        self.btn_convert.configure(state="normal", text="INICIAR CONVERSIÓN")
        self.status_label.configure(text="¡Todas las conversiones completadas!", text_color="#2CC985")
        from tkinter import messagebox
        messagebox.showinfo("Éxito", "Se han procesado todos los archivos.")
