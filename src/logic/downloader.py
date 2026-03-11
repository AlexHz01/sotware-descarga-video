import yt_dlp
import threading
import os

class DownloaderLogic:
    def __init__(self, progress_callback=None, success_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.success_callback = success_callback
        self.error_callback = error_callback
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def _extract_drive_stream(self, url, format_choice):
        from playwright.sync_api import sync_playwright
        import time
        import os
        
        found_url = None
        
        def clean_url(u):
            import urllib.parse
            parsed = urllib.parse.urlparse(u)
            qs = urllib.parse.parse_qs(parsed.query)
            for k in ['range', 'rn', 'rbuf', 'ump', 'srfvp']:
                qs.pop(k, None)
            parsed = parsed._replace(query=urllib.parse.urlencode(qs, doseq=True))
            return urllib.parse.urlunparse(parsed)

        def handle_request(request):
            nonlocal found_url
            if "videoplayback" in request.url:
                cleaned = clean_url(request.url)
                if format_choice == "MP3":
                    if "mime=audio" in request.url:
                        found_url = cleaned
                else:
                    if "mime=video" in request.url:
                        found_url = cleaned
                    elif not found_url and "mime=" not in request.url:
                        found_url = cleaned
                    elif not found_url: # fallback
                        found_url = cleaned

        def load_cookies_into_context(context, cookie_file):
            if not os.path.exists(cookie_file):
                return
            cookies = []
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('#') and not line.startswith('#HttpOnly_'):
                            continue
                        if not line.strip():
                            continue
                        parts = line.strip().split('\t')
                        if len(parts) >= 7:
                            # Netscape format: domain, flag, path, secure, expiration, name, value
                            domain = parts[0]
                            if domain.startswith('#HttpOnly_'):
                                domain = domain[10:]
                            
                            cookie = {
                                'domain': domain,
                                'path': parts[2],
                                'name': parts[5],
                                'value': parts[6],
                            }
                            # expiration
                            try:
                                exp = float(parts[4])
                                if exp > 0:
                                    cookie['expires'] = exp
                            except:
                                pass
                                
                            # secure
                            if parts[3].lower() == 'true':
                                cookie['secure'] = True
                                
                            cookies.append(cookie)
                if cookies:
                    context.add_cookies(cookies)
            except Exception as e:
                print(f"Error parseando cookies.txt: {e}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # Always headless now
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 720}
            )
            
            # Cargar cookies si existen
            cookie_file = "cookies.txt"
            if os.path.exists(cookie_file):
                if self.progress_callback:
                    self.progress_callback({'status': 'downloading', '_percent_str': ' 0.0% (Inyectando sesión de cookies...)'})
                load_cookies_into_context(context, cookie_file)
                
            page = context.new_page()
            page.on("request", handle_request)
            
            try:
                page.goto(url)
                
                for _ in range(20):
                    if found_url:
                        break
                    time.sleep(0.5)
                
                if not found_url:
                    try:
                        # Attempt to click the play button in the center
                        page.mouse.click(640, 360)
                        for _ in range(10):
                            if found_url:
                                break
                            time.sleep(0.5)
                    except:
                        pass
            except Exception as e:
                print(f"Playwright error: {e}")
            finally:
                context.close()
                browser.close()

        return found_url

    def progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Descarga Cancelada por Usuario")
        
        if self.progress_callback:
            self.progress_callback(d)

    def download(self, url, path, format_choice, quality_choice):
        self.is_cancelled = False
        try:
            download_url = url
            
            # Use Playwright for Google Drive to bypass quota/virus restrictions
            if "drive.google.com" in url:
                if self.progress_callback:
                    self.progress_callback({'status': 'downloading', '_percent_str': ' 0.0% (Automating Drive...)'})
                
                extracted_url = self._extract_drive_stream(url, format_choice)
                if extracted_url:
                    download_url = extracted_url
                else:
                    raise Exception("No se pudo interceptar el stream de Google Drive. Asegúrate de que el archivo tenga vista previa.")
            ydl_opts = {
                'outtmpl': f'{path}/%(title).50s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
                'no_color': True,
                'restrictfilenames': True,
                'windowsfilenames': True,
                # Usar un user-agent más común y evitar configuraciones experimentales
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }

            if os.path.exists("cookies.txt"):
                ydl_opts['cookiefile'] = "cookies.txt"

            # Lógica de Calidad
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
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else: # MP4
                ydl_opts['format'] = f"{video_fmt}[ext=mp4]+{audio_fmt}[ext=m4a]/{video_fmt}+bestaudio/best[ext=mp4]/best"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([download_url])
            
            if self.success_callback:
                self.success_callback()

        except Exception as e:
            if "Descarga Cancelada por Usuario" in str(e):
                # Handled via is_cancelled check in hooks and exceptions
                pass
            elif self.error_callback:
                self.error_callback(str(e))

    def get_info(self, url):
        """Fetch video metadata without downloading."""
        try:
            if "drive.google.com" in url:
                return {
                    'title': "Archivo de Google Drive",
                    'thumbnail': None,
                    'duration': 0,
                    'uploader': "Google Drive",
                    'view_count': 0,
                }
                
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                }
        except Exception as e:
            print(f"Error fetching info: {e}")
            if "drive.google.com" in url:
                return {
                    'title': "Archivo Playwright (Google Drive)",
                    'thumbnail': None,
                    'duration': 0,
                    'uploader': "Google Drive",
                    'view_count': 0,
                }
            return None
