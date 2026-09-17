"""
Shared branding and theme for the NSAI multi-vertical dashboard.
Import this at the top of every page (app.py and each file in pages/).
"""

import streamlit as st

BRAND_NAME = "NSAI"
BRAND_TAGLINE = "Data Intelligence for Industry & Infrastructure"

# Factory-AI / Stripe-inspired: clean light theme, single accent color, generous whitespace
COLORS = {
    "bg": "#F7F8FA",
    "surface": "#FFFFFF",
    "border": "#E4E7EC",
    "text": "#101828",
    "text_muted": "#667085",
    "accent": "#2563EB",       # indigo-blue, primary accent
    "accent_soft": "#EFF4FF",
    "success": "#12B76A",
    "warning": "#F79009",
    "danger": "#F04438",
}

def inject_theme():
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLORS['bg']};
            color: {COLORS['text']};
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLORS['surface']};
            border-right: 1px solid {COLORS['border']};
        }}
        h1, h2, h3 {{
            color: {COLORS['text']};
            font-weight: 700;
        }}
        p, span, label, .stCaption {{
            color: {COLORS['text_muted']};
        }}
        .nsai-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 0 20px 0;
            margin-bottom: 12px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        .nsai-logo {{
            width: 32px; height: 32px;
            background: {COLORS['accent']};
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 800; font-size: 15px;
        }}
        .nsai-name {{
            font-weight: 700; font-size: 16px; color: {COLORS['text']};
            line-height: 1.1;
        }}
        .nsai-tagline {{
            font-size: 11px; color: {COLORS['text_muted']};
        }}
        .metric-card {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        }}
        .metric-label {{
            font-size: 12px; font-weight: 600; letter-spacing: 0.04em;
            text-transform: uppercase; color: {COLORS['text_muted']};
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 28px; font-weight: 700; color: {COLORS['text']};
        }}
        .metric-sub {{
            font-size: 12.5px; color: {COLORS['text_muted']}; margin-top: 4px;
        }}
        .badge {{
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 11.5px; font-weight: 600;
        }}
        .badge-accent {{ background: {COLORS['accent_soft']}; color: {COLORS['accent']}; }}
        .badge-warn {{ background: #FFFAEB; color: {COLORS['warning']}; }}
        .section-title {{
            font-size: 13px; font-weight: 700; color: {COLORS['text_muted']};
            text-transform: uppercase; letter-spacing: 0.04em; margin: 6px 0 10px 0;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLORS['border']}; border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown(f"""
    <div class="nsai-brand">
        <div class="nsai-logo">N</div>
        <div>
            <div class="nsai-name">{BRAND_NAME}</div>
            <div class="nsai-tagline">{BRAND_TAGLINE}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value, sub=""):
    return f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>"""


def badge(text, kind="accent"):
    cls = "badge-accent" if kind == "accent" else "badge-warn"
    return f'<span class="badge {cls}">{text}</span>'


def whatsapp_mockup(title, body, timestamp="Today, 09:14 AM"):
    """Renders a static WhatsApp-style chat bubble mockup — visual only, no real send."""
    return f"""
    <div style="max-width:360px; background:#E5DDD5; border-radius:14px; padding:14px;
                border:1px solid {COLORS['border']}; box-shadow:0 1px 3px rgba(16,24,40,0.08);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <div style="width:28px;height:28px;background:#25D366;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">✓</div>
            <div style="font-weight:700; font-size:13px; color:#111B21;">NSAI Alerts</div>
        </div>
        <div style="background:#FFFFFF; border-radius:10px; padding:10px 12px; box-shadow:0 1px 1px rgba(0,0,0,0.06);">
            <div style="font-weight:700; font-size:13px; color:#111B21; margin-bottom:3px;">{title}</div>
            <div style="font-size:13px; color:#3B4A54; line-height:1.4;">{body}</div>
            <div style="font-size:10.5px; color:#8696A0; text-align:right; margin-top:6px;">{timestamp} ✓✓</div>
        </div>
    </div>
    """


def hero(headline, subtext):
    st.markdown(f"""
    <div style="text-align:center; padding:56px 20px 32px 20px; max-width:820px; margin:0 auto;">
        <h1 style="font-size:44px; line-height:1.15; font-weight:800; color:{COLORS['text']}; margin-bottom:18px;">
            {headline}
        </h1>
        <p style="font-size:17px; color:{COLORS['text_muted']}; line-height:1.6;">
            {subtext}
        </p>
    </div>
    """, unsafe_allow_html=True)


def feature_card_html(icon, title, desc, tag=""):
    tag_html = f'<span class="badge badge-accent" style="margin-left:8px;">{tag}</span>' if tag else ""
    return f"""
    <div class="metric-card" style="min-height:150px; display:flex; flex-direction:column; gap:8px;">
        <div style="font-size:26px;">{icon}</div>
        <div style="font-weight:700; font-size:16px; color:{COLORS['text']};">{title}{tag_html}</div>
        <div style="font-size:13.5px; color:{COLORS['text_muted']}; line-height:1.5;">{desc}</div>
    </div>
    """