import sys
import os

# Añadir el directorio actual al path para que las importaciones funcionen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
