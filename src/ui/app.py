import customtkinter as ctk
import os
from src.ui.components.sidebar import Sidebar
from src.ui.components.download_page import DownloadPage
from src.ui.components.facebook_page import FacebookPage
from src.ui.components.drive_page import DrivePage
from src.ui.components.convert_page import ConvertPage
from src.ui.components.settings_page import SettingsPage
from src.logic.downloader import DownloaderLogic
from src.logic.converter import ConverterLogic
from src.utils.config import ConfigManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cargar configuración
        self.config = ConfigManager.load_config()
        
        # Configurar Ventana
        self.title("Video Pro - Downloader & Converter")
        self.geometry("1000x650")
        ctk.set_appearance_mode(self.config["theme"])
        ctk.set_default_color_theme(self.config["color_theme"])

        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Inicializar Lógica
        self.downloader_logic = DownloaderLogic()
        self.converter_logic = ConverterLogic()

        self.pages = {}
        self.current_page = None

        # Contenedor de Páginas (Debe estar antes de la sidebar porque la sidebar carga la primera página)
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name):
        if self.current_page:
            self.current_page.grid_forget()
        
        if name not in self.pages:
            self.pages[name] = self.create_page(name)
        
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        self.current_page = self.pages[name]

    def create_page(self, name):
        if name == "download":
            return DownloadPage(self.container, self.downloader_logic, self.config)
        elif name == "facebook":
            return FacebookPage(self.container, self.downloader_logic, self.config)
        elif name == "drive":
            return DrivePage(self.container, self.downloader_logic, self.config)
        elif name == "convert":
            return ConvertPage(self.container, self.converter_logic, self.config)
        elif name == "settings":
            return SettingsPage(self.container, self.config, self.save_config)
        else:
            # Placeholder para páginas no implementadas (ej. History)
            page = ctk.CTkFrame(self.container, fg_color="transparent")
            ctk.CTkLabel(page, text=f"Página '{name}' en construcción...", font=("Roboto", 18)).pack(pady=100)
            return page

    def save_config(self, new_config):
        self.config = new_config
        ConfigManager.save_config(self.config)

if __name__ == "__main__":
    app = App()
    app.mainloop()
