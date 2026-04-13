from __future__ import annotations

import base64
from datetime import datetime
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st

from engine import (
    analyze_behavior,
    answer_follow_up,
    behavior_issue_choices,
    extract_behavior_context_from_image,
    get_routine_guide,
    has_openai_key,
)
from styles import inject_styles


NEW_PROFILE = "__new__"
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_CANDIDATES = ["logo.svg", "logo.png", "logo.webp", "logo.jpg", "logo.jpeg"]
LANGUAGE_OPTIONS = ["ru", "en"]
CONDITION_OPTIONS = [
    "recent_adoption",
    "rescue_history",
    "senior_pet",
    "pain_or_mobility",
    "noise_sensitivity",
    "multi_pet_home",
]
WHEN_OPTIONS = [
    "home_alone",
    "guests",
    "walks",
    "car",
    "night",
    "anytime",
    "litter_box",
    "mealtime",
    "new_home",
]
INTENSITY_OPTIONS = ["low", "medium", "high"]
DURATION_OPTIONS = ["sudden", "days", "weeks", "months"]

UI_TEXT = {
    "en": {
        "language": "Language",
        "language_ru": "Русский",
        "language_en": "English",
        "tagline": "AI behavior coach for calmer pets and calmer homes",
        "active_pet": "Active pet",
        "draft_pet": "Draft pet profile",
        "pet_profile": "Pet profile",
        "profile_hint": "Keep this simple. We only use it to personalize behavior guidance.",
        "profile_picker": "Choose a profile",
        "new_profile": "New draft profile",
        "pet_name": "Pet name",
        "pet_default_name": "My pet",
        "species": "Species",
        "dog": "Dog",
        "cat": "Cat",
        "age_years": "Age (years)",
        "weight_lb": "Weight (lb)",
        "breed_or_mix": "Breed or mix",
        "triggers": "Known triggers",
        "triggers_placeholder": "Doorbell, vacuum, strangers, nighttime, car rides",
        "conditions": "Context to keep in mind",
        "save_profile": "Save profile",
        "update_profile": "Update profile",
        "delete_pet": "Delete saved profile",
        "profile_saved": "Profile saved for {name}.",
        "profile_deleted": "Saved profile removed.",
        "behavior_tab": "Behavior Coach",
        "routine_tab": "Routine Plan",
        "history_tab": "History",
        "coach_title": "Behavior Coach",
        "coach_caption": "Describe what is happening, when it shows up, and how intense it feels. The app will give you a calmer same-day plan instead of a panic answer.",
        "issue_type": "What feels closest to the problem?",
        "description": "What is happening?",
        "description_placeholder": "Example: He barks and scratches the door when I leave. It starts after I pick up my keys and gets worse in 2-3 minutes.",
        "when_happens": "When does it usually happen?",
        "intensity": "Intensity",
        "duration": "How long has this been going on?",
        "optional_details": "Optional details",
        "already_tried": "What have you already tried?",
        "tried_placeholder": "Treats, longer walks, crate, ignoring, white noise, more play...",
        "upload_scene": "Add a photo of the setup (optional)",
        "photo_note": "A scene photo helps the app read the environment. If you only upload a photo, OPENAI_API_KEY needs to be connected.",
        "analyze_behavior": "Build my plan",
        "need_input": "Add a short description or a setup photo first.",
        "photo_only_warning": "For photo-only coaching, connect OPENAI_API_KEY or type a short description under the photo.",
        "reading_photo": "Reading the setup photo...",
        "result": "Result",
        "empty_title": "Start with one behavior problem.",
        "empty_copy": "You will get a likely pattern, same-day steps, a 7-day plan, and guidance on when to bring in a vet or trainer.",
        "detected_signals": "Signals I used",
        "image_read_title": "What I notice in the setup",
        "confidence": "Confidence: {value}",
        "ask_follow_up": "Ask a follow-up",
        "question": "Question",
        "follow_up_placeholder": "What should I do first tonight?",
        "answer_follow_up": "Answer follow-up",
        "routine_title": "Routine Plan",
        "routine_caption": "A simple baseline for calmer days. Use this first, then layer the issue-specific plan on top.",
        "weekly_focus": "Weekly focus",
        "history_title": "No coaching sessions yet",
        "history_copy": "Your recent behavior plans will show up here after the first run.",
        "clear_history": "Clear history",
        "history_empty": "Nothing saved yet",
        "history_behavior": "Behavior Coach",
        "help_note": "Pet Help AI is a coach, not a diagnosis tool. Sudden changes, pain signs, trouble urinating, or severe distress deserve veterinary input fast.",
        "chewy": "Chewy",
        "amazon": "Amazon",
    },
    "ru": {
        "language": "Язык",
        "language_ru": "Русский",
        "language_en": "English",
        "tagline": "AI-коуч по поведению для более спокойных питомцев и более спокойного дома",
        "active_pet": "Активный питомец",
        "draft_pet": "Черновик профиля",
        "pet_profile": "Профиль питомца",
        "profile_hint": "Держим это простым. Профиль нужен только для персонализации поведенческого плана.",
        "profile_picker": "Выбери профиль",
        "new_profile": "Новый черновик",
        "pet_name": "Имя питомца",
        "pet_default_name": "Мой питомец",
        "species": "Вид",
        "dog": "Собака",
        "cat": "Кошка",
        "age_years": "Возраст (лет)",
        "weight_lb": "Вес (lb)",
        "breed_or_mix": "Порода или метис",
        "triggers": "Известные триггеры",
        "triggers_placeholder": "Звонок в дверь, пылесос, чужие люди, ночь, поездки",
        "conditions": "Что важно учитывать",
        "save_profile": "Сохранить профиль",
        "update_profile": "Обновить профиль",
        "delete_pet": "Удалить сохраненный профиль",
        "profile_saved": "Профиль для {name} сохранен.",
        "profile_deleted": "Сохраненный профиль удален.",
        "behavior_tab": "Поведенческий коуч",
        "routine_tab": "Рутинный план",
        "history_tab": "История",
        "coach_title": "Поведенческий коуч",
        "coach_caption": "Опиши, что происходит, когда это случается и насколько это сильно. Ниже будет спокойный план на сегодня, а не тревожная паника.",
        "issue_type": "Что ближе всего к проблеме?",
        "description": "Что происходит?",
        "description_placeholder": "Например: Он лает и царапает дверь, когда я ухожу. Начинается уже после того, как я беру ключи, и через 2-3 минуты усиливается.",
        "when_happens": "Когда это обычно случается?",
        "intensity": "Насколько это сильно",
        "duration": "Как давно это идет?",
        "optional_details": "Необязательные детали",
        "already_tried": "Что вы уже пробовали?",
        "tried_placeholder": "Лакомства, длинные прогулки, клетка, игнорирование, белый шум, больше игр...",
        "upload_scene": "Добавить фото обстановки (необязательно)",
        "photo_note": "Фото помогает понять окружение. Если загружается только фото без текста, нужен подключенный OPENAI_API_KEY.",
        "analyze_behavior": "Собрать мой план",
        "need_input": "Сначала добавь короткое описание или фото обстановки.",
        "photo_only_warning": "Для коучинга только по фото нужен OPENAI_API_KEY или короткое описание под фото.",
        "reading_photo": "Читаю фото обстановки...",
        "result": "Результат",
        "empty_title": "Начни с одной поведенческой проблемы.",
        "empty_copy": "Ты получишь вероятный паттерн, шаги на сегодня, план на 7 дней и подсказку, когда уже подключать ветеринара или тренера.",
        "detected_signals": "Что я учел",
        "image_read_title": "Что я замечаю в обстановке",
        "confidence": "Уверенность: {value}",
        "ask_follow_up": "Задать уточняющий вопрос",
        "question": "Вопрос",
        "follow_up_placeholder": "Что мне сделать первым делом сегодня вечером?",
        "answer_follow_up": "Ответить",
        "routine_title": "Рутинный план",
        "routine_caption": "Простая спокойная база на каждый день. Сначала держим это, потом сверху добавляем точечный план по проблеме.",
        "weekly_focus": "Фокус недели",
        "history_title": "Пока нет сессий коучинга",
        "history_copy": "После первого запуска здесь появятся последние поведенческие планы.",
        "clear_history": "Очистить историю",
        "history_empty": "Пока ничего нет",
        "history_behavior": "Поведенческий коуч",
        "help_note": "Pet Help AI — это коуч, а не инструмент для диагноза. Резкие изменения, боль, проблемы с мочеиспусканием или тяжелый дистресс требуют более быстрого контакта с ветеринаром.",
        "chewy": "Chewy",
        "amazon": "Amazon",
    },
}

CONDITION_LABELS = {
    "en": {
        "recent_adoption": "Recent adoption",
        "rescue_history": "Rescue or unknown history",
        "senior_pet": "Senior pet",
        "pain_or_mobility": "Pain or mobility concerns",
        "noise_sensitivity": "Noise sensitivity",
        "multi_pet_home": "Multi-pet home",
    },
    "ru": {
        "recent_adoption": "Недавнее появление в доме",
        "rescue_history": "Приют или неизвестная история",
        "senior_pet": "Пожилой питомец",
        "pain_or_mobility": "Есть боль или сложности с движением",
        "noise_sensitivity": "Чувствительность к шуму",
        "multi_pet_home": "В доме несколько питомцев",
    },
}

WHEN_LABELS = {
    "en": {
        "home_alone": "When left home alone",
        "guests": "When guests or visitors appear",
        "walks": "On walks or near the front door",
        "car": "In the car or before a trip",
        "night": "At night",
        "anytime": "Across the day",
        "litter_box": "Around the litter box",
        "mealtime": "Around food, toys, or high-value items",
        "new_home": "Since a recent change",
    },
    "ru": {
        "home_alone": "Когда остается один дома",
        "guests": "Когда приходят гости или люди",
        "walks": "На прогулках или у входной двери",
        "car": "В машине или перед поездкой",
        "night": "Ночью",
        "anytime": "В течение дня",
        "litter_box": "Вокруг лотка",
        "mealtime": "Возле еды, игрушек или ценных вещей",
        "new_home": "После недавних перемен",
    },
}

INTENSITY_LABELS = {
    "en": {"low": "Low", "medium": "Medium", "high": "High"},
    "ru": {"low": "Низко", "medium": "Средне", "high": "Сильно"},
}

DURATION_LABELS = {
    "en": {"sudden": "Started suddenly", "days": "A few days", "weeks": "A few weeks", "months": "A month or more"},
    "ru": {"sudden": "Началось резко", "days": "Несколько дней", "weeks": "Несколько недель", "months": "Месяц и больше"},
}


def t(key: str, language: str, **kwargs: str) -> str:
    text = UI_TEXT[language].get(key, key)
    return text.format(**kwargs) if kwargs else text


def load_logo_data_uri() -> str | None:
    for filename in LOGO_CANDIDATES:
        candidate = ASSETS_DIR / filename
        if not candidate.exists():
            continue
        mime_type = {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".webp": "image/webp",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }.get(candidate.suffix.lower(), "image/png")
        encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    return None


def default_pet() -> dict[str, object]:
    return {
        "id": "",
        "name": "",
        "species": "dog",
        "age_years": 4.0,
        "weight_lb": 35.0,
        "breed": "",
        "triggers": "",
        "conditions": [],
    }


def ensure_state() -> None:
    if "language" not in st.session_state:
        st.session_state.language = "ru"
    if "pets" not in st.session_state:
        st.session_state.pets = []
    if "active_pet_id" not in st.session_state:
        st.session_state.active_pet_id = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None
    if "follow_up_answer" not in st.session_state:
        st.session_state.follow_up_answer = ""
    if "follow_up_question" not in st.session_state:
        st.session_state.follow_up_question = ""
    if "pet_choice" not in st.session_state:
        st.session_state.pet_choice = NEW_PROFILE

    required_inputs = [
        "pet_name_input",
        "species_input",
        "age_input",
        "weight_input",
        "breed_input",
        "triggers_input",
        "conditions_input",
    ]
    if any(key not in st.session_state for key in required_inputs):
        load_pet_into_inputs(default_pet())


def get_pet_by_id(pet_id: str | None) -> dict[str, object] | None:
    if not pet_id:
        return None
    for pet in st.session_state.pets:
        if pet["id"] == pet_id:
            return pet
    return None


def load_pet_into_inputs(pet: dict[str, object]) -> None:
    st.session_state.pet_name_input = str(pet.get("name", ""))
    st.session_state.species_input = str(pet.get("species", "dog"))
    st.session_state.age_input = float(pet.get("age_years", 4.0) or 4.0)
    st.session_state.weight_input = float(pet.get("weight_lb", 35.0) or 35.0)
    st.session_state.breed_input = str(pet.get("breed", ""))
    st.session_state.triggers_input = str(pet.get("triggers", ""))
    st.session_state.conditions_input = list(pet.get("conditions", []))


def current_pet_from_inputs(language: str) -> dict[str, object]:
    name = (st.session_state.get("pet_name_input") or "").strip()
    return {
        "id": st.session_state.get("active_pet_id") or "",
        "name": name or t("pet_default_name", language),
        "species": st.session_state.get("species_input", "dog"),
        "age_years": float(st.session_state.get("age_input", 4.0)),
        "weight_lb": float(st.session_state.get("weight_input", 35.0)),
        "breed": (st.session_state.get("breed_input") or "").strip(),
        "triggers": (st.session_state.get("triggers_input") or "").strip(),
        "conditions": list(st.session_state.get("conditions_input", [])),
    }


def on_pet_choice_change() -> None:
    choice = st.session_state.get("pet_choice", NEW_PROFILE)
    if choice == NEW_PROFILE:
        st.session_state.active_pet_id = None
        load_pet_into_inputs(default_pet())
        return
    pet = get_pet_by_id(choice)
    if pet:
        st.session_state.active_pet_id = pet["id"]
        load_pet_into_inputs(pet)


def persist_current_pet(language: str) -> str:
    pet = current_pet_from_inputs(language)
    pet_name = str(pet["name"])
    active_pet_id = st.session_state.get("active_pet_id")

    if active_pet_id:
        for index, saved_pet in enumerate(st.session_state.pets):
            if saved_pet["id"] == active_pet_id:
                updated = dict(pet)
                updated["id"] = active_pet_id
                st.session_state.pets[index] = updated
                st.session_state.pet_choice = active_pet_id
                return pet_name

    pet_id = str(uuid4())
    saved = dict(pet)
    saved["id"] = pet_id
    st.session_state.pets.append(saved)
    st.session_state.active_pet_id = pet_id
    st.session_state.pet_choice = pet_id
    return pet_name


def delete_active_pet() -> bool:
    active_pet_id = st.session_state.get("active_pet_id")
    if not active_pet_id:
        return False
    st.session_state.pets = [pet for pet in st.session_state.pets if pet["id"] != active_pet_id]
    st.session_state.active_pet_id = None
    st.session_state.pet_choice = NEW_PROFILE
    load_pet_into_inputs(default_pet())
    return True


def render_brand_logo(logo_uri: str | None) -> str:
    if logo_uri:
        return f'<img src="{logo_uri}" alt="Pet Help AI logo" class="brand-mark"/>'
    return '<div class="brand-fallback">PH</div>'


def render_sidebar_brand(logo_uri: str | None, language: str) -> None:
    mark = (
        f'<img src="{logo_uri}" alt="Pet Help AI logo" class="sidebar-brand-mark"/>'
        if logo_uri
        else '<div class="sidebar-brand-mark sidebar-fallback">PH</div>'
    )
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            {mark}
            <div>
                <div class="sidebar-brand-name">Pet Help AI</div>
                <div class="sidebar-brand-copy">{escape(t("tagline", language))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(pet: dict[str, object], logo_uri: str | None, language: str) -> None:
    species_label = t(str(pet["species"]), language)
    summary = f"{species_label}, {pet['age_years']:.0f}y, {pet['weight_lb']:.0f} lb"
    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand-lockup">
                {render_brand_logo(logo_uri)}
                <div>
                    <div class="brand-name">Pet Help AI</div>
                    <div class="brand-domain">pethelpai.com</div>
                </div>
            </div>
            <div class="app-summary">
                <div class="app-summary-label">{escape(t("active_pet", language))}</div>
                <div class="app-summary-name">{escape(str(pet["name"]))}</div>
                <div class="app-summary-copy">{escape(summary)}{f" • {escape(str(pet['breed']))}" if pet['breed'] else ''}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list_card(title: str, items: list[str]) -> None:
    list_html = "".join(f"<li>{escape(item)}</li>" for item in items if item)
    st.markdown(
        f"""
        <div class="detail-card">
            <h4>{escape(title)}</h4>
            <ul>{list_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result: dict[str, object], language: str) -> None:
    class_name = {
        "safe": "result-safe",
        "caution": "result-caution",
        "avoid": "result-avoid",
    }.get(str(result.get("verdict", "safe")), "result-safe")

    st.markdown(
        f"""
        <div class="result-card {class_name}">
            <div class="result-pill">{escape(str(result.get("badge_label", "")))}</div>
            <h2 class="result-title">{escape(str(result.get("result_title", "")))}</h2>
            <p class="result-copy">{escape(str(result.get("summary", "")))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confidence_text = t("confidence", language, value=str(result.get("confidence", "")))
    st.caption(confidence_text)

    if result.get("image_summary"):
        render_list_card(t("image_read_title", language), [str(result["image_summary"])])

    render_list_card(str(result.get("drivers_title", "")), list(result.get("drivers", [])))
    render_list_card(str(result.get("today_title", "")), list(result.get("today_steps", [])))
    render_list_card(str(result.get("week_title", "")), list(result.get("week_plan", [])))
    render_list_card(str(result.get("vet_title", "")), list(result.get("vet_flags", [])))

    toolkit_items = list(result.get("toolkit_items", []))
    if toolkit_items:
        st.markdown(f"##### {escape(str(result.get('toolkit_title', '')))}")
        for item in toolkit_items:
            st.markdown(
                f"""
                <div class="swap-card">
                    <div class="swap-label">{escape(str(result.get("toolkit_title", "")))}</div>
                    <h4>{escape(item["title"])}</h4>
                    <p>{escape(item["body"])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            col1.link_button(t("chewy", language), item["chewy_url"], use_container_width=True)
            col2.link_button(t("amazon", language), item["amazon_url"], use_container_width=True)

    with st.expander(t("detected_signals", language), expanded=False):
        for signal in result.get("detected_signals", []):
            st.markdown(f"- {signal}")


def render_empty_state(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <h3>{escape(title)}</h3>
            <p>{escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_follow_up(language: str) -> None:
    result = st.session_state.get("last_analysis")
    if not result:
        return

    with st.expander(t("ask_follow_up", language), expanded=False):
        st.text_input(t("question", language), key="follow_up_question", placeholder=t("follow_up_placeholder", language))
        if st.button(t("answer_follow_up", language), use_container_width=True):
            question = (st.session_state.get("follow_up_question") or "").strip()
            if question:
                st.session_state.follow_up_answer = answer_follow_up(question, result, language=language)
        if st.session_state.get("follow_up_answer"):
            st.markdown(
                f"""
                <div class="soft-note">{escape(st.session_state.follow_up_answer)}</div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar(logo_uri: str | None, language: str) -> None:
    render_sidebar_brand(logo_uri, language)

    st.sidebar.selectbox(
        t("language", language),
        LANGUAGE_OPTIONS,
        index=LANGUAGE_OPTIONS.index(language),
        format_func=lambda code: t(f"language_{code}", language),
        key="language",
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-note">
            <strong>{escape(t("pet_profile", language))}</strong><br/>
            {escape(t("profile_hint", language))}
        </div>
        """,
        unsafe_allow_html=True,
    )

    options = [NEW_PROFILE] + [pet["id"] for pet in st.session_state.pets]
    if st.session_state.get("pet_choice") not in options:
        st.session_state.pet_choice = st.session_state.get("active_pet_id") or NEW_PROFILE

    st.sidebar.selectbox(
        t("profile_picker", language),
        options,
        format_func=lambda value: (
            t("new_profile", language) if value == NEW_PROFILE else str(get_pet_by_id(value)["name"])
        ),
        key="pet_choice",
        on_change=on_pet_choice_change,
    )

    st.sidebar.text_input(t("pet_name", language), key="pet_name_input")
    st.sidebar.selectbox(
        t("species", language),
        ["dog", "cat"],
        format_func=lambda value: t(value, language),
        key="species_input",
    )
    st.sidebar.number_input(t("age_years", language), min_value=0.0, max_value=30.0, step=0.5, key="age_input")
    st.sidebar.number_input(t("weight_lb", language), min_value=1.0, max_value=250.0, step=1.0, key="weight_input")
    st.sidebar.text_input(t("breed_or_mix", language), key="breed_input")
    st.sidebar.text_area(
        t("triggers", language),
        key="triggers_input",
        height=90,
        placeholder=t("triggers_placeholder", language),
    )
    st.sidebar.multiselect(
        t("conditions", language),
        CONDITION_OPTIONS,
        format_func=lambda value: CONDITION_LABELS[language][value],
        key="conditions_input",
    )

    save_label = t("update_profile", language) if st.session_state.get("active_pet_id") else t("save_profile", language)
    if st.sidebar.button(save_label, use_container_width=True):
        saved_name = persist_current_pet(language)
        st.sidebar.success(t("profile_saved", language, name=saved_name))
    if st.session_state.get("active_pet_id") and st.sidebar.button(t("delete_pet", language), use_container_width=True):
        if delete_active_pet():
            st.sidebar.success(t("profile_deleted", language))

    st.sidebar.markdown(
        f"""
        <div class="soft-note">{escape(t("help_note", language))}</div>
        """,
        unsafe_allow_html=True,
    )


def run_behavior_coach(current_pet: dict[str, object], language: str) -> None:
    st.subheader(t("coach_title", language))
    st.caption(t("coach_caption", language))

    issue_choices = behavior_issue_choices(str(current_pet["species"]), language)
    issue_keys = [key for key, _label in issue_choices]
    issue_labels = {key: label for key, label in issue_choices}

    with st.form("behavior_coach_form", clear_on_submit=False):
        issue_key = st.selectbox(
            t("issue_type", language),
            issue_keys,
            format_func=lambda key: issue_labels[key],
        )
        description = st.text_area(
            t("description", language),
            height=140,
            placeholder=t("description_placeholder", language),
        )

        col1, col2, col3 = st.columns(3)
        when_happens = col1.selectbox(
            t("when_happens", language),
            WHEN_OPTIONS,
            format_func=lambda key: WHEN_LABELS[language][key],
        )
        intensity = col2.selectbox(
            t("intensity", language),
            INTENSITY_OPTIONS,
            format_func=lambda key: INTENSITY_LABELS[language][key],
        )
        duration = col3.selectbox(
            t("duration", language),
            DURATION_OPTIONS,
            format_func=lambda key: DURATION_LABELS[language][key],
        )

        with st.expander(t("optional_details", language), expanded=False):
            already_tried = st.text_area(
                t("already_tried", language),
                height=110,
                placeholder=t("tried_placeholder", language),
            )
            photo = st.file_uploader(
                t("upload_scene", language),
                type=["png", "jpg", "jpeg", "webp"],
                help=t("photo_note", language),
            )

        submitted = st.form_submit_button(t("analyze_behavior", language), use_container_width=True)

    if submitted:
        if not description.strip() and photo is None:
            st.warning(t("need_input", language))
        elif photo is not None and not description.strip() and not has_openai_key():
            st.warning(t("photo_only_warning", language))
        else:
            image_context = None
            if photo is not None and has_openai_key():
                with st.spinner(t("reading_photo", language)):
                    image_context = extract_behavior_context_from_image(photo.getvalue(), photo.type, language=language)

            result = analyze_behavior(
                pet_name=str(current_pet["name"]),
                species=str(current_pet["species"]),
                age_years=float(current_pet["age_years"]),
                weight_lb=float(current_pet["weight_lb"]),
                breed=str(current_pet["breed"]),
                triggers=str(current_pet["triggers"]),
                conditions=list(current_pet["conditions"]),
                issue_key=issue_key,
                description=description,
                when_happens=when_happens,
                intensity=intensity,
                duration=duration,
                already_tried=already_tried,
                image_context=image_context,
                language=language,
            )
            st.session_state.last_analysis = result
            st.session_state.follow_up_answer = ""
            st.session_state.follow_up_question = ""
            st.session_state.history = [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "kind": t("history_behavior", language),
                    "pet_name": current_pet["name"],
                    "issue_label": result["issue_label"],
                    "badge_label": result["badge_label"],
                    "summary": result["summary"],
                }
            ] + st.session_state.history[:11]

    st.markdown(f"##### {escape(t('result', language))}")
    if st.session_state.get("last_analysis"):
        render_result(st.session_state.last_analysis, language)
        render_follow_up(language)
    else:
        render_empty_state(t("empty_title", language), t("empty_copy", language))


def render_routine_tab(current_pet: dict[str, object], language: str) -> None:
    guide = get_routine_guide(current_pet, language)
    st.subheader(t("routine_title", language))
    st.caption(t("routine_caption", language))
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-kicker">Baseline</div>
            <p>{escape(str(guide['summary']))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for section in guide["sections"]:
        render_list_card(str(section["title"]), list(section["items"]))
    render_list_card(str(guide["weekly_title"]), list(guide["weekly_focus"]))


def render_history_tab(language: str) -> None:
    st.subheader(t("history_tab", language))
    if st.button(t("clear_history", language), use_container_width=False):
        st.session_state.history = []

    if not st.session_state.history:
        render_empty_state(t("history_title", language), t("history_copy", language))
        return

    for entry in st.session_state.history:
        st.markdown(
            f"""
            <div class="history-item">
                <div class="history-meta">{escape(str(entry['timestamp']))} • {escape(str(entry['kind']))}</div>
                <strong>{escape(str(entry['pet_name']))}</strong> • {escape(str(entry['issue_label']))}<br/>
                <em>{escape(str(entry['badge_label']))}</em>
                <p>{escape(str(entry['summary']))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(page_title="Pet Help AI", page_icon="🐾", layout="wide")
    inject_styles()
    ensure_state()

    language = st.session_state.language
    logo_uri = load_logo_data_uri()
    render_sidebar(logo_uri, language)
    language = st.session_state.language
    current_pet = current_pet_from_inputs(language)

    render_header(current_pet, logo_uri, language)

    tabs = st.tabs(
        [
            t("behavior_tab", language),
            t("routine_tab", language),
            t("history_tab", language),
        ]
    )

    with tabs[0]:
        run_behavior_coach(current_pet, language)
    with tabs[1]:
        render_routine_tab(current_pet, language)
    with tabs[2]:
        render_history_tab(language)


if __name__ == "__main__":
    main()
