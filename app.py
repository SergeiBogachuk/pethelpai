from __future__ import annotations

import base64
from datetime import date, datetime, time
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from emailer import email_configured
from engine import (
    DOCUMENT_TYPE_LABELS,
    DOCUMENT_TYPES,
    EVENT_TYPE_LABELS,
    EVENT_TYPES,
    EXPENSE_CATEGORIES,
    EXPENSE_CATEGORY_LABELS,
    LOG_TYPE_LABELS,
    LOG_TYPES,
    MEDICATION_FREQUENCIES,
    MEDICATION_FREQUENCY_LABELS,
    RECURRENCE_LABELS,
    RECURRENCE_OPTIONS,
    REMINDER_LABELS,
    REMINDER_OPTIONS,
    SEVERITY_LABELS,
    SEVERITY_OPTIONS,
    SEX_LABELS,
    SEX_OPTIONS,
    SPECIES_LABELS,
    SPECIES_OPTIONS,
    event_status,
    format_date,
    format_datetime,
    label,
    language_code,
    next_due_text,
    pet_age_display,
    pet_month_expense,
    pet_recent_records,
    smart_recommendations,
    starter_calendar_template,
    status_badge,
    upcoming_warning_level,
)
from storage import (
    activate_subscription,
    add_expense,
    add_weight_log,
    admin_users,
    analytics_summary,
    authenticate_user,
    cancel_subscription,
    connect,
    count_active_events,
    count_user_pets,
    create_care_event,
    create_document,
    create_health_log,
    create_medication_course,
    create_pet,
    create_support_ticket,
    create_user,
    dispatch_due_email_notifications,
    expense_summary,
    free_limits,
    get_pet,
    get_subscription,
    get_user,
    init_db,
    list_care_events,
    list_documents,
    list_expenses,
    list_health_logs,
    list_medication_courses,
    list_notifications,
    list_pets,
    list_support_tickets,
    list_today_tasks,
    list_upcoming_events,
    list_weight_logs,
    log_product_event,
    mark_event_completed,
    mark_event_missed,
    mark_medication_given,
    mark_notification_read,
    monthly_expense_rows,
    refresh_subscription_state,
    save_uploaded_file,
    start_trial,
    subscription_is_premium,
    update_password,
    update_pet,
    update_user_settings,
)
from styles import inject_styles


ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_CANDIDATES = ["logo.svg", "logo.png", "logo.webp", "logo.jpg", "logo.jpeg"]
TIMEZONE_OPTIONS = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Europe/Berlin",
    "Europe/London",
]
NAV_ITEMS = [
    "dashboard",
    "pets",
    "calendar",
    "health",
    "expenses",
    "documents",
    "subscription",
    "settings",
]

TEXT = {
    "en": {
        "app_tagline": "Your pet care dashboard, reminders, records, and spending in one calm place.",
        "language": "Language",
        "lang_ru": "Русский",
        "lang_en": "English",
        "login": "Sign in",
        "register": "Register",
        "reset": "Reset password",
        "email": "Email",
        "password": "Password",
        "name": "Name",
        "timezone": "Time zone",
        "login_button": "Sign in",
        "register_button": "Create account",
        "reset_button": "Update password",
        "logout": "Log out",
        "auth_error": "Wrong email or password.",
        "register_ok": "Account created. You can start using the app now.",
        "reset_ok": "Password updated.",
        "reset_hint": "This MVP uses a direct reset flow instead of email delivery.",
        "nav_dashboard": "Dashboard",
        "nav_pets": "Pets",
        "nav_calendar": "Calendar",
        "nav_health": "Health",
        "nav_expenses": "Expenses",
        "nav_documents": "Documents",
        "nav_subscription": "Subscription",
        "nav_settings": "Settings",
        "nav_admin": "Admin",
        "plan": "Plan",
        "free": "Free",
        "premium": "Premium",
        "trial": "Trial",
        "dashboard_title": "Dashboard",
        "today_tasks": "Today's tasks",
        "upcoming": "Upcoming reminders",
        "notifications": "Notifications",
        "recommendations": "Smart recommendations",
        "pets_overview": "Pets overview",
        "quick_actions": "Quick actions",
        "add_pet": "Add pet",
        "add_event": "Add event",
        "add_log": "Add symptom",
        "add_expense": "Add expense",
        "onboarding_title": "Start with your first pet",
        "onboarding_copy": "The first useful path is simple: add a pet, create 1-2 care events, then let the app remind you.",
        "pet_title": "Pets",
        "pet_select": "Choose pet",
        "pet_form_title": "Pet profile",
        "pet_saved": "Pet saved.",
        "starter_calendar": "Add starter calendar",
        "starter_added": "Starter events added.",
        "pet_photo": "Photo",
        "pet_name": "Pet name",
        "species": "Species",
        "breed": "Breed",
        "birth_date": "Birth date",
        "birth_date_known": "I know the birth date",
        "age_text": "Age text (optional)",
        "sex": "Sex",
        "weight": "Weight",
        "sterilized": "Sterilized / neutered",
        "color": "Color / special marks",
        "allergies": "Allergies",
        "chronic_conditions": "Chronic conditions",
        "chip_number": "Chip number",
        "clinic_name": "Clinic",
        "vet_name": "Doctor",
        "save_pet": "Save pet",
        "update_pet": "Update pet",
        "pet_card_upcoming": "Next important action",
        "pet_card_spend": "This month spend",
        "pet_card_records": "Recent records",
        "calendar_title": "Care calendar",
        "calendar_copy": "Keep one clean place for vaccines, treatments, grooming, food restocks, and custom reminders.",
        "event_type": "Event type",
        "event_title": "Title",
        "event_description": "Note",
        "scheduled_date": "Date",
        "scheduled_time": "Time",
        "recurrence": "Repeat",
        "reminders": "Reminders",
        "create_event": "Create event",
        "event_saved": "Event added.",
        "complete": "Mark done",
        "miss": "Mark missed",
        "health_title": "Health and care log",
        "disclaimer": "This service does not diagnose. If symptoms worry you, talk to a veterinarian.",
        "log_type": "Log type",
        "symptom": "Symptom",
        "severity": "Severity",
        "description": "Description",
        "appetite": "Appetite",
        "activity": "Activity",
        "stool": "Stool / vomiting",
        "mood": "Mood",
        "attachment": "Photo or video",
        "save_log": "Save log",
        "log_saved": "Health log added.",
        "medication_title": "Medications and procedures",
        "medicine_name": "Medication name",
        "dosage": "Dosage",
        "frequency": "Frequency",
        "start_date": "Start date",
        "end_date": "End date",
        "course_has_end": "This course has an end date",
        "note": "Comment",
        "save_course": "Save course",
        "course_saved": "Medication course added.",
        "mark_given": "I gave it",
        "weight_title": "Weight tracking",
        "weight_date": "Measurement date",
        "weight_note": "Weight note",
        "save_weight": "Save weight",
        "weight_saved": "Weight entry added.",
        "expenses_title": "Expenses",
        "category": "Category",
        "amount": "Amount",
        "currency": "Currency",
        "spent_at": "Spent at",
        "save_expense": "Save expense",
        "expense_saved": "Expense added.",
        "documents_title": "Documents",
        "document_type": "Document type",
        "document_note": "Document note",
        "upload_document": "Upload document",
        "document_saved": "Document added.",
        "subscription_title": "Subscription",
        "trial_action": "Start 7-day trial",
        "monthly_action": "Activate monthly premium",
        "yearly_action": "Activate yearly premium",
        "cancel_action": "Cancel subscription",
        "subscription_saved": "Subscription updated.",
        "settings_title": "Settings",
        "notifications_email": "Email reminders",
        "notifications_in_app": "In-app reminders",
        "notifications_push": "Push reminders",
        "save_settings": "Save settings",
        "settings_saved": "Settings updated.",
        "new_password": "New password",
        "support_title": "Support",
        "support_subject": "Subject",
        "support_message": "Message",
        "send_ticket": "Send ticket",
        "ticket_saved": "Support ticket created.",
        "admin_title": "Admin",
        "users": "Users",
        "subscriptions": "Subscriptions",
        "analytics": "Analytics",
        "support": "Support",
        "email_channel": "Email reminder delivery",
        "email_ready": "SMTP is configured. Due reminders can be sent by email.",
        "email_missing": "SMTP is not configured yet. Reminders still work inside the app, but email delivery is off.",
        "run_sweep": "Run reminder sweep now",
        "sweep_result": "Reminder sweep: {sent} sent, {failed} failed.",
        "phone_note": "Right now the external reminder channel is email. That already reaches the phone inbox. True push notifications come in the mobile app step.",
        "paywall_title": "Unlock Premium",
        "paywall_copy": "Premium opens multiple pets, unlimited reminders, document storage, full history, analytics, and family-ready workflows.",
        "second_pet_lock": "Free allows 1 pet. Premium unlocks multi-pet care.",
        "event_limit_lock": "Free includes a limited calendar. Premium unlocks unlimited recurring events.",
        "document_lock": "Document storage is available on Premium.",
        "no_data": "Nothing here yet.",
        "next_charge": "Next renewal",
        "status": "Status",
        "month_total": "This month",
        "all_time_total": "All time",
        "open_paywall": "See plans",
        "value_line": "Do not miss important care. Keep everything for your pet in one place.",
    },
    "ru": {
        "app_tagline": "Личный кабинет питомца, напоминания, история ухода и расходы в одном спокойном месте.",
        "language": "Язык",
        "lang_ru": "Русский",
        "lang_en": "English",
        "login": "Вход",
        "register": "Регистрация",
        "reset": "Сброс пароля",
        "email": "Email",
        "password": "Пароль",
        "name": "Имя",
        "timezone": "Часовой пояс",
        "login_button": "Войти",
        "register_button": "Создать аккаунт",
        "reset_button": "Обновить пароль",
        "logout": "Выйти",
        "auth_error": "Неверный email или пароль.",
        "register_ok": "Аккаунт создан. Можно сразу пользоваться приложением.",
        "reset_ok": "Пароль обновлен.",
        "reset_hint": "В этом MVP используется прямой сброс пароля без отправки email.",
        "nav_dashboard": "Дашборд",
        "nav_pets": "Питомцы",
        "nav_calendar": "Календарь",
        "nav_health": "Здоровье",
        "nav_expenses": "Расходы",
        "nav_documents": "Документы",
        "nav_subscription": "Подписка",
        "nav_settings": "Настройки",
        "nav_admin": "Админка",
        "plan": "Тариф",
        "free": "Free",
        "premium": "Premium",
        "trial": "Триал",
        "dashboard_title": "Дашборд",
        "today_tasks": "Задачи на сегодня",
        "upcoming": "Ближайшие напоминания",
        "notifications": "Уведомления",
        "recommendations": "Умные рекомендации",
        "pets_overview": "Питомцы",
        "quick_actions": "Быстрые действия",
        "add_pet": "Добавить питомца",
        "add_event": "Добавить событие",
        "add_log": "Добавить симптом",
        "add_expense": "Добавить расход",
        "onboarding_title": "Начни с первого питомца",
        "onboarding_copy": "Самый полезный старт здесь простой: добавить питомца, создать 1-2 события ухода и дальше уже получать напоминания.",
        "pet_title": "Питомцы",
        "pet_select": "Выбери питомца",
        "pet_form_title": "Профиль питомца",
        "pet_saved": "Питомец сохранен.",
        "starter_calendar": "Добавить стартовый календарь",
        "starter_added": "Стартовые события добавлены.",
        "pet_photo": "Фото",
        "pet_name": "Кличка",
        "species": "Вид",
        "breed": "Порода",
        "birth_date": "Дата рождения",
        "birth_date_known": "Я знаю точную дату рождения",
        "age_text": "Возраст текстом (необязательно)",
        "sex": "Пол",
        "weight": "Вес",
        "sterilized": "Стерилизован / кастрирован",
        "color": "Цвет / особые приметы",
        "allergies": "Аллергии",
        "chronic_conditions": "Хронические особенности",
        "chip_number": "Номер чипа",
        "clinic_name": "Ветклиника",
        "vet_name": "Врач",
        "save_pet": "Сохранить питомца",
        "update_pet": "Обновить питомца",
        "pet_card_upcoming": "Ближайшее важное действие",
        "pet_card_spend": "Расходы за месяц",
        "pet_card_records": "Последние записи",
        "calendar_title": "Календарь ухода",
        "calendar_copy": "Одна чистая точка для прививок, обработок, груминга, покупок корма и своих напоминаний.",
        "event_type": "Тип события",
        "event_title": "Название",
        "event_description": "Заметка",
        "scheduled_date": "Дата",
        "scheduled_time": "Время",
        "recurrence": "Повтор",
        "reminders": "Напоминания",
        "create_event": "Создать событие",
        "event_saved": "Событие добавлено.",
        "complete": "Отметить выполненным",
        "miss": "Отметить пропущенным",
        "health_title": "Журнал здоровья и ухода",
        "disclaimer": "Сервис не ставит диагнозы. Если симптомы тревожат, свяжитесь с ветеринаром.",
        "log_type": "Тип записи",
        "symptom": "Симптом",
        "severity": "Тяжесть",
        "description": "Описание",
        "appetite": "Аппетит",
        "activity": "Активность",
        "stool": "Стул / рвота",
        "mood": "Настроение",
        "attachment": "Фото или видео",
        "save_log": "Сохранить запись",
        "log_saved": "Запись здоровья добавлена.",
        "medication_title": "Лекарства и процедуры",
        "medicine_name": "Название лекарства",
        "dosage": "Дозировка",
        "frequency": "Частота",
        "start_date": "Дата начала",
        "end_date": "Дата окончания",
        "course_has_end": "У курса есть дата окончания",
        "note": "Комментарий",
        "save_course": "Сохранить курс",
        "course_saved": "Курс лекарства добавлен.",
        "mark_given": "Я дал лекарство",
        "weight_title": "Трекер веса",
        "weight_date": "Дата измерения",
        "weight_note": "Комментарий к весу",
        "save_weight": "Сохранить вес",
        "weight_saved": "Запись веса добавлена.",
        "expenses_title": "Расходы",
        "category": "Категория",
        "amount": "Сумма",
        "currency": "Валюта",
        "spent_at": "Дата расхода",
        "save_expense": "Сохранить расход",
        "expense_saved": "Расход добавлен.",
        "documents_title": "Документы",
        "document_type": "Тип документа",
        "document_note": "Заметка к документу",
        "upload_document": "Загрузить документ",
        "document_saved": "Документ добавлен.",
        "subscription_title": "Подписка",
        "trial_action": "Запустить 7-дневный триал",
        "monthly_action": "Активировать месячный Premium",
        "yearly_action": "Активировать годовой Premium",
        "cancel_action": "Отменить подписку",
        "subscription_saved": "Подписка обновлена.",
        "settings_title": "Настройки",
        "notifications_email": "Email-напоминания",
        "notifications_in_app": "In-app напоминания",
        "notifications_push": "Push-напоминания",
        "save_settings": "Сохранить настройки",
        "settings_saved": "Настройки обновлены.",
        "new_password": "Новый пароль",
        "support_title": "Поддержка",
        "support_subject": "Тема",
        "support_message": "Сообщение",
        "send_ticket": "Отправить тикет",
        "ticket_saved": "Тикет в поддержку создан.",
        "admin_title": "Админка",
        "users": "Пользователи",
        "subscriptions": "Подписки",
        "analytics": "Аналитика",
        "support": "Поддержка",
        "email_channel": "Доставка email-напоминаний",
        "email_ready": "SMTP уже настроен. Просроченные напоминания можно отправлять по email.",
        "email_missing": "SMTP пока не настроен. Напоминания работают внутри приложения, но email-доставка выключена.",
        "run_sweep": "Запустить отправку напоминаний",
        "sweep_result": "Отправка напоминаний: отправлено {sent}, ошибок {failed}.",
        "phone_note": "Сейчас внешний канал — это email. Он уже приходит на телефон в почту. Настоящие push-уведомления подключим на шаге мобильного приложения.",
        "paywall_title": "Открыть Premium",
        "paywall_copy": "Premium открывает несколько питомцев, безлимитные напоминания, хранение документов, полную историю, аналитику и семейный формат использования.",
        "second_pet_lock": "На Free доступен 1 питомец. Premium открывает несколько питомцев.",
        "event_limit_lock": "На Free календарь ограничен. Premium открывает безлимитные повторяющиеся события.",
        "document_lock": "Хранение документов доступно в Premium.",
        "no_data": "Пока ничего нет.",
        "next_charge": "Следующее списание",
        "status": "Статус",
        "month_total": "За месяц",
        "all_time_total": "За все время",
        "open_paywall": "Посмотреть тарифы",
        "value_line": "Не пропускайте важный уход. Храните всё по питомцу в одном месте.",
    },
}


def tr(key: str, language: str) -> str:
    return TEXT[language_code(language)].get(key, key)


def load_logo_data_uri() -> str | None:
    for filename in LOGO_CANDIDATES:
        file_path = ASSETS_DIR / filename
        if file_path.exists():
            mime = {
                ".png": "image/png",
                ".svg": "image/svg+xml",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
            }.get(file_path.suffix.lower(), "image/png")
            encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    return None


def uploaded_image_to_data_uri(uploaded_file: object) -> str:
    mime = getattr(uploaded_file, "type", None) or "image/png"
    payload = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.getbuffer()
    encoded = base64.b64encode(bytes(payload)).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def image_bytes_from_source(source: str | None) -> bytes | None:
    if not source:
        return None
    if source.startswith("data:image/") and "," in source:
        try:
            return base64.b64decode(source.split(",", 1)[1])
        except Exception:
            return None
    file_path = Path(source)
    if file_path.exists():
        try:
            return file_path.read_bytes()
        except OSError:
            return None
    return None


def render_avatar_image(source: str | None, width: int = 180) -> None:
    image_bytes = image_bytes_from_source(source)
    if image_bytes:
        st.image(image_bytes, width=width)


def inject_local_overrides() -> None:
    st.markdown(
        """
        <style>
        .metric-card {
            background: #ffffff;
            border: 1px solid rgba(20,54,59,0.08);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
        }
        .pet-card {
            background: #ffffff;
            border: 1px solid rgba(20,54,59,0.08);
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 0.9rem;
        }
        .pet-card h4, .metric-card h4 {
            margin: 0 0 0.35rem;
            color: #14363b;
        }
        .pet-meta {
            color: rgba(20,54,59,0.6);
            font-size: 0.88rem;
            margin-bottom: 0.5rem;
        }
        .warning-box {
            background: #fff8ed;
            border: 1px solid rgba(176,121,31,0.18);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
        }
        .lock-box {
            background: #ffffff;
            border: 1px dashed rgba(20,54,59,0.18);
            border-radius: 18px;
            padding: 1rem 1.05rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_state() -> None:
    if "language" not in st.session_state:
        st.session_state.language = "ru"
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "nav" not in st.session_state:
        st.session_state.nav = "dashboard"
    if "selected_pet_id" not in st.session_state:
        st.session_state.selected_pet_id = None
    if "last_email_dispatch_check" not in st.session_state:
        st.session_state.last_email_dispatch_check = None


def go_to(page: str) -> None:
    st.session_state.nav = page


def combine_date_time(d: date, t: time) -> str:
    return datetime.combine(d, t).replace(second=0, microsecond=0).isoformat()


def selected_pet_id(pets: list[dict[str, object]]) -> int | None:
    if not pets:
        return None
    valid_ids = [pet["id"] for pet in pets]
    if st.session_state.selected_pet_id not in valid_ids:
        st.session_state.selected_pet_id = valid_ids[0]
    return st.session_state.selected_pet_id


def render_brand(logo_uri: str | None, language: str, current_user: dict[str, object] | None, subscription: dict[str, object] | None) -> None:
    if logo_uri:
        mark = f'<img src="{logo_uri}" alt="Pet Help AI logo" class="sidebar-brand-mark"/>'
    else:
        mark = '<div class="sidebar-brand-mark sidebar-fallback">PH</div>'

    plan_text = ""
    if subscription:
        plan_text = f"{tr('plan', language)}: {status_badge(str(subscription.get('status', 'free')), language)}"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            {mark}
            <div>
                <div class="sidebar-brand-name">Pet Help AI</div>
                <div class="sidebar-brand-copy">{escape(tr('app_tagline', language))}</div>
            </div>
        </div>
        <div class="sidebar-note">
            <strong>{escape(str(current_user['name'])) if current_user else 'Pet Help AI'}</strong><br/>
            {escape(plan_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth(language: str) -> None:
    st.title("Pet Help AI")
    st.caption(tr("app_tagline", language))
    tab_login, tab_register, tab_reset = st.tabs([tr("login", language), tr("register", language), tr("reset", language)])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input(tr("email", language))
            password = st.text_input(tr("password", language), type="password")
            submitted = st.form_submit_button(tr("login_button", language), use_container_width=True)
        if submitted:
            user = authenticate_user(email, password)
            if user:
                st.session_state.user_id = user["id"]
                st.rerun()
            else:
                st.error(tr("auth_error", language))

    with tab_register:
        with st.form("register_form"):
            name = st.text_input(tr("name", language))
            email = st.text_input(tr("email", language), key="register_email")
            password = st.text_input(tr("password", language), type="password", key="register_password")
            timezone = st.selectbox(tr("timezone", language), TIMEZONE_OPTIONS)
            submitted = st.form_submit_button(tr("register_button", language), use_container_width=True)
        if submitted:
            try:
                user = create_user(name or "Pet Parent", email, password, timezone)
                st.session_state.user_id = user["id"]
                st.success(tr("register_ok", language))
                st.rerun()
            except Exception:
                st.error("Email already exists.")

    with tab_reset:
        st.caption(tr("reset_hint", language))
        with st.form("reset_form"):
            email = st.text_input(tr("email", language), key="reset_email")
            password = st.text_input(tr("new_password", language), type="password")
            submitted = st.form_submit_button(tr("reset_button", language), use_container_width=True)
        if submitted:
            if update_password(email, password):
                st.success(tr("reset_ok", language))
            else:
                st.error(tr("auth_error", language))


def render_paywall(language: str, message: str) -> None:
    st.markdown(
        f"""
        <div class="lock-box">
            <h3>{escape(tr('paywall_title', language))}</h3>
            <p>{escape(message)}</p>
            <p>{escape(tr('paywall_copy', language))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(tr("open_paywall", language), use_container_width=False):
        go_to("subscription")
        st.rerun()


def metric_card(title: str, value: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <h4>{escape(title)}</h4>
            <div style="font-size:1.6rem;color:#14363b;font-weight:700;">{escape(value)}</div>
            <div class="pet-meta">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(current_user: dict[str, object], subscription: dict[str, object], language: str, logo_uri: str | None) -> None:
    image = f'<img src="{logo_uri}" alt="logo" class="brand-mark"/>' if logo_uri else '<div class="brand-fallback">PH</div>'
    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand-lockup">
                {image}
                <div>
                    <div class="brand-name">Pet Help AI</div>
                    <div class="brand-domain">pethelpai.com</div>
                </div>
            </div>
            <div class="app-summary">
                <div class="app-summary-label">{escape(tr('plan', language))}</div>
                <div class="app-summary-name">{escape(str(current_user['name']))}</div>
                <div class="app-summary-copy">{escape(status_badge(str(subscription.get('status', 'free')), language))} • {escape(tr('value_line', language))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(current_user: dict[str, object], subscription: dict[str, object], language: str, logo_uri: str | None) -> str:
    render_brand(logo_uri, language, current_user, subscription)
    st.sidebar.selectbox(
        tr("language", language),
        ["ru", "en"],
        index=0 if language == "ru" else 1,
        key="language",
        format_func=lambda code: tr(f"lang_{code}", language),
    )
    nav_labels = {
        "dashboard": tr("nav_dashboard", language),
        "pets": tr("nav_pets", language),
        "calendar": tr("nav_calendar", language),
        "health": tr("nav_health", language),
        "expenses": tr("nav_expenses", language),
        "documents": tr("nav_documents", language),
        "subscription": tr("nav_subscription", language),
        "settings": tr("nav_settings", language),
    }
    pages = NAV_ITEMS + (["admin"] if current_user.get("role") == "admin" else [])
    selected = st.sidebar.radio(
        " ",
        pages,
        index=pages.index(st.session_state.nav) if st.session_state.nav in pages else 0,
        format_func=lambda item: nav_labels.get(item, tr("nav_admin", language)),
    )
    st.session_state.nav = selected
    pending_notifications = len(list_notifications(int(current_user["id"]), only_pending=True))
    st.sidebar.markdown(
        f"""
        <div class="soft-note">
            <strong>{escape(tr('notifications', language))}</strong><br/>
            {pending_notifications}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button(tr("logout", language), use_container_width=True):
        st.session_state.user_id = None
        st.rerun()
    return selected


def save_pet_form(user_id: int, language: str, pet: dict[str, object] | None = None) -> None:
    is_edit = pet is not None
    with st.form(f"pet_form_{pet['id'] if pet else 'new'}", clear_on_submit=not is_edit):
        avatar = st.file_uploader(tr("pet_photo", language), type=["png", "jpg", "jpeg", "webp"], key=f"avatar_{pet['id'] if pet else 'new'}")
        name = st.text_input(tr("pet_name", language), value=str(pet["name"]) if pet else "")
        c1, c2 = st.columns(2)
        species = c1.selectbox(
            tr("species", language),
            SPECIES_OPTIONS,
            index=SPECIES_OPTIONS.index(str(pet["species"])) if pet and pet["species"] in SPECIES_OPTIONS else 0,
            format_func=lambda key: label(SPECIES_LABELS, key, language),
        )
        breed = c2.text_input(tr("breed", language), value=str(pet["breed"]) if pet else "")
        c3, c4 = st.columns(2)
        birth_value = date.fromisoformat(pet["birth_date"]) if pet and pet.get("birth_date") else date.today()
        birth_known = c3.checkbox(tr("birth_date_known", language), value=bool(pet and pet.get("birth_date")))
        birth_date_value = c4.date_input(tr("birth_date", language), value=birth_value)
        age_text = st.text_input(tr("age_text", language), value=str(pet["age_text"]) if pet else "")
        c5, c6, c7 = st.columns(3)
        sex = c5.selectbox(
            tr("sex", language),
            SEX_OPTIONS,
            index=SEX_OPTIONS.index(str(pet["sex"])) if pet and pet.get("sex") in SEX_OPTIONS else 2,
            format_func=lambda key: label(SEX_LABELS, key, language),
        )
        weight = c6.number_input(tr("weight", language), min_value=0.1, step=0.1, value=float(pet["weight"]) if pet and pet.get("weight") else 1.0)
        sterilized = c7.checkbox(tr("sterilized", language), value=bool(pet["sterilized"]) if pet else False)
        color = st.text_input(tr("color", language), value=str(pet["color"]) if pet else "")
        allergies = st.text_area(tr("allergies", language), value=str(pet["allergies"]) if pet else "", height=70)
        chronic_conditions = st.text_area(tr("chronic_conditions", language), value=str(pet["chronic_conditions"]) if pet else "", height=70)
        c8, c9, c10 = st.columns(3)
        chip_number = c8.text_input(tr("chip_number", language), value=str(pet["chip_number"]) if pet else "")
        clinic_name = c9.text_input(tr("clinic_name", language), value=str(pet["clinic_name"]) if pet else "")
        vet_name = c10.text_input(tr("vet_name", language), value=str(pet["vet_name"]) if pet else "")
        submitted = st.form_submit_button(tr("update_pet", language) if is_edit else tr("save_pet", language), use_container_width=True)

    if submitted:
        avatar_url = pet["avatar_url"] if pet else None
        if avatar is not None:
            avatar_url = uploaded_image_to_data_uri(avatar)
        payload = {
            "name": name,
            "species": species,
            "breed": breed,
            "birth_date": birth_date_value.isoformat() if birth_known and birth_date_value else None,
            "age_text": age_text,
            "sex": sex,
            "weight": float(weight),
            "sterilized": sterilized,
            "color": color,
            "allergies": allergies,
            "chronic_conditions": chronic_conditions,
            "chip_number": chip_number,
            "avatar_url": avatar_url,
            "clinic_name": clinic_name,
            "vet_name": vet_name,
        }
        if is_edit:
            update_pet(int(pet["id"]), user_id, payload)
        else:
            create_pet(user_id, payload)
        st.success(tr("pet_saved", language))
        st.rerun()


def render_dashboard(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("dashboard_title", language))
    upcoming = list_upcoming_events(int(user["id"]))
    today_tasks = list_today_tasks(int(user["id"]))
    expenses = list_expenses(int(user["id"]))
    weights = list_weight_logs(int(user["id"]))
    medications = list_medication_courses(int(user["id"]))
    notifications = list_notifications(int(user["id"]))

    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return

    recommendations = smart_recommendations(
        pets=pets,
        events=upcoming,
        weights=weights,
        expenses=expenses,
        medications=medications,
        subscription=subscription,
        language=language,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(tr("nav_pets", language), str(len(pets)))
    with c2:
        metric_card(tr("today_tasks", language), str(len(today_tasks)))
    with c3:
        metric_card(tr("notifications", language), str(len(notifications)))
    with c4:
        summary = expense_summary(int(user["id"]))
        metric_card(tr("month_total", language), f"${summary['month']:.0f}")

    action1, action2, action3 = st.columns(3)
    if action1.button(tr("add_event", language), use_container_width=True):
        go_to("calendar")
        st.rerun()
    if action2.button(tr("add_log", language), use_container_width=True):
        go_to("health")
        st.rerun()
    if action3.button(tr("add_expense", language), use_container_width=True):
        go_to("expenses")
        st.rerun()

    if recommendations:
        st.markdown(f"#### {tr('recommendations', language)}")
        for item in recommendations:
            st.markdown(f"<div class='warning-box'>{escape(item)}</div>", unsafe_allow_html=True)

    st.markdown(f"#### {tr('today_tasks', language)}")
    if today_tasks:
        for task in today_tasks:
            cols = st.columns([6, 2, 2])
            cols[0].markdown(
                f"**{escape(task['title'])}**  \n{escape(task['pet_name'])} • {escape(format_datetime(task['scheduled_at'], language))}"
            )
            if cols[1].button(tr("complete", language), key=f"dash_complete_{task['id']}", use_container_width=True):
                mark_event_completed(int(user["id"]), int(task["id"]))
                st.rerun()
            if cols[2].button(tr("miss", language), key=f"dash_miss_{task['id']}", use_container_width=True):
                mark_event_missed(int(user["id"]), int(task["id"]))
                st.rerun()
    else:
        st.info(tr("no_data", language))

    st.markdown(f"#### {tr('notifications', language)}")
    if notifications:
        for note in notifications[:5]:
            title = note.get("event_title") or note["message"]
            cols = st.columns([8, 2])
            cols[0].markdown(f"**{escape(str(title))}**  \n{escape(note.get('pet_name') or '')} • {escape(format_datetime(note['send_at'], language))}")
            if cols[1].button("OK", key=f"note_{note['id']}", use_container_width=True):
                mark_notification_read(int(user["id"]), int(note["id"]))
                st.rerun()
    else:
        st.info(tr("no_data", language))

    st.markdown(f"#### {tr('pets_overview', language)}")
    health_logs = list_health_logs(int(user["id"]))
    for pet in pets:
        pet_upcoming = [event for event in upcoming if event["pet_id"] == pet["id"]]
        records = pet_recent_records(int(pet["id"]), list_care_events(int(user["id"]), pet_id=int(pet["id"])), health_logs)
        next_item = pet_upcoming[0] if pet_upcoming else None
        preview_col, detail_col = st.columns([1, 4])
        with preview_col:
            render_avatar_image(str(pet.get("avatar_url") or ""), width=90)
        with detail_col:
            st.markdown(
                f"""
                <div class="pet-card">
                    <h4>{escape(str(pet['name']))}</h4>
                    <div class="pet-meta">{escape(label(SPECIES_LABELS, str(pet['species']), language))} • {escape(pet_age_display(pet.get('birth_date'), pet.get('age_text'), language))}</div>
                    <div><strong>{escape(tr('pet_card_upcoming', language))}:</strong> {escape(next_item['title']) if next_item else '—'}</div>
                    <div><strong>{escape(tr('pet_card_spend', language))}:</strong> ${pet_month_expense(expenses, int(pet['id'])):.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if records:
            for record in records[:3]:
                st.caption(f"{record['title']} • {format_datetime(record['timestamp'], language)}")


def render_empty_onboarding(user_id: int, subscription: dict[str, object], language: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <h3>{escape(tr('onboarding_title', language))}</h3>
            <p>{escape(tr('onboarding_copy', language))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    save_pet_form(user_id, language)


def render_pets_page(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("pet_title", language))
    limits = free_limits(subscription)
    premium = subscription_is_premium(subscription)

    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return

    col_main, col_side = st.columns([2, 1])
    with col_side:
        if st.button(tr("add_pet", language), use_container_width=True):
            if limits["max_pets"] is not None and count_user_pets(int(user["id"])) >= limits["max_pets"]:
                log_product_event(int(user["id"]), "paywall_opened", {"source": "second_pet"})
                render_paywall(language, tr("second_pet_lock", language))
            else:
                st.session_state.show_new_pet_form = True
        if st.session_state.get("show_new_pet_form"):
            save_pet_form(int(user["id"]), language)

    selected_id = selected_pet_id(pets)
    pet_map = {pet["id"]: pet for pet in pets}
    pet = pet_map[selected_id] if selected_id else pets[0]

    with col_main:
        st.selectbox(
            tr("pet_select", language),
            [item["id"] for item in pets],
            index=[item["id"] for item in pets].index(pet["id"]),
            format_func=lambda item: str(pet_map[item]["name"]),
            key="selected_pet_id",
        )
        pet = pet_map[st.session_state.selected_pet_id]

        render_avatar_image(str(pet.get("avatar_url") or ""), width=180)

        c1, c2, c3 = st.columns(3)
        c1.metric(tr("species", language), label(SPECIES_LABELS, str(pet["species"]), language))
        c2.metric(tr("weight", language), f"{pet.get('weight') or '—'} lb")
        c3.metric("Age", pet_age_display(pet.get("birth_date"), pet.get("age_text"), language))

        st.markdown(f"#### {tr('pet_form_title', language)}")
        save_pet_form(int(user["id"]), language, pet)

        if st.button(tr("starter_calendar", language), use_container_width=False):
            for template in starter_calendar_template(str(pet["species"]), language):
                create_care_event(
                    int(user["id"]),
                    {
                        "pet_id": int(pet["id"]),
                        **template,
                    },
                )
            st.success(tr("starter_added", language))
            st.rerun()

        pet_events = list_care_events(int(user["id"]), pet_id=int(pet["id"]))
        pet_logs = list_health_logs(int(user["id"]), pet_id=int(pet["id"]))
        pet_docs = list_documents(int(user["id"]), pet_id=int(pet["id"]))
        pet_expenses = [row for row in list_expenses(int(user["id"]), pet_id=int(pet["id"]))]
        st.markdown(f"#### {tr('pet_card_upcoming', language)}")
        if pet_events:
            for event in pet_events[:5]:
                st.markdown(f"- {event['title']} • {format_datetime(event['scheduled_at'], language)} • {status_badge(event_status(event), language)}")
        else:
            st.info(tr("no_data", language))

        st.markdown(f"#### {tr('pet_card_records', language)}")
        recent = pet_recent_records(int(pet["id"]), pet_events, pet_logs)
        if recent:
            for item in recent:
                st.markdown(f"- {item['title']} • {format_datetime(item['timestamp'], language)}")
        else:
            st.info(tr("no_data", language))

        st.markdown(f"#### {tr('documents_title', language)}")
        st.caption(f"{len(pet_docs)} docs • ${sum(item['amount'] for item in pet_expenses):.0f} total spend")


def render_calendar_page(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("calendar_title", language))
    st.caption(tr("calendar_copy", language))
    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return

    limits = free_limits(subscription)
    with st.expander(tr("add_event", language), expanded=True):
        with st.form("event_form"):
            pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item))
            event_type = st.selectbox(tr("event_type", language), EVENT_TYPES, format_func=lambda key: label(EVENT_TYPE_LABELS, key, language))
            title = st.text_input(tr("event_title", language))
            description = st.text_area(tr("event_description", language), height=80)
            c1, c2 = st.columns(2)
            event_date = c1.date_input(tr("scheduled_date", language), value=date.today())
            event_time = c2.time_input(tr("scheduled_time", language), value=time(10, 0))
            c3, c4 = st.columns(2)
            recurrence = c3.selectbox(tr("recurrence", language), RECURRENCE_OPTIONS, format_func=lambda key: label(RECURRENCE_LABELS, key, language))
            reminders = c4.multiselect(tr("reminders", language), REMINDER_OPTIONS, default=["1d", "day_of"], format_func=lambda key: label(REMINDER_LABELS, key, language))
            submitted = st.form_submit_button(tr("create_event", language), use_container_width=True)
        if submitted:
            if limits["max_events"] is not None and count_active_events(int(user["id"])) >= limits["max_events"]:
                log_product_event(int(user["id"]), "paywall_opened", {"source": "event_limit"})
                render_paywall(language, tr("event_limit_lock", language))
            else:
                if not limits["advanced_reminders"] and len(reminders) > 2:
                    reminders = reminders[:2]
                create_care_event(
                    int(user["id"]),
                    {
                        "pet_id": pet_id,
                        "type": event_type,
                        "title": title or label(EVENT_TYPE_LABELS, event_type, language),
                        "description": description,
                        "scheduled_at": combine_date_time(event_date, event_time),
                        "recurrence_rule": recurrence,
                        "reminder_settings": reminders,
                    },
                )
                st.success(tr("event_saved", language))
                st.rerun()

    events = list_care_events(int(user["id"]))
    event_filter_pet = st.selectbox(tr("pet_select", language), ["all"] + [pet["id"] for pet in pets], format_func=lambda value: tr("nav_pets", language) if value == "all" else next(p["name"] for p in pets if p["id"] == value))
    filtered = [event for event in events if event_filter_pet == "all" or event["pet_id"] == event_filter_pet]
    warning = upcoming_warning_level(filtered[:5])
    if warning != "calm":
        text = "Urgent reminders are close." if language == "en" else "Есть очень близкие напоминания."
        st.markdown(f"<div class='warning-box'>{escape(text)}</div>", unsafe_allow_html=True)
    for event in filtered:
        status = event_status(event)
        cols = st.columns([6, 2, 2])
        cols[0].markdown(
            f"**{escape(event['title'])}**  \n{escape(event['pet_name'])} • {escape(label(EVENT_TYPE_LABELS, event['type'], language))} • {escape(format_datetime(event['scheduled_at'], language))} • {escape(status_badge(status, language))}"
        )
        if status == "planned" and cols[1].button(tr("complete", language), key=f"event_complete_{event['id']}", use_container_width=True):
            mark_event_completed(int(user["id"]), int(event["id"]))
            st.rerun()
        if status == "planned" and cols[2].button(tr("miss", language), key=f"event_miss_{event['id']}", use_container_width=True):
            mark_event_missed(int(user["id"]), int(event["id"]))
            st.rerun()


def render_health_page(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("health_title", language))
    st.caption(tr("disclaimer", language))
    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return

    tab_logs, tab_meds, tab_weight = st.tabs([tr("health_title", language), tr("medication_title", language), tr("weight_title", language)])

    with tab_logs:
        with st.form("health_form"):
            pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item), key="health_pet")
            log_type = st.selectbox(tr("log_type", language), LOG_TYPES, format_func=lambda key: label(LOG_TYPE_LABELS, key, language))
            symptom = st.text_input(tr("symptom", language))
            severity = st.selectbox(tr("severity", language), SEVERITY_OPTIONS, format_func=lambda key: label(SEVERITY_LABELS, key, language))
            description = st.text_area(tr("description", language), height=90)
            c1, c2, c3 = st.columns(3)
            appetite = c1.text_input(tr("appetite", language))
            activity = c2.text_input(tr("activity", language))
            stool = c3.text_input(tr("stool", language))
            mood = st.text_input(tr("mood", language))
            attachment = st.file_uploader(tr("attachment", language), type=["png", "jpg", "jpeg", "webp", "mp4", "mov"], key="health_attachment")
            submitted = st.form_submit_button(tr("save_log", language), use_container_width=True)
        if submitted:
            attachment_url = save_uploaded_file(attachment, int(user["id"]), "health") if attachment else None
            create_health_log(
                int(user["id"]),
                {
                    "pet_id": pet_id,
                    "log_type": log_type,
                    "symptom": symptom,
                    "severity": severity,
                    "description": description,
                    "attachment_url": attachment_url,
                    "recorded_at": now_iso_local(),
                    "appetite": appetite,
                    "activity": activity,
                    "stool_vomit": stool,
                    "mood": mood,
                },
            )
            st.success(tr("log_saved", language))
            st.rerun()

        logs = list_health_logs(int(user["id"]))
        for item in logs[:20]:
            st.markdown(f"**{item.get('symptom') or label(LOG_TYPE_LABELS, item['log_type'], language)}**  \n{item['pet_name']} • {format_datetime(item['recorded_at'], language)}")
            if item.get("description"):
                st.caption(item["description"])

    with tab_meds:
        with st.form("med_form"):
            pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item), key="med_pet")
            medicine_name = st.text_input(tr("medicine_name", language))
            dosage = st.text_input(tr("dosage", language))
            frequency = st.selectbox(tr("frequency", language), MEDICATION_FREQUENCIES, format_func=lambda key: label(MEDICATION_FREQUENCY_LABELS, key, language))
            c1, c2 = st.columns(2)
            start = c1.date_input(tr("start_date", language), value=date.today(), key="med_start")
            has_end_date = c2.checkbox(tr("course_has_end", language), value=False)
            end = st.date_input(tr("end_date", language), value=date.today(), key="med_end")
            note = st.text_area(tr("note", language), height=80)
            submitted = st.form_submit_button(tr("save_course", language), use_container_width=True)
        if submitted:
            create_medication_course(
                int(user["id"]),
                {
                    "pet_id": pet_id,
                    "medicine_name": medicine_name,
                    "dosage": dosage,
                    "frequency": frequency,
                    "start_date": datetime.combine(start, time(9, 0)).isoformat(),
                    "end_date": datetime.combine(end, time(9, 0)).isoformat() if has_end_date else None,
                    "note": note,
                },
            )
            st.success(tr("course_saved", language))
            st.rerun()

        courses = list_medication_courses(int(user["id"]))
        for course in courses:
            cols = st.columns([7, 2])
            cols[0].markdown(
                f"**{course['medicine_name']}**  \n{course['pet_name']} • {label(MEDICATION_FREQUENCY_LABELS, course['frequency'], language)} • {format_datetime(course.get('next_due_at'), language)}"
            )
            if course["status"] == "active" and cols[1].button(tr("mark_given", language), key=f"med_{course['id']}", use_container_width=True):
                mark_medication_given(int(user["id"]), int(course["id"]))
                st.rerun()

    with tab_weight:
        with st.form("weight_form"):
            pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item), key="weight_pet")
            c1, c2 = st.columns(2)
            weight = c1.number_input(tr("weight", language), min_value=0.1, step=0.1)
            measured = c2.date_input(tr("weight_date", language), value=date.today())
            note = st.text_input(tr("weight_note", language))
            submitted = st.form_submit_button(tr("save_weight", language), use_container_width=True)
        if submitted:
            add_weight_log(int(user["id"]), pet_id, float(weight), datetime.combine(measured, time(9, 0)).isoformat(), note)
            st.success(tr("weight_saved", language))
            st.rerun()

        weight_logs = list_weight_logs(int(user["id"]))
        if weight_logs:
            frame = pd.DataFrame(weight_logs)
            frame["measured_at"] = pd.to_datetime(frame["measured_at"])
            chart = frame[["measured_at", "weight"]].set_index("measured_at")
            st.line_chart(chart)
            st.dataframe(frame[["pet_name", "weight", "measured_at", "note"]], use_container_width=True)
        else:
            st.info(tr("no_data", language))


def render_expenses_page(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("expenses_title", language))
    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return

    with st.form("expense_form"):
        pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item))
        c1, c2, c3 = st.columns(3)
        category = c1.selectbox(tr("category", language), EXPENSE_CATEGORIES, format_func=lambda key: label(EXPENSE_CATEGORY_LABELS, key, language))
        amount = c2.number_input(tr("amount", language), min_value=0.0, step=1.0)
        currency = c3.text_input(tr("currency", language), value="USD")
        spent_at = st.date_input(tr("spent_at", language), value=date.today())
        note = st.text_input(tr("note", language))
        submitted = st.form_submit_button(tr("save_expense", language), use_container_width=True)
    if submitted:
        add_expense(
            int(user["id"]),
            {
                "pet_id": pet_id,
                "category": category,
                "amount": amount,
                "currency": currency,
                "spent_at": datetime.combine(spent_at, time(9, 0)).isoformat(),
                "note": note,
            },
        )
        st.success(tr("expense_saved", language))
        st.rerun()

    summary = expense_summary(int(user["id"]))
    c1, c2 = st.columns(2)
    c1.metric(tr("month_total", language), f"${summary['month']:.0f}")
    c2.metric(tr("all_time_total", language), f"${summary['all_time']:.0f}")
    monthly_rows = monthly_expense_rows(int(user["id"]))
    if monthly_rows:
        frame = pd.DataFrame(monthly_rows).set_index("month")
        st.bar_chart(frame)
    expenses = list_expenses(int(user["id"]))
    if expenses:
        st.dataframe(pd.DataFrame(expenses)[["pet_name", "category", "amount", "currency", "spent_at", "note"]], use_container_width=True)
    else:
        st.info(tr("no_data", language))


def render_documents_page(user: dict[str, object], subscription: dict[str, object], pets: list[dict[str, object]], language: str) -> None:
    st.title(tr("documents_title", language))
    if not pets:
        render_empty_onboarding(int(user["id"]), subscription, language)
        return
    if not subscription_is_premium(subscription):
        render_paywall(language, tr("document_lock", language))
        return

    with st.form("document_form"):
        pet_id = st.selectbox(tr("pet_select", language), [pet["id"] for pet in pets], format_func=lambda item: next(p["name"] for p in pets if p["id"] == item))
        doc_type = st.selectbox(tr("document_type", language), DOCUMENT_TYPES, format_func=lambda key: label(DOCUMENT_TYPE_LABELS, key, language))
        note = st.text_input(tr("document_note", language))
        file = st.file_uploader(tr("upload_document", language), type=["png", "jpg", "jpeg", "webp", "pdf", "txt"])
        submitted = st.form_submit_button(tr("upload_document", language), use_container_width=True)
    if submitted and file is not None:
        path = save_uploaded_file(file, int(user["id"]), "document")
        create_document(
            int(user["id"]),
            {
                "pet_id": pet_id,
                "type": doc_type,
                "file_url": path,
                "file_name": file.name,
                "uploaded_at": now_iso_local(),
                "note": note,
            },
        )
        st.success(tr("document_saved", language))
        st.rerun()

    docs = list_documents(int(user["id"]))
    for doc in docs:
        file_path = Path(str(doc["file_url"]))
        st.markdown(f"**{doc['file_name']}**  \n{doc['pet_name']} • {label(DOCUMENT_TYPE_LABELS, doc['type'], language)} • {format_datetime(doc['uploaded_at'], language)}")
        if file_path.exists():
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                st.image(str(file_path), width=240)
            with st.expander(doc["file_name"], expanded=False):
                st.download_button(doc["file_name"], data=file_path.read_bytes(), file_name=doc["file_name"])


def render_subscription_page(user: dict[str, object], subscription: dict[str, object], language: str) -> None:
    st.title(tr("subscription_title", language))
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-kicker">{escape(tr('status', language))}</div>
            <h3>{escape(status_badge(str(subscription.get('status', 'free')), language))}</h3>
            <p>{escape(tr('value_line', language))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    if c1.button(tr("trial_action", language), use_container_width=True):
        start_trial(int(user["id"]))
        st.success(tr("subscription_saved", language))
        st.rerun()
    if c2.button(tr("monthly_action", language), use_container_width=True):
        activate_subscription(int(user["id"]), "premium_monthly")
        st.success(tr("subscription_saved", language))
        st.rerun()
    if c3.button(tr("yearly_action", language), use_container_width=True):
        activate_subscription(int(user["id"]), "premium_yearly")
        st.success(tr("subscription_saved", language))
        st.rerun()
    if subscription.get("status") in {"trialing", "active", "canceled"}:
        st.caption(f"{tr('next_charge', language)}: {next_due_text(subscription, language)}")
        if st.button(tr("cancel_action", language), use_container_width=False):
            cancel_subscription(int(user["id"]))
            st.success(tr("subscription_saved", language))
            st.rerun()

    st.markdown("### Free vs Premium")
    free_col, premium_col = st.columns(2)
    free_col.markdown(
        """
        - 1 pet
        - Basic dashboard
        - Limited calendar
        - Basic reminders
        - Basic health log
        - Basic expenses
        """
    )
    premium_col.markdown(
        """
        - Multiple pets
        - Unlimited recurring events
        - Full history
        - Documents and files
        - Expense analytics
        - Trial and renewal flow
        """
    )


def render_settings_page(user: dict[str, object], language: str) -> None:
    st.title(tr("settings_title", language))
    st.markdown(f"### {tr('email_channel', language)}")
    st.caption(tr("phone_note", language))
    if email_configured():
        st.success(tr("email_ready", language))
        if st.button(tr("run_sweep", language), use_container_width=False, key="settings_sweep"):
            result = dispatch_due_email_notifications(int(user["id"]))
            st.success(tr("sweep_result", language).format(sent=result["sent"], failed=result["failed"]))
    else:
        st.info(tr("email_missing", language))

    with st.form("settings_form"):
        name = st.text_input(tr("name", language), value=str(user["name"]))
        timezone = st.selectbox(tr("timezone", language), TIMEZONE_OPTIONS, index=TIMEZONE_OPTIONS.index(str(user["timezone"])) if str(user["timezone"]) in TIMEZONE_OPTIONS else 0)
        c1, c2, c3 = st.columns(3)
        email_on = c1.checkbox(tr("notifications_email", language), value=bool(user["notification_email"]))
        in_app = c2.checkbox(tr("notifications_in_app", language), value=bool(user["notification_in_app"]))
        push_on = c3.checkbox(tr("notifications_push", language), value=bool(user["notification_push"]))
        submitted = st.form_submit_button(tr("save_settings", language), use_container_width=True)
    if submitted:
        update_user_settings(int(user["id"]), name=name, timezone=timezone, notification_email=email_on, notification_in_app=in_app, notification_push=push_on)
        st.success(tr("settings_saved", language))
        st.rerun()

    st.markdown(f"### {tr('reset', language)}")
    with st.form("password_change_form"):
        new_password = st.text_input(tr("new_password", language), type="password")
        submitted = st.form_submit_button(tr("reset_button", language), use_container_width=False)
    if submitted and new_password:
        update_password(str(user["email"]), new_password)
        st.success(tr("reset_ok", language))

    st.markdown(f"### {tr('support_title', language)}")
    with st.form("support_form"):
        subject = st.text_input(tr("support_subject", language))
        message = st.text_area(tr("support_message", language), height=120)
        submitted = st.form_submit_button(tr("send_ticket", language), use_container_width=False)
    if submitted and subject and message:
        create_support_ticket(int(user["id"]), subject, message)
        st.success(tr("ticket_saved", language))


def render_admin_page(language: str) -> None:
    st.title(tr("admin_title", language))
    summary = analytics_summary()
    totals = summary["totals"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("users", language), str(totals["users"]))
    c2.metric(tr("nav_pets", language), str(totals["pets"]))
    c3.metric(tr("subscriptions", language), str(totals["subscriptions"]))
    c4.metric("DAU / WAU / MAU", f"{totals['dau']} / {totals['wau']} / {totals['mau']}")

    if email_configured():
        if st.button(tr("run_sweep", language), use_container_width=False, key="admin_sweep"):
            result = dispatch_due_email_notifications()
            st.success(tr("sweep_result", language).format(sent=result["sent"], failed=result["failed"]))
    else:
        st.info(tr("email_missing", language))

    st.markdown(f"### {tr('analytics', language)}")
    if summary["events"]:
        st.dataframe(pd.DataFrame(summary["events"]), use_container_width=True)
    st.markdown(f"### {tr('users', language)}")
    st.dataframe(pd.DataFrame(admin_users()), use_container_width=True)
    st.markdown(f"### {tr('support', language)}")
    tickets = list_support_tickets()
    if tickets:
        st.dataframe(pd.DataFrame(tickets), use_container_width=True)
    else:
        st.info(tr("no_data", language))


def now_iso_local() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def maybe_dispatch_email_notifications() -> None:
    if not email_configured():
        return
    now = datetime.utcnow()
    last = st.session_state.get("last_email_dispatch_check")
    if isinstance(last, datetime) and (now - last).total_seconds() < 300:
        return
    dispatch_due_email_notifications()
    st.session_state.last_email_dispatch_check = now


def main() -> None:
    init_db()
    st.set_page_config(page_title="Pet Help AI", page_icon="🐾", layout="wide")
    inject_styles()
    inject_local_overrides()
    ensure_state()

    language = language_code(st.session_state.language)
    logo_uri = load_logo_data_uri()

    if not st.session_state.user_id:
        render_auth(language)
        return

    refresh_subscription_state(int(st.session_state.user_id))
    user = get_user(int(st.session_state.user_id))
    if not user:
        st.session_state.user_id = None
        st.rerun()
        return
    maybe_dispatch_email_notifications()
    subscription = get_subscription(int(user["id"]))
    pets = list_pets(int(user["id"]))

    render_header(user, subscription, language, logo_uri)
    selected_page = render_sidebar(user, subscription, language, logo_uri)

    if selected_page == "dashboard":
        render_dashboard(user, subscription, pets, language)
    elif selected_page == "pets":
        render_pets_page(user, subscription, pets, language)
    elif selected_page == "calendar":
        render_calendar_page(user, subscription, pets, language)
    elif selected_page == "health":
        render_health_page(user, subscription, pets, language)
    elif selected_page == "expenses":
        render_expenses_page(user, subscription, pets, language)
    elif selected_page == "documents":
        render_documents_page(user, subscription, pets, language)
    elif selected_page == "subscription":
        render_subscription_page(user, subscription, language)
    elif selected_page == "settings":
        render_settings_page(user, language)
    elif selected_page == "admin" and user.get("role") == "admin":
        render_admin_page(language)


if __name__ == "__main__":
    main()
