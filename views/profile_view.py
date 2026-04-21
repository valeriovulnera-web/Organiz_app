import flet as ft

from database.db_manager import get_pref, set_pref, get_stats, get_streak, clear_completed_tasks

SURFACE = "#1A1A2E"
CARD = "#16213E"
PRIMARY = "#7C4DFF"
ACCENT = "#FF6B35"
TEXT = "#FFFFFE"
SUBTEXT = "#A7A9BE"


def _show_snack(page, text, color=PRIMARY):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(text, color=TEXT),
        bgcolor=color,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()


def build_profile_view(page: ft.Page, navigate):
    name = get_pref("user_name", "Amico")
    stats = get_stats()
    streak = get_streak()
    total = stats["total"]
    completed = stats["completed"]
    rate = int((completed / total * 100) if total > 0 else 0)

    name_field = ft.TextField(
        label="Il tuo nome",
        value=name,
        bgcolor=CARD,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
        suffix=ft.IconButton(
            icon=ft.Icons.SAVE,
            icon_color=PRIMARY,
            tooltip="Salva nome",
            on_click=lambda e: save_name(),
        ),
    )

    def save_name():
        new_name = name_field.value.strip()
        if new_name:
            set_pref("user_name", new_name)
            _show_snack(page, f"👋 Ciao, {new_name}!")
            navigate()
        else:
            name_field.error_text = "Inserisci un nome"
            page.update()

    def _stat_row(label, value, color=TEXT):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(label, size=13, color=SUBTEXT, expand=True),
                    ft.Text(str(value), size=14, color=color, weight=ft.FontWeight.BOLD),
                ],
            ),
            bgcolor=CARD,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

    def on_clear_completed(e):
        def confirm(e):
            clear_completed_tasks()
            page.dialog.open = False
            page.update()
            navigate(3)
            _show_snack(page, "🧹 Task completate eliminate!")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Svuota completate?", color=TEXT),
            content=ft.Text(
                "Vuoi eliminare tutte le task già completate? Questa azione non è reversibile.",
                color=SUBTEXT,
                no_wrap=False,
            ),
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

    streak_color = ACCENT if streak >= 3 else PRIMARY

    return ft.Column(
        [
            # Avatar + name
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text("🧑", size=48),
                            bgcolor=f"{PRIMARY}33",
                            border_radius=50,
                            padding=16,
                            alignment=ft.Alignment(0, 0),
                            width=88,
                            height=88,
                        ),
                        ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Organiz — il tuo spazio personale", size=12, color=SUBTEXT),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.only(bottom=20),
            ),
            # Change name
            ft.Text("Impostazioni", size=13, color=SUBTEXT, weight=ft.FontWeight.BOLD),
            ft.Container(height=6),
            name_field,
            ft.Container(height=20),
            # Stats
            ft.Text("Le tue statistiche", size=13, color=SUBTEXT, weight=ft.FontWeight.BOLD),
            ft.Container(height=6),
            ft.Column(
                [
                    _stat_row("📋 Task totali create", total),
                    _stat_row("✅ Task completate", completed, "#4CAF50"),
                    _stat_row("⚠️ Task scadute", stats["overdue"], "#FF5722"),
                    _stat_row("📈 Tasso di completamento", f"{rate}%", PRIMARY),
                    _stat_row(
                        "🔥 Streak attuale",
                        f"{streak} {'giorno' if streak == 1 else 'giorni'}",
                        streak_color,
                    ),
                ],
                spacing=6,
            ),
            ft.Container(height=20),
            # Orion companion info
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("🤖", size=28),
                        ft.Column(
                            [
                                ft.Text("Orion — il tuo companion", size=13, color=PRIMARY, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Sono qui per motivarti, ricordarti i tuoi obiettivi "
                                    "e festeggiare ogni tuo traguardo. Conta su di me!",
                                    size=12,
                                    color=SUBTEXT,
                                    no_wrap=False,
                                ),
                            ],
                            expand=True,
                            spacing=4,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                bgcolor=f"{PRIMARY}1A",
                border_radius=14,
                padding=14,
            ),
            ft.Container(height=20),
            # Danger zone
            ft.Text("Gestione dati", size=13, color=SUBTEXT, weight=ft.FontWeight.BOLD),
            ft.Container(height=6),
            ft.ElevatedButton(
                "🧹 Elimina task completate",
                on_click=on_clear_completed,
                bgcolor=CARD,
                color="#F44336",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                width=float("inf"),
            ),
            ft.Container(height=80),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )


def _close_dialog(page):
    page.dialog.open = False
    page.update()
