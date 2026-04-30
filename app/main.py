import threading
import uvicorn
import flet as ft
from fastapi import FastAPI
from ui import main as build_dashboard
from database import probar_conexion
from database import esperar_y_crear_tablas

app = FastAPI()

@app.get("/")
def read_root():
    return {"Smart_Liquor": "Conectado a Supabase y Operativo 🚀"}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main_flet(page: ft.Page):
    build_dashboard(page)


if __name__ == "__main__":
    # 1. Esperamos a que la DB esté lista antes de lanzar todo lo demás
    if esperar_y_crear_tablas():
        # 2. Si la DB conectó, lanzamos la API y la Web
        print("Iniciando servicios...")
        threading.Thread(target=run_api, daemon=True).start()
        ft.app(target=main_flet, view=ft.AppView.WEB_BROWSER, port=8502, host="0.0.0.0")
    else:
        print("El sistema no pudo iniciar debido a fallas en la Base de Datos.")