"""
nav.py — Shared navigation helper.
Renders a sticky top navbar (always visible) + sidebar nav.
Works with Streamlit 1.37+ (switch_page API).
"""
import streamlit as st

PAGES = [
    ("app.py",                  "Home",          "🏠"),
    ("pages/1_Verifier.py",     "Live Verifier", "▶"),
    ("pages/2_How_It_Works.py", "How It Works",  "📖"),
    ("pages/3_Evidence.py",     "Evidence",      "🔎"),
    ("pages/5_AI_Assistant.py", "AI Assistant",  "🤖"),
    ("pages/4_About.py",        "About",         "ℹ️"),
]

_TOPNAV_CSS = """
<style>
/* ── sticky top navbar ── */
.topnav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 999999;
  background: rgba(15, 15, 26, 0.97);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(99,102,241,0.25);
  display: flex;
  align-items: center;
  padding: 0 28px;
  height: 52px;
  gap: 4px;
}
.topnav-brand {
  font-weight: 800;
  font-size: 1rem;
  color: #818cf8;
  margin-right: 20px;
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.topnav-brand span { color: #e2e8f0; }
.topnav a {
  color: #94a3b8;
  text-decoration: none !important;
  font-size: 0.86rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.topnav a:hover {
  background: rgba(99,102,241,0.15);
  color: #e2e8f0;
}
.topnav a.active {
  background: rgba(99,102,241,0.18);
  color: #818cf8;
  font-weight: 700;
}
.topnav-spacer { flex: 1; }
.topnav-badge {
  font-size: 0.72rem;
  color: #475569;
  white-space: nowrap;
  border: 1px solid rgba(99,102,241,0.18);
  padding: 3px 10px;
  border-radius: 100px;
}
/* push page content below the fixed bar */
.block-container { margin-top: 52px !important; }
/* keep sidebar below the bar */
section[data-testid="stSidebar"] { top: 52px !important; }
/* sidebar nav button style */
section[data-testid="stSidebar"] .stButton button {
  background: transparent !important;
  border: 1px solid rgba(99,102,241,0.18) !important;
  color: #94a3b8 !important;
  text-align: left !important;
  font-size: 0.86rem !important;
  padding: 7px 12px !important;
  margin-bottom: 3px !important;
  border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
  background: rgba(99,102,241,0.1) !important;
  border-color: rgba(99,102,241,0.4) !important;
  color: #e2e8f0 !important;
}

/* ── Streamlit light theme ── */
[data-theme="light"] {
  --pp-page: #f6f7fb;
  --pp-surface: #ffffff;
  --pp-surface-muted: #eef1f7;
  --pp-text: #172033;
  --pp-muted: #526070;
  --pp-subtle: #687587;
  --pp-border: rgba(55, 65, 81, 0.18);
  --pp-accent: #4f46c7;
  --pp-accent-soft: rgba(79, 70, 199, 0.1);
}

[data-theme="light"] .stApp,
[data-theme="light"] [data-testid="stAppViewContainer"] {
  background: var(--pp-page) !important;
  color: var(--pp-text) !important;
}
[data-theme="light"] section[data-testid="stSidebar"] {
  background: #eef0f6 !important;
  border-right: 1px solid var(--pp-border);
}
[data-theme="light"] section[data-testid="stSidebar"] .stMarkdown,
[data-theme="light"] section[data-testid="stSidebar"] .stCaption,
[data-theme="light"] section[data-testid="stSidebar"] p,
[data-theme="light"] section[data-testid="stSidebar"] li {
  color: var(--pp-text) !important;
}
[data-theme="light"] section[data-testid="stSidebar"] .stButton button {
  color: #39465a !important;
  border-color: rgba(79, 70, 199, 0.2) !important;
}
[data-theme="light"] section[data-testid="stSidebar"] .stButton button:hover {
  background: rgba(79, 70, 199, 0.1) !important;
  color: var(--pp-accent) !important;
}

[data-theme="light"] .topnav {
  background: rgba(255, 255, 255, 0.97);
  border-bottom-color: rgba(79, 70, 199, 0.2);
}
[data-theme="light"] .topnav-brand span,
[data-theme="light"] .topnav a:hover {
  color: var(--pp-text);
}
[data-theme="light"] .topnav a { color: #526070; }
[data-theme="light"] .topnav a.active {
  background: rgba(79, 70, 199, 0.12);
  color: var(--pp-accent);
}
[data-theme="light"] .topnav-badge { color: #687587; }

[data-theme="light"] .page-header,
[data-theme="light"] .page-hero,
[data-theme="light"] .stat-card,
[data-theme="light"] .feature-card,
[data-theme="light"] .step-row,
[data-theme="light"] .step-big,
[data-theme="light"] .arch-box,
[data-theme="light"] .file-card,
[data-theme="light"] .team-card,
[data-theme="light"] .value-card,
[data-theme="light"] .contact-card {
  background: var(--pp-surface) !important;
  border-color: var(--pp-border) !important;
}
[data-theme="light"] .page-header h1,
[data-theme="light"] .page-hero h1,
[data-theme="light"] .section-title,
[data-theme="light"] .step-content h3,
[data-theme="light"] .step-row h4,
[data-theme="light"] .feature-card h3,
[data-theme="light"] .file-card h4,
[data-theme="light"] .team-name,
[data-theme="light"] .contact-card h4,
[data-theme="light"] .cta-box h2 {
  color: var(--pp-text) !important;
}
[data-theme="light"] .page-header p,
[data-theme="light"] .page-hero p,
[data-theme="light"] .section-desc,
[data-theme="light"] .step-content p,
[data-theme="light"] .step-row p,
[data-theme="light"] .feature-card p,
[data-theme="light"] .file-card p,
[data-theme="light"] .arch-box ul,
[data-theme="light"] .value-card p,
[data-theme="light"] .contact-card p,
[data-theme="light"] .hero-desc,
[data-theme="light"] .cta-box p {
  color: var(--pp-muted) !important;
}
[data-theme="light"] .section-badge,
[data-theme="light"] .badge,
[data-theme="light"] .section-label,
[data-theme="light"] .arch-box h4,
[data-theme="light"] .value-card h4,
[data-theme="light"] .stat-num,
[data-theme="light"] .hero-sub-title {
  color: var(--pp-accent) !important;
}
[data-theme="light"] .stat-label,
[data-theme="light"] .footer,
[data-theme="light"] .team-desc,
[data-theme="light"] .disclaimer {
  color: var(--pp-subtle) !important;
}
[data-theme="light"] .step-content code,
[data-theme="light"] .arch-box li code,
[data-theme="light"] .table-wrap td code {
  color: #4338a8 !important;
  background: var(--pp-accent-soft) !important;
}
[data-theme="light"] .table-wrap th {
  background: var(--pp-surface-muted) !important;
  color: var(--pp-accent) !important;
}
[data-theme="light"] .table-wrap td { color: var(--pp-muted) !important; }
[data-theme="light"] .key-hint { color: var(--pp-muted) !important; }
[data-theme="light"] .key-title-ok { color: #15803d !important; }
[data-theme="light"] .key-box-ok { background: rgba(34, 197, 94, 0.08) !important; }
[data-theme="light"] .footer { border-top-color: var(--pp-border) !important; }

/* Inline markup used by the home and verifier pages. */
[data-theme="light"] div[style*="#1a1a2e"] {
  background: var(--pp-surface) !important;
}
[data-theme="light"] [style*="color:#e2e8f0"],
[data-theme="light"] [style*="color: #e2e8f0"] {
  color: var(--pp-text) !important;
}
[data-theme="light"] [style*="color:#94a3b8"],
[data-theme="light"] [style*="color: #94a3b8"],
[data-theme="light"] [style*="color:#cbd5e1"],
[data-theme="light"] [style*="color: #cbd5e1"] {
  color: var(--pp-muted) !important;
}
</style>
"""

def _topnav_html(current: str) -> str:
    items = ""
    for path, label, icon in PAGES:
        is_active = (path == current) or (current and path.endswith(current))
        # Use Streamlit's URL path scheme: app.py = "/", pages/1_X.py = "/1_X"
        if path == "app.py":
            href = "/"
        else:
            # e.g. pages/1_Verifier.py  →  /1_Verifier
            name = path.split("/")[-1].replace(".py", "")
            href = f"/{name}"
        active_cls = ' class="active"' if is_active else ""
        items += f'<a href="{href}"{active_cls}>{icon} {label}</a>\n'
    return f"""
<div class="topnav">
  <div class="topnav-brand">Proof<span>Patch</span></div>
  {items}
  <div class="topnav-spacer"></div>
  <div class="topnav-badge">IBM Bob 2.0 Hackathon</div>
</div>
"""

def nav_sidebar(current: str = ""):
    """Render sticky top navbar + sidebar navigation."""
    # Inject CSS + top navbar
    st.markdown(_TOPNAV_CSS, unsafe_allow_html=True)
    st.markdown(_topnav_html(current), unsafe_allow_html=True)

    # Sidebar nav (still useful when open)
    with st.sidebar:
        st.markdown("## 🔬 ProofPatch")
        st.caption("IBM Bob 2.0 Hackathon")
        st.markdown("---")
        for path, label, icon in PAGES:
            is_current = (path == current) or (current and path.endswith(current))
            if is_current:
                st.markdown(f"**→ {icon} {label}**")
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{path}", use_container_width=True):
                    st.switch_page(path)
        st.markdown("---")
        st.caption("Fix bugs. Show proof.")
