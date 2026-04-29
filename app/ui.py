import flet as ft
from models import Producto, Pedido 

def main(page: ft.Page):
    page.title = "Smart-Liquor DevOps - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK 

    # Función de apoyo para diseño
    def obtener_color_fila(alerta_roja):
        return ft.colors.RED_900 if alerta_roja else None

    # Componente de Pedidos con los nuevos estados
    selector_pedido = ft.Dropdown(
        label="Estado de Pedido",
        options=[
            ft.dropdown.Option("Recibido"),
            ft.dropdown.Option("En tránsito"),
            ft.dropdown.Option("Entregado"),
        ]
    )

    btn_suministro = ft.ElevatedButton(
        "Añadir Suministro", 
        icon="add"
    )

    page.add(
        ft.Text("Panel de Control Real", size=25, weight="bold"),
        selector_pedido,
        btn_suministro
    )

if __name__ == "__main__":
    ft.app(target=main)