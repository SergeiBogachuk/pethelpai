from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


EVENT_TYPES = [
    "vaccination",
    "medication",
    "parasite_treatment",
    "deworming",
    "vet_visit",
    "grooming",
    "nail_trim",
    "food_purchase",
    "follow_up_exam",
    "custom",
]

EVENT_TYPE_LABELS = {
    "en": {
        "vaccination": "Vaccination",
        "medication": "Medication",
        "parasite_treatment": "Flea / tick treatment",
        "deworming": "Deworming",
        "vet_visit": "Vet visit",
        "grooming": "Grooming",
        "nail_trim": "Nail trim",
        "food_purchase": "Food purchase",
        "follow_up_exam": "Follow-up exam",
        "custom": "Custom event",
    },
    "ru": {
        "vaccination": "Прививка",
        "medication": "Лекарство",
        "parasite_treatment": "Обработка от блох / клещей",
        "deworming": "Дегельминтизация",
        "vet_visit": "Визит к ветеринару",
        "grooming": "Груминг",
        "nail_trim": "Стрижка когтей",
        "food_purchase": "Покупка корма",
        "follow_up_exam": "Повторное обследование",
        "custom": "Свое событие",
    },
}

RECURRENCE_OPTIONS = ["none", "daily", "weekly", "monthly", "yearly"]
RECURRENCE_LABELS = {
    "en": {
        "none": "One time",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "yearly": "Yearly",
    },
    "ru": {
        "none": "Один раз",
        "daily": "Ежедневно",
        "weekly": "Еженедельно",
        "monthly": "Ежемесячно",
        "yearly": "Ежегодно",
    },
}

REMINDER_OPTIONS = ["3d", "1d", "12h", "day_of"]
REMINDER_LABELS = {
    "en": {"3d": "3 days before", "1d": "1 day before", "12h": "12 hours before", "day_of": "Same day"},
    "ru": {"3d": "За 3 дня", "1d": "За 1 день", "12h": "За 12 часов", "day_of": "В день события"},
}

LOG_TYPES = ["symptom", "note", "procedure_result"]
LOG_TYPE_LABELS = {
    "en": {"symptom": "Symptom", "note": "General note", "procedure_result": "After procedure"},
    "ru": {"symptom": "Симптом", "note": "Заметка", "procedure_result": "После процедуры"},
}

SEVERITY_OPTIONS = ["light", "medium", "strong"]
SEVERITY_LABELS = {
    "en": {"light": "Light", "medium": "Medium", "strong": "Strong"},
    "ru": {"light": "Легкая", "medium": "Средняя", "strong": "Сильная"},
}

MEDICATION_FREQUENCIES = ["once", "every_12h", "daily", "weekly", "monthly"]
MEDICATION_FREQUENCY_LABELS = {
    "en": {
        "once": "Once",
        "every_12h": "Every 12 hours",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
    },
    "ru": {
        "once": "Один раз",
        "every_12h": "Каждые 12 часов",
        "daily": "Каждый день",
        "weekly": "Раз в неделю",
        "monthly": "Раз в месяц",
    },
}

EXPENSE_CATEGORIES = ["food", "vet", "medications", "grooming", "toys", "accessories", "insurance", "other"]
EXPENSE_CATEGORY_LABELS = {
    "en": {
        "food": "Food",
        "vet": "Veterinary",
        "medications": "Medications",
        "grooming": "Grooming",
        "toys": "Toys",
        "accessories": "Accessories",
        "insurance": "Insurance",
        "other": "Other",
    },
    "ru": {
        "food": "Корм",
        "vet": "Ветеринар",
        "medications": "Лекарства",
        "grooming": "Груминг",
        "toys": "Игрушки",
        "accessories": "Аксессуары",
        "insurance": "Страховка",
        "other": "Прочее",
    },
}

DOCUMENT_TYPES = ["passport", "certificate", "lab_result", "receipt", "prescription", "other"]
DOCUMENT_TYPE_LABELS = {
    "en": {
        "passport": "Pet passport",
        "certificate": "Certificate",
        "lab_result": "Lab result",
        "receipt": "Receipt",
        "prescription": "Vet prescription",
        "other": "Other",
    },
    "ru": {
        "passport": "Паспорт животного",
        "certificate": "Сертификат",
        "lab_result": "Результат анализа",
        "receipt": "Чек",
        "prescription": "Назначение врача",
        "other": "Прочее",
    },
}

SEX_OPTIONS = ["female", "male", "unknown"]
SEX_LABELS = {
    "en": {"female": "Female", "male": "Male", "unknown": "Unknown"},
    "ru": {"female": "Девочка", "male": "Мальчик", "unknown": "Не указано"},
}

SPECIES_OPTIONS = ["dog", "cat", "other"]
SPECIES_LABELS = {
    "en": {"dog": "Dog", "cat": "Cat", "other": "Other"},
    "ru": {"dog": "Собака", "cat": "Кошка", "other": "Другое"},
}

SMART_RECOMMENDATIONS = {
    "en": {
        "add_first_event": "You already added a pet. The next value moment is your first care event.",
        "weight_overdue": "Weight has not been updated in a while. Add a fresh weight entry.",
        "food_repeat": "Food expenses are recurring often. Consider adding a food purchase reminder.",
        "medication_end": "A medication course is near its end. Confirm whether the course should be closed.",
        "starter_calendar_puppy": "Because this looks like a young pet, use the starter care calendar.",
        "no_activity": "There has been little recent activity. A quick update keeps the timeline useful.",
        "document_locked": "Document storage is part of Premium. Upgrade when you want a full record vault.",
    },
    "ru": {
        "add_first_event": "Питомец уже добавлен. Следующая точка ценности — первое событие ухода.",
        "weight_overdue": "Вес давно не обновляли. Добавь свежую запись о весе.",
        "food_repeat": "Расходы на корм повторяются часто. Можно добавить напоминание о покупке корма.",
        "medication_end": "Курс лекарства подходит к концу. Стоит подтвердить, завершен ли он.",
        "starter_calendar_puppy": "Питомец выглядит молодым — можно использовать стартовый календарь ухода.",
        "no_activity": "Давно не было активности. Короткое обновление сохранит пользу таймлайна.",
        "document_locked": "Хранение документов входит в Premium. Обновление откроет полный архив по питомцу.",
    },
}


def language_code(language: str | None) -> str:
    return "ru" if str(language or "").lower().startswith("ru") else "en"


def label(mapping: dict[str, dict[str, str]], key: str, language: str) -> str:
    lang = language_code(language)
    return mapping[lang].get(key, key)


def format_datetime(value: str | None, language: str) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if language_code(language) == "ru":
        return dt.strftime("%d.%m.%Y %H:%M")
    return dt.strftime("%b %d, %Y %H:%M")


def format_date(value: str | None, language: str) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if language_code(language) == "ru":
        return dt.strftime("%d.%m.%Y")
    return dt.strftime("%b %d, %Y")


def pet_age_display(birth_date: str | None, age_text: str | None, language: str) -> str:
    if age_text:
        return age_text
    if not birth_date:
        return "—"
    try:
        born = datetime.fromisoformat(birth_date)
    except ValueError:
        return birth_date
    days = max((datetime.utcnow() - born).days, 0)
    if days < 30:
        return f"{days} d" if language_code(language) == "en" else f"{days} д"
    if days < 365:
        months = max(days // 30, 1)
        return f"{months} mo" if language_code(language) == "en" else f"{months} мес"
    years = round(days / 365, 1)
    return f"{years} y" if language_code(language) == "en" else f"{years} г"


def event_status(event: dict[str, Any]) -> str:
    status = event.get("status") or "planned"
    if status == "planned":
        scheduled_at = event.get("scheduled_at")
        try:
            dt = datetime.fromisoformat(scheduled_at)
        except (TypeError, ValueError):
            return status
        if dt < datetime.utcnow():
            return "missed"
    return status


def status_badge(status: str, language: str) -> str:
    mapping = {
        "planned": {"en": "Planned", "ru": "Запланировано"},
        "completed": {"en": "Completed", "ru": "Выполнено"},
        "missed": {"en": "Missed", "ru": "Пропущено"},
        "free": {"en": "Free", "ru": "Free"},
        "trialing": {"en": "Trial", "ru": "Триал"},
        "active": {"en": "Premium", "ru": "Premium"},
        "canceled": {"en": "Canceled", "ru": "Отменено"},
    }
    return mapping.get(status, {}).get(language_code(language), status)


def next_due_text(subscription: dict[str, Any], language: str) -> str:
    status = subscription.get("status", "free")
    if status == "trialing":
        key = subscription.get("trial_ends_at")
    else:
        key = subscription.get("renewal_at") or subscription.get("expires_at")
    if not key:
        return "—"
    return format_datetime(key, language)


def pet_month_expense(expenses: list[dict[str, Any]], pet_id: int) -> float:
    month_prefix = datetime.utcnow().strftime("%Y-%m")
    return sum(float(item["amount"]) for item in expenses if item["pet_id"] == pet_id and str(item["spent_at"]).startswith(month_prefix))


def pet_recent_records(
    pet_id: int,
    events: list[dict[str, Any]],
    logs: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for event in events:
        if event["pet_id"] == pet_id:
            items.append(
                {
                    "kind": "event",
                    "title": event["title"],
                    "timestamp": event.get("completed_at") or event.get("scheduled_at"),
                }
            )
    for log in logs:
        if log["pet_id"] == pet_id:
            items.append(
                {
                    "kind": "log",
                    "title": log.get("symptom") or log.get("description") or log.get("log_type", "log"),
                    "timestamp": log.get("recorded_at"),
                }
            )
    items.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    return items[:limit]


def smart_recommendations(
    *,
    pets: list[dict[str, Any]],
    events: list[dict[str, Any]],
    weights: list[dict[str, Any]],
    expenses: list[dict[str, Any]],
    medications: list[dict[str, Any]],
    subscription: dict[str, Any],
    language: str = "en",
) -> list[str]:
    lang = language_code(language)
    tips: list[str] = []
    if pets and not events:
        tips.append(SMART_RECOMMENDATIONS[lang]["add_first_event"])

    if pets:
        last_weight = weights[-1]["measured_at"] if weights else None
        if last_weight:
            try:
                if datetime.utcnow() - datetime.fromisoformat(last_weight) > timedelta(days=30):
                    tips.append(SMART_RECOMMENDATIONS[lang]["weight_overdue"])
            except ValueError:
                pass
        else:
            tips.append(SMART_RECOMMENDATIONS[lang]["weight_overdue"])

    month_counts = sum(1 for expense in expenses if expense["category"] == "food" and str(expense["spent_at"]).startswith(datetime.utcnow().strftime("%Y-%m")))
    if month_counts >= 2:
        tips.append(SMART_RECOMMENDATIONS[lang]["food_repeat"])

    for med in medications:
        next_due = med.get("next_due_at")
        end_date = med.get("end_date")
        if end_date and next_due:
            try:
                if datetime.fromisoformat(end_date) - datetime.utcnow() < timedelta(days=2):
                    tips.append(SMART_RECOMMENDATIONS[lang]["medication_end"])
                    break
            except ValueError:
                continue

    for pet in pets:
        age_text = (pet.get("age_text") or "").lower()
        birth_date = pet.get("birth_date")
        young = any(word in age_text for word in ["kitten", "puppy", "котен", "щен"])
        if birth_date and not young:
            try:
                young = datetime.utcnow() - datetime.fromisoformat(birth_date) < timedelta(days=365)
            except ValueError:
                young = False
        if young:
            tips.append(SMART_RECOMMENDATIONS[lang]["starter_calendar_puppy"])
            break

    if not subscription.get("status") in {"trialing", "active"}:
        tips.append(SMART_RECOMMENDATIONS[lang]["document_locked"])

    if not tips and pets:
        tips.append(SMART_RECOMMENDATIONS[lang]["no_activity"])

    deduped: list[str] = []
    for item in tips:
        if item not in deduped:
            deduped.append(item)
    return deduped[:4]


def starter_calendar_template(species: str, language: str) -> list[dict[str, Any]]:
    lang = language_code(language)
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    def title(en: str, ru: str) -> str:
        return ru if lang == "ru" else en

    if species == "cat":
        return [
            {
                "type": "parasite_treatment",
                "title": title("Monthly parasite treatment", "Ежемесячная обработка от паразитов"),
                "description": title("Repeat every month so it is not forgotten.", "Повторяется каждый месяц, чтобы не забыть."),
                "scheduled_at": (now + timedelta(days=7)).isoformat(),
                "recurrence_rule": "monthly",
                "reminder_settings": ["3d", "1d", "day_of"],
            },
            {
                "type": "nail_trim",
                "title": title("Nail trim check", "Проверка когтей"),
                "description": title("Quick reminder to trim or check nails.", "Короткое напоминание проверить или подстричь когти."),
                "scheduled_at": (now + timedelta(days=14)).isoformat(),
                "recurrence_rule": "monthly",
                "reminder_settings": ["1d", "day_of"],
            },
            {
                "type": "food_purchase",
                "title": title("Check food stock", "Проверить запас корма"),
                "description": title("Restock before food runs out.", "Пополнить корм до того, как он закончится."),
                "scheduled_at": (now + timedelta(days=10)).isoformat(),
                "recurrence_rule": "monthly",
                "reminder_settings": ["3d", "day_of"],
            },
        ]
    return [
        {
            "type": "parasite_treatment",
            "title": title("Monthly flea and tick treatment", "Ежемесячная обработка от блох и клещей"),
            "description": title("Keeps regular parasite control visible.", "Позволяет держать регулярную обработку под контролем."),
            "scheduled_at": (now + timedelta(days=7)).isoformat(),
            "recurrence_rule": "monthly",
            "reminder_settings": ["3d", "1d", "day_of"],
        },
        {
            "type": "nail_trim",
            "title": title("Nail trim", "Стрижка когтей"),
            "description": title("Short routine care reminder.", "Короткое рутинное напоминание по уходу."),
            "scheduled_at": (now + timedelta(days=14)).isoformat(),
            "recurrence_rule": "monthly",
            "reminder_settings": ["1d", "day_of"],
        },
        {
            "type": "food_purchase",
            "title": title("Check food bag", "Проверить запас корма"),
            "description": title("Avoid last-minute food runs.", "Чтобы не вспоминать о корме в последний момент."),
            "scheduled_at": (now + timedelta(days=10)).isoformat(),
            "recurrence_rule": "monthly",
            "reminder_settings": ["3d", "day_of"],
        },
    ]


def upcoming_warning_level(items: list[dict[str, Any]]) -> str:
    if not items:
        return "calm"
    now = datetime.utcnow()
    for item in items:
        try:
            if datetime.fromisoformat(item["scheduled_at"]) <= now + timedelta(hours=12):
                return "urgent"
        except (KeyError, ValueError, TypeError):
            continue
    return "watch"
