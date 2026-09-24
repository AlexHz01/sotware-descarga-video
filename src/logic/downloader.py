import threading
import os
import subprocess
import json
import re
import platform
import urllib.request
import stat

class DownloaderLogic:
    def __init__(self, progress_callback=None, success_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.success_callback = success_callback
        self.error_callback = error_callback
        self.current_process = None
        self.is_cancelled = False
        
        # Asegurar binario de yt-dlp
        self.bin_dir = os.path.join(os.getcwd(), 'bin')
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)
            
        self.system = platform.system()
        if self.system == "Windows":
            self.yt_dlp_path = os.path.join(self.bin_dir, 'yt-dlp.exe')
            self.download_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        else:
            self.yt_dlp_path = os.path.join(self.bin_dir, 'yt-dlp')
            self.download_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

        self.ensure_yt_dlp()

    def ensure_yt_dlp(self):
        if not os.path.exists(self.yt_dlp_path):
            print(f"Descargando yt-dlp desde {self.download_url}...")
            urllib.request.urlretrieve(self.download_url, self.yt_dlp_path)
            if self.system != "Windows":
                # Dar permisos de ejecución en Linux/Mac
                st = os.stat(self.yt_dlp_path)
                os.chmod(self.yt_dlp_path, st.st_mode | stat.S_IEXEC)
            print("yt-dlp descargado correctamente.")
        else:
            # Auto-actualizar
            self.update_yt_dlp()

    def update_yt_dlp(self):
        print("Buscando actualizaciones de yt-dlp...")
        try:
            creationflags = 0x08000000 if self.system == "Windows" else 0
            subprocess.run([self.yt_dlp_path, '-U'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
            print("yt-dlp actualizado.")
        except Exception as e:
            print(f"Error actualizando yt-dlp: {e}")

    def cancel(self):
        self.is_cancelled = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass

    def download(self, url, path, format_choice, quality_choice):
        self.is_cancelled = False
        
        # Comando base
        cmd = [
            self.yt_dlp_path,
            '--newline',
            '--no-check-certificate',
            '--restrict-filenames',
            '--windows-filenames',
            '-o', f'{path}/%(title).50s.%(ext)s',
        ]

        # Lógica de Calidad y Formato
        height_map = {
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360
        }
        height_limit = height_map.get(quality_choice)
        video_fmt = f"bestvideo[height<={height_limit}]" if height_limit else "bestvideo"
        audio_fmt = "bestaudio"

        if format_choice == "MP3":
            cmd.extend(['-f', 'bestaudio/best', '--extract-audio', '--audio-format', 'mp3', '--audio-quality', '192'])
        else: # MP4
            cmd.extend(['-f', f'{video_fmt}[ext=mp4]+{audio_fmt}[ext=m4a]/{video_fmt}+bestaudio/best[ext=mp4]/best'])

        cmd.append(url)

        try:
            creationflags = 0x08000000 if self.system == "Windows" else 0
            # Iniciar proceso
            self.current_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creationflags
            )

            progress_regex = re.compile(r'\[download\]\s+([0-9.]+)%')

            for line in self.current_process.stdout:
                if self.is_cancelled:
                    break
                
                match = progress_regex.search(line)
                if match and self.progress_callback:
                    percent_str = match.group(1) + "%"
                    self.progress_callback({
                        'status': 'downloading',
                        '_percent_str': percent_str
                    })

            self.current_process.wait()

            if self.is_cancelled:
                return

            if self.current_process.returncode == 0:
                if self.success_callback:
                    self.success_callback()
            else:
                if self.error_callback:
                    self.error_callback(f"Error de descarga (código {self.current_process.returncode})")

        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))
        finally:
            self.current_process = None

    def get_info(self, url):
        """Fetch video metadata without downloading."""
        try:
            cmd = [
                self.yt_dlp_path,
                '--dump-json',
                '--no-check-certificate',
                '--quiet',
                url
            ]
            
            creationflags = 0x08000000 if self.system == "Windows" else 0

            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creationflags
            )

            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                }
            else:
                print(f"Error fetching info: {result.stderr}")
                return None
        except Exception as e:
            print(f"Exception fetching info: {e}")
            return None
