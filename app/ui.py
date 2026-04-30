import flet as ft
from app.database import engine 
from sqlalchemy.orm import Session
import app.crud as crud         
import threading # Para cargar datos en segundo plano

def main(page: ft.Page):
    page.title = "Smart-Liquor DevOps - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 700
    
    # 1. Componentes visuales
    txt_estado = ft.Text("Iniciando sistema...", color="amber")
    prg_carga = ft.ProgressBar(width=400, color="amber", visible=True)
    
    tabla_productos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Estado")),
        ],
        rows=[]
    )

    # 2. Función que corre en SEGUNDO PLANO
    def hilo_carga_datos():
        try:
            with Session(engine) as db:
                productos = crud.obtener_productos(db)
                tabla_productos.rows.clear()
                for p in productos:
                    icono = "warning" if p.alerta_roja else "check_circle"
                    color = "yellow" if p.alerta_roja else "green"
                    
                    tabla_productos.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(p.nombre)),
                            ft.DataCell(ft.Text(str(p.stock_actual))),
                            ft.DataCell(ft.Icon(icono, color=color)),
                        ])
                    )
                txt_estado.value = "Conectado a Supabase"
                txt_estado.color = "green"
        except Exception as ex:
            txt_estado.value = f"Error: No se pudo conectar a la DB"
            txt_estado.color = "red"
            print(f"DEBUG ERROR: {ex}")
        
        prg_carga.visible = False
        page.update()

    # 3. Función para disparar la carga sin bloquear la vista
    def cargar_datos_click(e=None):
        prg_carga.visible = True
        txt_estado.value = "Consultando base de datos..."
        page.update()
        threading.Thread(target=hilo_carga_datos, daemon=True).start()

    # 4. Construir la UI básica (Esto saldrá de inmediato)
    page.add(
        ft.Column([
            ft.Text("Smart-Liquor Dashboard", size=32, weight="bold"),
            txt_estado,
            prg_carga,
            ft.Divider(),
            ft.Container(content=tabla_productos, height=300, padding=10),
            ft.FilledButton("Forzar Recarga", icon="refresh", on_click=cargar_datos_click)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    page.update()
    
    # Lanzar la carga automática al abrir
    cargar_datos_click()

if __name__ == "__main__":
    ft.run(main)