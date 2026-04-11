from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --pet-ink: #14363b;
            --pet-copy: #33565a;
            --pet-soft: #6a8487;
            --pet-shell: #fcfaf6;
            --pet-card: rgba(255, 255, 255, 0.9);
            --pet-line: rgba(20, 54, 59, 0.12);
            --pet-mint: #d5efe4;
            --pet-coral: #ef9d7f;
            --pet-gold: #ffd08a;
            --pet-rose: #ffebe3;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(239, 157, 127, 0.17), transparent 24%),
                radial-gradient(circle at top right, rgba(213, 239, 228, 0.55), transparent 22%),
                linear-gradient(180deg, #fffefb 0%, #fcfaf6 42%, #faf6f0 100%);
            color: var(--pet-copy);
        }

        [data-testid="stAppViewContainer"] > .main > div {
            padding-top: 1.5rem;
        }

        [data-testid="stAppViewContainer"] [data-testid="block-container"] {
            max-width: 1160px;
            padding-top: 1rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(252,247,239,0.98) 100%);
            border-right: 1px solid var(--pet-line);
        }

        [data-testid="stSidebar"] * {
            color: var(--pet-copy);
        }

        h1, h2, h3, h4 {
            font-family: Georgia, "Times New Roman", serif;
            color: var(--pet-ink);
            letter-spacing: -0.02em;
        }

        p, li, label, .stMarkdown, .stTextInput, .stTextArea, .stSelectbox, .stNumberInput {
            font-family: "Avenir Next", "Trebuchet MS", sans-serif;
        }

        button[data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.55rem 0.95rem;
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(20, 54, 59, 0.08);
            color: var(--pet-soft);
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: var(--pet-ink);
            color: #fffef9;
            border-color: var(--pet-ink);
        }

        .stTextArea textarea,
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div,
        .stRadio > div,
        .stFileUploader,
        .stCameraInput {
            border-radius: 16px !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 14px;
            font-weight: 700;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 1.55rem 1.55rem 1.4rem;
            border-radius: 26px;
            background:
                linear-gradient(145deg, rgba(18, 70, 75, 0.98) 0%, rgba(24, 92, 97, 0.94) 48%, rgba(239, 157, 127, 0.82) 100%);
            box-shadow: 0 20px 60px rgba(31, 62, 67, 0.14);
            margin-bottom: 0.95rem;
            color: #fffef9;
        }

        .brand-lockup {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            margin-bottom: 0.95rem;
        }

        .brand-mark,
        .brand-fallback {
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.18);
            object-fit: cover;
            flex-shrink: 0;
        }

        .brand-fallback {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            letter-spacing: 0.06em;
            color: #fffef9;
        }

        .brand-name {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: #fffef9;
        }

        .brand-domain {
            font-size: 0.83rem;
            color: rgba(255, 250, 245, 0.82);
        }

        .hero-shell:before,
        .hero-shell:after {
            content: "";
            position: absolute;
            border-radius: 999px;
            filter: blur(6px);
            opacity: 0.42;
        }

        .hero-shell:before {
            width: 220px;
            height: 220px;
            background: rgba(255, 233, 210, 0.26);
            top: -105px;
            right: -35px;
        }

        .hero-shell:after {
            width: 190px;
            height: 190px;
            background: rgba(189, 232, 215, 0.22);
            bottom: -90px;
            left: -40px;
        }

        .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.36rem 0.72rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            background: rgba(255, 255, 255, 0.18);
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: clamp(2rem, 3.4vw, 3.45rem);
            line-height: 1.04;
            margin: 0 0 0.6rem;
            max-width: 620px;
        }

        .hero-copy {
            max-width: 600px;
            margin: 0;
            font-size: 0.99rem;
            line-height: 1.65;
            color: rgba(255, 250, 245, 0.92);
        }

        .hero-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.95rem;
        }

        .hero-chip {
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            font-size: 0.84rem;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.14);
        }

        .status-card,
        .surface-card {
            background: var(--pet-card);
            border: 1px solid var(--pet-line);
            border-radius: 22px;
            padding: 1rem 1.05rem;
            box-shadow: 0 14px 40px rgba(24, 56, 61, 0.06);
        }

        .status-card {
            height: 100%;
            padding: 1.1rem 1.1rem 1rem;
        }

        .status-label {
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(20, 54, 59, 0.5);
            margin-bottom: 0.4rem;
        }

        .status-name {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.65rem;
            color: var(--pet-ink);
            margin: 0 0 0.35rem;
        }

        .status-copy {
            margin: 0 0 0.85rem;
            line-height: 1.6;
            color: var(--pet-copy);
        }

        .status-row {
            display: grid;
            gap: 0.7rem;
        }

        .status-pill {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 0.72rem 0.8rem;
            border-radius: 16px;
            background: rgba(250, 247, 242, 0.9);
            border: 1px solid rgba(20, 54, 59, 0.08);
            font-size: 0.92rem;
        }

        .status-pill strong {
            color: var(--pet-ink);
            font-weight: 700;
        }

        .focus-strip {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.82rem 0.95rem;
            margin: 0.15rem 0 1.2rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(20, 54, 59, 0.09);
        }

        .focus-copy {
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .focus-badge {
            white-space: nowrap;
            padding: 0.45rem 0.74rem;
            border-radius: 999px;
            background: rgba(20, 54, 59, 0.06);
            color: var(--pet-ink);
            font-weight: 700;
            font-size: 0.84rem;
        }

        .surface-card ul {
            margin: 0.4rem 0 0;
            padding-left: 1.1rem;
        }

        .surface-card li {
            margin-bottom: 0.42rem;
            line-height: 1.6;
        }

        .result-card {
            padding: 1.1rem 1.15rem;
            border-radius: 24px;
            border: 1px solid transparent;
            margin-bottom: 0.7rem;
        }

        .result-safe {
            background: linear-gradient(180deg, rgba(226, 248, 237, 0.9), rgba(255,255,255,0.95));
            border-color: rgba(23, 114, 69, 0.18);
        }

        .result-caution {
            background: linear-gradient(180deg, rgba(255, 241, 217, 0.92), rgba(255,255,255,0.95));
            border-color: rgba(154, 99, 0, 0.18);
        }

        .result-avoid {
            background: linear-gradient(180deg, rgba(255, 230, 223, 0.95), rgba(255,255,255,0.97));
            border-color: rgba(164, 45, 45, 0.18);
        }

        .result-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.34rem 0.74rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            background: rgba(255, 255, 255, 0.84);
            margin-bottom: 0.62rem;
        }

        .result-title {
            margin: 0;
            font-size: 1.85rem;
            color: var(--pet-ink);
        }

        .result-copy {
            margin: 0.58rem 0 0;
            font-size: 0.98rem;
            line-height: 1.62;
        }

        .detail-card {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(20, 54, 59, 0.08);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            height: 100%;
        }

        .detail-card h4 {
            margin: 0 0 0.48rem;
            font-size: 1.02rem;
        }

        .detail-card ul {
            margin: 0;
            padding-left: 1rem;
        }

        .detail-card li {
            margin-bottom: 0.36rem;
            line-height: 1.58;
        }

        .section-kicker {
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(20, 54, 59, 0.5);
            margin-bottom: 0.32rem;
        }

        .empty-state {
            background: rgba(255, 255, 255, 0.75);
            border: 1px dashed rgba(20, 54, 59, 0.18);
            border-radius: 22px;
            padding: 1.15rem 1.15rem;
        }

        .empty-state h3 {
            margin: 0 0 0.45rem;
        }

        .empty-state p {
            margin: 0;
            line-height: 1.6;
        }

        .history-item {
            padding: 0.9rem 1rem;
            border-radius: 18px;
            border: 1px solid var(--pet-line);
            background: rgba(255, 255, 255, 0.7);
            margin-bottom: 0.75rem;
        }

        .history-meta {
            color: rgba(20, 54, 59, 0.58);
            font-size: 0.88rem;
            margin-bottom: 0.35rem;
        }

        .sidebar-note {
            padding: 0.95rem 1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--pet-line);
            margin-bottom: 0.9rem;
            line-height: 1.65;
        }

        .soft-note {
            padding: 0.78rem 0.9rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(20, 54, 59, 0.08);
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        .sidebar-brand {
            display: grid;
            grid-template-columns: 54px 1fr;
            gap: 0.85rem;
            align-items: center;
            padding: 0.95rem 1rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(20, 54, 59, 0.08);
            margin-bottom: 0.85rem;
        }

        .sidebar-brand-mark {
            width: 54px;
            height: 54px;
            border-radius: 15px;
            object-fit: cover;
            background: rgba(20, 54, 59, 0.08);
        }

        .sidebar-fallback {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: var(--pet-ink);
            letter-spacing: 0.06em;
        }

        .sidebar-brand-name {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.15rem;
            color: var(--pet-ink);
            margin-bottom: 0.12rem;
        }

        .sidebar-brand-copy {
            font-size: 0.88rem;
            line-height: 1.45;
            color: var(--pet-soft);
        }

        @media (max-width: 900px) {
            .focus-strip {
                flex-direction: column;
                align-items: flex-start;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
