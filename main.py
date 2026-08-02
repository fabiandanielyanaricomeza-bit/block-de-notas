import flet as ft
import csv
import os
from datetime import datetime

# Archivo donde se guardarán las notas
archivo_notas = 'mis_notas.csv'

def main(page: ft.Page):
    # --- CONFIGURACIÓN BÁSICA ---
    page.title = "Block de Notas Flet"
    page.padding = 20

    # Estado del tema actual por defecto
    tema_actual = "Oscuro"

    # Diccionario completo de temas con colores personalizados
    temas = {
        "Claro": {
            "mode": ft.ThemeMode.LIGHT,
            "body_bg": "#f5f6fa",
            "appbar_bg": "#ffffff",
            "appbar_fg": "#2f3640",
            "card_bg": "#ffffff",
            "card_fg": "#2f3640",
            "date_color": "#718093"
        },
        "Oscuro": {
            "mode": ft.ThemeMode.DARK,
            "body_bg": "#121212",
            "appbar_bg": "#1e1e1e",
            "appbar_fg": "#ffffff",
            "card_bg": "#252526",
            "card_fg": "#ffffff",
            "date_color": "#a0a0a0"
        },
        "Rojo Pasión": {
            "mode": ft.ThemeMode.DARK,
            "body_bg": "#1a0505",
            "appbar_bg": "#8b0000",
            "appbar_fg": "#ffffff",
            "card_bg": "#2d0a0a",
            "card_fg": "#ffffff",
            "date_color": "#ff9999"
        },
        "Verde Esmeralda": {
            "mode": ft.ThemeMode.DARK,
            "body_bg": "#051a0a",
            "appbar_bg": "#006400",
            "appbar_fg": "#ffffff",
            "card_bg": "#0a2d14",
            "card_fg": "#ffffff",
            "date_color": "#99ffbb"
        },
        "Púrpura Místico": {
            "mode": ft.ThemeMode.DARK,
            "body_bg": "#12051a",
            "appbar_bg": "#4b0082",
            "appbar_fg": "#ffffff",
            "card_bg": "#220a3a",
            "card_fg": "#ffffff",
            "date_color": "#e0b0ff"
        },
        "Ámbar Neón": {
            "mode": ft.ThemeMode.DARK,
            "body_bg": "#1a1205",
            "appbar_bg": "#ff8c00",
            "appbar_fg": "#1a1205",
            "card_bg": "#33260a",
            "card_fg": "#ffffff",
            "date_color": "#ffdfba"
        }
    }

    cache_header = []
    cache_rows = []

    def cargar_datos_iniciales():
        nonlocal cache_header, cache_rows
        if os.path.exists(archivo_notas):
            with open(archivo_notas, mode='r', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                if reader:
                    cache_header = reader[0]
                    cache_rows = reader[1:]
                else:
                    cache_header = ['Fecha', 'Titulo', 'Contenido']
                    cache_rows = []
        else:
            cache_header = ['Fecha', 'Titulo', 'Contenido']
            cache_rows = []
            with open(archivo_notas, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cache_header)

    def sincronizar_disco():
        with open(archivo_notas, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cache_header)
            writer.writerows(cache_rows)

    cargar_datos_iniciales()
    nota_en_edicion_index = None

    # --- COMPONENTES DE LA VISTA DE EDICIÓN ---
    in_titulo = ft.TextField(
        label="Título de la nota", 
        text_style=ft.TextStyle(size=18, weight="bold"), 
        border=ft.InputBorder.UNDERLINE
    )
    
    in_contenido = ft.TextField(
        label="Escribe tu nota aquí...",
        multiline=True,
        expand=True, 
        border=ft.InputBorder.NONE
    )

    # --- FUNCIONES DE NAVEGACIÓN Y ACCIÓN ---
    def cambiar_vista_inicio():
        nonlocal nota_en_edicion_index
        nota_en_edicion_index = None
        vista_edicion.visible = False
        vista_inicio.visible = True
        page.appbar = appbar_inicio
        aplicar_estilo_actual()
        cargar_notas()

    def cambiar_vista_edicion():
        nonlocal nota_en_edicion_index
        nota_en_edicion_index = None
        in_titulo.value = ""
        in_contenido.value = ""
        vista_inicio.visible = False
        vista_edicion.visible = True
        page.appbar = appbar_edicion
        aplicar_estilo_actual()

    def intentar_cancelar(e):
        if in_titulo.value.strip() or in_contenido.value.strip():
            dlg_advertencia.open = True
            page.update()
        else:
            cambiar_vista_inicio()

    def guardar_y_volver():
        nonlocal nota_en_edicion_index
        t = in_titulo.value.strip()
        c = in_contenido.value.strip()
        
        if not t and not c:
            page.overlay.append(ft.SnackBar(ft.Text("No puedes guardar una nota vacía"), open=True))
            page.update()
            return
            
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        titulo_final = t if t else "Sin título"
        
        if nota_en_edicion_index is not None and 0 <= nota_en_edicion_index < len(cache_rows):
            cache_rows[nota_en_edicion_index] = [fecha_actual, titulo_final, c]
        else:
            cache_rows.append([fecha_actual, titulo_final, c])
            
        sincronizar_disco()
        page.overlay.append(ft.SnackBar(ft.Text("Nota guardada exitosamente"), open=True))
        cambiar_vista_inicio()

    # --- BARRAS SUPERIORES (APPBARS) ---
    appbar_inicio = ft.AppBar(
        title=ft.Text("Mis Notas", weight="bold", no_wrap=True),
        actions=[
            ft.TextButton("Temas", on_click=lambda e: abrir_menu_temas()),
            ft.TextButton("Añadir", icon="add", on_click=lambda e: cambiar_vista_edicion()),
            ft.Container(width=5)
        ]
    )

    appbar_edicion = ft.AppBar(
        automatically_imply_leading=False,
        leading=None,
        title=ft.Text("Gestión de Nota", weight="bold", no_wrap=True),
        actions=[
            ft.TextButton("Guardar", on_click=lambda e: guardar_y_volver()),
            ft.TextButton("X Cancelar", on_click=intentar_cancelar),
            ft.Container(width=10)
        ]
    )

    def aplicar_estilo_actual():
        t = temas[tema_actual]
        page.theme_mode = t["mode"]
        page.bgcolor = t["body_bg"]
        
        appbar_inicio.bgcolor = t["appbar_bg"]
        appbar_inicio.title.color = t["appbar_fg"]
        for action in appbar_inicio.actions:
            if isinstance(action, ft.TextButton):
                action.style = ft.ButtonStyle(color=t["appbar_fg"])

        appbar_edicion.bgcolor = t["appbar_bg"]
        appbar_edicion.title.color = t["appbar_fg"]
        for action in appbar_edicion.actions:
            if isinstance(action, ft.TextButton):
                action.style = ft.ButtonStyle(color=t["appbar_fg"])
                
        page.update()

    # --- DIÁLOGOS Y VENTANAS FLOTANTES ---
    def cerrar_dialogo_advertencia(e=None):
        dlg_advertencia.open = False
        page.update()

    def descartar_y_volver(e):
        cerrar_dialogo_advertencia()
        cambiar_vista_inicio()

    dlg_advertencia = ft.AlertDialog(
        title=ft.Text("¿Descartar nota?", weight="bold", color="red900"),
        content=ft.Text("Tienes texto escrito. Si sales ahora, se perderá. ¿Estás seguro?"),
        actions=[
            ft.TextButton("No, seguir editando", on_click=cerrar_dialogo_advertencia),
            ft.TextButton("Sí, salir", on_click=descartar_y_volver, style=ft.ButtonStyle(color="red"))
        ]
    )
    page.overlay.append(dlg_advertencia)

    index_a_borrar = None

    def cerrar_dlg_borrar(e=None):
        dlg_confirmar_borrar.open = False
        page.update()

    def ejecutar_borrar(e):
        nonlocal index_a_borrar
        if index_a_borrar is not None:
            if 0 <= index_a_borrar < len(cache_rows):
                cache_rows.pop(index_a_borrar)
                sincronizar_disco()
                    
        cerrar_dlg_borrar()
        page.overlay.append(ft.SnackBar(ft.Text("Nota borrada definitivamente"), open=True))
        cargar_notas()

    dlg_confirmar_borrar = ft.AlertDialog(
        title=ft.Text("¿Estás seguro?", weight="bold", color="red900"),
        content=ft.Text("Esta nota se borrará definitivamente y no se podrá recuperar."),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dlg_borrar),
            ft.TextButton("Sí, borrar", on_click=ejecutar_borrar, style=ft.ButtonStyle(color="red"))
        ]
    )
    page.overlay.append(dlg_confirmar_borrar)

    txt_detalle_titulo = ft.Text("", weight="bold", size=20, no_wrap=True)
    txt_detalle_fecha = ft.Text("", size=12, color="grey", no_wrap=True)
    txt_detalle_contenido = ft.TextField(
        multiline=True, 
        read_only=True, 
        border=ft.InputBorder.NONE, 
        expand=True
    )

    dlg_detalle = ft.AlertDialog(
        title=txt_detalle_titulo,
        content=ft.Container(
            content=ft.Column([
                txt_detalle_fecha,
                ft.Divider(),
                txt_detalle_contenido
            ], expand=True),
            width=500,
            height=400
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar_vista_detalle())
        ]
    )
    page.overlay.append(dlg_detalle)

    def abrir_detalle(titulo, fecha, contenido):
        txt_detalle_titulo.value = titulo
        txt_detalle_fecha.value = f"Creado/Modificado: {fecha}"
        txt_detalle_contenido.value = contenido
        dlg_detalle.open = True
        page.update()

    def cerrar_vista_detalle():
        dlg_detalle.open = False
        page.update()

    dlg_info = ft.AlertDialog(
        title=ft.Text("Información", weight="bold"),
        content=ft.Column([
            ft.Text("Versión: 2.3.0"),
            ft.Text("Creador: Tú (Desarrollador)"),
            ft.Text("Block de Notas con Temas Coordinados.")
        ], tight=True),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar_info())
        ]
    )
    page.overlay.append(dlg_info)

    def cerrar_info():
        dlg_info.open = False
        page.update()

    # --- CAMBIO DE TEMA ---
    def cambiar_tema(nombre_tema):
        nonlocal tema_actual
        tema_actual = nombre_tema
        dlg_menu_temas.open = False
        aplicar_estilo_actual()
        cargar_notas()

    def abrir_informacion(e):
        dlg_menu_temas.open = False
        page.update()
        dlg_info.open = True
        page.update()

    # --- MENÚ DE TEMAS (DIÁLOGO CON BOTONES DE TEXTO) ---
    dlg_menu_temas = ft.AlertDialog(
        title=ft.Text("Elige un Tema", weight="bold"),
        content=ft.Column(
            controls=[
                ft.TextButton("Tema Claro", icon="light_mode", on_click=lambda e: cambiar_tema("Claro")),
                ft.TextButton("Tema Oscuro Clásico", icon="dark_mode", on_click=lambda e: cambiar_tema("Oscuro")),
                ft.TextButton("Rojo Pasión", icon="local_fire_department", on_click=lambda e: cambiar_tema("Rojo Pasión")),
                ft.TextButton("Verde Esmeralda", icon="eco", on_click=lambda e: cambiar_tema("Verde Esmeralda")),
                ft.TextButton("Púrpura Místico", icon="auto_awesome", on_click=lambda e: cambiar_tema("Púrpura Místico")),
                ft.TextButton("Ámbar Neón", icon="flash_on", on_click=lambda e: cambiar_tema("Ámbar Neón")),
                ft.Divider(),
                ft.TextButton("Información", icon="info_outline", on_click=lambda e: abrir_informacion(e)),
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar_menu_temas())
        ]
    )
    page.overlay.append(dlg_menu_temas)

    def abrir_menu_temas():
        dlg_menu_temas.open = True
        page.update()

    def cerrar_menu_temas():
        dlg_menu_temas.open = False
        page.update()

    # --- CONTENEDORES DE LAS VISTAS ---
    lista_notas_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    vista_inicio = ft.Column([lista_notas_ui], expand=True)
    
    vista_edicion = ft.Column(
        controls=[in_titulo, in_contenido], 
        expand=True, 
        visible=False
    )

    def preparar_editar(idx, titulo, contenido):
        nonlocal nota_en_edicion_index
        nota_en_edicion_index = idx
        in_titulo.value = titulo
        in_contenido.value = contenido
        vista_inicio.visible = False
        vista_edicion.visible = True
        page.appbar = appbar_edicion
        aplicar_estilo_actual()

    def preparar_borrar(idx):
        nonlocal index_a_borrar
        index_a_borrar = idx
        dlg_confirmar_borrar.open = True
        page.update()

    # --- RENDERIZAR LA LISTA DE NOTAS ---
    def cargar_notas():
        t = temas[tema_actual]
        lista_notas_ui.controls.clear()
        
        if not cache_rows:
            lista_notas_ui.controls.append(
                ft.Container(
                    content=ft.Row(
                        [ft.Text("No hay notas. Presiona 'Añadir' para crear una.", color=t["date_color"], no_wrap=True)],
                        alignment="center"
                    ),
                    padding=50
                )
            )
        else:
            for idx in range(len(cache_rows) - 1, -1, -1):
                fila = cache_rows[idx]
                if len(fila) >= 3:
                    fecha, titulo, contenido = fila[0], fila[1], fila[2]
                    
                    item = ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(titulo, weight="bold", size=16, expand=True, color=t["card_fg"], no_wrap=True),
                                    ft.Text(fecha, size=12, color=t["date_color"], no_wrap=True)
                                ], expand=True),
                                expand=True,
                                on_click=lambda e, t_val=titulo, f_val=fecha, c_val=contenido: abrir_detalle(t_val, f_val, c_val)
                            ),
                            ft.PopupMenuButton(
                                icon="more_vert",
                                icon_color=t["card_fg"],
                                items=[
                                    ft.PopupMenuItem(content=ft.Text("Editar"), on_click=lambda e, i=idx, tit=titulo, con=contenido: preparar_editar(i, tit, con)),
                                    ft.PopupMenuItem(content=ft.Text("Borrar"), on_click=lambda e, i=idx: preparar_borrar(i)),
                                ]
                            )
                        ]),
                        bgcolor=t["card_bg"],
                        padding=15,
                        border_radius=8,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=3,
                            color="#000000" if t["mode"] == ft.ThemeMode.DARK else "#dcdde1",
                            offset=ft.Offset(0, 1)
                        )
                    )
                    lista_notas_ui.controls.append(item)
        page.update()

    # --- ARRANQUE INICIAL ---
    page.add(vista_inicio, vista_edicion)
    cambiar_vista_inicio()

try:
    ft.run(main, view=ft.AppView.WEB_BROWSER)
except AttributeError:
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    
