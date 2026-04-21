import flet as ft
from datetime import datetime, timedelta

from database.db_manager import get_stats, get_all_tasks, get_pref, complete_task, uncomplete_task, get_streak
from companion.messages import get_dashboard_message, get_motivational_quote, priority_color, category_icon

_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
_MONTHS = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

SURFACE = "#1A1A2E"
CARD = "#16213E"
PRIMARY = "#7C4DFF"
ACCENT = "#FF6B35"
TEXT = "#FFFFFE"
SUBTEXT = "#A7A9BE"


def _format_due(due_date_str):
    if not due_date_str:
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if due_date_str == today:
        return "Oggi"
    if due_date_str == tomorrow:
        return "Domani"
    if due_date_str == yesterday:
        return "Ieri"
    try:
        d = datetime.strptime(due_date_str, "%Y-%m-%d")
        return d.strftime("%d/%m")
    except ValueError:
        return due_date_str


def _stat_card(emoji, value, label, color):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(emoji, size=22),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=11, color=SUBTEXT),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=CARD,
        border_radius=14,
        padding=ft.padding.symmetric(vertical=14, horizontal=8),
        expand=True,
    )


def build_dashboard(page: ft.Page, navigate):
    name = get_pref("user_name", "Amico")
    stats = get_stats()
    streak = get_streak()
    all_tasks = get_all_tasks()
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = [
        t for t in all_tasks
        if not t["completed"] and (t["due_date"] == today or not t["due_date"])
    ]

    now = datetime.now()
    date_str = f"{_DAYS[now.weekday()]}, {now.day} {_MONTHS[now.month - 1]} {now.year}"
    hour = now.hour
    if 6 <= hour < 12:
        saluto = "Buongiorno"
    elif 12 <= hour < 18:
        saluto = "Buon pomeriggio"
    elif 18 <= hour < 22:
        saluto = "Buonasera"
    else:
        saluto = "Ciao"

    def on_complete(e, task_id):
        if e.control.value:
            complete_task(task_id)
        else:
            uncomplete_task(task_id)
        remaining = stats["today"] - (1 if e.control.value else -1)
        all_done = remaining <= 0 and stats["total"] > 0
        from companion.messages import get_task_completion_message
        msg = get_task_completion_message(all_done=all_done)
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"🤖 {msg}", color=TEXT),
            bgcolor=PRIMARY,
            duration=3000,
        )
        page.snack_bar.open = True
        navigate()

    def task_row(task):
        due_label = _format_due(task.get("due_date"))
        pcolor = priority_color(task.get("priority", 3))
        icon = category_icon(task.get("category", "Generale"))
        subtitle_parts = [f"{icon} {task.get('category', 'Generale')}"]
        if due_label:
            subtitle_parts.append(f"📅 {due_label}")

        return ft.Container(
            content=ft.Row(
                [
                    ft.Checkbox(
                        value=bool(task["completed"]),
                        fill_color=PRIMARY,
                        on_change=lambda e, tid=task["id"]: on_complete(e, tid),
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
                            ),
                            ft.Text("  ·  ".join(subtitle_parts), size=11, color=SUBTEXT),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Container(
                        width=6,
                        height=6,
                        border_radius=3,
                        bgcolor=pcolor,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CARD,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            margin=ft.margin.only(bottom=6),
        )

    task_items = (
        [task_row(t) for t in today_tasks[:5]]
        if today_tasks
        else [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("🎉", size=36),
                        ft.Text("Nessuna task per oggi!", size=14, color=SUBTEXT),
                        ft.Text("Aggiungine una nella sezione Task", size=11, color=SUBTEXT),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                padding=ft.padding.symmetric(vertical=20),
                alignment=ft.alignment.CENTER,
            )
        ]
    )

    streak_display = (
        ft.Container(
            content=ft.Row(
                [
                    ft.Text("🔥", size=16),
                    ft.Text(
                        f"Streak: {streak} {'giorno' if streak == 1 else 'giorni'} di fila!",
                        size=13,
                        color=ACCENT,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=6,
            ),
            bgcolor=f"{ACCENT}22",
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
        )
        if streak > 0
        else ft.Container()
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"{saluto}, {name}! 👋", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text(date_str, size=12, color=SUBTEXT),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    streak_display,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=14),
            # Orion companion card
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("🤖", size=26),
                            bgcolor=f"{PRIMARY}33",
                            border_radius=30,
                            padding=10,
                        ),
                        ft.Column(
                            [
                                ft.Text("Orion", size=11, color=PRIMARY, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    get_dashboard_message(stats),
                                    size=13,
                                    color=TEXT,
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
                bgcolor=SURFACE,
                border_radius=16,
                padding=16,
            ),
            ft.Container(height=14),
            # Stats row
            ft.Row(
                [
                    _stat_card("📋", str(stats["today"]), "Oggi", PRIMARY),
                    _stat_card("✅", str(stats["completed"]), "Completate", "#4CAF50"),
                    _stat_card("⚠️", str(stats["overdue"]), "Scadute", "#FF5722"),
                ],
                spacing=8,
            ),
            ft.Container(height=20),
            # Today's tasks
            ft.Row(
                [
                    ft.Text("📌 Task di oggi", size=15, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.TextButton(
                        "Vedi tutto →",
                        on_click=lambda _: navigate(1),
                        style=ft.ButtonStyle(color=PRIMARY),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=6),
            *task_items,
            ft.Container(height=16),
            # Quote of the day
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("💭 Frase del giorno", size=11, color=SUBTEXT, weight=ft.FontWeight.BOLD),
                        ft.Container(height=4),
                        ft.Text(get_motivational_quote(), size=13, color=TEXT, italic=True, no_wrap=False),
                    ],
                    spacing=0,
                ),
                bgcolor=SURFACE,
                border_radius=16,
                padding=16,
            ),
            ft.Container(height=80),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )
