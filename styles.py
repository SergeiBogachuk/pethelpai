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
            --pet-shell: #f8f7f3;
            --pet-card: #ffffff;
            --pet-line: rgba(20, 54, 59, 0.1);
            --pet-safe: #edf7f0;
            --pet-caution: #faf3e6;
            --pet-avoid: #faece8;
        }

        .stApp {
            background: var(--pet-shell);
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
            background: #fbfaf7;
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

        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1rem 1.1rem;
            border-radius: 20px;
            background: var(--pet-card);
            border: 1px solid var(--pet-line);
            margin-bottom: 1rem;
        }

        .brand-lockup {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .brand-mark,
        .brand-fallback {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            background: rgba(20, 54, 59, 0.06);
            border: 1px solid rgba(20, 54, 59, 0.08);
            object-fit: cover;
            flex-shrink: 0;
        }

        .brand-fallback {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            letter-spacing: 0.06em;
            color: var(--pet-ink);
        }

        .brand-name {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.18rem;
            font-weight: 700;
            color: var(--pet-ink);
        }

        .brand-domain {
            font-size: 0.83rem;
            color: var(--pet-soft);
        }

        .app-summary {
            text-align: right;
            max-width: 340px;
        }

        .app-summary-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--pet-soft);
            margin-bottom: 0.2rem;
        }

        .app-summary-name {
            font-family: Georgia, "Times New Roman", serif;
            color: var(--pet-ink);
            font-size: 1.1rem;
            margin-bottom: 0.2rem;
        }

        .app-summary-copy {
            font-size: 0.9rem;
            line-height: 1.5;
            color: var(--pet-soft);
        }

        .surface-card {
            background: var(--pet-card);
            border: 1px solid var(--pet-line);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            box-shadow: none;
        }

        .section-card {
            background: var(--pet-card);
            border: 1px solid var(--pet-line);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            margin-bottom: 1rem;
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
            padding: 1rem 1.05rem;
            border-radius: 18px;
            border: 1px solid var(--pet-line);
            margin-bottom: 0.85rem;
        }

        .result-safe {
            background: var(--pet-safe);
        }

        .result-caution {
            background: var(--pet-caution);
        }

        .result-avoid {
            background: var(--pet-avoid);
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
            background: rgba(255, 255, 255, 0.92);
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
            background: #ffffff;
            border: 1px solid rgba(20, 54, 59, 0.08);
            border-radius: 16px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.75rem;
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

        .swap-card {
            background: #ffffff;
            border: 1px solid rgba(20, 54, 59, 0.08);
            border-radius: 16px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.7rem;
        }

        .swap-card h4 {
            margin: 0 0 0.42rem;
            font-size: 1.05rem;
            color: var(--pet-ink);
        }

        .swap-card p {
            margin: 0;
            line-height: 1.58;
            font-size: 0.94rem;
        }

        .swap-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(20, 54, 59, 0.5);
            margin-bottom: 0.45rem;
        }

        .section-kicker {
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(20, 54, 59, 0.5);
            margin-bottom: 0.32rem;
        }

        .empty-state {
            background: #ffffff;
            border: 1px dashed rgba(20, 54, 59, 0.18);
            border-radius: 18px;
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
            border-radius: 16px;
            border: 1px solid var(--pet-line);
            background: #ffffff;
            margin-bottom: 0.75rem;
        }

        .history-meta {
            color: rgba(20, 54, 59, 0.58);
            font-size: 0.88rem;
            margin-bottom: 0.35rem;
        }

        .sidebar-note {
            padding: 0.95rem 1rem;
            border-radius: 16px;
            background: #ffffff;
            border: 1px solid var(--pet-line);
            margin-bottom: 0.9rem;
            line-height: 1.65;
        }

        .soft-note {
            padding: 0.78rem 0.9rem;
            border-radius: 16px;
            background: #ffffff;
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
            border-radius: 18px;
            background: #ffffff;
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
            .app-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .app-summary {
                text-align: left;
                max-width: unset;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
