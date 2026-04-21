import flet as ft
from datetime import datetime, timedelta

from database.db_manager import (
    get_all_tasks, add_task, update_task, delete_task,
    complete_task, uncomplete_task,
)
from companion.messages import priority_color, priority_label, category_icon, PRIORITY_LABELS

SURFACE = "#1A1A2E"
CARD = "#16213E"
PRIMARY = "#7C4DFF"
TEXT = "#FFFFFE"
SUBTEXT = "#A7A9BE"

CATEGORIES = ["Generale", "Lavoro", "Casa", "Studio", "Salute", "Personale", "Obiettivi"]

_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
_MONTHS = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]


def _format_due(due_date_str):
    if not due_date_str:
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if due_date_str == today:
        return ("Oggi", "#7C4DFF")
    if due_date_str == tomorrow:
        return ("Domani", "#FF9800")
    if due_date_str < today:
        return ("Scaduta", "#F44336")
    try:
        d = datetime.strptime(due_date_str, "%Y-%m-%d")
        return (d.strftime("%d/%m"), SUBTEXT)
    except ValueError:
        return (due_date_str, SUBTEXT)


def _show_snack(page, text, color=PRIMARY):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(text, color=TEXT),
        bgcolor=color,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()


def _task_form_dialog(page, navigate, existing_task=None):
    is_edit = existing_task is not None

    title_field = ft.TextField(
        label="Titolo *",
        value=existing_task["title"] if is_edit else "",
        autofocus=not is_edit,
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    desc_field = ft.TextField(
        label="Descrizione (opzionale)",
        value=existing_task.get("description", "") if is_edit else "",
        multiline=True,
        min_lines=2,
        max_lines=4,
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    cat_dropdown = ft.Dropdown(
        label="Categoria",
        value=existing_task.get("category", "Generale") if is_edit else "Generale",
        options=[ft.dropdown.Option(c) for c in CATEGORIES],
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    priority_value = [existing_task.get("priority", 3) if is_edit else 3]
    priority_label_text = ft.Text(
        f"Priorità: {priority_label(priority_value[0])}",
        size=13,
        color=priority_color(priority_value[0]),
    )

    def on_priority_change(e):
        priority_value[0] = int(e.control.value)
        priority_label_text.value = f"Priorità: {priority_label(priority_value[0])}"
        priority_label_text.color = priority_color(priority_value[0])
        page.update()

    priority_slider = ft.Slider(
        min=1,
        max=5,
        divisions=4,
        value=float(priority_value[0]),
        label="{value}",
        active_color=PRIMARY,
        on_change=on_priority_change,
    )

    selected_date = [existing_task.get("due_date") if is_edit else None]
    date_display = ft.Text(
        selected_date[0] if selected_date[0] else "Nessuna scadenza",
        size=13,
        color=PRIMARY if selected_date[0] else SUBTEXT,
    )

    def on_date_change(e):
        if e.control.value:
            selected_date[0] = e.control.value.strftime("%Y-%m-%d")
            date_display.value = selected_date[0]
            date_display.color = PRIMARY
        else:
            selected_date[0] = None
            date_display.value = "Nessuna scadenza"
            date_display.color = SUBTEXT
        page.update()

    def clear_date(e):
        selected_date[0] = None
        date_display.value = "Nessuna scadenza"
        date_display.color = SUBTEXT
        page.update()

    date_picker = ft.DatePicker(on_change=on_date_change, first_date=datetime(2020, 1, 1))
    page.overlay.append(date_picker)

    def on_save(e):
        if not title_field.value.strip():
            title_field.error_text = "Il titolo è obbligatorio"
            page.update()
            return

        if is_edit:
            update_task(
                existing_task["id"],
                title_field.value.strip(),
                desc_field.value.strip(),
                cat_dropdown.value,
                priority_value[0],
                selected_date[0],
            )
            _show_snack(page, "✅ Task aggiornata!")
        else:
            add_task(
                title_field.value.strip(),
                desc_field.value.strip(),
                cat_dropdown.value,
                priority_value[0],
                selected_date[0],
            )
            _show_snack(page, "✅ Task aggiunta!")

        page.dialog.open = False
        if date_picker in page.overlay:
            page.overlay.remove(date_picker)
        navigate()

    def on_cancel(e):
        page.dialog.open = False
        if date_picker in page.overlay:
            page.overlay.remove(date_picker)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Modifica Task" if is_edit else "Nuova Task", color=TEXT, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                title_field,
                ft.Container(height=8),
                desc_field,
                ft.Container(height=8),
                cat_dropdown,
                ft.Container(height=12),
                priority_label_text,
                priority_slider,
                ft.Container(height=4),
                ft.Row(
                    [
                        ft.Icon(ft.icons.CALENDAR_TODAY, color=PRIMARY, size=18),
                        ft.TextButton(
                            "Scegli scadenza",
                            on_click=lambda _: date_picker.pick_date(),
                            style=ft.ButtonStyle(color=PRIMARY),
                        ),
                        date_display,
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            icon_size=16,
                            icon_color=SUBTEXT,
                            on_click=clear_date,
                            visible=bool(selected_date[0]),
                        ),
                    ],
                    spacing=4,
                    wrap=True,
                ),
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            width=320,
        ),
        actions=[
            ft.TextButton("Annulla", on_click=on_cancel, style=ft.ButtonStyle(color=SUBTEXT)),
            ft.ElevatedButton(
                "Salva",
                on_click=on_save,
                bgcolor=PRIMARY,
                color=TEXT,
            ),
        ],
        bgcolor=SURFACE,
        shape=ft.RoundedRectangleBorder(radius=16),
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


def build_tasks_view(page: ft.Page, navigate):
    current_tab = [0]
    tasks_column = ft.Column(spacing=6)

    def load_tasks():
        tasks = get_all_tasks()
        today = datetime.now().strftime("%Y-%m-%d")

        if current_tab[0] == 0:
            filtered = [t for t in tasks if not t["completed"]]
        elif current_tab[0] == 1:
            filtered = [t for t in tasks if not t["completed"] and (t["due_date"] == today or not t["due_date"])]
        else:
            filtered = [t for t in tasks if t["completed"]]

        tasks_column.controls.clear()

        if not filtered:
            tasks_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("📭", size=40),
                            ft.Text(
                                "Nessuna task qui!" if current_tab[0] < 2 else "Nessuna task completata.",
                                size=14,
                                color=SUBTEXT,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=ft.padding.symmetric(vertical=40),
                    alignment=ft.alignment.center,
                )
            )
        else:
            for task in filtered:
                tasks_column.controls.append(_build_task_card(task, page, load_tasks, navigate))

        page.update()

    def _build_task_card(task, page, refresh, navigate):
        pcolor = priority_color(task.get("priority", 3))
        icon = category_icon(task.get("category", "Generale"))
        due_info = _format_due(task.get("due_date"))

        def on_check(e):
            if e.control.value:
                complete_task(task["id"])
            else:
                uncomplete_task(task["id"])
            refresh()
            _show_snack(page, "✅ Task aggiornata!")

        def on_delete(e):
            def confirm_delete(e):
                delete_task(task["id"])
                page.dialog.open = False
                page.update()
                refresh()
                _show_snack(page, "🗑️ Task eliminata.", color="#555")

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Elimina task?", color=TEXT),
                content=ft.Text(f"Vuoi eliminare \"{task['title']}\"?", color=SUBTEXT),
                actions=[
                    ft.TextButton("Annulla", on_click=lambda _: _close_dialog(page), style=ft.ButtonStyle(color=SUBTEXT)),
                    ft.ElevatedButton("Elimina", on_click=confirm_delete, bgcolor="#F44336", color=TEXT),
                ],
                bgcolor=SURFACE,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

        def on_edit(e):
            _task_form_dialog(page, refresh, existing_task=task)

        due_chip = ft.Container()
        if due_info:
            label, color = due_info
            due_chip = ft.Container(
                content=ft.Text(label, size=10, color=color, weight=ft.FontWeight.BOLD),
                bgcolor=f"{color}22",
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Checkbox(
                                value=bool(task["completed"]),
                                fill_color=PRIMARY,
                                on_change=on_check,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        task["title"],
                                        size=14,
                                        color=TEXT,
                                        weight=ft.FontWeight.W_500,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        spans=[
                                            ft.TextSpan(
                                                style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                                            )
                                        ] if task["completed"] else [],
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(f"{icon} {task.get('category', 'Generale')}", size=11, color=SUBTEXT),
                                            ft.Container(
                                                content=ft.Text(
                                                    priority_label(task.get("priority", 3)),
                                                    size=10,
                                                    color=pcolor,
                                                ),
                                                bgcolor=f"{pcolor}22",
                                                border_radius=8,
                                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            ),
                                            due_chip,
                                        ],
                                        spacing=6,
                                        wrap=True,
                                    ),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT_OUTLINED,
                                        icon_size=18,
                                        icon_color=SUBTEXT,
                                        on_click=on_edit,
                                        tooltip="Modifica",
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE,
                                        icon_size=18,
                                        icon_color="#F44336",
                                        on_click=on_delete,
                                        tooltip="Elimina",
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    *(
                        [ft.Container(
                            content=ft.Text(task["description"], size=12, color=SUBTEXT, no_wrap=False),
                            padding=ft.padding.only(left=48, bottom=4),
                        )]
                        if task.get("description")
                        else []
                    ),
                ],
                spacing=0,
            ),
            bgcolor=CARD,
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
        )

    def on_tab_change(e):
        current_tab[0] = e.control.selected_index
        load_tasks()

    tabs = ft.Tabs(
        selected_index=0,
        on_change=on_tab_change,
        indicator_color=PRIMARY,
        label_color=PRIMARY,
        unselected_label_color=SUBTEXT,
        tabs=[
            ft.Tab(text="Aperte"),
            ft.Tab(text="Oggi"),
            ft.Tab(text="Completate"),
        ],
    )

    load_tasks()

    return ft.Stack(
        [
            ft.Column(
                [
                    ft.Text("Le tue Task", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Container(height=8),
                    tabs,
                    ft.Container(height=8),
                    tasks_column,
                    ft.Container(height=80),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0,
            ),
            ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.icons.ADD,
                    bgcolor=PRIMARY,
                    foreground_color=TEXT,
                    on_click=lambda _: _task_form_dialog(page, load_tasks),
                    tooltip="Nuova Task",
                ),
                alignment=ft.alignment.bottom_right,
                padding=ft.padding.only(right=16, bottom=16),
                expand=True,
            ),
        ],
        expand=True,
    )


def _close_dialog(page):
    page.dialog.open = False
    page.update()
