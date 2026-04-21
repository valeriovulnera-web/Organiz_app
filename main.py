import flet as ft

from database.db_manager import init_db, get_pref, set_pref, get_due_reminders
from views.dashboard import build_dashboard
from views.tasks_view import build_tasks_view
from views.reminders_view import build_reminders_view
from views.profile_view import build_profile_view

BG = "#0D0D1A"
SURFACE = "#1A1A2E"
PRIMARY = "#7C4DFF"
ACCENT = "#FF6B35"
TEXT = "#FFFFFE"
SUBTEXT = "#A7A9BE"

NAV_ITEMS = [
    ("Home", ft.icons.HOME_OUTLINED, ft.icons.HOME),
    ("Task", ft.icons.CHECK_BOX_OUTLINED, ft.icons.CHECK_BOX),
    ("Promemoria", ft.icons.NOTIFICATIONS_OUTLINED, ft.icons.NOTIFICATIONS),
    ("Profilo", ft.icons.PERSON_OUTLINED, ft.icons.PERSON),
]


def main(page: ft.Page):
    page.title = "Organiz"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = ft.padding.only(left=16, right=16, top=16)
    page.window_width = 420
    page.window_height = 820

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            secondary=ACCENT,
            surface=SURFACE,
            background=BG,
            on_primary=TEXT,
        ),
        font_family="Roboto",
    )

    init_db()

    current_index = [0]
    main_content = ft.Container(expand=True)

    def navigate(index=None):
        if index is not None:
            current_index[0] = index
        idx = current_index[0]
        nav_bar.selected_index = idx

        builders = [
            lambda: build_dashboard(page, navigate),
            lambda: build_tasks_view(page, navigate),
            lambda: build_reminders_view(page, navigate),
            lambda: build_profile_view(page, navigate),
        ]
        main_content.content = builders[idx]()
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=icon_off,
                selected_icon=icon_on,
                label=label,
            )
            for label, icon_off, icon_on in NAV_ITEMS
        ],
        selected_index=0,
        on_change=lambda e: navigate(e.control.selected_index),
        bgcolor=SURFACE,
        indicator_color=f"{PRIMARY}55",
        surface_tint_color=PRIMARY,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
    )

    page.add(
        ft.Column(
            [main_content, nav_bar],
            expand=True,
            spacing=0,
        )
    )

    # First launch onboarding
    name = get_pref("user_name")
    if not name:
        _show_onboarding(page, navigate)
    else:
        navigate(0)
        _check_due_reminders(page, navigate)


def _show_onboarding(page: ft.Page, navigate):
    name_field = ft.TextField(
        label="Come ti chiami?",
        hint_text="Es. Marco, Giulia...",
        autofocus=True,
        bgcolor="#16213E",
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=SUBTEXT),
    )

    def on_start(e):
        raw = name_field.value.strip()
        name = raw if raw else "Amico"
        set_pref("user_name", name)
        page.dialog.open = False
        page.update()
        navigate(0)
        _check_due_reminders(page, navigate)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Benvenuto in Organiz! 🚀", color=TEXT, size=18, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("🤖", size=48),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "Ciao! Sono Orion, il tuo assistente personale.\n"
                    "Ti aiuterò a organizzarti, ricordarti le cose importanti "
                    "e spronare te a raggiungere i tuoi obiettivi ogni giorno.",
                    color=SUBTEXT,
                    size=13,
                    no_wrap=False,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                name_field,
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=300,
        ),
        actions=[
            ft.ElevatedButton(
                "Iniziamo! 🎯",
                on_click=on_start,
                bgcolor=PRIMARY,
                color=TEXT,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        bgcolor=SURFACE,
        shape=ft.RoundedRectangleBorder(radius=20),
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


def _check_due_reminders(page: ft.Page, navigate):
    due = get_due_reminders()
    if not due:
        return
    count = len(due)
    label = f"🔔 Hai {count} promemoria {'in scadenza' if count == 1 else 'in scadenza'}!"
    page.snack_bar = ft.SnackBar(
        content=ft.Text(label, color=TEXT),
        bgcolor=ACCENT,
        duration=4000,
    )
    page.snack_bar.open = True
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
