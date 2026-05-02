import asyncio
import flet as ft
from sqlalchemy.orm import Session, joinedload
from database import engine
import models
import crud


# ============================================================
#  HELPER: ejecuta consultas síncronas sin bloquear el event loop
# ============================================================
async def run_db(fn):
    def _execute():
        with Session(engine) as db:
            return fn(db)
    return await asyncio.to_thread(_execute)


# Mapa de colores por estado logístico (usado en badge y borde del dropdown)
COLORES_ESTADO = {
    "recibido":  "#f57c00",   # naranja
    "en ruta":   "#1565c0",   # azul
    "entregado": "#2e7d32",   # verde
    "cancelado": "#c62828",   # rojo
}


# ============================================================
#  FUNCIÓN PRINCIPAL DEL DASHBOARD
# ============================================================
async def main(page: ft.Page):
    page.title = "Smart-Liquor DevOps - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b0d0f"
    page.padding = 25

    txt_ventas  = ft.Text("S/ 0.00", size=30, weight="bold", color="amber")
    txt_pedidos = ft.Text("0",       size=30, weight="bold")
    txt_alertas = ft.Text("0",       size=30, weight="bold", color="red")

    lista_pedidos_ui    = ft.Column(spacing=10, scroll="always")
    lista_inventario_ui = ft.Column(spacing=10, scroll="always")

    # --------------------------------------------------------
    async def cambiar_estado(pedido_id: int, nuevo_estado: str):
        """Persiste el nuevo estado en la DB y refresca el panel de métricas."""
        await run_db(
            lambda db: crud.actualizar_estado_pedido(db, pedido_id, nuevo_estado)
        )
        # Solo actualizamos métricas sin reconstruir toda la lista
        await actualizar_metricas()

    async def actualizar_metricas():
        """Recalcula las tres métricas sin reconstruir las tarjetas."""
        peds = await run_db(lambda db: db.query(models.Pedido).all())
        ventas = sum(p.total_pedido for p in peds if p.total_pedido)
        txt_ventas.value  = f"S/ {ventas:,.2f}"
        txt_pedidos.value = str(len(peds))
        await page.update_async()

    # --------------------------------------------------------
    async def refrescar_datos(e=None):
        try:
            prods = await run_db(lambda db: db.query(models.Producto).all())
            peds  = await run_db(
                lambda db: (
                    db.query(models.Pedido)
                    .options(
                        joinedload(models.Pedido.cliente),
                        joinedload(models.Pedido.items)
                            .joinedload(models.DetallePedido.producto),
                    )
                    .order_by(models.Pedido.id.desc())
                    .all()
                )
            )

            # 1. Métricas
            criticos = [p for p in prods if (p.stock_actual or 0) <= (p.stock_minimo or 10)]
            txt_alertas.value = str(len(criticos))
            txt_pedidos.value = str(len(peds))
            ventas = sum(p.total_pedido for p in peds if p.total_pedido)
            txt_ventas.value  = f"S/ {ventas:,.2f}"

            # --------------------------------------------------
            # 2. Tarjetas de Pedidos
            # --------------------------------------------------
            lista_pedidos_ui.controls.clear()

            for p in peds:
                nombre_cliente = p.cliente.nombre_completo if p.cliente else "Anonimo"
                total          = p.total_pedido or 0.0
                estado_actual  = p.estado_logistico or "recibido"
                color_estado   = COLORES_ESTADO.get(estado_actual, "grey")

                # ---- Panel de ítems (colapsable) ----
                filas_items = []
                if p.items:
                    for item in p.items:
                        nombre_prod = item.producto.nombre if item.producto else "Producto eliminado"
                        precio_unit = (item.producto.precio_venta or 0) if item.producto else 0
                        subtotal    = precio_unit * (item.cantidad or 0)
                        filas_items.append(
                            ft.Row(
                                controls=[
                                    ft.Icon("circle", size=7, color="amber"),
                                    ft.Text(nombre_prod, expand=True, size=13),
                                    ft.Text(f"x{item.cantidad}", width=40, size=13,
                                            color="grey", text_align="right"),
                                    ft.Text(f"S/ {subtotal:.2f}", width=75, size=13,
                                            color="amber", text_align="right"),
                                ],
                                spacing=8,
                                vertical_alignment="center",
                            )
                        )
                else:
                    filas_items.append(
                        ft.Text("Sin items registrados", color="grey", size=12, italic=True)
                    )

                panel_detalle = ft.Container(
                    visible=False,
                    content=ft.Column(
                        controls=[
                            ft.Divider(height=10, color="#2a2d30"),
                            ft.Row(
                                controls=[
                                    ft.Text("PRODUCTO",  size=11, color="#555", expand=True),
                                    ft.Text("CANT.",     size=11, color="#555", width=40, text_align="right"),
                                    ft.Text("SUBTOTAL",  size=11, color="#555", width=75, text_align="right"),
                                ],
                                spacing=8,
                            ),
                            *filas_items,
                        ],
                        spacing=6,
                    ),
                    padding=ft.padding.only(left=4, right=4, top=0, bottom=6),
                )

                # ---- Botón flecha ----
                btn_expand = ft.IconButton(
                    icon="keyboard_arrow_down",
                    icon_color="white",
                    icon_size=22,
                    tooltip="Ver detalle del pedido",
                )

                async def toggle(e, _panel=panel_detalle, _btn=btn_expand):
                    _panel.visible  = not _panel.visible
                    _btn.icon       = "keyboard_arrow_up" if _panel.visible else "keyboard_arrow_down"
                    _btn.icon_color = "amber"             if _panel.visible else "white"
                    await page.update_async()

                btn_expand.on_click = toggle

                # ---- Dropdown de estado ----
                # El borde cambia de color según el estado seleccionado en tiempo real
                dropdown_estado = ft.Dropdown(
                    value=estado_actual,
                    width=140,
                    content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    options=[
                        ft.dropdown.Option(key="recibido",  text="📥  Recibido"),
                        ft.dropdown.Option(key="en camino",   text="🚚  En camino"),
                        ft.dropdown.Option(key="entregado", text="✅  Entregado"),
                        ft.dropdown.Option(key="cancelado", text="❌  Cancelado"),
                    ],
                    border_color=color_estado,
                    color="white",
                    bgcolor="#0b0d0f",
                    # Closure captura pid y el propio dropdown
                    on_change=lambda e, pid=p.id, dd=None: asyncio.ensure_future(
                        _on_estado_change(e, pid)
                    ),
                )

                async def _on_estado_change(e, pid: int, _dd=dropdown_estado):
                    nuevo = e.control.value
                    # Actualizar borde inmediatamente (feedback visual)
                    _dd.border_color = COLORES_ESTADO.get(nuevo, "grey")
                    await page.update_async()
                    # Persistir en DB
                    await cambiar_estado(pid, nuevo)

                # Reasignamos on_change con el closure correcto
                dropdown_estado.on_change = lambda e, pid=p.id, _dd=dropdown_estado: (
                    asyncio.ensure_future(_on_estado_change(e, pid, _dd))
                )

                # ---- Tarjeta completa ----
                lista_pedidos_ui.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon("shopping_cart", color="orange", size=20),
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    f"Pedido #{p.id}  —  {nombre_cliente}",
                                                    weight="bold", size=14,
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(f"S/ {total:.2f}",
                                                                color="amber", size=13),
                                                        dropdown_estado,   # ← selector aquí
                                                    ],
                                                    spacing=10,
                                                    vertical_alignment="center",
                                                ),
                                            ],
                                            expand=True,
                                            spacing=4,
                                        ),
                                        btn_expand,
                                    ],
                                    vertical_alignment="center",
                                    spacing=12,
                                ),
                                panel_detalle,
                            ],
                            spacing=0,
                        ),
                        bgcolor="#16191c",
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    )
                )

            # --------------------------------------------------
            # 3. Inventario
            # --------------------------------------------------
            lista_inventario_ui.controls.clear()
            for pr in prods:
                es_bajo = (pr.stock_actual or 0) <= (pr.stock_minimo or 10)
                lista_inventario_ui.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(pr.nombre, weight="bold", expand=True),
                            ft.Text(
                                f"Stock: {pr.stock_actual}",
                                color="red" if es_bajo else "white",
                            ),
                            ft.IconButton(
                                icon="add",
                                icon_color="green",
                                on_click=lambda e, pid=pr.id: asyncio.ensure_future(
                                    abrir_suministro(pid)
                                ),
                            ),
                        ]),
                        padding=10,
                        bgcolor="#16191c",
                        border_radius=10,
                    )
                )

            await page.update_async()

        except Exception as ex:
            print(f"[UI ERROR] {ex}")

    # --------------------------------------------------------
    #  DIALOGO DE SUMINISTRO
    # --------------------------------------------------------
    input_stock = ft.TextField(label="Cantidad a sumar", value="10", width=150)
    id_actual   = ft.Text("", visible=False)

    async def guardar_suministro(e):
        await run_db(
            lambda db: crud.sumar_stock_producto(
                db, int(id_actual.value), int(input_stock.value)
            )
        )
        modal.open = False
        await refrescar_datos()

    modal = ft.AlertDialog(
        title=ft.Text("Sumar Stock al Producto"),
        content=input_stock,
        actions=[
            ft.ElevatedButton(
                "Guardar",
                on_click=guardar_suministro,
                bgcolor="green",
                color="white",
            )
        ],
    )
    page.overlay.append(modal)

    async def abrir_suministro(pid: int):
        id_actual.value   = str(pid)
        input_stock.value = "10"
        modal.open        = True
        await page.update_async()

    # --------------------------------------------------------
    #  LAYOUT
    # --------------------------------------------------------
    await page.add_async(
        ft.Row(
            controls=[
                ft.Column([
                    ft.Text("Smart-Liquor Dashboard", size=28, weight="bold"),
                    ft.Text("Logistica Chincha  •  Supabase Cloud", color="grey"),
                ]),
                ft.IconButton("refresh", on_click=refrescar_datos, tooltip="Actualizar"),
            ],
            alignment="spaceBetween",
        ),
        ft.Divider(height=20, color="#232629"),
        ft.Row([
            ft.Column([ft.Text("VENTAS TOTALES", size=10, color="grey"), txt_ventas],  expand=True),
            ft.Column([ft.Text("PEDIDOS",        size=10, color="grey"), txt_pedidos], expand=True),
            ft.Column([ft.Text("STOCK CRITICO",  size=10, color="grey"), txt_alertas], expand=True),
        ]),
        ft.Divider(height=20, color="#232629"),
        ft.Row(
            controls=[
                ft.Column([
                    ft.Text("Pedidos Recientes", size=18, weight="bold"),
                    ft.Container(content=lista_pedidos_ui, height=450),
                ], expand=2),
                ft.Column([
                    ft.Text("Inventario", size=18, weight="bold"),
                    ft.Container(content=lista_inventario_ui, height=450),
                ], expand=1),
            ],
            vertical_alignment="start",
            spacing=30,
        ),
    )

    await refrescar_datos()