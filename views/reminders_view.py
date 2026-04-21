import flet as ft
from datetime import datetime, timedelta

from database.db_manager import get_all_reminders, add_reminder, delete_reminder

SURFACE = "#1A1A2E"
CARD = "#16213E"
PRIMARY = "#7C4DFF"
ACCENT = "#FF6B35"
TEXT = "#FFFFFE"
SUBTEXT = "#A7A9BE"

RECURRENCE_OPTIONS = {
    "none": "Nessuna ricorrenza",
    "daily": "Ogni giorno",
    "weekly": "Ogni settimana",
}


def _show_snack(page, text, color=PRIMARY):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(text, color=TEXT),
        bgcolor=color,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()


def _format_remind_at(remind_at_str):
    try:
        dt = datetime.strptime(remind_at_str, "%Y-%m-%d %H:%M")
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        date_str = dt.strftime("%Y-%m-%d")
        if date_str == today:
            prefix = "Oggi"
        elif date_str == tomorrow:
            prefix = "Domani"
        else:
            prefix = dt.strftime("%d/%m/%Y")
        return f"{prefix} alle {dt.strftime('%H:%M')}"
    except ValueError:
        return remind_at_str


def _is_past(remind_at_str):
    try:
        dt = datetime.strptime(remind_at_str, "%Y-%m-%d %H:%M")
        return dt < datetime.now()
    except ValueError:
        return False


def _add_reminder_dialog(page, refresh):
    title_field = ft.TextField(
        label="Titolo promemoria *",
        autofocus=True,
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    message_field = ft.TextField(
        label="Messaggio (opzionale)",
        multiline=True,
        min_lines=2,
        max_lines=3,
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    recurrence_dropdown = ft.Dropdown(
        label="Ricorrenza",
        value="none",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in RECURRENCE_OPTIONS.items()],
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    selected_date = [datetime.now().strftime("%Y-%m-%d")]
    selected_time = [datetime.now().strftime("%H:%M")]

    date_display = ft.Text(selected_date[0], size=13, color=PRIMARY)
    time_display = ft.Text(selected_time[0], size=13, color=PRIMARY)

    def on_date_change(e):
        if e.control.value:
            selected_date[0] = e.control.value.strftime("%Y-%m-%d")
            date_display.value = selected_date[0]
        page.update()

    def on_time_change(e):
        if e.control.value:
            t = e.control.value
            selected_time[0] = f"{t.hour:02d}:{t.minute:02d}"
            time_display.value = selected_time[0]
        page.update()

    date_picker = ft.DatePicker(on_change=on_date_change, first_date=datetime(2020, 1, 1))
    time_picker = ft.TimePicker(on_change=on_time_change, confirm_text="OK", cancel_text="Annulla")
    page.overlay.extend([date_picker, time_picker])

    def on_save(e):
        if not title_field.value.strip():
            title_field.error_text = "Il titolo è obbligatorio"
            page.update()
            return

        remind_at = f"{selected_date[0]} {selected_time[0]}"
        add_reminder(
            title=title_field.value.strip(),
            remind_at=remind_at,
            message=message_field.value.strip(),
            recurrence=recurrence_dropdown.value,
        )
        page.dialog.open = False
        for picker in [date_picker, time_picker]:
            if picker in page.overlay:
                page.overlay.remove(picker)
        _show_snack(page, "🔔 Promemoria aggiunto!")
        refresh()

    def on_cancel(e):
        page.dialog.open = False
        for picker in [date_picker, time_picker]:
            if picker in page.overlay:
                page.overlay.remove(picker)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuovo Promemoria", color=TEXT, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                title_field,
                ft.Container(height=8),
                message_field,
                ft.Container(height=12),
                ft.Text("Data e ora", size=12, color=SUBTEXT),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "📅 Data",
                            on_click=lambda _: date_picker.pick_date(),
                            bgcolor=CARD,
                            color=PRIMARY,
                        ),
                        date_display,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "🕐 Ora",
                            on_click=lambda _: time_picker.pick_time(),
                            bgcolor=CARD,
                            color=PRIMARY,
                        ),
                        time_display,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=8),
                recurrence_dropdown,
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            width=320,
        ),
        actions=[
            ft.TextButton("Annulla", on_click=on_cancel, style=ft.ButtonStyle(color=SUBTEXT)),
            ft.ElevatedButton("Salva", on_click=on_save, bgcolor=PRIMARY, color=TEXT),
        ],
        bgcolor=SURFACE,
        shape=ft.RoundedRectangleBorder(radius=16),
    )
    page.dialog = dialog
    dialog.open = True
    page.update()


def build_reminders_view(page: ft.Page, navigate):
    reminders_column = ft.Column(spacing=8)

    def load_reminders():
        reminders = get_all_reminders()
        reminders_column.controls.clear()

        if not reminders:
            reminders_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("🔕", size=40),
                            ft.Text("Nessun promemoria attivo.", size=14, color=SUBTEXT),
                            ft.Text("Aggiungine uno con il pulsante +", size=11, color=SUBTEXT),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=ft.padding.symmetric(vertical=40),
                    alignment=ft.alignment.CENTER,
                )
            )
        else:
            for r in reminders:
                reminders_column.controls.append(_reminder_card(r, page, load_reminders))

        page.update()

    def _reminder_card(r, page, refresh):
        past = _is_past(r["remind_at"])
        recurrence_label = RECURRENCE_OPTIONS.get(r.get("recurrence", "none"), "")
        time_color = "#F44336" if past else ACCENT

        def on_delete(e):
            def confirm(e):
                delete_reminder(r["id"])
                page.dialog.open = False
                page.update()
                refresh()
                _show_snack(page, "🗑️ Promemoria eliminato.", color="#555")

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Elimina promemoria?", color=TEXT),
                content=ft.Text(f"Vuoi eliminare \"{r['title']}\"?", color=SUBTEXT),
                actions=[
                    ft.TextButton("Annulla", on_click=lambda _: _close_dialog(page), style=ft.ButtonStyle(color=SUBTEXT)),
                    ft.ElevatedButton("Elimina", on_click=confirm, bgcolor="#F44336", color=TEXT),
                ],
                bgcolor=SURFACE,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        status_icon = "⏰" if not past else "🔴"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(status_icon, size=24),
                        bgcolor=f"{ACCENT}22",
                        border_radius=24,
                        padding=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(r["title"], size=14, color=TEXT, weight=ft.FontWeight.W_500),
                            ft.Text(
                                _format_remind_at(r["remind_at"]),
                                size=12,
                                color=time_color,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                [
                                    ft.Text(recurrence_label, size=11, color=SUBTEXT),
                                    *(
                                        [ft.Text(f"· {r['message']}", size=11, color=SUBTEXT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)]
                                        if r.get("message")
                                        else []
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        expand=True,
                        spacing=3,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_size=18,
                        icon_color="#F44336",
                        on_click=on_delete,
                        tooltip="Elimina",
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CARD,
            border_radius=14,
            padding=14,
        )

    load_reminders()

    return ft.Stack(
        [
            ft.Column(
                [
                    ft.Text("Promemoria", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Container(height=4),
                    ft.Text("I tuoi promemoria attivi", size=13, color=SUBTEXT),
                    ft.Container(height=12),
                    reminders_column,
                    ft.Container(height=80),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0,
            ),
            ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.ADD_ALERT,
                    bgcolor=ACCENT,
                    foreground_color=TEXT,
                    on_click=lambda _: _add_reminder_dialog(page, load_reminders),
                    tooltip="Nuovo Promemoria",
                ),
                alignment=ft.alignment.BOTTOM_RIGHT,
                padding=ft.padding.only(right=16, bottom=16),
                expand=True,
            ),
        ],
        expand=True,
    )


def _close_dialog(page):
    page.dialog.open = False
    page.update()
