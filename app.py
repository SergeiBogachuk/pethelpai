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


def ensure_state() -> None:
    st.session_state.setdefault("pet_profiles", [])
    st.session_state.setdefault("selected_profile_id", "__new__")
    st.session_state.setdefault("last_food_analysis", None)
    st.session_state.setdefault("last_emergency_analysis", None)
    st.session_state.setdefault("food_follow_up_answer", "")
    st.session_state.setdefault("history", [])


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


def format_profile_label(profile: dict[str, object]) -> str:
    name = str(profile.get("name") or "Your pet")
    species = str(profile.get("species") or "Dog")
    weight = profile.get("weight_lbs") or 0
    return f"{name} • {species} • {weight:.0f} lb"


def current_pet_summary(profile: dict[str, object]) -> str:
    breed = str(profile.get("breed") or "").strip()
    species = str(profile.get("species") or "Dog")
    age_years = float(profile.get("age_years") or 0)
    weight_lbs = float(profile.get("weight_lbs") or 0)
    conditions = profile.get("conditions") or []
    details = [species]

    if age_years:
        details.append(f"{age_years:.0f} years")
    if weight_lbs:
        details.append(f"{weight_lbs:.0f} lb")
    if breed:
        details.append(breed)
    if conditions:
        details.append(", ".join(conditions))

    return " • ".join(details)


def render_header(current_pet: dict[str, object]) -> None:
    photo_mode = "Photo + text" if has_openai_key() else "Text first"
    right_copy = current_pet_summary(current_pet)
    logo_data_uri = load_logo_data_uri()
    logo_markup = (
        f'<img src="{logo_data_uri}" alt="Pet Help AI logo" class="brand-mark" />'
        if logo_data_uri
        else '<div class="brand-fallback">PH</div>'
    )

    left_col, right_col = st.columns([1.5, 0.95], gap="large")
    with left_col:
        st.markdown(
            f"""
            <div class="hero-shell">
                <div class="brand-lockup">
                    {logo_markup}
                    <div>
                        <div class="brand-name">Pet Help AI</div>
                        <div class="brand-domain">pethelpai.com</div>
                    </div>
                </div>
                <h1 class="hero-title">Know what's safe for your pet in seconds.</h1>
                <p class="hero-copy">
                    Built for quick food questions, ingredient checks, and those anxious
                    “my pet already ate this” moments when you need a clear next step fast.
                </p>
                <div class="hero-chip-row">
                    <div class="hero-chip">Dogs + cats</div>
                    <div class="hero-chip">Plain-language verdicts</div>
                    <div class="hero-chip">Personalized to {escape(str(current_pet.get("name") or "your pet"))}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Active Pet Profile</div>
                <p class="status-name">{escape(str(current_pet.get("name") or "Draft pet"))}</p>
                <p class="status-copy">{escape(right_copy)}</p>
                <div class="status-row">
                    <div class="status-pill"><span>Scan mode</span><strong>{escape(photo_mode)}</strong></div>
                    <div class="status-pill"><span>Best for</span><strong>Food safety checks</strong></div>
                    <div class="status-pill"><span>Escalates when</span><strong>Toxins or symptoms appear</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_focus_strip() -> None:
    st.markdown(
        """
        <div class="focus-strip">
            <div class="focus-copy">
                Start with a short food description. Use <strong>Emergency Mode</strong> only if the food was already eaten
                or symptoms have started.
            </div>
            <div class="focus-badge">Clear, fast triage</div>
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


def shop_search_url(provider: str, query: str) -> str:
    encoded = quote_plus(query)
    if provider == "Chewy":
        return f"https://www.chewy.com/s?query={encoded}"
    return f"https://www.amazon.com/s?k={encoded}"


def render_safe_swap(analysis: dict[str, object]) -> None:
    safe_swap = analysis.get("safe_swap") or {}
    items = safe_swap.get("items") or []
    if not items:
        return

    if analysis.get("verdict") == "Avoid" and analysis.get("already_ate"):
        render_soft_note(
            "This case is urgent enough that the immediate focus should stay on veterinary guidance. Safe Swap is better used for the next shopping run, not instead of care."
        )
        return

    def _render_swap_body() -> None:
        if safe_swap.get("subtitle"):
            st.caption(str(safe_swap["subtitle"]))

        swap_columns = st.columns(len(items), gap="large")
        for index, (column, item) in enumerate(zip(swap_columns, items)):
            with column:
                st.markdown(
                    f"""
                    <div class="swap-card">
                        <div class="swap-label">Swap Idea {index + 1}</div>
                        <h4>{escape(str(item['title']))}</h4>
                        <p>{escape(str(item['why']))}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                link_col1, link_col2 = st.columns(2)
                with link_col1:
                    st.link_button(
                        "Chewy",
                        shop_search_url("Chewy", str(item["query"])),
                        use_container_width=True,
                    )
                with link_col2:
                    st.link_button(
                        "Amazon",
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


def render_analysis(analysis: dict[str, object]) -> None:
    verdict = str(analysis["verdict"]).lower()
    badge_color = str(analysis["badge_color"])
    matched_labels = analysis.get("matched_labels") or []

    st.markdown(
        f"""
        <div class="result-card result-{verdict}">
            <div class="result-pill" style="color:{badge_color};">{escape(str(analysis['badge_label']))}</div>
            <h2 class="result-title">{escape(str(analysis['verdict']))}</h2>
            <p class="result-copy">{escape(str(analysis['summary']))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    risk_value = {"Safe": 0.2, "Caution": 0.62, "Avoid": 0.96}[str(analysis["verdict"])]
    st.caption(f"Confidence: {analysis['confidence'].title()}")
    st.progress(risk_value)

    if matched_labels:
        st.markdown("`Signals detected:` " + ", ".join(f"`{label}`" for label in matched_labels))

    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        render_detail_card("Do This Now", list(analysis["actions"])[:3])
    with right_col:
        render_detail_card("Why This Verdict", list(analysis["reasons"])[:3] or ["The item needs a closer ingredient check."])

    with st.expander("Symptoms to watch", expanded=str(analysis["verdict"]) == "Avoid"):
        for symptom in analysis["watch_for"]:
            st.write(f"- {symptom}")

    with st.expander("Safer alternatives", expanded=False):
        for item in analysis["alternatives"]:
            st.write(f"- {item}")

    render_safe_swap(analysis)

    if analysis.get("image_summary"):
        with st.expander("Image read", expanded=False):
            st.write(str(analysis["image_summary"]))


def add_to_history(channel: str, analysis: dict[str, object], current_pet: dict[str, object]) -> None:
    item = {
        "id": uuid4().hex[:8],
        "channel": channel,
        "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),
        "verdict": analysis["verdict"],
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


def render_history() -> None:
    if not st.session_state.history:
        render_empty_state(
            "History",
            "No checks yet",
            "Run a food safety scan or emergency review and your recent decisions will show up here.",
        )
        return

    for item in st.session_state.history:
        st.markdown(
            f"""
            <div class="history-item">
                <div class="history-meta">{escape(item['timestamp'])} • {escape(item['channel'])} • {escape(item['pet_name'])}</div>
                <strong>{escape(item['verdict'])}</strong> — {escape(item['summary'])}<br/>
                <span class="history-meta">{escape(str(item['food_text']))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def sidebar_profile_editor() -> dict[str, object]:
    profiles = st.session_state.pet_profiles
    options = ["__new__"] + [profile["id"] for profile in profiles]
    labels = {"__new__": "Draft pet profile"}
    labels.update({profile["id"]: format_profile_label(profile) for profile in profiles})

    if st.session_state.selected_profile_id not in options:
        st.session_state.selected_profile_id = "__new__"

    with st.expander("Pet profile", expanded=True):
        selected_profile_id = st.selectbox(
            "Active pet",
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

        st.markdown(
            """
            <div class="sidebar-note">
                Keep one pet profile accurate first. Weight, age, and chronic conditions can change how cautious the verdict should be.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(f"pet-profile-form-{selected_profile_id}"):
            name = st.text_input("Pet name", value=str(defaults.get("name") or ""))
            species = st.radio("Species", options=["Dog", "Cat"], index=0 if defaults.get("species") == "Dog" else 1, horizontal=True)
            age_years = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=float(defaults.get("age_years") or 0), step=1.0)
            weight_lbs = st.number_input("Weight (lb)", min_value=0.0, max_value=250.0, value=float(defaults.get("weight_lbs") or 0), step=1.0)
            breed = st.text_input("Breed or mix", value=str(defaults.get("breed") or ""))
            allergies = st.text_input("Allergies", value=str(defaults.get("allergies") or ""), placeholder="Chicken, dairy, beef")
            conditions = st.multiselect("Conditions", options=CONDITION_OPTIONS, default=list(defaults.get("conditions") or []))
            submitted = st.form_submit_button(
                "Save pet profile" if selected_profile_id == "__new__" else "Update pet profile",
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
            st.success(f"Profile saved for {profile_to_save['name']}.")
            st.rerun()

        if selected_profile_id != "__new__" and st.button("Delete active pet", use_container_width=True):
            remove_profile(selected_profile_id)
            st.session_state.selected_profile_id = "__new__"
            st.rerun()

    with st.expander("How verdicts work", expanded=False):
        st.write("`Safe` means relatively low risk when plain and portion-controlled.")
        st.write("`Caution` means ingredient, amount, or pet-specific risk needs a closer look.")
        st.write("`Avoid` means pause and escalate quickly, especially if the food was already eaten.")

    st.markdown(
        """
        <div class="sidebar-note">
            Pet Help AI supports quick decisions, but it does not replace a licensed veterinarian for urgent or worsening cases.
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        logo_data_uri = load_logo_data_uri()
        sidebar_logo = (
            f'<img src="{logo_data_uri}" alt="Pet Help AI logo" class="sidebar-brand-mark" />'
            if logo_data_uri
            else '<div class="sidebar-brand-mark sidebar-fallback">PH</div>'
        )
        st.markdown(
            f"""
            <div class="sidebar-brand">
                {sidebar_logo}
                <div>
                    <div class="sidebar-brand-name">Pet Help AI</div>
                    <div class="sidebar-brand-copy">Fast, minimal food safety checks for pet parents.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Fast, minimal food safety checks for pet parents.")
        current_pet = sidebar_profile_editor()

    render_header(current_pet)
    render_focus_strip()

    if not has_openai_key():
        render_soft_note(
            "Photo understanding is ready, but it needs OPENAI_API_KEY. The app still works right now with text descriptions and ingredient lists."
        )

    food_tab, emergency_tab, care_tab, history_tab = st.tabs(
        ["Food Check", "Emergency Mode", "Care Guide", "History"]
    )

    with food_tab:
        left_col, right_col = st.columns([1.05, 0.95], gap="large")
        with left_col:
            st.markdown("### Scan food, ingredients, or treats")
            st.caption("Best for routine questions before you share food, leftovers, or treats.")

            image_file = None
            with st.expander("Add photo (optional)", expanded=False):
                image_mode = st.radio("Image input", options=["Skip image", "Use camera", "Upload photo"], horizontal=True)

                if image_mode == "Use camera":
                    image_file = st.camera_input("Take a picture of the food or packaging")
                elif image_mode == "Upload photo":
                    image_file = st.file_uploader("Upload a food photo", type=["jpg", "jpeg", "png"], key="food_uploader")

                if image_file is not None:
                    st.image(image_file, caption="Photo for analysis", use_container_width=True)

            manual_text = st.text_area(
                "Food description or ingredients",
                placeholder="Example: peanut butter, banana, plain yogurt\nOr: chicken nuggets with ketchup\nOr paste the ingredient list from the package",
                height=160,
            )
            control_col1, control_col2 = st.columns(2)
            with control_col1:
                already_ate = st.toggle("My pet already ate some of this")
            with control_col2:
                amount = st.select_slider("Amount", options=AMOUNT_OPTIONS, value="Small bite")

            st.caption("Examples: peanut butter, rotisserie chicken, garlic bread, grapes, yogurt")

            if st.button("Analyze food safety", type="primary", use_container_width=True):
                if not manual_text.strip() and image_file is None:
                    st.warning("Add a food description, an ingredient list, or a photo first.")
                elif image_file is not None and not manual_text.strip() and not has_openai_key():
                    st.warning("For photo-only checks, add `OPENAI_API_KEY` or type a short food description below the image.")
                else:
                    image_summary = ""
                    if image_file is not None:
                        with st.spinner("Reading the photo..."):
                            image_result = extract_food_context_from_image(
                                image_file.getvalue(),
                                image_file.type or "image/jpeg",
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
                    )
                    st.session_state.last_food_analysis = analysis
                    st.session_state.food_follow_up_answer = ""
                    add_to_history("Food Check", analysis, current_pet)

        with right_col:
            st.markdown("### Verdict")
            if st.session_state.last_food_analysis:
                render_analysis(st.session_state.last_food_analysis)

                follow_up_question = st.text_input(
                    "Ask a follow-up",
                    placeholder="What symptoms should I watch for?",
                    key="food_follow_up_question",
                )
                if st.button("Answer follow-up", use_container_width=True):
                    st.session_state.food_follow_up_answer = answer_follow_up(
                        follow_up_question,
                        st.session_state.last_food_analysis,
                        current_pet,
                    )
                if st.session_state.food_follow_up_answer:
                    st.success(st.session_state.food_follow_up_answer)
            else:
                render_empty_state(
                    "Food Check",
                    "Type the food first, then get the verdict.",
                    "You will see one clear result, the immediate next steps, and the top reasons behind the decision.",
                )

    with emergency_tab:
        emergency_left, emergency_right = st.columns([1.05, 0.95], gap="large")
        with emergency_left:
            st.markdown("### My pet already ate this")
            st.caption("Use this only when the food is already gone or symptoms have started.")
            emergency_food = st.text_area(
                "What was eaten?",
                placeholder="Example: half a chocolate chip cookie\nOr: garlic pizza crust\nOr: sugar-free gum",
                height=140,
            )
            emergency_meta_left, emergency_meta_right = st.columns(2)
            with emergency_meta_left:
                emergency_amount = st.select_slider("How much?", options=AMOUNT_OPTIONS, value="Small bite", key="emergency_amount")
            with emergency_meta_right:
                time_since = st.selectbox("When did it happen?", options=TIME_OPTIONS)
            with st.expander("Symptoms (optional but helpful)", expanded=False):
                symptoms = st.multiselect("Current symptoms", options=SYMPTOM_OPTIONS)

            if st.button("Run emergency review", type="primary", use_container_width=True):
                if not emergency_food.strip():
                    st.warning("Describe what your pet ate so I can triage the risk.")
                else:
                    analysis = analyze_food(
                        food_text=emergency_food,
                        pet_profile=current_pet,
                        already_ate=True,
                        amount_label=emergency_amount,
                        symptoms=symptoms,
                        time_since=time_since,
                    )
                    st.session_state.last_emergency_analysis = analysis
                    add_to_history("Emergency Mode", analysis, current_pet)

        with emergency_right:
            st.markdown("### Emergency read")
            if st.session_state.last_emergency_analysis:
                render_analysis(st.session_state.last_emergency_analysis)
            else:
                render_empty_state(
                    "Emergency Mode",
                    "Use this when the food is already eaten.",
                    "This path weighs symptoms, amount, and known toxins more aggressively than the regular food check.",
                )

    with care_tab:
        care = get_care_tips(current_pet)
        st.markdown("### Personalized care guide")
        st.caption("A calmer everyday baseline based on the active pet profile.")
        care_col1, care_col2, care_col3 = st.columns(3)
        with care_col1:
            render_list_card("Safer Everyday Picks", care["daily_choices"])
        with care_col2:
            render_list_card("Always Double-Check", care["red_flags"])
        with care_col3:
            render_list_card("Profile-Specific Notes", care["personalization"])

    with history_tab:
        st.markdown("### Recent checks")
        render_history()
        if st.session_state.history and st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()


if __name__ == "__main__":
    main()
