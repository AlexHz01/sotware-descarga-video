import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, config, save_callback):
        super().__init__(master, fg_color="transparent")
        self.config = config
        self.save_callback = save_callback
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Ajustes de la Aplicación", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # --- Tema ---
        frame_theme = ctk.CTkFrame(self)
        frame_theme.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        frame_theme.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_theme, text="Modo de Apariencia:").grid(row=0, column=0, padx=20, pady=20)
        self.combo_theme = ctk.CTkComboBox(frame_theme, values=["Dark", "Light", "System"], command=self.change_theme)
        self.combo_theme.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.combo_theme.set(self.config.get("theme", "Dark"))
        
        # --- Carpeta de Descarga ---
        frame_path = ctk.CTkFrame(self)
        frame_path.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        frame_path.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame_path, text="Carpeta de Descarga Predeterminada:").grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.entry_path = ctk.CTkEntry(frame_path)
        self.entry_path.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="ew")
        self.entry_path.insert(0, self.config.get("download_path", ""))
        
        self.btn_browse = ctk.CTkButton(frame_path, text="Cambiar", width=100, command=self.browse_folder)
        self.btn_browse.grid(row=1, column=1, padx=(0, 20), pady=20)
        
        # --- Guardar ---
        self.btn_save = ctk.CTkButton(self, text="GUARDAR CAMBIOS", height=50, fg_color="#2CC985", hover_color="#229C68", command=self.save_settings)
        self.btn_save.grid(row=3, column=0, pady=20, sticky="ew")

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, folder)

    def save_settings(self):
        self.config["theme"] = self.combo_theme.get()
        self.config["download_path"] = self.entry_path.get()
        self.save_callback(self.config)
        from tkinter import messagebox
        messagebox.showinfo("Ajustes", "Configuración guardada correctamente.")
