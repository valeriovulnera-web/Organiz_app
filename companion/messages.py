import random
from datetime import datetime

# ── Greetings ────────────────────────────────────────────────────────────────

_GREETINGS_MORNING = [
    "Buongiorno! Una nuova giornata piena di possibilità ti aspetta.",
    "Buongiorno! Il momento migliore per iniziare è adesso.",
    "Ciao! Il mattino è tuo. Cosa conquisti oggi?",
    "Buongiorno! Inizia con energia: la giornata promette bene.",
]

_GREETINGS_AFTERNOON = [
    "Ciao! Il pomeriggio è nel pieno — ancora tempo per fare grandi cose.",
    "Ehi! Come stai andando? Dai, un passo alla volta!",
    "Buon pomeriggio! Non mollare, sei a metà strada.",
    "Ciao! Il pomeriggio è perfetto per un secondo slancio.",
]

_GREETINGS_EVENING = [
    "Buonasera! Hai fatto del tuo meglio oggi, e questo conta.",
    "Ehi! La serata è ottima per rivedere i progressi di oggi.",
    "Buonasera! Qualche task ancora aperta? Chiudiamola insieme.",
    "Ciao! La sera è il momento giusto per pianificare domani.",
]

_GREETINGS_NIGHT = [
    "Ciao nottambulo! Rispetto per chi lavora anche di notte.",
    "Sei ancora sveglio? Ricordati di riposare — domani si ricomincia!",
    "Notte fonda, ma sei qui. Cosa vuoi sistemare prima di dormire?",
]

# ── Task feedback ─────────────────────────────────────────────────────────────

_TASK_COMPLETED = [
    "Ottimo lavoro! Hai completato un'altra task. Avanti così!",
    "Bravo! Ogni piccola vittoria conta. Continua!",
    "Fatto! Un passo alla volta si arriva lontano.",
    "Eccellente! Lo sapevo che ce l'avresti fatta.",
    "Sì! Un task in meno, una soddisfazione in più.",
    "Perfetto! La costanza è il tuo superpotere.",
]

_TASK_ALL_DONE = [
    "INCREDIBILE! Hai completato tutto per oggi. Sei un mito! 🏆",
    "Lista svuotata! Prenditi una pausa, te la sei guadagnata. 🎉",
    "WOW! Tutte le task completate. Sei straordinario! 🌟",
    "Giornata da 10! Hai finito tutto — ora goditi il merito. 🚀",
]

# ── Dashboard messages ────────────────────────────────────────────────────────

_NO_TASKS = [
    "Nessuna task ancora! Aggiungine una e inizia il tuo percorso. 🚀",
    "La lista è vuota. Cosa vuoi realizzare oggi?",
    "Pronti a partire! Aggiungi la tua prima task.",
]

_OVERDUE = [
    "Ho visto che hai task in ritardo. Oggi è il giorno giusto per recuperare!",
    "Alcune cose aspettano da un po'. Inizia dalla più semplice — prenditi lo slancio!",
    "Task scadute? Nessun problema, l'importante è riprendere. Ce la fai!",
]

_MANY_TODAY = [
    "Hai {} task per oggi. Inizia dalla più importante e non guardare indietro!",
    "Giornata da {} obiettivi. Attaccali uno alla volta — ce la fai!",
    "{} task oggi. Dividile per priorità e vai: sei più forte di quanto pensi.",
]

_FEW_TODAY = [
    "Oggi hai solo {} cosa da fare. Facile — concentrati e chiudila!",
    "Giornata leggera: {} task. Perfetto per fare le cose per bene.",
]

_ALL_CAUGHT_UP = [
    "Sei in regola con tutto! Aggiorna la lista o goditi il merito. 😎",
    "Nessuna task urgente. Pianifica la prossima mossa!",
]

# ── Motivational quotes ───────────────────────────────────────────────────────

_QUOTES = [
    "\"Il segreto per andare avanti è iniziare.\" — Mark Twain",
    "\"Non aspettare. Il momento perfetto non arriverà mai.\" — Napoleone Hill",
    "\"Ogni grande viaggio inizia con un singolo passo.\" — Lao Tzu",
    "\"Il successo è la somma di piccoli sforzi ripetuti ogni giorno.\" — R. Collier",
    "\"Fai quello che puoi, con quello che hai, dove sei.\" — Theodore Roosevelt",
    "\"La disciplina è il ponte tra gli obiettivi e i risultati.\" — Jim Rohn",
    "\"Non rimandare a domani quello che puoi fare oggi.\" — Benjamin Franklin",
    "\"Ogni giorno fai qualcosa che ti spaventa un po'.\" — Eleanor Roosevelt",
    "\"Il coraggio non è assenza di paura, ma decidere che altro è più importante.\" — Ambrose Redmoon",
    "\"Chi vuole fare trova un modo. Chi non vuole trova una scusa.\" — proverbio",
    "\"Non devi essere bravo per iniziare, ma devi iniziare per diventare bravo.\" — Zig Ziglar",
    "\"Ogni mattino siamo nati di nuovo. Ciò che facciamo oggi è ciò che conta di più.\" — Buddha",
]


# ── Public API ────────────────────────────────────────────────────────────────

def get_greeting(name=""):
    hour = datetime.now().hour
    if 6 <= hour < 12:
        pool = _GREETINGS_MORNING
    elif 12 <= hour < 18:
        pool = _GREETINGS_AFTERNOON
    elif 18 <= hour < 22:
        pool = _GREETINGS_EVENING
    else:
        pool = _GREETINGS_NIGHT
    return random.choice(pool)


def get_task_completion_message(all_done=False):
    if all_done:
        return random.choice(_TASK_ALL_DONE)
    return random.choice(_TASK_COMPLETED)


def get_dashboard_message(stats):
    total = stats.get("total", 0)
    today = stats.get("today", 0)
    overdue = stats.get("overdue", 0)
    completed = stats.get("completed", 0)

    if total == 0:
        return random.choice(_NO_TASKS)
    if overdue > 0:
        return random.choice(_OVERDUE)
    if today == 0 and completed > 0:
        return random.choice(_ALL_CAUGHT_UP)
    if today >= 4:
        return random.choice(_MANY_TODAY).format(today)
    if today > 0:
        return random.choice(_FEW_TODAY).format(today)
    return get_greeting()


def get_motivational_quote():
    return random.choice(_QUOTES)


# ── Priority helpers ──────────────────────────────────────────────────────────

PRIORITY_LABELS = {1: "Bassa", 2: "Medio-bassa", 3: "Media", 4: "Alta", 5: "Urgente"}
PRIORITY_COLORS = {
    1: "#4CAF50",
    2: "#8BC34A",
    3: "#FF9800",
    4: "#FF5722",
    5: "#F44336",
}

CATEGORY_ICONS = {
    "Lavoro": "💼",
    "Casa": "🏠",
    "Studio": "📚",
    "Salute": "💪",
    "Personale": "⭐",
    "Obiettivi": "🎯",
    "Generale": "📝",
}


def priority_label(p):
    return PRIORITY_LABELS.get(p, "Media")


def priority_color(p):
    return PRIORITY_COLORS.get(p, "#FF9800")


def category_icon(cat):
    return CATEGORY_ICONS.get(cat, "📝")
