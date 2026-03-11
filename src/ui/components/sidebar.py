import customtkinter as ctk
import os
from PIL import Image

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, select_callback):
        super().__init__(master, width=200, corner_radius=0)
        self.select_callback = select_callback
        
        self.grid_rowconfigure(5, weight=1) # Spacer
        
        # Logo o Título
        self.label_logo = ctk.CTkLabel(self, text="VIDEO\nPRO", font=("Roboto", 24, "bold"), text_color="#2CC985")
        self.label_logo.grid(row=0, column=0, padx=20, pady=(30, 40))
        
        # Botones de navegación
        self.btn_download = self.create_nav_button("YouTube", 1)
        self.btn_facebook = self.create_nav_button("Facebook", 2)
        self.btn_drive = self.create_nav_button("Drive", 3)
        self.btn_convert = self.create_nav_button("Convertidor", 4)
        self.btn_history = self.create_nav_button("Historial", 5)
        self.btn_settings = self.create_nav_button("Ajustes", 6)
        
        self.buttons = {
            "download": self.btn_download,
            "facebook": self.btn_facebook,
            "drive": self.btn_drive,
            "convert": self.btn_convert,
            "history": self.btn_history,
            "settings": self.btn_settings
        }
        
        self.select("download")

    def create_nav_button(self, text, row):
        btn = ctk.CTkButton(self, text=text, corner_radius=0, height=45, border_spacing=10,
                            fg_color="transparent", text_color=("gray10", "gray90"),
                            hover_color=("gray70", "gray30"), anchor="w",
                            command=lambda: self.select(text.lower()))
        key = text.lower().replace("youtube", "download").replace("descargas", "download").replace("convertidor", "convert").replace("historial", "history").replace("ajustes", "settings")
        btn.configure(command=lambda k=key: self.select(k))
        btn.grid(row=row, column=0, sticky="ew")
        return btn

    def select(self, name):
        # Reset colors
        for key, btn in self.buttons.items():
            btn.configure(fg_color="transparent")
        
        # Highlight selected
        if name in self.buttons:
            self.buttons[name].configure(fg_color=("gray75", "gray25"))
            self.select_callback(name)
