"""anti gooner — Version 2 « Console ».

DA : brutaliste / terminal. Noir profond, vert acide, monospace (JetBrains Mono) et titres
condensés en capitales (Archivo). Angles vifs, bordures 1 px, barres de progression ASCII.
UX : la barre latérale devient un « rail de commande » toujours visible (navigation,
projets avec progression, système). Chaque projet s'ouvre en tableau Kanban par urgence
(En retard · ≤ 3 jours · Plus tard · Fait) avec un ajout rapide de tâche en une ligne.
"""
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st  # noqa: E402

import core as c  # noqa: E402
from core import esc, tr  # noqa: E402

c.apply_theme(base="dark", primaryColor="#C8FF2E", backgroundColor="#0B0B0C",
              secondaryBackgroundColor="#151517", textColor="#E8E8E3")
st.set_page_config(page_title="ANTI_GOONER // console", page_icon="▌", layout="wide",
                   initial_sidebar_state="auto")
c.init_backend()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&family=JetBrains+Mono:wght@400;500;700;800&display=swap');
/* Les blocs HTML (sans <p>) ne doivent pas hériter de la marge négative de Streamlit. */
[data-testid="stMarkdownContainer"]:not(:has(> p)) { margin-bottom:0 !important; }
:root {
  --bg:#0B0B0C; --panel:#111113; --panel2:#18181B; --line:#2A2A2F; --line2:#3A3A40;
  --text:#E8E8E3; --dim:#8D8D86; --acid:#C8FF2E; --late:#FF5A36; --soon:#FFB020; --ok:#C8FF2E; --info:#5AD7FF;
  --mono:'JetBrains Mono', ui-monospace, monospace; --cond:'Archivo', 'Arial Narrow', sans-serif;
}
.stApp { background:var(--bg); color:var(--text);
  background-image:linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
  background-size:32px 32px; }
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp li { font-family:var(--mono); }
#MainMenu, footer { visibility:hidden; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1320px; padding:1.4rem 2rem 4rem; }
* { border-radius:0 !important; }
::selection { background:var(--acid); color:#000; }

/* ---------- Rail de commande (sidebar) ---------- */
[data-testid="stSidebar"] { background:var(--panel); border-right:1px solid var(--line2); }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.45rem; }
.brand { font-family:var(--cond); font-stretch:68%; font-weight:900; font-size:1.9rem; white-space:nowrap; letter-spacing:-.01em; line-height:.9;
  text-transform:uppercase; color:var(--text); padding:.2rem 0 .1rem; }
.brand span { background:var(--acid); color:#000; padding:0 .25rem; }
.who { font-size:.72rem; color:var(--dim); margin-bottom:.6rem; }
.who b { color:var(--acid); font-weight:500; }
.rail-h { font-size:.68rem; font-weight:700; letter-spacing:.14em; color:var(--dim); text-transform:uppercase;
  border-top:1px solid var(--line); padding-top:.7rem; margin-top:.7rem; display:flex; justify-content:space-between; }
[class*="st-key-rail_"] button { justify-content:flex-start !important; text-align:left; background:transparent !important;
  border:1px solid transparent !important; min-height:2.3rem; padding:.2rem .6rem !important; }
[class*="st-key-rail_"] button p { font-size:.86rem !important; font-weight:700; letter-spacing:.04em; color:var(--text) !important; }
[class*="st-key-rail_"] button:hover { border-color:var(--line2) !important; background:var(--panel2) !important; }
[class*="st-key-rail_"] button[data-testid="stBaseButton-primary"] { background:var(--acid) !important; }
[class*="st-key-rail_"] button[data-testid="stBaseButton-primary"] p { color:#000 !important; }
[class*="st-key-hit_"] { position:relative; gap:0 !important; }
[class*="st-key-hit_"] [data-testid="stElementContainer"]:has(button) { position:absolute; inset:0; z-index:3; margin:0; width:100% !important; height:100%; }
[class*="st-key-hit_"] .stButton, [class*="st-key-hit_"] .stButton button { width:100%; height:100%; min-height:0; }
[class*="st-key-hit_"] .stButton button { opacity:0; padding:0; border:0; cursor:pointer; }
.rp { border:1px solid var(--line); padding:.55rem .65rem; background:var(--bg); transition:border-color .15s ease, transform .15s ease; }
[class*="st-key-hit_"]:hover .rp { border-color:var(--acid); transform:translateX(3px); }
.rp.on { border-color:var(--acid); box-shadow:inset 3px 0 0 var(--acid); }
.rp-n { font-size:.8rem; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rp-b { font-size:.72rem; color:var(--acid); letter-spacing:-.02em; margin-top:.15rem; }
.rp-b em { font-style:normal; color:var(--dim); }

/* ---------- Barre d'état ---------- */
.status { display:flex; flex-wrap:wrap; border:1px solid var(--line2); background:var(--panel); font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; }
.status > span { padding:.5rem .8rem; border-right:1px solid var(--line); color:var(--dim); }
.status > span b { color:var(--text); font-weight:700; }
.status > span.ok b { color:var(--acid); } .status > span.warn b { color:var(--soon); }
.status > span:last-child { margin-left:auto; border-right:0; border-left:1px solid var(--line); }
.blink { animation:blink 1.1s steps(1) infinite; color:var(--acid); }
@keyframes blink { 50% { opacity:0; } }

/* ---------- Titres ---------- */
.path { font-size:.75rem; color:var(--dim); margin:1.4rem 0 .1rem; }
.path b { color:var(--acid); font-weight:500; }
.h1 { font-family:var(--cond); font-stretch:68%; font-weight:900; font-size:clamp(3rem, 9vw, 6.5rem); line-height:.85; text-transform:uppercase;
  letter-spacing:-.01em; color:var(--text); margin:0 0 .8rem; word-break:break-word; }
.h1 span { color:var(--acid); }
.h2 { font-size:.78rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--text); display:flex; align-items:center;
  gap:.6rem; margin:1.6rem 0 .5rem; }
.h2::before { content:""; width:.6rem; height:.6rem; background:var(--acid); }
.h2 em { font-style:normal; color:var(--dim); font-weight:500; }
.empty { border:1px dashed var(--line2); color:var(--dim); padding:2rem; text-align:center; font-size:.85rem; }

/* ---------- Boutons ---------- */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
  background:var(--panel); border:1px solid var(--line2); color:var(--text); min-height:2.6rem; box-shadow:none;
  transition:background .12s ease, color .12s ease, border-color .12s ease; }
.stButton button p, .stDownloadButton button p, .stFormSubmitButton button p { font-weight:700; font-size:.82rem; letter-spacing:.06em; text-transform:uppercase; }
.stButton button:hover, .stDownloadButton button:hover { border-color:var(--acid); color:var(--acid); background:var(--panel2); }
.stButton button[data-testid="stBaseButton-primary"], .stFormSubmitButton button { background:var(--acid); border-color:var(--acid); color:#000; }
.stButton button[data-testid="stBaseButton-primary"] p, .stFormSubmitButton button p { color:#000; }
.stButton button[data-testid="stBaseButton-primary"]:hover, .stFormSubmitButton button:hover { background:#fff; border-color:#fff; color:#000; }
button:focus-visible { outline:2px solid var(--acid) !important; outline-offset:2px; }
button[data-testid="stPopoverButton"] > div:last-child { display:none; }

/* ---------- Grille projets ---------- */
[class*="st-key-tile_"] { border:1px solid var(--line2); background:var(--panel); padding:0; gap:0 !important; transition:transform .15s ease, box-shadow .15s ease; }
[class*="st-key-tile_"]:hover { transform:translate(-3px, -3px); box-shadow:6px 6px 0 var(--acid); border-color:var(--acid); }
.tile { padding:.9rem 1rem .8rem; }
.tile-top { display:flex; justify-content:space-between; font-size:.68rem; color:var(--dim); letter-spacing:.08em; }
.tile-top i { display:inline-block; width:.6rem; height:.6rem; margin-right:.4rem; vertical-align:0; }
.tile-n { font-family:var(--cond); font-stretch:75%; font-weight:800; font-size:1.75rem; line-height:1; text-transform:uppercase; margin:.7rem 0 .35rem; color:var(--text); }
.tile-d { font-size:.75rem; color:var(--dim); min-height:2.2rem; line-height:1.45; }
.ascii { font-size:.8rem; color:var(--acid); margin:.7rem 0 .2rem; white-space:nowrap; letter-spacing:-.04em; }
.ascii em { color:var(--line2); font-style:normal; }
.ascii b { color:var(--text); font-weight:700; margin-left:.4rem; letter-spacing:0; }
.tile-f { display:flex; justify-content:space-between; align-items:center; font-size:.72rem; color:var(--dim); border-top:1px solid var(--line); padding-top:.6rem; margin-top:.6rem; }
[class*="st-key-tile_"] .stButton button { border:0; border-top:1px solid var(--line2); width:100%; justify-content:space-between; }
.st-key-add_tile button { min-height:100% !important; height:100%; border:1px dashed var(--acid) !important; background:transparent !important; }
.st-key-add_tile button p { color:var(--acid) !important; font-size:1rem !important; }
.st-key-add_tile button:hover { background:var(--acid) !important; } .st-key-add_tile button:hover p { color:#000 !important; }
.st-key-add_tile, .st-key-add_tile .stButton { height:100%; min-height:12rem; }

.tag { font-size:.66rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; padding:.12rem .4rem; white-space:nowrap; }
.tag.late { background:var(--late); color:#000; } .tag.soon { background:var(--soon); color:#000; }
.tag.ok { border:1px solid var(--acid); color:var(--acid); } .tag.done { border:1px solid var(--line2); color:var(--dim); }

/* ---------- Mes tâches (table) ---------- */
.st-key-mine { border:1px solid var(--line2); background:var(--panel); }
[class*="st-key-mrow_"] { border-bottom:1px solid var(--line); padding:.3rem .8rem; }
[class*="st-key-mrow_"]:last-child { border-bottom:0; }
[class*="st-key-mrow_"]:hover { background:var(--panel2); }
.mono-s { font-size:.76rem; color:var(--dim); white-space:nowrap; }
.mono-t { font-size:.86rem; color:var(--text); font-weight:500; }

/* ---------- Kanban ---------- */
.meta { display:grid; grid-template-columns:repeat(4, 1fr); border:1px solid var(--line2); background:var(--panel); margin-bottom:.8rem; }
.meta > div { padding:.7rem .9rem; border-right:1px solid var(--line); }
.meta > div:last-child { border-right:0; }
.meta small { display:block; font-size:.64rem; letter-spacing:.14em; color:var(--dim); text-transform:uppercase; margin-bottom:.3rem; }
.meta b { font-size:1rem; color:var(--text); }
.meta .ascii { margin:0; }
.desc { color:var(--dim); font-size:.85rem; margin:-.2rem 0 1rem; max-width:52rem; }
.st-key-quick { border:1px solid var(--line2); background:var(--panel); padding:.55rem .7rem .2rem; }
.st-key-quick [data-testid="stForm"] { border:0; padding:0; }
.st-key-quick label p { font-size:.66rem !important; letter-spacing:.12em; text-transform:uppercase; color:var(--dim) !important; }
.st-key-board_cols > div > [data-testid="stHorizontalBlock"] { gap:.8rem; align-items:stretch; }
[class*="st-key-lane_"] { border:1px solid var(--line2); background:rgba(17,17,19,.9); padding:.6rem; min-height:12rem; height:100%; }
.lane-h { display:flex; justify-content:space-between; font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase;
  padding:.2rem .1rem .55rem; border-bottom:2px solid var(--line2); margin-bottom:.2rem; color:var(--text); }
.lane-h.late { border-color:var(--late); } .lane-h.soon { border-color:var(--soon); } .lane-h.ok { border-color:var(--acid); } .lane-h.done { border-color:var(--line2); color:var(--dim); }
.lane-empty { color:var(--line2); font-size:.75rem; text-align:center; padding:1.2rem 0; }
[class*="st-key-task_"] { border:1px solid var(--line); background:var(--bg); padding:.5rem .55rem .45rem; margin-bottom:.1rem; transition:border-color .12s ease; }
[class*="st-key-task_"]:hover { border-color:var(--text); }
[class*="st-key-task_late_"] { box-shadow:inset 3px 0 0 var(--late); }
[class*="st-key-task_soon_"] { box-shadow:inset 3px 0 0 var(--soon); }
[class*="st-key-task_ok_"] { box-shadow:inset 3px 0 0 var(--acid); }
[class*="st-key-task_done_"] { opacity:.55; } [class*="st-key-task_done_"]:hover { opacity:1; }
[class*="st-key-task_"] [data-testid="stHorizontalBlock"] { gap:.35rem; }
[class*="st-key-task_"] [data-testid="stVerticalBlock"] { gap:.2rem; }
.k-t { font-size:.84rem; font-weight:700; color:var(--text); line-height:1.3; }
.k-t.done { text-decoration:line-through; color:var(--dim); }
.k-m { font-size:.68rem; color:var(--dim); display:flex; flex-wrap:wrap; gap:.35rem .55rem; align-items:center; margin-top:.25rem; }
.k-m b { color:var(--text); font-weight:500; }
label[data-baseweb="checkbox"] > span:first-child { border-radius:0 !important; }
[class*="st-key-task_"] button[data-testid="stPopoverButton"], [class*="st-key-mrow_"] button[data-testid="stPopoverButton"] { min-height:1.7rem; padding:0 .35rem; border-color:var(--line); background:transparent; }

/* ---------- Planning ---------- */
.kpi { display:grid; grid-template-columns:repeat(3, 1fr); gap:.8rem; margin:.2rem 0 1rem; }
.kpi > div { border:1px solid var(--line2); background:var(--panel); padding:.8rem 1rem; }
.kpi small { font-size:.66rem; letter-spacing:.14em; text-transform:uppercase; color:var(--dim); }
.kpi b { display:block; font-family:var(--cond); font-stretch:70%; font-weight:900; font-size:clamp(2.2rem, 5vw, 3.6rem); line-height:1; color:var(--acid); margin-top:.3rem; }
.period { font-family:var(--cond); font-stretch:75%; font-weight:800; font-size:1.5rem; text-transform:uppercase; text-align:center; color:var(--text); }
.legend { font-size:.7rem; color:var(--dim); letter-spacing:.06em; text-transform:uppercase; }
.legend i { display:inline-block; width:.65rem; height:.65rem; margin:0 .35rem 0 .9rem; vertical-align:-1px; }
.st-key-week > div > [data-testid="stHorizontalBlock"] { gap:.4rem; }
.wk { border:1px solid var(--line2); background:var(--panel); height:170px; display:flex; flex-direction:column; justify-content:flex-end; padding:.5rem .4rem .4rem; }
.wk.sel { border-color:var(--acid); box-shadow:inset 0 0 0 1px var(--acid); }
.wk .t { font-size:.7rem; color:var(--text); text-align:center; margin-bottom:.3rem; font-weight:700; }
.wk .bar { height:100px; display:flex; flex-direction:column; justify-content:flex-end; background:repeating-linear-gradient(0deg, var(--line) 0 1px, transparent 1px 10px); }
.wk .bar .o { background:var(--acid); } .wk .bar .d { background:var(--line2); }
.wk .dt { font-size:.68rem; color:var(--dim); text-align:center; margin-top:.35rem; }
.wk.today .dt { color:var(--acid); }
.st-key-week .stButton button { min-height:2rem; }
.mh { font-size:.66rem; letter-spacing:.14em; color:var(--dim); text-align:center; text-transform:uppercase; }
.st-key-month > div > [data-testid="stHorizontalBlock"] { gap:.3rem; }
.mc { height:64px; border:1px solid var(--line); padding:.3rem .4rem; display:flex; flex-direction:column; justify-content:space-between; }
.mc b { font-size:.8rem; color:var(--text); } .mc span { font-size:.64rem; color:var(--text); }
.mc.out { opacity:.25; } .mc.sel { outline:2px solid var(--acid); outline-offset:-2px; } .mc.today b { color:var(--acid); }

/* ---------- Dialogues & champs ---------- */
[data-testid="stDialog"] div[role="dialog"] { background:var(--panel); border:1px solid var(--acid); box-shadow:10px 10px 0 rgba(200,255,46,.25); }
[data-testid="stDialog"] h2 { font-family:var(--cond) !important; font-stretch:75%; font-weight:900 !important; text-transform:uppercase; letter-spacing:0; }
.dialog-intro { font-size:.7rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--text);
  border-bottom:1px solid var(--line2); padding:.3rem 0; margin:.9rem 0 .4rem; }
.dialog-intro b { background:var(--acid); color:#000; padding:0 .3rem; margin-right:.6rem; }
.stTextInput input, .stTextArea textarea, .stDateInput input { font-family:var(--mono) !important; }
[data-testid="stPopoverBody"] { border:1px solid var(--acid); background:var(--panel); }
.st-key-lang [role="radiogroup"] { gap:0; }
.st-key-lang label { border:1px solid var(--line2); padding:.15rem .6rem; margin-right:-1px; }
.st-key-lang label > div:first-child { display:none; }
.st-key-lang label p { font-size:.72rem !important; font-weight:700; }
.st-key-lang label:has(input:checked) { background:var(--acid); border-color:var(--acid); }
.st-key-lang label:has(input:checked) p { color:#000 !important; }
.ok-line { font-size:.72rem; color:var(--acid); }
.login { margin:10vh 0 1.5rem; }
.login p { color:var(--dim); font-size:.95rem; }

/* ---------- Responsive ---------- */
@media (max-width: 1024px) {
  .block-container { padding:1rem 1rem 3rem; }
  .st-key-grid [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
  .st-key-grid [data-testid="stColumn"] { flex:1 1 calc(50% - 1rem) !important; min-width:calc(50% - 1rem) !important; }
  .st-key-board_cols > div > [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
  .st-key-board_cols > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { flex:1 1 calc(50% - .8rem) !important; min-width:calc(50% - .8rem) !important; }
  .meta { grid-template-columns:1fr 1fr; }
  .meta > div:nth-child(2) { border-right:0; } .meta > div:nth-child(-n+2) { border-bottom:1px solid var(--line); }
}
.st-key-mnav { display:none; }
@media (max-width: 640px) {
  .st-key-mnav { display:block; }
  .st-key-mnav [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:.3rem; }
  .st-key-mnav [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; }
  [class*="st-key-task_"] [data-testid="stHorizontalBlock"], [class*="st-key-mrow_"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
  [class*="st-key-task_"] [data-testid="stColumn"], [class*="st-key-mrow_"] [data-testid="stColumn"] { min-width:0 !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:first-child, [class*="st-key-mrow_"] [data-testid="stColumn"]:first-child { flex:0 0 1.7rem !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:last-child { flex:0 0 2.2rem !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:nth-child(2), [class*="st-key-mrow_"] [data-testid="stColumn"]:nth-child(3) { flex:1 1 auto !important; width:auto !important; }
  [class*="st-key-mrow_"] [data-testid="stColumn"]:nth-child(2), [class*="st-key-mrow_"] [data-testid="stColumn"]:nth-child(4) { display:none; }
  .h1 { font-size:2.6rem; }
  .st-key-grid [data-testid="stColumn"], .st-key-board_cols > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { flex:1 1 100% !important; min-width:100% !important; }
  .kpi { grid-template-columns:1fr; }
  .st-key-week > div > [data-testid="stHorizontalBlock"], .st-key-month > div > [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:.15rem; }
  .st-key-week [data-testid="stColumn"], .st-key-month [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; }
  .wk { height:120px; padding:.3rem .1rem; } .wk .bar { height:60px; } .wk .t { font-size:.55rem; }
  .st-key-week .stButton button p { font-size:.6rem !important; letter-spacing:0; }
  .mc { height:46px; padding:.15rem; } .mc span { display:none; }
  .status > span:last-child { margin-left:0; border-left:0; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def hero(text):
    st.markdown(f'<div class="login"><div class="path">~/anti_gooner <span class="blink">▌</span></div>'
                f'<div class="h1">ANTI<span>_</span>GOONER</div><p>&gt; {text}</p></div>', unsafe_allow_html=True)
    c.language_switch()


c.auth_gate(hero)
cal_row, cal_err = c.bootstrap()
st.session_state.setdefault("page", "projects")


def go(page):
    st.session_state.page = page
    st.session_state.open = None


def open_project(pid):
    st.session_state.page = "projects"
    st.session_state.open = pid


def tag(d, done=False):
    cls, txt = c.due_info(d, done)
    return f'<span class="tag {cls}">{esc(txt)}</span>'


def ascii_bar(p, width=14):
    pct = c.pct(p)
    full = round(pct / 100 * width)
    return f'[{"█" * full}<em>{"░" * (width - full)}</em>]<b>{pct:>3}%</b>'


# ---------- Rail de commande ----------
def rail():
    with st.sidebar:
        st.markdown('<div class="brand">ANTI<span>_</span>GOONER</div>'
                    f'<div class="who">user@<b>{esc(c.me()["name"].lower())}</b> · {date.today():%Y.%m.%d}</div>',
                    unsafe_allow_html=True)
        for i, (pid, label) in enumerate([("projects", "Projets"), ("planning", "Charge de travail")], 1):
            active = st.session_state.page == pid and not (pid == "projects" and st.session_state.open)
            with st.container(key=f"rail_{pid}"):
                st.button(f"[{i}] {tr(label).upper()}", on_click=go, args=(pid,), use_container_width=True,
                          type="primary" if active else "secondary")
        projects = c.sorted_projects()
        st.markdown(f'<div class="rail-h"><span>// {tr("Avancement")}</span><span>{len(projects):02d}</span></div>', unsafe_allow_html=True)
        if not projects:
            st.caption(tr("L'avancement de chaque projet apparaîtra ici."))
        for p in projects:
            done, total = c.progress(p)
            with st.container(key=f"hit_r{p['id']}"):
                st.markdown(f'<div class="rp{" on" if p["id"] == st.session_state.open else ""}">'
                            f'<div class="rp-n">{esc(p["name"])}</div>'
                            f'<div class="rp-b">{ascii_bar(p, 12)} <em>{done}/{total}</em></div></div>', unsafe_allow_html=True)
                st.button(p["name"], key=f"go_{p['id']}", on_click=open_project, args=(p["id"],))
        st.markdown('<div class="rail-h"><span>// Google Calendar</span></div>', unsafe_allow_html=True)
        c.calendar_panel(cal_row, cal_err, link_style=(
            "display:block;text-align:center;padding:.6rem;background:#C8FF2E;color:#000;"
            "font-family:monospace;font-weight:700;text-transform:uppercase;text-decoration:none"))
        st.markdown(f'<div class="rail-h"><span>// {tr("Système")}</span></div>', unsafe_allow_html=True)
        c.export_button("⤓ " + tr("Exporter les données"))
        c.language_switch()
        st.markdown(f'<div class="ok-line">● {esc(tr("Connecté : {name}").format(name=c.me()["name"]))}</div>', unsafe_allow_html=True)
        st.button("⏻ " + tr("Se déconnecter"), key="logout", on_click=st.logout, use_container_width=True)


def status_bar():
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    cal = '<span class="ok">CAL <b>SYNC</b></span>' if cal_row else '<span class="warn">CAL <b>OFFLINE</b></span>'
    st.markdown(
        '<div class="status">'
        f'<span>{tr("Projets").upper()} <b>{len(st.session_state.projects):02d}</b></span>'
        f'<span>{tr("Ouvertes").upper()} <b>{c.open_count():02d}</b></span>'
        f'<span>{tr("Cette semaine").upper()} <b>{c.format_duration(summary["week"]) if summary["week"] else "0"}</b></span>'
        f'{cal}<span>{datetime.now():%H:%M} <span class="blink">▌</span></span></div>', unsafe_allow_html=True)


# ---------- Carte tâche (kanban et listes) ----------
def task_card(p, t, suffix="", show_project=False):
    s = f"_{suffix}" if suffix else ""
    with st.container(key=f"task_{c.task_status(t)}_{t['id']}{s}"):
        a, b, m = st.columns([0.16, 1, 0.22], vertical_alignment="top")
        with a:
            c.task_checkbox(p, t, s)
        proj = f'<span>{esc(p["name"])}</span>' if show_project else ""
        by = f'<span>✓ {esc(t["by"])}</span>' if t["done"] and t.get("by") else ""
        b.markdown(
            f'<div class="k-t{" done" if t["done"] else ""}">{c.star(t)}{esc(t["title"])}</div>'
            f'<div class="k-m">{proj}<span>@<b>{esc(tr(t["owner"]))}</b></span><span>{c.parse(t["due"]):%d.%m}</span>'
            f'<span>⏱ {c.format_duration(t.get("duration_minutes", 60))}</span>{tag(t["due"], t["done"])}{by}</div>',
            unsafe_allow_html=True)
        with m.popover("⋯"):
            c.task_menu(p, t, s)


# ---------- Projets ----------
def board():
    projects = c.sorted_projects()
    st.markdown('<div class="path">~/<b>projets</b></div>'
                f'<div class="h1">{tr("Projets")}<span>/</span></div>', unsafe_allow_html=True)
    items = ["add"] + projects
    with st.container(key="grid"):
        for r in range(0, len(items), 3):
            cols = st.columns(3, gap="medium")
            for col, p in zip(cols, items[r:r + 3]):
                with col:
                    if p == "add":
                        if st.button("[+] " + tr("Nouveau projet"), key="add_tile", use_container_width=True):
                            c.open_new_project()
                        continue
                    done, total = c.progress(p)
                    with st.container(key=f"tile_{p['id']}"):
                        st.markdown(
                            f'<div class="tile"><div class="tile-top"><span><i style="background:{p["color"]}"></i>#{esc(p["id"])}</span>'
                            f'<span>DL {c.parse(p["due"]):%d.%m.%y}</span></div>'
                            f'<div class="tile-n">{esc(p["name"])}</div><div class="tile-d">{esc(p.get("desc")) or "—"}</div>'
                            f'<div class="ascii">{ascii_bar(p)}</div>'
                            f'<div class="tile-f"><span>{tr("{done}/{total} tâches").format(done=done, total=total)}</span>'
                            f'{tag(p["due"], c.project_finished(p))}</div></div>', unsafe_allow_html=True)
                        st.button(tr("Ouvrir") + " →", key=f"open_{p['id']}", on_click=open_project, args=(p["id"],),
                                  use_container_width=True)
    if not projects:
        st.markdown(f'<div class="empty">&gt; {tr(c.NO_PROJECT)}</div>', unsafe_allow_html=True)
    mine_all = c.my_open_tasks()
    st.markdown(f'<div class="h2">{tr("Mes tâches")} <em>({len(mine_all)})</em></div>', unsafe_allow_html=True)
    if not mine_all:
        st.markdown(f'<div class="empty">&gt; {tr("Tout est à jour.")}</div>', unsafe_allow_html=True)
        return
    with st.container(key="mine"):
        for p, t in mine_all[:10]:
            with st.container(key=f"mrow_{t['id']}"):
                cols = st.columns([0.25, 0.8, 4, 2.2, 1.3], vertical_alignment="center")
                with cols[0]:
                    c.task_checkbox(p, t, "_mine")
                cols[1].markdown(f'<span class="mono-s">{c.parse(t["due"]):%d.%m}</span>', unsafe_allow_html=True)
                cols[2].markdown(f'<span class="mono-t">{c.star(t)}{esc(t["title"])}</span>', unsafe_allow_html=True)
                cols[3].markdown(f'<span class="mono-s">{esc(p["name"])}</span>', unsafe_allow_html=True)
                cols[4].markdown(tag(t["due"]), unsafe_allow_html=True)
    if len(mine_all) > 10:
        st.caption(tr("+ {n} autres tâches").format(n=len(mine_all) - 10))


def lanes(p):
    today = date.today()
    groups = {"late": [], "soon": [], "ok": [], "done": []}
    for t in sorted(p["tasks"], key=lambda t: t["due"]):
        if t["done"]:
            groups["done"].append(t)
        else:
            n = (c.parse(t["due"]) - today).days
            groups["late" if n < 0 else "soon" if n <= 3 else "ok"].append(t)
    return groups


def project_view(p):
    done, total = c.progress(p)
    slug = "".join(ch if ch.isalnum() else "_" for ch in p["name"].lower())
    st.markdown(f'<div class="path">~/projets/<b>{esc(slug)}</b></div><div class="h1">{esc(p["name"])}</div>'
                + (f'<div class="desc">&gt; {esc(p["desc"])}</div>' if p.get("desc") else ""), unsafe_allow_html=True)
    owner = next((m for m, i in zip(p["members"], p["member_ids"]) if i == p.get("owner_id")), "—")
    st.markdown(
        '<div class="meta">'
        f'<div><small>{tr("Deadline")}</small><b>{c.parse(p["due"]):%d.%m.%Y}</b> {tag(p["due"], c.project_finished(p))}</div>'
        f'<div><small>{tr("Progression")} · {done}/{total}</small><div class="ascii">{ascii_bar(p, 16)}</div></div>'
        f'<div><small>{tr("Membres")} · {len(p["members"])}</small><b>{", ".join(esc(m) for m in p["members"])}</b></div>'
        f'<div><small>{tr("Propriétaire")}</small><b>{esc(owner)}</b></div></div>', unsafe_allow_html=True)
    a1, a2, a3, a4, a5 = st.columns([1, 1.1, 1.1, 0.9, 1.6])
    a1.button("← " + tr("Retour"), key="back", on_click=c.set_open, args=(None,), use_container_width=True)
    if a2.button("[+] " + tr("Nouvelle tâche"), type="primary", key="add_task", use_container_width=True):
        c.open_new_task(p["id"])
    if a3.button(tr("Gérer le projet"), key=f"manage_{p['id']}", use_container_width=True):
        c.open_edit_project(p["id"])
    if c.is_owner(p) and a4.button(tr("Supprimer"), key="del_project", use_container_width=True):
        c.open_confirm_delete(p["id"])
    with a5:
        c.ics_button(p, "⤓ .ics")

    # Ajout rapide : une ligne, valeurs par défaut (J+3, tout le monde, 1 h).
    with st.container(key="quick"):
        with st.form(f"quick_{p['id']}", clear_on_submit=True, border=False):
            q = st.columns([3, 1.2, 1.2, 1.1, 0.9], vertical_alignment="bottom")
            title = q[0].text_input(tr("Ajout rapide"), placeholder="> " + tr("Ajouter une tâche…"))
            due = q[1].date_input(tr("Deadline"), value=date.today() + timedelta(days=3), format="DD/MM/YYYY")
            owner_sel = q[2].selectbox(tr("Responsable"), [c.EVERYONE] + p["members"], format_func=tr)
            dur = q[3].selectbox(tr("Durée"), c.DURATION_OPTIONS, index=3, format_func=c.format_duration)
            ok = q[4].form_submit_button("↵ " + tr("Ajouter"), use_container_width=True)
        if ok:
            if title.strip():
                c.add_task(p["id"], title, due, owner_sel, dur)
                st.toast(tr("Tâche ajoutée ✨"))
                st.rerun()
            else:
                st.error(tr("Donne un nom à la tâche."))

    if not p["tasks"]:
        st.markdown(f'<div class="empty">&gt; {tr("Pas encore de tâche. Ajoute la première avec sa deadline.")}</div>', unsafe_allow_html=True)
        return
    groups = lanes(p)
    labels = {"late": tr("En retard"), "soon": "≤ 3 " + ("jours" if c.lang() == "FR" else "days"),
              "ok": tr("Plus tard"), "done": tr("Terminées")}
    st.write("")
    with st.container(key="board_cols"):
        cols = st.columns(4)
        for col, key in zip(cols, ["late", "soon", "ok", "done"]):
            with col, st.container(key=f"lane_{key}"):
                st.markdown(f'<div class="lane-h {key}"><span>{labels[key]}</span><span>{len(groups[key]):02d}</span></div>',
                            unsafe_allow_html=True)
                if not groups[key]:
                    st.markdown('<div class="lane-empty">— ∅ —</div>', unsafe_allow_html=True)
                for t in groups[key]:
                    task_card(p, t)


# ---------- Planning ----------
def item_card(item, suffix):
    p, t = c.find_task(item)
    if t:
        task_card(p, t, suffix, show_project=True)


def planning():
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    st.markdown('<div class="path">~/<b>planning</b></div>'
                f'<div class="h1">{tr("Charge de travail")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi">'
                f'<div><small>{tr("Heures restantes")}</small><b>{c.format_duration(summary["total"])}</b></div>'
                f'<div><small>{tr(c.TODAY)}</small><b>{c.format_duration(summary["today"]) if summary["today"] else "0"}</b></div>'
                f'<div><small>{tr("Cette semaine")}</small><b>{c.format_duration(summary["week"]) if summary["week"] else "0"}</b></div></div>',
                unsafe_allow_html=True)
    view, start, end, days, sel_key = c.workload_period()
    p1, p2, prev, lab, nxt = st.columns([1, 1, 0.5, 3, 0.5], vertical_alignment="center")
    p1.button(tr("Semaine"), key="pw", on_click=c.set_period, args=("Semaine",), use_container_width=True,
              type="primary" if view == "Semaine" else "secondary")
    p2.button(tr("Mois"), key="pm", on_click=c.set_period, args=("Mois",), use_container_width=True,
              type="primary" if view == "Mois" else "secondary")
    prev.button("◀", key="pprev", on_click=c.shift_period, args=(-1,), use_container_width=True,
                help=tr("Semaine précédente" if view == "Semaine" else "Mois précédent"))
    lab.markdown(f'<div class="period">{esc(c.period_label(view, start, end))}</div>', unsafe_allow_html=True)
    nxt.button("▶", key="pnext", on_click=c.shift_period, args=(1,), use_container_width=True,
               help=tr("Semaine suivante" if view == "Semaine" else "Mois suivant"))
    period = [x for x in rows if start <= x["date"] <= end]
    o = sum(x["minutes"] for x in period if not x["done"])
    d = sum(x["minutes"] for x in period if x["done"])
    st.markdown(f'<div class="legend"><i style="background:var(--acid)"></i>{tr("Ouvertes")} {c.format_duration(o) if o else "0"}'
                f'<i style="background:var(--line2)"></i>{tr("Terminées")} {c.format_duration(d) if d else "0"}</div>', unsafe_allow_html=True)
    selected = st.session_state[sel_key]
    today = date.today()
    names = c.DAY_NAMES[c.lang()]
    if view == "Semaine":
        peak = max([sum(c.day_load(rows, day)) for day in days] + [60])
        with st.container(key="week"):
            cols = st.columns(7)
            for i, (col, day) in enumerate(zip(cols, days)):
                op, fi = c.day_load(rows, day)
                with col:
                    st.markdown(f'<div class="wk{" sel" if day == selected else ""}{" today" if day == today else ""}">'
                                f'<div class="t">{c.format_duration(op + fi) if op + fi else "--"}</div>'
                                f'<div class="bar"><div class="d" style="height:{fi / peak * 100:.0f}%"></div>'
                                f'<div class="o" style="height:{op / peak * 100:.0f}%"></div></div>'
                                f'<div class="dt">{day:%d.%m}</div></div>', unsafe_allow_html=True)
                    st.button(names[i].upper(), key=f"wd_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day),
                              use_container_width=True, type="primary" if day == selected else "secondary")
    else:
        with st.container(key="month"):
            head = st.columns(7)
            for col, n in zip(head, names):
                col.markdown(f'<div class="mh">{n}</div>', unsafe_allow_html=True)
            for w in range(0, len(days), 7):
                cols = st.columns(7)
                for col, day in zip(cols, days[w:w + 7]):
                    op, fi = c.day_load(rows, day)
                    # Intensité : plus la journée est chargée, plus la case est verte.
                    alpha = min(1, (op + fi) / 360) * .55
                    with col, st.container(key=f"hit_m{day.isoformat()}"):
                        st.markdown(f'<div class="mc{" out" if day.month != start.month else ""}{" sel" if day == selected else ""}'
                                    f'{" today" if day == today else ""}" style="background:rgba(200,255,46,{alpha:.2f})">'
                                    f'<b>{day.day:02d}</b><span>{c.format_duration(op + fi) if op + fi else ""}</span></div>',
                                    unsafe_allow_html=True)
                        st.button(f"{day:%d/%m}", key=f"md_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day))
    sel_rows = sorted((x for x in rows if x["date"] == selected), key=lambda x: (x["done"], x["project"], x["title"]))
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown(f'<div class="h2">{esc(c.fmt_long(selected))} <em>({len(sel_rows)})</em></div>', unsafe_allow_html=True)
        for item in sel_rows:
            item_card(item, f"sel_{view}")
        if not sel_rows:
            st.markdown(f'<div class="empty">&gt; {tr("Aucune tâche avec une échéance ce jour-là.")}</div>', unsafe_allow_html=True)
    upcoming = sorted((x for x in rows if not x["done"] and x["date"] >= today), key=lambda x: (x["date"], x["project"]))
    with right:
        st.markdown(f'<div class="h2">{tr("Tâches ouvertes")} <em>({len(upcoming)})</em></div>', unsafe_allow_html=True)
        for item in upcoming[:30]:
            item_card(item, "up")
        if not upcoming:
            st.markdown(f'<div class="empty">&gt; {tr("Aucune tâche ouverte à venir.")}</div>', unsafe_allow_html=True)
    completed = sorted((x for x in rows if x["done"]), key=lambda x: (x["date"], x["project"]))
    st.markdown(f'<div class="h2">{tr("Tâches terminées")} <em>({len(completed)})</em></div>', unsafe_allow_html=True)
    if completed:
        cols = st.columns(3)
        for i, item in enumerate(completed[:30]):
            with cols[i % 3]:
                item_card(item, "done")
    else:
        st.markdown(f'<div class="empty">&gt; {tr("Aucune tâche terminée pour le moment.")}</div>', unsafe_allow_html=True)


# ---------- Rendu ----------
rail()
# Sur mobile, le rail est replié : on garde une navigation compacte en haut de page.
with st.container(key="mnav"):
    m1, m2 = st.columns(2)
    m1.button("[1] " + tr("Projets").upper(), key="m_projects", on_click=go, args=("projects",), use_container_width=True,
              type="primary" if st.session_state.page == "projects" else "secondary")
    m2.button("[2] " + tr("Planning").upper(), key="m_planning", on_click=go, args=("planning",), use_container_width=True,
              type="primary" if st.session_state.page == "planning" else "secondary")
top_l, top_r = st.columns([5, 1.2], vertical_alignment="center")
with top_l:
    status_bar()
with top_r:
    if cal_row:
        if st.button("↻ SYNC", key="calendar_sync_main", use_container_width=True, help=tr("Synchroniser Google Calendar")):
            c.run_sync(tr("Calendrier synchronisé"))
c.important_banner()
if st.session_state.page == "planning":
    planning()
else:
    current = c.get_project(st.session_state.open) if st.session_state.open else None
    if current:
        project_view(current)
    else:
        board()
