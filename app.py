from __future__ import annotations

import base64
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote_plus
from uuid import uuid4

import streamlit as st

from engine import (
    analyze_food,
    answer_follow_up,
    extract_food_context_from_image,
    get_care_tips,
    has_openai_key,
)
from styles import inject_styles


CONDITION_OPTIONS = [
    "Pancreatitis",
    "Kidney disease",
    "Diabetes",
    "Sensitive stomach",
    "Food allergies",
    "Heart disease",
]

SYMPTOM_OPTIONS = [
    "Vomiting",
    "Diarrhea",
    "Drooling",
    "Lethargy",
    "Restlessness",
    "Tremors",
    "Stumbling",
    "Pale gums",
    "Trouble breathing",
    "Collapse",
    "Seizure",
]

AMOUNT_OPTIONS = ["Lick or crumb", "Small bite", "Moderate portion", "Large portion"]
TIME_OPTIONS = ["Within 30 minutes", "30 minutes to 2 hours", "2 to 6 hours ago", "More than 6 hours ago"]
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_CANDIDATES = ["logo.svg", "logo.png", "logo.webp", "logo.jpg", "logo.jpeg"]
LANGUAGE_OPTIONS = ["ru", "en"]

UI_TEXT = {
    "en": {
        "language": "Language",
        "language_ru": "Русский",
        "language_en": "English",
        "tagline": "Fast food-safety checks for dogs and cats",
        "active_pet": "Active pet",
        "pet_profile": "Pet profile",
        "draft_pet": "Draft pet profile",
        "accurate_profile": "Accurate age and weight make the result more reliable.",
        "pet_name": "Pet name",
        "species": "Species",
        "dog": "Dog",
        "cat": "Cat",
        "age_years": "Age (years)",
        "weight_lb": "Weight (lb)",
        "breed_or_mix": "Breed or mix",
        "allergies": "Allergies",
        "allergies_placeholder": "Chicken, dairy, beef",
        "conditions": "Conditions",
        "save_profile": "Save pet profile",
        "update_profile": "Update pet profile",
        "delete_pet": "Delete active pet",
        "profile_saved": "Profile saved for {name}.",
        "how_verdicts_work": "How verdicts work",
        "verdict_safe_expl": "`Safe` means relatively low risk when plain and portion-controlled.",
        "verdict_caution_expl": "`Caution` means ingredient, amount, or pet-specific risk needs a closer look.",
        "verdict_avoid_expl": "`Avoid` means pause and escalate quickly, especially if the food was already eaten.",
        "vet_note": "For urgent or worsening symptoms, contact a veterinarian.",
        "food_tab": "Food Check",
        "emergency_tab": "Emergency Mode",
        "care_tab": "Care Guide",
        "history_tab": "History",
        "food_title": "Food Check",
        "food_caption": "Describe the food first. If it was already eaten, switch to Emergency Mode.",
        "add_photo": "Add photo (optional)",
        "image_input": "Image input",
        "skip_image": "Skip image",
        "use_camera": "Use camera",
        "upload_photo": "Upload photo",
        "photo_api_note": "Photo-only checks need OPENAI_API_KEY. Text checks already work.",
        "take_picture": "Take a picture of the food or packaging",
        "upload_food_photo": "Upload a food photo",
        "photo_caption": "Photo for analysis",
        "food_description": "Food description or ingredients",
        "food_placeholder": "Example: peanut butter, banana, plain yogurt\nOr: chicken nuggets with ketchup\nOr paste the ingredient list from the package",
        "already_ate": "My pet already ate some of this",
        "amount": "Amount",
        "food_examples": "Examples: peanut butter, rotisserie chicken, garlic bread, grapes, yogurt",
        "analyze_food": "Analyze food safety",
        "need_input": "Add a food description, an ingredient list, or a photo first.",
        "photo_only_warning": "For photo-only checks, add `OPENAI_API_KEY` or type a short food description below the image.",
        "reading_photo": "Reading the photo...",
        "result": "Result",
        "empty_food_title": "Type the food first, then get the verdict.",
        "empty_food_copy": "You will see one clear result and the immediate next steps below.",
        "ask_follow_up": "Ask a follow-up",
        "question": "Question",
        "follow_up_placeholder": "What symptoms should I watch for?",
        "answer_follow_up": "Answer follow-up",
        "emergency_title": "Emergency Mode",
        "emergency_caption": "Use this only if the food was already eaten or symptoms have started.",
        "what_was_eaten": "What was eaten?",
        "emergency_placeholder": "Example: half a chocolate chip cookie\nOr: garlic pizza crust\nOr: sugar-free gum",
        "how_much": "How much?",
        "when_happened": "When did it happen?",
        "symptoms_optional": "Symptoms (optional but helpful)",
        "current_symptoms": "Current symptoms",
        "run_emergency": "Run emergency review",
        "emergency_need_input": "Describe what your pet ate so I can triage the risk.",
        "empty_emergency_title": "Use this when the food is already eaten.",
        "empty_emergency_copy": "This path weighs symptoms, amount, and known toxins more aggressively than the regular food check.",
        "care_title": "Personalized care guide",
        "care_caption": "A calmer everyday baseline based on the active pet profile.",
        "safer_picks": "Safer Everyday Picks",
        "double_check": "Always Double-Check",
        "profile_notes": "Profile-Specific Notes",
        "recent_checks": "Recent checks",
        "clear_history": "Clear history",
        "history_title": "No checks yet",
        "history_copy": "Run a food safety scan or emergency review and your recent decisions will show up here.",
        "what_to_do": "What To Do Now",
        "why_verdict": "Why This Verdict",
        "symptoms_to_watch": "Symptoms to watch",
        "more_detail": "More detail",
        "detected_signals": "Detected signals",
        "image_read": "Photo read",
        "confidence": "Confidence: {value}",
        "swap_idea": "Swap Idea {index}",
        "chewy": "Chewy",
        "amazon": "Amazon",
        "photo_read_title": "What I see in the photo",
        "history_food": "Food Check",
        "history_emergency": "Emergency Mode",
    },
    "ru": {
        "language": "Язык",
        "language_ru": "Русский",
        "language_en": "English",
        "tagline": "Быстрая проверка еды для собак и кошек",
        "active_pet": "Активный питомец",
        "pet_profile": "Профиль питомца",
        "draft_pet": "Черновик профиля питомца",
        "accurate_profile": "Точный возраст и вес делают результат надежнее.",
        "pet_name": "Имя питомца",
        "species": "Вид",
        "dog": "Собака",
        "cat": "Кошка",
        "age_years": "Возраст (лет)",
        "weight_lb": "Вес (lb)",
        "breed_or_mix": "Порода или метис",
        "allergies": "Аллергии",
        "allergies_placeholder": "Курица, молочное, говядина",
        "conditions": "Состояния",
        "save_profile": "Сохранить профиль",
        "update_profile": "Обновить профиль",
        "delete_pet": "Удалить активного питомца",
        "profile_saved": "Профиль для {name} сохранен.",
        "how_verdicts_work": "Как работают вердикты",
        "verdict_safe_expl": "`Можно` значит относительно низкий риск, если еда простая и порция маленькая.",
        "verdict_caution_expl": "`Осторожно` значит, что состав, количество или профиль питомца требуют более внимательной проверки.",
        "verdict_avoid_expl": "`Нельзя` значит, что лучше остановиться и быстрее усилить осторожность, особенно если еда уже съедена.",
        "vet_note": "Если симптомы срочные или усиливаются, свяжитесь с ветеринаром.",
        "food_tab": "Проверка еды",
        "emergency_tab": "Экстренный режим",
        "care_tab": "Гид по уходу",
        "history_tab": "История",
        "food_title": "Проверка еды",
        "food_caption": "Сначала опиши еду. Если питомец уже съел это, перейди в экстренный режим.",
        "add_photo": "Добавить фото (необязательно)",
        "image_input": "Источник изображения",
        "skip_image": "Без фото",
        "use_camera": "Камера",
        "upload_photo": "Загрузить фото",
        "photo_api_note": "Для проверки только по фото нужен OPENAI_API_KEY. Текстовая проверка уже работает.",
        "take_picture": "Сделай фото еды или упаковки",
        "upload_food_photo": "Загрузи фото еды",
        "photo_caption": "Фото для анализа",
        "food_description": "Описание еды или ингредиенты",
        "food_placeholder": "Например: арахисовая паста, банан, простой йогурт\nИли: куриные наггетсы с кетчупом\nИли вставь состав с упаковки",
        "already_ate": "Питомец уже это съел",
        "amount": "Количество",
        "food_examples": "Примеры: арахисовая паста, курица-гриль, чесночный хлеб, виноград, йогурт",
        "analyze_food": "Проверить безопасность еды",
        "need_input": "Сначала добавь описание еды, состав или фото.",
        "photo_only_warning": "Для проверки только по фото добавь `OPENAI_API_KEY` или напиши короткое описание еды под фото.",
        "reading_photo": "Читаю фото...",
        "result": "Результат",
        "empty_food_title": "Сначала введи еду, потом получишь вердикт.",
        "empty_food_copy": "Ниже появится один понятный вывод и следующие шаги.",
        "ask_follow_up": "Задать уточняющий вопрос",
        "question": "Вопрос",
        "follow_up_placeholder": "За какими симптомами мне следить?",
        "answer_follow_up": "Ответить",
        "emergency_title": "Экстренный режим",
        "emergency_caption": "Используй это только если еда уже съедена или симптомы уже начались.",
        "what_was_eaten": "Что было съедено?",
        "emergency_placeholder": "Например: половина печенья с шоколадом\nИли: корочка пиццы с чесноком\nИли: жвачка без сахара",
        "how_much": "Сколько?",
        "when_happened": "Когда это произошло?",
        "symptoms_optional": "Симптомы (необязательно, но полезно)",
        "current_symptoms": "Текущие симптомы",
        "run_emergency": "Запустить экстренную проверку",
        "emergency_need_input": "Опиши, что именно съел питомец, чтобы я мог оценить риск.",
        "empty_emergency_title": "Используй этот режим, когда еда уже съедена.",
        "empty_emergency_copy": "Здесь симптомы, количество и известные токсины оцениваются строже, чем в обычной проверке еды.",
        "care_title": "Персональный гид по уходу",
        "care_caption": "Спокойная повседневная база с учетом активного профиля питомца.",
        "safer_picks": "Более безопасные варианты на каждый день",
        "double_check": "Что всегда перепроверять",
        "profile_notes": "Заметки под профиль питомца",
        "recent_checks": "Последние проверки",
        "clear_history": "Очистить историю",
        "history_title": "Пока нет проверок",
        "history_copy": "Сделай проверку еды или экстренный разбор, и последние решения появятся здесь.",
        "what_to_do": "Что делать сейчас",
        "why_verdict": "Почему такой вердикт",
        "symptoms_to_watch": "За какими симптомами следить",
        "more_detail": "Больше деталей",
        "detected_signals": "Обнаруженные сигналы",
        "image_read": "Что прочитано с фото",
        "confidence": "Уверенность: {value}",
        "swap_idea": "Идея замены {index}",
        "chewy": "Chewy",
        "amazon": "Amazon",
        "photo_read_title": "Что я вижу на фото",
        "history_food": "Проверка еды",
        "history_emergency": "Экстренный режим",
    },
}

DISPLAY_LABELS = {
    "Pancreatitis": {"en": "Pancreatitis", "ru": "Панкреатит"},
    "Kidney disease": {"en": "Kidney disease", "ru": "Болезнь почек"},
    "Diabetes": {"en": "Diabetes", "ru": "Диабет"},
    "Sensitive stomach": {"en": "Sensitive stomach", "ru": "Чувствительный желудок"},
    "Food allergies": {"en": "Food allergies", "ru": "Пищевые аллергии"},
    "Heart disease": {"en": "Heart disease", "ru": "Болезнь сердца"},
    "Vomiting": {"en": "Vomiting", "ru": "Рвота"},
    "Diarrhea": {"en": "Diarrhea", "ru": "Диарея"},
    "Drooling": {"en": "Drooling", "ru": "Слюнотечение"},
    "Lethargy": {"en": "Lethargy", "ru": "Вялость"},
    "Restlessness": {"en": "Restlessness", "ru": "Беспокойство"},
    "Tremors": {"en": "Tremors", "ru": "Тремор"},
    "Stumbling": {"en": "Stumbling", "ru": "Шаткость"},
    "Pale gums": {"en": "Pale gums", "ru": "Бледные десны"},
    "Trouble breathing": {"en": "Trouble breathing", "ru": "Трудное дыхание"},
    "Collapse": {"en": "Collapse", "ru": "Коллапс"},
    "Seizure": {"en": "Seizure", "ru": "Судорога"},
    "Lick or crumb": {"en": "Lick or crumb", "ru": "Лизок или крошка"},
    "Small bite": {"en": "Small bite", "ru": "Маленький кусочек"},
    "Moderate portion": {"en": "Moderate portion", "ru": "Средняя порция"},
    "Large portion": {"en": "Large portion", "ru": "Большая порция"},
    "Within 30 minutes": {"en": "Within 30 minutes", "ru": "В течение 30 минут"},
    "30 minutes to 2 hours": {"en": "30 minutes to 2 hours", "ru": "От 30 минут до 2 часов"},
    "2 to 6 hours ago": {"en": "2 to 6 hours ago", "ru": "2–6 часов назад"},
    "More than 6 hours ago": {"en": "More than 6 hours ago", "ru": "Больше 6 часов назад"},
}


@st.cache_data(show_spinner=False)
def load_logo_data_uri() -> str:
    mime_by_suffix = {
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".webp": "image/webp",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    for filename in LOGO_CANDIDATES:
        path = ASSETS_DIR / filename
        if not path.exists():
            continue

        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        mime_type = mime_by_suffix.get(path.suffix.lower(), "image/png")
        return f"data:{mime_type};base64,{encoded}"

    return ""


def t(language: str, key: str, **kwargs: object) -> str:
    template = UI_TEXT.get(language, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))
    return template.format(**kwargs)


def display_label(language: str, value: str) -> str:
    return DISPLAY_LABELS.get(value, {}).get(language, value)


def ensure_state() -> None:
    st.session_state.setdefault("pet_profiles", [])
    st.session_state.setdefault("selected_profile_id", "__new__")
    st.session_state.setdefault("last_food_analysis", None)
    st.session_state.setdefault("last_emergency_analysis", None)
    st.session_state.setdefault("food_follow_up_answer", "")
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("language", "ru")


def make_profile(
    profile_id: str,
    name: str,
    species: str,
    age_years: float,
    weight_lbs: float,
    breed: str,
    allergies: str,
    conditions: list[str],
) -> dict[str, object]:
    clean_name = name.strip() or "Your pet"
    return {
        "id": profile_id,
        "name": clean_name,
        "species": species,
        "age_years": float(age_years or 0),
        "weight_lbs": float(weight_lbs or 0),
        "breed": breed.strip(),
        "allergies": allergies.strip(),
        "conditions": conditions,
    }


def get_profile(profile_id: str) -> dict[str, object] | None:
    for profile in st.session_state.pet_profiles:
        if profile["id"] == profile_id:
            return profile
    return None


def upsert_profile(profile: dict[str, object]) -> None:
    for index, existing in enumerate(st.session_state.pet_profiles):
        if existing["id"] == profile["id"]:
            st.session_state.pet_profiles[index] = profile
            return
    st.session_state.pet_profiles.append(profile)


def remove_profile(profile_id: str) -> None:
    st.session_state.pet_profiles = [
        profile for profile in st.session_state.pet_profiles if profile["id"] != profile_id
    ]


def format_profile_label(profile: dict[str, object], language: str) -> str:
    name = str(profile.get("name") or "Your pet")
    species = display_label(language, str(profile.get("species") or "Dog"))
    weight = profile.get("weight_lbs") or 0
    return f"{name} • {species} • {weight:.0f} lb"


def current_pet_summary(profile: dict[str, object], language: str) -> str:
    breed = str(profile.get("breed") or "").strip()
    species = display_label(language, str(profile.get("species") or "Dog"))
    age_years = float(profile.get("age_years") or 0)
    weight_lbs = float(profile.get("weight_lbs") or 0)
    details = [species]

    if age_years:
        details.append(f"{age_years:.0f} {'лет' if language == 'ru' else 'years'}")
    if weight_lbs:
        details.append(f"{weight_lbs:.0f} lb")
    if breed:
        details.append(breed)

    return " • ".join(details)


def render_header(current_pet: dict[str, object], language: str) -> None:
    right_copy = current_pet_summary(current_pet, language)
    logo_data_uri = load_logo_data_uri()
    logo_markup = (
        f'<img src="{logo_data_uri}" alt="Pet Help AI logo" class="brand-mark" />'
        if logo_data_uri
        else '<div class="brand-fallback">PH</div>'
    )

    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand-lockup">
                {logo_markup}
                <div>
                    <div class="brand-name">Pet Help AI</div>
                    <div class="brand-domain">{escape(t(language, "tagline"))}</div>
                </div>
            </div>
            <div class="app-summary">
                <div class="app-summary-label">{escape(t(language, "active_pet"))}</div>
                <div class="app-summary-name">{escape(str(current_pet.get("name") or t(language, "draft_pet")))}</div>
                <div class="app-summary-copy">{escape(right_copy)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_soft_note(message: str) -> None:
    st.markdown(
        f'<div class="soft-note">{escape(message)}</div>',
        unsafe_allow_html=True,
    )


def render_empty_state(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="section-kicker">{escape(kicker)}</div>
            <h3>{escape(title)}</h3>
            <p>{escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detail_card(title: str, items: list[str]) -> None:
    bullets = "".join(f"<li>{escape(item)}</li>" for item in items)
    st.markdown(
        f"""
        <div class="detail-card">
            <h4>{escape(title)}</h4>
            <ul>{bullets}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summary_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def shop_search_url(provider: str, query: str) -> str:
    encoded = quote_plus(query)
    if provider == "Chewy":
        return f"https://www.chewy.com/s?query={encoded}"
    return f"https://www.amazon.com/s?k={encoded}"


def render_safe_swap(analysis: dict[str, object], language: str) -> None:
    safe_swap = analysis.get("safe_swap") or {}
    items = safe_swap.get("items") or []
    if not items:
        return

    if analysis.get("verdict") == "Avoid" and analysis.get("already_ate"):
        render_soft_note(
            "В этой ситуации главное — ветеринарная помощь. Блок Safe Swap лучше использовать позже, для следующей покупки, а не вместо помощи."
            if language == "ru"
            else "This case is urgent enough that the immediate focus should stay on veterinary guidance. Safe Swap is better used for the next shopping run, not instead of care."
        )
        return

    def _render_swap_body() -> None:
        if safe_swap.get("subtitle"):
            st.caption(str(safe_swap["subtitle"]))

        for index, item in enumerate(items):
            st.markdown(
                f"""
                <div class="swap-card">
                    <div class="swap-label">{escape(t(language, "swap_idea", index=index + 1))}</div>
                    <h4>{escape(str(item['title']))}</h4>
                    <p>{escape(str(item['why']))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            link_col1, link_col2 = st.columns(2)
            with link_col1:
                st.link_button(
                    t(language, "chewy"),
                    shop_search_url("Chewy", str(item["query"])),
                    use_container_width=True,
                )
            with link_col2:
                st.link_button(
                    t(language, "amazon"),
                    shop_search_url("Amazon", str(item["query"])),
                    use_container_width=True,
                )

        if safe_swap.get("note"):
            st.caption(str(safe_swap["note"]))

    if analysis.get("verdict") == "Safe":
        with st.expander(str(safe_swap.get("title") or "Safe Swap"), expanded=False):
            _render_swap_body()
        return

    st.markdown(f"### {escape(str(safe_swap.get('title') or 'Safe Swap'))}")
    _render_swap_body()


def render_analysis(analysis: dict[str, object], language: str) -> None:
    verdict = str(analysis["verdict"]).lower()
    badge_color = str(analysis["badge_color"])
    matched_labels = analysis.get("matched_labels") or []

    st.markdown(
        f"""
        <div class="result-card result-{verdict}">
            <div class="result-pill" style="color:{badge_color};">{escape(str(analysis['badge_label']))}</div>
            <h2 class="result-title">{escape(str(analysis.get('verdict_display') or analysis['verdict']))}</h2>
            <p class="result-copy">{escape(str(analysis['summary']))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confidence_value = {
        "high": "Высокая" if language == "ru" else "High",
        "medium": "Средняя" if language == "ru" else "Medium",
        "low": "Низкая" if language == "ru" else "Low",
    }.get(str(analysis["confidence"]).lower(), str(analysis["confidence"]))
    st.caption(t(language, "confidence", value=confidence_value))

    if analysis.get("image_summary"):
        render_detail_card(t(language, "photo_read_title"), summary_lines(str(analysis["image_summary"])))

    render_detail_card(t(language, "what_to_do"), list(analysis["actions"])[:3])
    render_detail_card(
        t(language, "why_verdict"),
        list(analysis["reasons"])[:3]
        or (["Нужна более точная проверка состава."] if language == "ru" else ["The item needs a closer ingredient check."]),
    )

    with st.expander(t(language, "symptoms_to_watch"), expanded=str(analysis["verdict"]) == "Avoid"):
        for symptom in analysis["watch_for"]:
            st.write(f"- {symptom}")

    if matched_labels:
        with st.expander(t(language, "more_detail"), expanded=False):
            if matched_labels:
                st.caption(t(language, "detected_signals"))
                st.write(", ".join(matched_labels))

    render_safe_swap(analysis, language)


def add_to_history(channel: str, analysis: dict[str, object], current_pet: dict[str, object]) -> None:
    item = {
        "id": uuid4().hex[:8],
        "channel": channel,
        "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),
        "verdict": analysis["verdict"],
        "verdict_display": analysis.get("verdict_display", analysis["verdict"]),
        "summary": analysis["summary"],
        "food_text": analysis.get("food_text") or "Image-led scan",
        "pet_name": current_pet.get("name") or "Your pet",
    }
    st.session_state.history = [item] + st.session_state.history[:19]


def render_list_card(title: str, items: list[str]) -> None:
    bullets = "".join(f"<li>{escape(item)}</li>" for item in items)
    st.markdown(
        f"""
        <div class="surface-card">
            <div class="section-kicker">{escape(title)}</div>
            <ul>{bullets}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history(language: str) -> None:
    if not st.session_state.history:
        render_empty_state(
            t(language, "history_tab"),
            t(language, "history_title"),
            t(language, "history_copy"),
        )
        return

    for item in st.session_state.history:
        channel_label = t(language, "history_food") if item["channel"] == "food" else t(language, "history_emergency")
        st.markdown(
            f"""
            <div class="history-item">
                <div class="history-meta">{escape(item['timestamp'])} • {escape(channel_label)} • {escape(item['pet_name'])}</div>
                <strong>{escape(str(item.get('verdict_display') or item['verdict']))}</strong> — {escape(item['summary'])}<br/>
                <span class="history-meta">{escape(str(item['food_text']))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def sidebar_profile_editor(language: str) -> dict[str, object]:
    profiles = st.session_state.pet_profiles
    options = ["__new__"] + [profile["id"] for profile in profiles]
    labels = {"__new__": t(language, "draft_pet")}
    labels.update({profile["id"]: format_profile_label(profile, language) for profile in profiles})

    if st.session_state.selected_profile_id not in options:
        st.session_state.selected_profile_id = "__new__"

    with st.expander(t(language, "pet_profile"), expanded=True):
        selected_profile_id = st.selectbox(
            t(language, "active_pet"),
            options=options,
            index=options.index(st.session_state.selected_profile_id),
            format_func=lambda profile_id: labels[profile_id],
            key="profile_selector",
        )
        st.session_state.selected_profile_id = selected_profile_id
        selected_profile = get_profile(selected_profile_id) if selected_profile_id != "__new__" else None

        defaults = selected_profile or {
            "id": "__draft__",
            "name": "",
            "species": "Dog",
            "age_years": 4.0,
            "weight_lbs": 25.0,
            "breed": "",
            "allergies": "",
            "conditions": [],
        }

        st.caption(t(language, "accurate_profile"))

        with st.form(f"pet-profile-form-{selected_profile_id}"):
            name = st.text_input(t(language, "pet_name"), value=str(defaults.get("name") or ""))
            species = st.radio(
                t(language, "species"),
                options=["Dog", "Cat"],
                index=0 if defaults.get("species") == "Dog" else 1,
                horizontal=True,
                format_func=lambda option: display_label(language, option),
            )
            age_years = st.number_input(t(language, "age_years"), min_value=0.0, max_value=30.0, value=float(defaults.get("age_years") or 0), step=1.0)
            weight_lbs = st.number_input(t(language, "weight_lb"), min_value=0.0, max_value=250.0, value=float(defaults.get("weight_lbs") or 0), step=1.0)
            breed = st.text_input(t(language, "breed_or_mix"), value=str(defaults.get("breed") or ""))
            allergies = st.text_input(
                t(language, "allergies"),
                value=str(defaults.get("allergies") or ""),
                placeholder=t(language, "allergies_placeholder"),
            )
            conditions = st.multiselect(
                t(language, "conditions"),
                options=CONDITION_OPTIONS,
                default=list(defaults.get("conditions") or []),
                format_func=lambda option: display_label(language, option),
            )
            submitted = st.form_submit_button(
                t(language, "save_profile") if selected_profile_id == "__new__" else t(language, "update_profile"),
                use_container_width=True,
            )

        draft_profile = make_profile(
            profile_id=selected_profile_id if selected_profile_id != "__new__" else "__draft__",
            name=name,
            species=species,
            age_years=age_years,
            weight_lbs=weight_lbs,
            breed=breed,
            allergies=allergies,
            conditions=conditions,
        )

        if submitted:
            profile_to_save = dict(draft_profile)
            if selected_profile_id == "__new__":
                profile_to_save["id"] = uuid4().hex[:8]
            upsert_profile(profile_to_save)
            st.session_state.selected_profile_id = str(profile_to_save["id"])
            st.success(t(language, "profile_saved", name=profile_to_save["name"]))
            st.rerun()

        if selected_profile_id != "__new__" and st.button(t(language, "delete_pet"), use_container_width=True):
            remove_profile(selected_profile_id)
            st.session_state.selected_profile_id = "__new__"
            st.rerun()

    with st.expander(t(language, "how_verdicts_work"), expanded=False):
        st.write(t(language, "verdict_safe_expl"))
        st.write(t(language, "verdict_caution_expl"))
        st.write(t(language, "verdict_avoid_expl"))

    st.caption(t(language, "vet_note"))

    return draft_profile if selected_profile_id == "__new__" else (selected_profile or draft_profile)


def main() -> None:
    st.set_page_config(
        page_title="Pet Help AI",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    ensure_state()
    inject_styles()

    with st.sidebar:
        language = st.selectbox(
            t(st.session_state.language, "language"),
            options=LANGUAGE_OPTIONS,
            index=LANGUAGE_OPTIONS.index(st.session_state.language),
            format_func=lambda option: t(st.session_state.language, f"language_{option}"),
            key="language",
        )
        current_pet = sidebar_profile_editor(language)

    render_header(current_pet, language)

    food_tab, emergency_tab, care_tab, history_tab = st.tabs(
        [t(language, "food_tab"), t(language, "emergency_tab"), t(language, "care_tab"), t(language, "history_tab")]
    )

    with food_tab:
        st.markdown(f"### {t(language, 'food_title')}")
        st.caption(t(language, "food_caption"))

        image_file = None
        with st.expander(t(language, "add_photo"), expanded=False):
            image_mode = st.radio(
                t(language, "image_input"),
                options=["Skip image", "Use camera", "Upload photo"],
                horizontal=True,
                format_func=lambda option: t(
                    language,
                    {"Skip image": "skip_image", "Use camera": "use_camera", "Upload photo": "upload_photo"}[option],
                ),
            )
            if not has_openai_key():
                st.caption(t(language, "photo_api_note"))

            if image_mode == "Use camera":
                image_file = st.camera_input(t(language, "take_picture"))
            elif image_mode == "Upload photo":
                image_file = st.file_uploader(t(language, "upload_food_photo"), type=["jpg", "jpeg", "png"], key="food_uploader")

            if image_file is not None:
                st.image(image_file, caption=t(language, "photo_caption"), use_container_width=True)

        manual_text = st.text_area(
            t(language, "food_description"),
            placeholder=t(language, "food_placeholder"),
            height=160,
        )
        control_col1, control_col2 = st.columns(2)
        with control_col1:
            already_ate = st.toggle(t(language, "already_ate"))
        with control_col2:
            amount = st.select_slider(
                t(language, "amount"),
                options=AMOUNT_OPTIONS,
                value="Small bite",
                format_func=lambda option: display_label(language, option),
            )

        st.caption(t(language, "food_examples"))

        if st.button(t(language, "analyze_food"), type="primary", use_container_width=True):
            if not manual_text.strip() and image_file is None:
                st.warning(t(language, "need_input"))
            elif image_file is not None and not manual_text.strip() and not has_openai_key():
                st.warning(t(language, "photo_only_warning"))
            else:
                image_summary = ""
                if image_file is not None:
                    with st.spinner(t(language, "reading_photo")):
                        image_result = extract_food_context_from_image(
                            image_file.getvalue(),
                            image_file.type or "image/jpeg",
                            language=language,
                        )
                    image_summary = str(image_result["summary"] or "")
                    if image_result["error"] and not image_summary:
                        st.info(str(image_result["error"]))

                analysis = analyze_food(
                    food_text=manual_text,
                    pet_profile=current_pet,
                    already_ate=already_ate,
                    amount_label=amount,
                    image_summary=image_summary,
                    language=language,
                )
                st.session_state.last_food_analysis = analysis
                st.session_state.food_follow_up_answer = ""
                add_to_history("food", analysis, current_pet)

        st.markdown(f"### {t(language, 'result')}")
        if st.session_state.last_food_analysis:
            render_analysis(st.session_state.last_food_analysis, language)

            with st.expander(t(language, "ask_follow_up"), expanded=False):
                follow_up_question = st.text_input(
                    t(language, "question"),
                    placeholder=t(language, "follow_up_placeholder"),
                    key="food_follow_up_question",
                )
                if st.button(t(language, "answer_follow_up"), use_container_width=True):
                    st.session_state.food_follow_up_answer = answer_follow_up(
                        follow_up_question,
                        st.session_state.last_food_analysis,
                        current_pet,
                        language=language,
                    )
                if st.session_state.food_follow_up_answer:
                    st.success(st.session_state.food_follow_up_answer)
        else:
            render_empty_state(
                t(language, "food_tab"),
                t(language, "empty_food_title"),
                t(language, "empty_food_copy"),
            )

    with emergency_tab:
        st.markdown(f"### {t(language, 'emergency_title')}")
        st.caption(t(language, "emergency_caption"))
        emergency_food = st.text_area(
            t(language, "what_was_eaten"),
            placeholder=t(language, "emergency_placeholder"),
            height=140,
        )
        emergency_meta_left, emergency_meta_right = st.columns(2)
        with emergency_meta_left:
            emergency_amount = st.select_slider(
                t(language, "how_much"),
                options=AMOUNT_OPTIONS,
                value="Small bite",
                key="emergency_amount",
                format_func=lambda option: display_label(language, option),
            )
        with emergency_meta_right:
            time_since = st.selectbox(
                t(language, "when_happened"),
                options=TIME_OPTIONS,
                format_func=lambda option: display_label(language, option),
            )
        with st.expander(t(language, "symptoms_optional"), expanded=False):
            symptoms = st.multiselect(
                t(language, "current_symptoms"),
                options=SYMPTOM_OPTIONS,
                format_func=lambda option: display_label(language, option),
            )

        if st.button(t(language, "run_emergency"), type="primary", use_container_width=True):
            if not emergency_food.strip():
                st.warning(t(language, "emergency_need_input"))
            else:
                analysis = analyze_food(
                    food_text=emergency_food,
                    pet_profile=current_pet,
                    already_ate=True,
                    amount_label=emergency_amount,
                    symptoms=symptoms,
                    time_since=time_since,
                    language=language,
                )
                st.session_state.last_emergency_analysis = analysis
                add_to_history("emergency", analysis, current_pet)

        st.markdown(f"### {t(language, 'result')}")
        if st.session_state.last_emergency_analysis:
            render_analysis(st.session_state.last_emergency_analysis, language)
        else:
            render_empty_state(
                t(language, "emergency_tab"),
                t(language, "empty_emergency_title"),
                t(language, "empty_emergency_copy"),
            )

    with care_tab:
        care = get_care_tips(current_pet, language=language)
        st.markdown(f"### {t(language, 'care_title')}")
        st.caption(t(language, "care_caption"))
        render_list_card(t(language, "safer_picks"), care["daily_choices"])
        render_list_card(t(language, "double_check"), care["red_flags"])
        render_list_card(t(language, "profile_notes"), care["personalization"])

    with history_tab:
        st.markdown(f"### {t(language, 'recent_checks')}")
        render_history(language)
        if st.session_state.history and st.button(t(language, "clear_history"), use_container_width=True):
            st.session_state.history = []
            st.rerun()


if __name__ == "__main__":
    main()
