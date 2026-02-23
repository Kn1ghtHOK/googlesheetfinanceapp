import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import urllib.parse
import base64
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finance",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Constants ─────────────────────────────────────────────────────────────────
CLIENT_ID      = st.secrets["CLIENT_ID"]
CLIENT_SECRET  = st.secrets["CLIENT_SECRET"]
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
SHEET_NAME     = st.secrets["SHEET_NAME"]
REDIRECT_URI   = "https://henrysfinanceapp.streamlit.app/"
SCOPES         = "https://www.googleapis.com/auth/spreadsheets.readonly"
AUTH_URL       = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL      = "https://oauth2.googleapis.com/token"
MN_TAX_RATE    = float(st.secrets["TAX_RATE"])
HOURLY_RATE    = float(st.secrets["HOURLY_RATE"])
STORAGE_KEY    = "pf_token_v1"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── Black everywhere ── */
.stApp, .stApp > div,
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
.block-container,
div[data-testid="stVerticalBlock"] {
    background: #080808 !important;
}

/* ── Number input: hide label, large clean text ── */
div[data-testid="stNumberInput"] label { display: none !important; }
div[data-testid="stNumberInput"] > div > div {
    background: #0d0d0d !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 14px !important;
}
div[data-testid="stNumberInput"] input {
    color: #e8e8e8 !important;
    font-family: 'DM Serif Display', Georgia, serif !important;
    font-size: 28px !important;
    letter-spacing: -0.5px !important;
    text-align: right !important;
    padding-right: 14px !important;
}
div[data-testid="stNumberInput"] button {
    color: #404040 !important;
    background: transparent !important;
    border: none !important;
}
div[data-testid="stNumberInput"] > div > div:focus-within {
    border-color: #333 !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.025) !important;
}

/* ── Text input (search) ── */
div[data-baseweb="input"] > div {
    background: #0d0d0d !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 12px !important;
}
div[data-baseweb="input"] > div:focus-within {
    border-color: #333 !important;
}
div[data-baseweb="input"] input {
    color: #d8d8d8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
div[data-baseweb="input"] input::placeholder { color: #303030 !important; }

/* ── Regular buttons ── */
button[kind="secondary"] {
    background: #0d0d0d !important;
    color: #c0c0c0 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}
button[kind="secondary"]:hover {
    background: #141414 !important;
    border-color: #282828 !important;
}

/* ── Sign-in link button ── */
a[data-testid="stLinkButton"] button {
    background: #f0f0f0 !important;
    color: #080808 !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* ── Misc ── */
hr { border-color: #161616 !important; }
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
.stSpinner > div { border-top-color: #fff !important; }

/* ═══════════════ CUSTOM COMPONENTS ═══════════════ */

.wordmark {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px; font-weight: 600;
    letter-spacing: 3.5px; text-transform: uppercase;
    color: #2a2a2a; margin-bottom: 8px;
}
.page-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 40px; color: #efefef;
    letter-spacing: -0.6px; line-height: 1;
    margin: 0 0 28px;
}

/* Hero balance */
.hero-balance {
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 24px;
    padding: 28px 24px 22px;
    margin-bottom: 22px;
    position: relative; overflow: hidden;
}
.hero-balance::after {
    content: '';
    position: absolute; top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #222, transparent);
}
.hero-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: 1.8px; text-transform: uppercase;
    color: #383838; margin-bottom: 10px;
}
.hero-amount {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 56px; letter-spacing: -1.5px;
    line-height: 1; margin-bottom: 8px;
}
.hero-sub { font-size: 12px; color: #2e2e2e; letter-spacing: 0.3px; }

.spend-color  { color: #ff453a; }
.save-color   { color: #30d158; }
.give-color   { color: #0a84ff; }
.pos-color    { color: #30d158; }
.neg-color    { color: #ff453a; }
.neutral-color { color: #d0d0d0; }

.section-label {
    font-size: 9px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: #383838; margin: 28px 0 12px;
}

/* Estimator */
.est-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 6px 0 4px;
}
.est-label {
    font-size: 13px; font-weight: 500;
    color: #505050; letter-spacing: 0.3px;
}

.breakdown-rows {
    background: #060606;
    border: 1px solid #161616;
    border-radius: 16px; overflow: hidden;
    margin-top: 8px;
}
.brow {
    display: flex; justify-content: space-between; align-items: center;
    padding: 11px 18px; border-bottom: 1px solid #101010;
    font-size: 13px; color: #484848;
}
.brow:last-child { border-bottom: none; }
.bval {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 18px; color: #aaa; letter-spacing: -0.2px;
}
.brow.total-row { padding: 14px 18px; border-top: 1px solid #1a1a1a; }
.brow.total-row .blab {
    font-size: 9px; font-weight: 600;
    letter-spacing: 1.8px; text-transform: uppercase; color: #383838;
}
.brow.total-row .bval { font-size: 26px; color: #c8c8c8; letter-spacing: -0.5px; }

.verdict {
    border-radius: 16px; padding: 20px 18px;
    margin-top: 12px; text-align: center;
}
.verdict.yes { background: rgba(48,209,88,0.07); border: 1px solid rgba(48,209,88,0.13); }
.verdict.no  { background: rgba(255,69,58,0.07); border: 1px solid rgba(255,69,58,0.13); }
.v-eye {
    font-size: 9px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
}
.verdict.yes .v-eye { color: #30d158; }
.verdict.no  .v-eye { color: #ff453a; }
.v-num {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 38px; letter-spacing: -1px; line-height: 1; margin-bottom: 8px;
}
.verdict.yes .v-num { color: #30d158; }
.verdict.no  .v-num { color: #ff453a; }
.v-desc { font-size: 13px; color: #484848; margin-bottom: 14px; }
.work-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: #0d0d0d; border: 1px solid #1e1e1e;
    border-radius: 20px; padding: 7px 14px;
    font-size: 12px; color: #585858;
}
.work-badge strong { color: #a0a0a0; }

/* Ledger */
.ledger {
    background: #0d0d0d; border: 1px solid #1a1a1a;
    border-radius: 20px; overflow: hidden; margin-bottom: 22px;
}
.ledger-row {
    display: flex; align-items: center;
    padding: 13px 18px; border-bottom: 1px solid #101010;
    gap: 13px; transition: background 0.1s;
}
.ledger-row:last-child { border-bottom: none; }
.ledger-row:hover { background: #101010; }
.l-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.li-pos  { background: rgba(48,209,88,0.09); }
.li-neg  { background: rgba(255,69,58,0.09); }
.li-mix  { background: rgba(255,255,255,0.04); }
.l-info  { flex: 1; min-width: 0; }
.l-name  { font-size: 14px; font-weight: 500; color: #d8d8d8;
           white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.l-type  { font-size: 11px; color: #383838; margin-top: 2px; letter-spacing: 0.5px; }
.l-amt   { font-family: 'DM Serif Display', Georgia, serif;
           font-size: 17px; letter-spacing: -0.2px; flex-shrink: 0; }

/* Sign-in */
.signin-outer {
    min-height: 88vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 40px 24px;
}
.signin-wordmark {
    font-size: 10px; font-weight: 600; letter-spacing: 4px;
    text-transform: uppercase; color: #222; margin-bottom: 52px;
}
.signin-glyph { font-size: 48px; color: #222; margin-bottom: 32px; }
.signin-h {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 48px; color: #efefef; letter-spacing: -1px;
    line-height: 1.05; margin-bottom: 14px;
}
.signin-p { font-size: 15px; color: #404040; line-height: 1.65; margin-bottom: 48px; }

.empty-state { text-align: center; padding: 40px 20px;
               font-size: 13px; color: #282828; letter-spacing: 0.3px; }
.footer-text { text-align: center; font-size: 10px; color: #1e1e1e;
               letter-spacing: 1.5px; text-transform: uppercase;
               margin-top: 24px; padding-bottom: 24px; }

/* ── Native pill card buttons ── */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 18px !important;
    padding: 14px 10px 12px !important;
    height: auto !important;
    min-height: 78px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1.3 !important;
    white-space: pre-line !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 9px !important;
    font-weight: 600 !important;
    letter-spacing: 1.4px !important;
    color: #505050 !important;
    transition: background 0.15s, border-color 0.15s !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
    background: #111 !important;
    border-color: #252525 !important;
    color: #606060 !important;
}
.pill-active-spend div[data-testid="stButton"] > button {
    background: #150a0a !important;
    border-color: rgba(255,69,58,0.25) !important;
    color: #ff453a !important;
}
.pill-active-save div[data-testid="stButton"] > button {
    background: #0a1510 !important;
    border-color: rgba(48,209,88,0.25) !important;
    color: #30d158 !important;
}
.pill-active-give div[data-testid="stButton"] > button {
    background: #080d18 !important;
    border-color: rgba(10,132,255,0.25) !important;
    color: #0a84ff !important;
}
</style>
""", unsafe_allow_html=True)


# ── JS: clear-on-focus + block scroll-on-enter ────────────────────────────────
BEHAVIOR_JS = """
<script>
(function() {
    function setup() {
        var doc = window.parent.document;
        // Block Enter from scrolling page on number inputs
        if (!doc._hf_enter_bound) {
            doc._hf_enter_bound = true;
            doc.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    var el = doc.activeElement;
                    if (el && el.type === 'number') {
                        e.preventDefault();
                        e.stopImmediatePropagation();
                        el.blur();
                    }
                }
            }, true);
        }
        // Clear-on-focus for number inputs showing 0
        doc.querySelectorAll('input[type="number"]').forEach(function(inp) {
            if (!inp._hf_focus) {
                inp._hf_focus = true;
                inp.addEventListener('focus', function() {
                    if (parseFloat(this.value) === 0 || this.value === '0.00') {
                        this.value = '';
                        this.dispatchEvent(new Event('input', {bubbles: true}));
                    }
                });
                inp.addEventListener('blur', function() {
                    if (this.value === '' || this.value === null) {
                        this.value = '0.00';
                        this.dispatchEvent(new Event('input', {bubbles: true}));
                    }
                });
            }
        });
    }
    setup();
    setTimeout(setup, 600);
    setTimeout(setup, 1400);
})();
</script>
"""


# ── Persistent login helpers ──────────────────────────────────────────────────
def save_token_js(token_info):
    encoded = base64.b64encode(json.dumps(token_info).encode()).decode()
    components.html(f"""
    <script>
        try {{ localStorage.setItem('{STORAGE_KEY}', '{encoded}'); }} catch(e) {{}}
    </script>""", height=0)

def inject_restore_js():
    components.html(f"""
    <script>
    (function() {{
        var s = null;
        try {{ s = localStorage.getItem('{STORAGE_KEY}'); }} catch(e) {{}}
        if (!s) return;
        var url = new URL(window.parent.location.href);
        if (url.searchParams.has('code') || url.searchParams.has('_rt')) return;
        url.searchParams.set('_rt', s);
        window.parent.location.replace(url.toString());
    }})();
    </script>""", height=0)

def clear_token_js():
    components.html(f"""
    <script>
        try {{ localStorage.removeItem('{STORAGE_KEY}'); }} catch(e) {{}}
    </script>""", height=0)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(v):
    if v == 0: return "$0.00"
    sign = "+" if v > 0 else "−"
    return f"{sign}${abs(v):,.2f}"

def fmt_abs(v):
    return f"${abs(v):,.2f}"

def fmt_hours(h):
    if h < 1:    return f"{max(1,int(h*60))} min"
    elif h < 8:
        hh, m = int(h), int((h%1)*60)
        return f"{hh}h {m}m" if m else f"{hh}h"
    else:        return f"{h/8:.1f} work days"

def tx_icon(v):
    if v > 0: return "↑", "li-pos"
    if v < 0: return "↓", "li-neg"
    return "·", "li-mix"

def tx_type(v):
    if v > 0: return "Credit"
    if v < 0: return "Debit"
    return "—"

def color_cls(v):
    if v > 0: return "pos-color"
    if v < 0: return "neg-color"
    return "neutral-color"


# ── OAuth ─────────────────────────────────────────────────────────────────────
def get_auth_url():
    return AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI,
        "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent",
    })

def exchange_code(code):
    return requests.post(TOKEN_URL, data={
        "code": code, "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).json()


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_data(access_token):
    h = {"Authorization": f"Bearer {access_token}"}
    def f(v):
        try: return float(str(v).replace(",","").replace("$",""))
        except: return 0.0

    tot = requests.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"
        f"/values/{urllib.parse.quote(SHEET_NAME+'!I5:K5')}", headers=h
    ).json()
    row = tot.get("values",[[0,0,0]])[0]
    s1 = f(row[0]) if len(row)>0 else 0.0
    s2 = f(row[1]) if len(row)>1 else 0.0
    s3 = f(row[2]) if len(row)>2 else 0.0

    txr = requests.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"
        f"/values/{urllib.parse.quote(SHEET_NAME+'!A3:D999')}", headers=h
    ).json()
    records = []
    for r in txr.get("values",[]):
        name = r[0] if r else ""
        if not name: continue
        records.append({"name":name,
            "spending": f(r[1]) if len(r)>1 and r[1] else 0.0,
            "savings":  f(r[2]) if len(r)>2 and r[2] else 0.0,
            "giving":   f(r[3]) if len(r)>3 and r[3] else 0.0,
        })
    df = pd.DataFrame(records) if records else pd.DataFrame(
        columns=["name","spending","savings","giving"])
    return df.iloc[::-1].reset_index(drop=True), s1, s2, s3


# ── Auth flow & Routing ───────────────────────────────────────────────────────
qp = st.query_params

# 1. Restore from localStorage redirect
if "_rt" in qp and "token_info" not in st.session_state:
    try:
        ti = json.loads(base64.b64decode(qp["_rt"]).decode())
        if "access_token" in ti:
            st.session_state["token_info"] = ti
    except Exception:
        pass
    if "_rt" in st.query_params: del st.query_params["_rt"]
    st.rerun()

# 2. Handle OAuth callback
if "code" in qp and "token_info" not in st.session_state:
    with st.spinner("Authenticating…"):
        ti = exchange_code(qp["code"])
    if "access_token" in ti:
        st.session_state["token_info"] = ti
        st.session_state["_save_token"] = True
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Authentication failed.")
        st.json(ti)
    
# ── Sign-in screen ────────────────────────────────────────────────────────────
if "token_info" not in st.session_state:
    inject_restore_js()
    st.markdown("""
    <style>
    /* Remove Streamlit's default top padding on the sign-in screen */
    .block-container { padding-top: 0 !important; }
    </style>
    <div class="signin-outer">
        <div class="signin-glyph">◈</div>
        <div class="signin-h">Your money,<br>clearly.</div>
        <div class="signin-p">Secure access to your spending,<br>savings &amp; giving accounts.</div>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.link_button("Sign in with Google", get_auth_url(), use_container_width=True)
    st.stop()

# Persist token to localStorage after fresh OAuth
if st.session_state.pop("_save_token", False):
    save_token_js(st.session_state["token_info"])

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    df, spending_total, savings_total, giving_total = fetch_data(
        st.session_state["token_info"]["access_token"])
except Exception as e:
    st.error(f"Unable to retrieve account data: {e}")
    clear_token_js()
    if st.button("Sign Out"):
        del st.session_state["token_info"]
        st.rerun()
    st.stop()

spend_df = df[df["spending"] != 0].reset_index(drop=True)
save_df  = df[df["savings"]  != 0].reset_index(drop=True)
give_df  = df[df["giving"]   != 0].reset_index(drop=True)

# Default view
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "spending"
view = st.session_state["active_view"]

# ── Inject behavior JS ────────────────────────────────────────────────────────
st.markdown(BEHAVIOR_JS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_h, col_btn = st.columns([5,1])
with col_h:
    st.markdown("""
    <div style='padding:28px 0 0'>
        <div class='wordmark'>Personal Finance</div>
        <div class='page-title'>Overview</div>
    </div>""", unsafe_allow_html=True)
with col_btn:
    st.markdown("<div style='margin-top:42px'></div>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        clear_token_js()
        del st.session_state["token_info"]
        st.cache_data.clear()
        st.rerun()

# ── Clickable pill cards (native st.button — instant, zero-reload) ────────────
pill_col1, pill_col2, pill_col3 = st.columns(3)

with pill_col1:
    if view == "spending":
        st.markdown('<div class="pill-active-spend">', unsafe_allow_html=True)
    if st.button(
        f"DISCRETIONARY\n{fmt_abs(spending_total)}",
        key="pill_spend", use_container_width=True
    ):
        st.session_state["active_view"] = "spending"
        st.rerun()
    if view == "spending":
        st.markdown('</div>', unsafe_allow_html=True)

with pill_col2:
    if view == "savings":
        st.markdown('<div class="pill-active-save">', unsafe_allow_html=True)
    if st.button(
        f"RESERVES\n{fmt_abs(savings_total)}",
        key="pill_save", use_container_width=True
    ):
        st.session_state["active_view"] = "savings"
        st.rerun()
    if view == "savings":
        st.markdown('</div>', unsafe_allow_html=True)

with pill_col3:
    if view == "giving":
        st.markdown('<div class="pill-active-give">', unsafe_allow_html=True)
    if st.button(
        f"CHARITABLE\n{fmt_abs(giving_total)}",
        key="pill_give", use_container_width=True
    ):
        st.session_state["active_view"] = "giving"
        st.rerun()
    if view == "giving":
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


# ── Helper: render ledger rows ────────────────────────────────────────────────
def render_ledger(data, col):
    if data.empty:
        st.markdown('<div class="empty-state">No transactions on record.</div>', unsafe_allow_html=True)
        return
    html = ""
    for _, r in data.iterrows():
        v = r[col]
        icon, icls = tx_icon(v)
        html += f"""
        <div class="ledger-row">
            <div class="l-icon {icls}">{icon}</div>
            <div class="l-info">
                <div class="l-name">{r['name']}</div>
                <div class="l-type">{tx_type(v)}</div>
            </div>
            <div class="l-amt {color_cls(v)}">{fmt(v)}</div>
        </div>"""
    st.markdown(f'<div class="ledger">{html}</div>', unsafe_allow_html=True)


# ╔═════════════════════════════════════════════════════════════════════════════
# ║  SPENDING VIEW
# ╚═════════════════════════════════════════════════════════════════════════════
if view == "spending":

    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">Discretionary Balance</div>
        <div class="hero-amount spend-color">{fmt_abs(spending_total)}</div>
        <div class="hero-sub">Available to spend · Synced from ledger</div>
    </div>""", unsafe_allow_html=True)

    # ── Purchase Estimator ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Purchase Estimator</div>', unsafe_allow_html=True)

    est_col, price_col = st.columns([2, 3])
    with est_col:
        st.markdown("""
        <div style='display:flex;align-items:center;height:68px'>
            <span style='font-size:14px;color:#484848;letter-spacing:0.3px;font-weight:500'>
                Purchase Estimator
            </span>
        </div>""", unsafe_allow_html=True)
    with price_col:
        price_input = st.number_input(
            "price", min_value=0.0, value=0.0, step=0.01, format="%.2f",
            label_visibility="collapsed", key="price_est"
        )

    if price_input > 0:
        tax_amt    = price_input * MN_TAX_RATE
        total_cost = price_input + tax_amt
        after      = spending_total - total_cost
        can_afford = after >= 0
        hrs_total  = total_cost / HOURLY_RATE

        st.markdown(f"""
        <div class="breakdown-rows">
            <div class="brow">
                <span>Sticker price</span>
                <span class="bval">{fmt_abs(price_input)}</span>
            </div>
            <div class="brow">
                <span>Sales tax <small style='color:#282828'>7.375%</small></span>
                <span class="bval">+ {fmt_abs(tax_amt)}</span>
            </div>
            <div class="brow total-row">
                <span class="blab">Total cost</span>
                <span class="bval">{fmt_abs(total_cost)}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        if can_afford:
            st.markdown(f"""
            <div class="verdict yes">
                <div class="v-eye">Remaining balance</div>
                <div class="v-num">{fmt_abs(after)}</div>
                <div class="v-desc">You can afford this purchase</div>
                <div class="work-badge">⏱&nbsp; costs <strong>{fmt_hours(hrs_total)}</strong> of work @ ${HOURLY_RATE:.0f}/hr</div>
            </div>""", unsafe_allow_html=True)
        else:
            shortfall  = abs(after)
            hrs_needed = shortfall / HOURLY_RATE
            st.markdown(f"""
            <div class="verdict no">
                <div class="v-eye">Shortfall</div>
                <div class="v-num">{fmt_abs(shortfall)}</div>
                <div class="v-desc">You need {fmt_abs(shortfall)} more to afford this</div>
                <div class="work-badge">⏱&nbsp; need <strong>{fmt_hours(hrs_needed)}</strong> more work @ ${HOURLY_RATE:.0f}/hr</div>
            </div>
            <p style='text-align:center;font-size:11px;color:#242424;margin-top:10px;letter-spacing:0.3px'>
                Full cost = <strong style='color:#323232'>{fmt_hours(hrs_total)}</strong> of work
            </p>""", unsafe_allow_html=True)

    # ── Transaction Ledger ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Transaction Ledger</div>', unsafe_allow_html=True)
    srch = st.text_input("Search", placeholder="🔍  Search transactions…",
                          label_visibility="collapsed", key="srch_spend")
    disp = spend_df[spend_df["name"].str.contains(srch, case=False, na=False)] \
           if srch else spend_df
    render_ledger(disp, "spending")

    if not spend_df.empty:
        st.markdown('<div class="section-label">Balance History</div>', unsafe_allow_html=True)
        chron = spend_df.iloc[::-1].reset_index(drop=True)
        st.line_chart(pd.DataFrame({"Discretionary": chron["spending"].cumsum()}),
                      color=["#ff453a"])


# ╔═════════════════════════════════════════════════════════════════════════════
# ║  SAVINGS VIEW
# ╚═════════════════════════════════════════════════════════════════════════════
elif view == "savings":

    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">Reserve Balance</div>
        <div class="hero-amount save-color">{fmt_abs(savings_total)}</div>
        <div class="hero-sub">Long-term reserves · Growing steadily</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Deposit Ledger</div>', unsafe_allow_html=True)
    srch_sv = st.text_input("Search", placeholder="🔍  Search deposits…",
                             label_visibility="collapsed", key="srch_save")
    disp_sv = save_df[save_df["name"].str.contains(srch_sv, case=False, na=False)] \
              if srch_sv else save_df
    render_ledger(disp_sv, "savings")

    if not save_df.empty:
        st.markdown('<div class="section-label">Reserve Growth</div>', unsafe_allow_html=True)
        chron_sv = save_df.iloc[::-1].reset_index(drop=True)
        st.line_chart(pd.DataFrame({"Reserves": chron_sv["savings"].cumsum()}),
                      color=["#30d158"])


# ╔═════════════════════════════════════════════════════════════════════════════
# ║  GIVING VIEW
# ╚═════════════════════════════════════════════════════════════════════════════
elif view == "giving":

    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">Charitable Balance</div>
        <div class="hero-amount give-color">{fmt_abs(giving_total)}</div>
        <div class="hero-sub">Set aside for giving · Making a difference</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Contribution Ledger</div>', unsafe_allow_html=True)
    srch_g = st.text_input("Search", placeholder="🔍  Search contributions…",
                            label_visibility="collapsed", key="srch_give")
    disp_g = give_df[give_df["name"].str.contains(srch_g, case=False, na=False)] \
             if srch_g else give_df
    render_ledger(disp_g, "giving")

    if not give_df.empty:
        st.markdown('<div class="section-label">Giving History</div>', unsafe_allow_html=True)
        chron_g = give_df.iloc[::-1].reset_index(drop=True)
        st.line_chart(pd.DataFrame({"Charitable": chron_g["giving"].cumsum()}),
                      color=["#0a84ff"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,2,1])
with c2:
    if st.button("↻  Sync Ledger", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
st.markdown('<div class="footer-text">Personal Finance · Secure Account Access</div>',
            unsafe_allow_html=True)

