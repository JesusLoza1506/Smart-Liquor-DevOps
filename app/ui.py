import flet as ft
from sqlalchemy.orm import Session
from app.database import engine
import app.crud as crud
import threading
from datetime import datetime

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "Smart-Liquor DevOps - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f1113" # Fondo ultra oscuro como en la imagen
    page.padding = 30
    page.window_width = 1200
    page.window_height = 850

    # --- COMPONENTES DINÁMICOS ---
    txt_estado = ft.Text("Sincronizando con base de datos...", color="amber", size=12)
    
    # Referencias para actualizar valores
    val_ventas = ft.Text("S/ 0.00", size=32, weight="bold")
    val_pedidos = ft.Text("0", size=32, weight="bold")
    val_alertas = ft.Text("0", size=32, weight="bold")
    val_ticket = ft.Text("S/ 0.00", size=32, weight="bold")
    
    tabla_pedidos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("CLIENTE / PRODUCTO")),
            ft.DataColumn(ft.Text("MONTO")),
            ft.DataColumn(ft.Text("ESTADO")),
        ],
        rows=[]
    )

    # --- LÓGICA DE CARGA REAL ---
    def actualizar_dashboard():
        try:
            with Session(engine) as db:
                productos = crud.obtener_productos(db) #
                alertas_count = len([p for p in productos if p.alerta_roja]) #
                
                # Simulación de cálculos basados en modelos reales
                # En un sistema completo, aquí sumarías el 'total_pedido' de models.Pedido
                val_alertas.value = str(alertas_count)
                val_ventas.value = f"S/ {sum(p.precio_venta * p.stock_actual for p in productos):,.2f}"
                
                # Actualizar Tabla de Pedidos Recientes
                tabla_pedidos.rows.clear()
                # Aquí podrías consultar db.query(models.Pedido)
                
                txt_estado.value = "🟢 Sistema en Vivo - Conectado"
                txt_estado.color = "green"
        except Exception as e:
            txt_estado.value = f"🔴 Error de Conexión: {str(e)}"
            txt_estado.color = "red"
        page.update()

    # --- UI COMPONENTS (Basados en tu imagen) ---
    def crear_card_metrica(titulo, valor, icono, color_icon):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icono, color=color_icon), ft.Text(titulo, color="grey")]),
                valor,
            ]),
            bgcolor="#1a1c1e", padding=20, border_radius=15, expand=True
        )

    header = ft.Row([
        ft.Column([
            ft.Text("Dashboard", size=40, weight="bold"),
            ft.Text("Smart-Liquor > Dashboard", color="orange"),
        ]),
        ft.Column([
            ft.Text(datetime.now().strftime("%A, %d %B %Y"), color="grey"),
            ft.ElevatedButton("Actualizar", icon="refresh", on_click=lambda _: threading.Thread(target=actualizar_dashboard).start())
        ], horizontal_alignment="end")
    ], alignment="spaceBetween")

    # --- ENSAMBLAJE ---
    page.add(
        header,
        ft.Divider(height=20, color="transparent"),
        ft.Row([
            crear_card_metrica("Total Ventas", val_ventas, "monetization_on", "green"),
            crear_card_metrica("Pedidos Hoy", val_pedidos, "assignment", "blue"),
            crear_card_metrica("Stock Crítico", val_alertas, "warning", "red"),
            crear_card_metrica("Ticket Promedio", val_ticket, "analytics", "cyan"),
        ], spacing=20),
        ft.Divider(height=30, color="transparent"),
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Pedidos Recientes", size=20, weight="bold"),
                    tabla_pedidos
                ]),
                bgcolor="#1a1c1e", padding=20, border_radius=15, expand=2
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Alertas Críticas", size=20, weight="bold"),
                    ft.Text("Revisión inmediata", color="grey")
                    # Aquí iría el componente de stock bajo
                ]),
                bgcolor="#1a1c1e", padding=20, border_radius=15, expand=1
            )
        ], alignment="start", spacing=20),
        txt_estado
    )

    # Carga inicial
    threading.Thread(target=actualizar_dashboard, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main)