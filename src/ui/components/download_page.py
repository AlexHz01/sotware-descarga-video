import customtkinter as ctk
import threading
from PIL import Image
import urllib.request
import io
import os

class DownloadPage(ctk.CTkFrame):
    def __init__(self, master, downloader_logic, config):
        super().__init__(master, fg_color="transparent")
        self.downloader_logic = downloader_logic
        self.config = config
        
        self.download_queue = []
        self.is_downloading = False
        self.current_video_info = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1) # Spacer for queue
        
        # --- Cabecera ---
        self.label_title = ctk.CTkLabel(self, text="Descargador de YouTube", font=("Roboto", 24, "bold"))
        self.label_title.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # --- Entrada URL ---
        self.frame_url = ctk.CTkFrame(self)
        self.frame_url.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.frame_url.grid_columnconfigure(0, weight=1)
        
        self.entry_url = ctk.CTkEntry(self.frame_url, placeholder_text="Pega el link de YouTube aquí...", height=45)
        self.entry_url.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")
        self.entry_url.bind("<KeyRelease>", self.on_url_change)
        
        self.btn_search = ctk.CTkButton(self.frame_url, text="Buscar", width=100, height=45, command=self.fetch_video_info)
        self.btn_search.grid(row=0, column=1, padx=(0, 20), pady=20)
        
        # --- Preview Card ---
        self.preview_card = ctk.CTkFrame(self, height=150)
        self.preview_card.grid_columnconfigure(1, weight=1)
        # No grid it initially
        
        self.img_label = ctk.CTkLabel(self.preview_card, text="", width=180, height=100, fg_color="gray30", corner_radius=8)
        self.img_label.grid(row=0, column=0, padx=20, pady=20)
        
        self.info_label = ctk.CTkLabel(self.preview_card, text="Cargando información...", font=("Roboto", 14), justify="left", anchor="w")
        self.info_label.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # --- Configuración de Descarga ---
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.frame_settings.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(self.frame_settings, text="Calidad:").grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.combo_quality = ctk.CTkComboBox(self.frame_settings, values=["Mejor Calidad", "1080p", "720p", "480p", "360p"])
        self.combo_quality.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.combo_quality.set(self.config.get("last_quality", "1080p"))
        
        ctk.CTkLabel(self.frame_settings, text="Formato:").grid(row=0, column=1, padx=20, pady=(10, 0), sticky="w")
        self.combo_format = ctk.CTkComboBox(self.frame_settings, values=["MP4", "MP3"])
        self.combo_format.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")
        self.combo_format.set("MP4")
        
        # --- Botones de Acción ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=4, column=0, pady=20, sticky="ew")
        self.frame_actions.grid_columnconfigure((0,1), weight=1)

        self.btn_add_queue = ctk.CTkButton(self.frame_actions, text="AÑADIR A LA COLA", height=50, font=("Roboto", 16, "bold"),
                                          command=self.add_to_queue)
        self.btn_add_queue.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_download_now = ctk.CTkButton(self.frame_actions, text="DESCARGAR AHORA", height=50, font=("Roboto", 16, "bold"),
                                            fg_color="#2CC985", hover_color="#229C68", command=self.download_now)
        self.btn_download_now.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # --- Cola de Descarga ---
        self.queue_frame = ctk.CTkScrollableFrame(self, height=150, label_text="Cola de Descargas")
        self.queue_frame.grid(row=5, column=0, sticky="ew", pady=(10, 20))
        self.queue_frame.grid_columnconfigure(0, weight=1)

        # --- Progreso y Estado ---
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Listo para descargar", text_color="gray60")
        self.status_label.grid(row=7, column=0)

        self.fetching_thread = None

    def on_url_change(self, event):
        url = self.entry_url.get()
        if "youtube.com" in url or "youtu.be" in url:
            if not self.fetching_thread or not self.fetching_thread.is_alive():
                self.fetch_video_info()

    def fetch_video_info(self):
        url = self.entry_url.get()
        if not url: return
        
        self.preview_card.grid(row=2, column=0, sticky="ew")
        self.info_label.configure(text="Buscando video...")
        
        def task():
            info = self.downloader_logic.get_info(url)
            if info:
                info['url'] = url
                self.current_video_info = info
                self.after(0, lambda: self.update_preview(info))
            else:
                self.after(0, lambda: self.info_label.configure(text="No se pudo obtener la información."))
        
        self.fetching_thread = threading.Thread(target=task)
        self.fetching_thread.start()

    def update_preview(self, info):
        title = info.get('title', 'Sin título')
        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Desconocido')
        
        mins, secs = divmod(duration, 60)
        dur_str = f"{mins}:{secs:02d}"
        
        text = f"Título: {title}\nCanal: {uploader}\nDuración: {dur_str}"
        self.info_label.configure(text=text)
        
        thumb_url = info.get('thumbnail')
        if thumb_url:
            threading.Thread(target=self.load_thumbnail, args=(thumb_url,)).start()

    def load_thumbnail(self, url):
        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data))
            ctk_img = ctk.CTkImage(light_image=image, dark_image=image, size=(180, 100))
            self.after(0, lambda: self.img_label.configure(image=ctk_img, text=""))
        except:
            pass

    def add_to_queue(self):
        if not self.current_video_info:
            url = self.entry_url.get()
            if not url: return
            self.fetch_video_info()
            return
        
        item = {
            'info': self.current_video_info,
            'quality': self.combo_quality.get(),
            'format': self.combo_format.get(),
            'status': 'pendiente'
        }
        self.download_queue.append(item)
        self.add_queue_item_ui(item)
        self.entry_url.delete(0, 'end')
        self.current_video_info = None
        self.preview_card.grid_forget()
        
        if not self.is_downloading:
            threading.Thread(target=self.process_queue).start()

    def add_queue_item_ui(self, item):
        frame = ctk.CTkFrame(self.queue_frame, fg_color=("gray85", "gray20"))
        frame.grid(row=len(self.download_queue), column=0, sticky="ew", pady=2, padx=5)
        frame.grid_columnconfigure(0, weight=1)
        
        title = item['info'].get('title', 'Video')
        lbl = ctk.CTkLabel(frame, text=title, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        status_lbl = ctk.CTkLabel(frame, text="Pendiente", text_color="gray60")
        status_lbl.grid(row=0, column=1, padx=10, pady=5)
        
        item['ui_frame'] = frame
        item['ui_status'] = status_lbl

    def download_now(self):
        # Primero añadir a la cola y asegurar que empiece
        self.add_to_queue()

    def process_queue(self):
        if not self.download_queue or self.is_downloading:
            return
        
        self.is_downloading = True
        
        while self.download_queue:
            item = self.download_queue[0]
            item['ui_status'].configure(text="Descargando...", text_color="yellow")
            
            url = item['info']['url']
            quality = item['quality']
            fmt = item['format']
            path = self.config.get("download_path")
            
            # Semáforo para esperar el fin de la descarga
            done_event = threading.Event()
            
            def progress(d):
                if d['status'] == 'downloading':
                    import re
                    p_str = d.get('_percent_str', '0%')
                    clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%', '').strip()
                    try:
                        p_val = float(clean_p)
                        self.after(0, lambda: self.progress_bar.set(p_val/100))
                        self.after(0, lambda: self.status_label.configure(text=f"Bajando: {item['info']['title'][:30]}... ({p_str})"))
                    except: pass

            def success():
                self.after(0, lambda: item['ui_status'].configure(text="Completado", text_color="#2CC985"))
                done_event.set()
                
            def error(msg):
                self.after(0, lambda: item['ui_status'].configure(text="Error", text_color="red"))
                self.after(0, lambda: self.status_label.configure(text=f"Error en {item['info']['title'][:20]}"))
                done_event.set()

            self.downloader_logic.progress_callback = progress
            self.downloader_logic.success_callback = success
            self.downloader_logic.error_callback = error
            
            # Ejecutar descarga (en este mismo hilo worker de la cola)
            self.downloader_logic.download(url, path, fmt, quality)
            done_event.wait()
            
            # Remover de la cola y actualizar lista
            self.download_queue.pop(0)
            self.after(0, lambda f=item['ui_frame']: f.destroy())
            
        self.is_downloading = False
        self.after(0, lambda: self.status_label.configure(text="Todas las descargas terminadas"))
        self.after(0, lambda: self.progress_bar.set(0))
