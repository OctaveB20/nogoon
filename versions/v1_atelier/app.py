"""anti gooner — Version 1 « Atelier ».

DA : éditorial, papier crème, encre noire, accent vermillon, typographie serif (Fraunces).
UX : pas de barre latérale ; un bandeau de journal en haut avec trois rubriques
(Projets · Planning · Réglages). Les projets forment un « index » lisible d'un coup d'œil,
les tâches un tableau réglé, et « À faire pour toi » se coche directement depuis l'accueil.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st  # noqa: E402

import core as c  # noqa: E402
from core import esc, tr  # noqa: E402

c.apply_theme(base="light", primaryColor="#D9481E", backgroundColor="#F3EEE4",
              secondaryBackgroundColor="#EAE3D6", textColor="#1C1B19")
st.set_page_config(page_title="anti gooner — atelier", page_icon="✒️", layout="wide",
                   initial_sidebar_state="collapsed")
c.init_backend()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,400;1,9..144,600&family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;600&display=swap');
/* Les blocs HTML (sans <p>) ne doivent pas hériter de la marge négative de Streamlit. */
[data-testid="stMarkdownContainer"]:not(:has(> p)) { margin-bottom:0 !important; }
:root {
  --paper:#F3EEE4; --paper2:#EAE3D6; --card:#FBF8F2; --ink:#1C1B19; --ink2:#5E5A52; --ink3:#8C877C;
  --rule:#1C1B19; --hair:rgba(28,27,25,.14); --accent:#D9481E;
  --late:#C2361B; --soon:#A86A12; --ok:#2F6B4F;
  --serif:'Fraunces', Georgia, serif; --sans:'Geist', system-ui, sans-serif; --mono:'Geist Mono', ui-monospace, monospace;
}
.stApp { background: var(--paper); color: var(--ink); }
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp li { font-family: var(--sans); }
#MainMenu, footer, [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] { display:none !important; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1160px; padding: 3.6rem 2rem 4rem; }
[data-testid="stVerticalBlock"] { gap: .6rem; }

/* ---------- Masthead ---------- */
.mast-top { display:flex; justify-content:space-between; align-items:flex-end; font-family:var(--mono);
  font-size:.74rem; letter-spacing:.08em; text-transform:uppercase; color:var(--ink2);
  border-bottom:1px solid var(--rule); padding-bottom:.45rem; }
.mast-title { font-family:var(--serif); font-weight:800; font-size:clamp(3rem, 9vw, 6.4rem);
  line-height:.9; letter-spacing:-.045em; margin:.9rem 0 .2rem; color:var(--ink); }
.mast-title em { font-style:italic; font-weight:400; color:var(--accent); }
.mast-sub { font-family:var(--serif); font-style:italic; font-size:1.15rem; color:var(--ink2); margin:0 0 .9rem; }
.mast-strip { display:flex; flex-wrap:wrap; gap:0; border-top:3px double var(--rule); border-bottom:1px solid var(--rule);
  font-family:var(--mono); font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; }
.mast-strip span { padding:.55rem 1rem .5rem 0; margin-right:1rem; border-right:1px solid var(--hair); }
.mast-strip span:last-child { border-right:0; }
.mast-strip b { font-weight:600; color:var(--ink); }

/* Langue */
.st-key-lang [role="radiogroup"] { gap:0; justify-content:flex-end; }
.st-key-lang label { border:1px solid var(--rule); padding:.15rem .7rem; margin:0 0 0 -1px; cursor:pointer; background:transparent; }
.st-key-lang label > div:first-child { display:none; }
.st-key-lang label p { font-family:var(--mono) !important; font-size:.72rem; font-weight:600; color:var(--ink) !important; }
.st-key-lang label:has(input:checked) { background:var(--ink); }
.st-key-lang label:has(input:checked) p { color:var(--paper) !important; }

/* Rubriques (navigation) */
.st-key-nav { border-bottom:1px solid var(--rule); margin-bottom:1.6rem; }
.st-key-nav [data-testid="stHorizontalBlock"] { gap:1.8rem !important; flex-wrap:nowrap !important; }
.st-key-nav [data-testid="stColumn"] { width:auto !important; flex:0 0 auto !important; min-width:0 !important; }
.st-key-nav .stButton button { background:transparent !important; border:0 !important; border-radius:0 !important;
  box-shadow:none !important; padding:.7rem 0 .55rem !important; min-height:0 !important; color:var(--ink3) !important;
  border-bottom:3px solid transparent !important; margin-bottom:-1px; }
.st-key-nav .stButton button p { font-family:var(--serif) !important; font-size:1.35rem !important; font-weight:600; letter-spacing:-.01em; }
.st-key-nav .stButton button p { color:var(--ink3) !important; }
.st-key-nav .stButton button:hover p { color:var(--ink) !important; }
.st-key-nav .stButton button[data-testid="stBaseButton-primary"] { border-bottom-color:var(--accent) !important; }
.st-key-nav .stButton button[data-testid="stBaseButton-primary"] p { color:var(--ink) !important; }

/* ---------- Boutons ---------- */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
  border-radius:0; border:1px solid var(--rule); background:transparent; color:var(--ink);
  font-weight:600; box-shadow:none; transition:background .15s ease, color .15s ease; min-height:2.6rem; }
.stButton button:hover, .stDownloadButton button:hover { background:var(--ink); color:var(--paper); border-color:var(--ink); }
.stButton button:hover p, .stDownloadButton button:hover p { color:var(--paper); }
.stButton button[data-testid="stBaseButton-primary"], .stFormSubmitButton button {
  background:var(--accent); border-color:var(--accent); color:#fff; }
.stButton button[data-testid="stBaseButton-primary"] p, .stFormSubmitButton button p { color:#fff; }
.stButton button[data-testid="stBaseButton-primary"]:hover { background:var(--ink); border-color:var(--ink); }
button:focus-visible { outline:2px solid var(--accent) !important; outline-offset:2px; }

/* ---------- Titres de section ---------- */
.kicker { font-family:var(--mono); font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:var(--accent); margin:0; }
.h-sec { font-family:var(--serif); font-weight:600; font-size:2rem; letter-spacing:-.03em; line-height:1.05; margin:.15rem 0 .4rem; color:var(--ink); }
.h-sec em { font-style:italic; font-weight:400; }
.h-small { font-family:var(--serif); font-weight:600; font-size:1.3rem; letter-spacing:-.02em; margin:1.6rem 0 .3rem;
  border-bottom:1px solid var(--rule); padding-bottom:.35rem; display:flex; justify-content:space-between; align-items:baseline; color:var(--ink); }
.h-small span { font-family:var(--mono); font-size:.75rem; font-weight:400; color:var(--ink2); }

/* ---------- Index des projets ---------- */
[class*="st-key-hit_"] { position:relative; gap:0 !important; }
[class*="st-key-hit_"] [data-testid="stElementContainer"]:has(button) { position:absolute; inset:0; z-index:3; margin:0; width:100% !important; height:100%; }
[class*="st-key-hit_"] .stButton, [class*="st-key-hit_"] .stButton button { width:100%; height:100%; min-height:0; }
[class*="st-key-hit_"] .stButton button { opacity:0; padding:0; border:0; cursor:pointer; }
[class*="st-key-hit_"] .stButton button:focus-visible { opacity:.08; }
.idx-row { display:grid; grid-template-columns:3.4rem 1fr 9.5rem 8.5rem; gap:1.2rem; align-items:center;
  padding:1.15rem .2rem 1.15rem 0; border-bottom:1px solid var(--hair); transition:background .2s ease, padding .2s ease; }
[class*="st-key-hit_"]:hover .idx-row { background:var(--card); padding-left:.8rem; }
.idx-num { font-family:var(--mono); font-size:.85rem; color:var(--ink3); align-self:start; padding-top:.45rem; }
.idx-name { font-family:var(--serif); font-size:1.65rem; font-weight:600; letter-spacing:-.025em; line-height:1.1; color:var(--ink);
  display:flex; align-items:center; gap:.55rem; }
.idx-name i { width:.55rem; height:.55rem; border-radius:50%; display:inline-block; flex:none; }
.idx-desc { color:var(--ink2); font-size:.92rem; margin-top:.25rem; font-family:var(--serif); font-style:italic; }
.idx-prog { font-family:var(--mono); font-size:.76rem; color:var(--ink2); }
.bar { height:3px; background:var(--hair); margin-top:.4rem; }
.bar > div { height:100%; background:var(--ink); }
.idx-due { text-align:right; }
.idx-due b { display:block; font-family:var(--serif); font-size:1.25rem; font-weight:600; color:var(--ink); }
.tag { font-family:var(--mono); font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; padding:.12rem .4rem; border:1px solid currentColor; white-space:nowrap; }
.tag.late { color:var(--late); } .tag.soon { color:var(--soon); } .tag.ok { color:var(--ok); } .tag.done { color:var(--ink3); }
.empty { font-family:var(--serif); font-style:italic; font-size:1.1rem; color:var(--ink2); padding:2.2rem 0; text-align:center; border-bottom:1px solid var(--hair); }

/* ---------- Colonne « À faire pour toi » ---------- */
.st-key-aside { background:var(--card); border:1px solid var(--rule); padding:1.1rem 1.1rem .6rem; }
.st-key-aside .h-small { margin-top:0; }
[class*="st-key-mine_"] { border-bottom:1px solid var(--hair); padding:.35rem 0 .45rem; }
[class*="st-key-mine_"] [data-testid="stHorizontalBlock"] { gap:.4rem; align-items:flex-start; }
.mine-t { font-weight:600; font-size:.93rem; line-height:1.3; color:var(--ink); }
.mine-m { font-family:var(--mono); font-size:.7rem; color:var(--ink2); margin-top:.2rem; display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }

/* ---------- Vue projet ---------- */
.crumb { font-family:var(--mono); font-size:.75rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink2); }
.st-key-back .stButton button { border:0; padding:0; min-height:0; background:transparent !important; color:var(--ink2) !important; }
.st-key-back .stButton button p { font-family:var(--mono); font-size:.75rem; letter-spacing:.06em; text-transform:uppercase; }
.st-key-back .stButton button:hover p { color:var(--accent) !important; }
.ph-title { font-family:var(--serif); font-weight:800; font-size:clamp(2.4rem, 6vw, 4.2rem); letter-spacing:-.045em; line-height:.95; margin:.6rem 0 .5rem; color:var(--ink); }
.ph-desc { font-family:var(--serif); font-style:italic; font-size:1.2rem; color:var(--ink2); max-width:46rem; margin-bottom:1.2rem; }
.facts { display:grid; grid-template-columns:repeat(4, 1fr); border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); margin-bottom:1.1rem; }
.facts > div { padding:.8rem 1rem .8rem 0; border-right:1px solid var(--hair); }
.facts > div + div { padding-left:1rem; }
.facts > div:last-child { border-right:0; }
.facts small { display:block; font-family:var(--mono); font-size:.68rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink3); margin-bottom:.25rem; }
.facts b { font-family:var(--serif); font-size:1.35rem; font-weight:600; color:var(--ink); }
.facts .who { font-size:.95rem; font-family:var(--sans); font-weight:500; line-height:1.5; }

/* ---------- Tableau des tâches ---------- */
[class*="st-key-thead"] { border-bottom:1px solid var(--rule); padding:.2rem 0; }
[class*="st-key-thead"] [data-testid="stHorizontalBlock"] { gap:.6rem; }
.thead { font-family:var(--mono); font-size:.68rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink3); }
button[data-testid="stPopoverButton"] > div:last-child { display:none; }
[class*="st-key-task_"] { border-bottom:1px solid var(--hair); padding:.25rem 0; transition:background .15s ease; }
[class*="st-key-task_"]:hover { background:var(--card); }
[class*="st-key-task_"] [data-testid="stHorizontalBlock"] { gap:.6rem; }
[class*="st-key-task_late_"] .t-title::before { content:"● "; color:var(--late); font-size:.7rem; vertical-align:middle; }
.t-title { font-weight:600; color:var(--ink); font-size:1rem; line-height:1.3; }
.t-title.done { text-decoration:line-through; text-decoration-color:var(--accent); color:var(--ink3); }
.t-sub { font-family:var(--mono); font-size:.68rem; color:var(--ink3); margin-top:.1rem; }
.t-owner { font-size:.88rem; color:var(--ink2); display:flex; align-items:center; gap:.4rem; }
.ini { width:1.45rem; height:1.45rem; border-radius:50%; border:1px solid var(--rule); display:inline-flex; align-items:center;
  justify-content:center; font-family:var(--mono); font-size:.68rem; color:var(--ink); background:var(--paper); flex:none; }
.t-due { font-family:var(--mono); font-size:.78rem; color:var(--ink); display:flex; flex-direction:column; gap:.2rem; align-items:flex-start; }
.t-dur { font-family:var(--mono); font-size:.78rem; color:var(--ink2); }
[class*="st-key-task_"] label[data-baseweb="checkbox"] > span:first-child,
[class*="st-key-mine_"] label[data-baseweb="checkbox"] > span:first-child { border-radius:0 !important; border:1.5px solid var(--ink) !important; width:1.15rem; height:1.15rem; }
[class*="st-key-task_"] button[data-testid="stPopoverButton"] { border:0; background:transparent; min-height:2rem; padding:0 .4rem; box-shadow:none; }
[class*="st-key-task_"] button[data-testid="stPopoverButton"]:hover { background:var(--ink); color:var(--paper); }

/* ---------- Planning ---------- */
.kpis { display:grid; grid-template-columns:repeat(3, 1fr); border-top:3px double var(--rule); border-bottom:1px solid var(--rule); margin:.4rem 0 1.4rem; }
.kpis > div { padding:1rem 1.2rem 1rem 0; border-right:1px solid var(--hair); }
.kpis > div + div { padding-left:1.2rem; }
.kpis > div:last-child { border-right:0; }
.kpis small { font-family:var(--mono); font-size:.7rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink3); }
.kpis b { display:block; font-family:var(--serif); font-size:clamp(2rem, 5vw, 3.2rem); font-weight:600; letter-spacing:-.04em; line-height:1; margin-top:.3rem; color:var(--ink); }
.st-key-period [data-testid="stHorizontalBlock"] { align-items:center; }
.st-key-period .stButton button { min-height:2.2rem; }
.period-label { font-family:var(--serif); font-size:1.5rem; font-weight:600; text-align:center; letter-spacing:-.02em; color:var(--ink); }
.legend { font-family:var(--mono); font-size:.72rem; color:var(--ink2); text-transform:uppercase; letter-spacing:.06em; margin:.2rem 0 .6rem; }
.legend i { display:inline-block; width:.7rem; height:.7rem; vertical-align:-1px; margin:0 .3rem 0 1rem; }
.legend i.o { background:var(--ink); } .legend i.d { background:repeating-linear-gradient(45deg, var(--ink3) 0 2px, transparent 2px 4px); border:1px solid var(--ink3); }
.st-key-week [data-testid="stHorizontalBlock"] { gap:0 !important; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); }
.st-key-week [data-testid="stColumn"] { border-right:1px solid var(--hair); padding:0 .35rem; }
.st-key-week [data-testid="stColumn"]:last-child { border-right:0; }
.wday { height:150px; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; padding:.6rem 0 .3rem; }
.wday.sel { background:var(--card); }
.wday .tot { font-family:var(--mono); font-size:.72rem; color:var(--ink); margin-bottom:.35rem; }
.wday .col { width:16px; height:96px; display:flex; flex-direction:column; justify-content:flex-end; border-bottom:1px solid var(--ink); }
.wday .col .o { background:var(--ink); } .wday .col .d { background:repeating-linear-gradient(45deg, var(--ink3) 0 2px, transparent 2px 4px); }
.wday .dt { font-family:var(--mono); font-size:.7rem; color:var(--ink2); margin-top:.4rem; }
.wday.today .dt { color:var(--accent); font-weight:600; }
.st-key-week .stButton button { border:0; min-height:2rem; background:transparent; }
.st-key-week .stButton button p { font-family:var(--serif); font-size:1rem; }
.st-key-week .stButton button[data-testid="stBaseButton-primary"] { background:var(--ink); color:var(--paper); }
.st-key-week .stButton button[data-testid="stBaseButton-primary"] p { color:var(--paper); }
.st-key-month [data-testid="stHorizontalBlock"] { gap:0 !important; }
.st-key-month [data-testid="stColumn"] { border-right:1px solid var(--hair); border-bottom:1px solid var(--hair); }
.mhead { font-family:var(--mono); font-size:.68rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink3); padding:.3rem .4rem; border-bottom:1px solid var(--rule); }
[class*="st-key-mcell_"] { min-height:78px; padding:.35rem .45rem; }
.mc b { font-family:var(--serif); font-size:1.05rem; font-weight:600; color:var(--ink); }
.mc span { display:block; font-family:var(--mono); font-size:.66rem; color:var(--ink2); margin-top:.2rem; }
.mc .ink { height:3px; background:var(--ink); margin-top:.3rem; }
.mc.out { opacity:.3; } .mc.today b { color:var(--accent); }
[class*="st-key-mcell_sel_"] { background:var(--card); box-shadow:inset 0 0 0 2px var(--ink); }

/* ---------- Réglages ---------- */
[class*="st-key-panel_"] { border:1px solid var(--rule); padding:1.1rem 1.2rem 1rem; background:var(--card); height:100%; }
.panel-t { font-family:var(--serif); font-size:1.35rem; font-weight:600; letter-spacing:-.02em; margin-bottom:.4rem; color:var(--ink); }
.status { font-family:var(--mono); font-size:.8rem; color:var(--ok); margin:.2rem 0 .6rem; }

/* ---------- Dialogues ---------- */
[data-testid="stDialog"] div[role="dialog"] { background:var(--paper); border:1px solid var(--rule); border-radius:0; box-shadow:12px 12px 0 rgba(28,27,25,.9); }
[data-testid="stDialog"] h2, [data-testid="stDialog"] [data-testid="stMarkdownContainer"] h2 { font-family:var(--serif) !important; font-weight:600; letter-spacing:-.03em; }
.dialog-intro { font-family:var(--mono); font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink);
  border-bottom:1px solid var(--rule); padding:.3rem 0; margin:1rem 0 .4rem; }
.dialog-intro b { color:var(--accent); margin-right:.6rem; }
.stTextInput input, .stTextArea textarea, .stDateInput input, [data-baseweb="select"] > div { border-radius:0 !important; }
[data-testid="stForm"] { border:0; padding:0; }
[data-testid="stPopoverBody"] { border-radius:0; border:1px solid var(--rule); }

/* ---------- Écran de connexion ---------- */
.login { max-width:40rem; margin:6vh auto 1.5rem; text-align:left; }
.login .mast-title { font-size:clamp(3.4rem, 12vw, 7rem); }
.login p { font-family:var(--serif); font-style:italic; font-size:1.3rem; color:var(--ink2); }

/* ---------- Responsive ---------- */
@media (max-width: 900px) {
  .block-container { padding:3.4rem 1rem 3rem; }
  .idx-row { grid-template-columns:2.2rem 1fr; }
  .idx-prog, .idx-due { grid-column:2; text-align:left; }
  .idx-due b { display:inline; margin-right:.5rem; }
  .facts, .kpis { grid-template-columns:1fr 1fr; }
  .facts > div:nth-child(2) { border-right:0; }
  .facts > div:nth-child(3) { padding-left:0; border-top:1px solid var(--hair); }
  .facts > div:nth-child(4) { border-top:1px solid var(--hair); }
  .kpis > div:nth-child(3) { padding-left:0; grid-column:1 / -1; border-top:1px solid var(--hair); }
  [class*="st-key-thead"] { display:none; }
  .st-key-nav .stButton button p { font-size:1.1rem !important; }
  .st-key-nav [data-testid="stHorizontalBlock"] { gap:1.1rem !important; }
}
@media (max-width: 640px) {
  [class*="st-key-task_"] [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; row-gap:.1rem !important; }
  [class*="st-key-task_"] [data-testid="stColumn"] { min-width:0 !important; width:auto !important; flex:0 0 auto !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:nth-child(1) { flex:0 0 1.8rem !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:nth-child(2) { flex:1 1 calc(100% - 2.6rem) !important; }
  [class*="st-key-task_"] [data-testid="stColumn"]:nth-child(3) { margin-left:2.4rem; }
  [class*="st-key-task_"] [data-testid="stColumn"]:nth-child(6) { margin-left:auto; }
  .t-due { flex-direction:row; align-items:center; gap:.4rem; }
  [class*="st-key-mine_"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
  [class*="st-key-mine_"] [data-testid="stColumn"] { min-width:0 !important; }
  [class*="st-key-mine_"] [data-testid="stColumn"]:first-child { flex:0 0 1.8rem !important; }
  .mast-top { flex-direction:column; align-items:flex-start; gap:.2rem; }
  .st-key-week [data-testid="stHorizontalBlock"], .st-key-month [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
  .st-key-week [data-testid="stColumn"], .st-key-month [data-testid="stColumn"] { min-width:0 !important; width:auto !important; flex:1 1 0 !important; padding:0 .1rem; }
  .wday { height:120px; } .wday .col { height:70px; width:10px; } .wday .tot { font-size:.58rem; }
  .st-key-week .stButton button p { font-size:.75rem; }
  [class*="st-key-mcell_"] { min-height:54px; padding:.2rem; }
  .mc span { display:none; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ---------- Éléments communs ----------
def masthead_top():
    left, right = st.columns([5, 1], vertical_alignment="bottom")
    left.markdown(
        f'<div class="mast-top"><span>{esc(c.fmt_long(date.today()).capitalize())} {date.today().year}</span>'
        f'<span>{esc(tr(c.TAGLINE))}</span></div>',
        unsafe_allow_html=True)
    with right:
        c.language_switch()


def hero(text):
    masthead_top()
    st.markdown(f'<div class="login"><div class="mast-title">anti <em>gooner</em></div><p>{text}</p></div>',
                unsafe_allow_html=True)


c.auth_gate(hero)
cal_row, cal_err = c.bootstrap()

st.session_state.setdefault("page", "projects")


def go(page):
    st.session_state.page = page
    if page != "projects":
        st.session_state.open = None


def tag(d, done=False):
    cls, txt = c.due_info(d, done)
    return f'<span class="tag {cls}">{esc(txt)}</span>'


def masthead():
    masthead_top()
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    st.markdown('<div class="mast-title">anti <em>gooner</em></div>'
                f'<div class="mast-sub">{esc(tr(c.TAGLINE))}</div>',
                unsafe_allow_html=True)
    sync_txt = "Google Calendar ✓" if cal_row else tr("Google Calendar non connecté.")
    st.markdown(
        '<div class="mast-strip">'
        f'<span><b>{c.pl(len(st.session_state.projects), "projet", "projets")}</b></span>'
        f'<span><b>{c.pl(c.open_count(), "tâche à faire", "tâches à faire")}</b></span>'
        f'<span>{esc(tr("Cette semaine"))} · <b>{c.format_duration(summary["week"]) if summary["week"] else "—"}</b></span>'
        f'<span>{esc(sync_txt)}</span></div>', unsafe_allow_html=True)
    with st.container(key="nav"):
        cols = st.columns([1, 1, 1, 6])
        for col, (pid, label) in zip(cols, [("projects", "Projets"), ("planning", "Planning"), ("settings", "Réglages")]):
            col.button(tr(label), key=f"nav_{pid}", on_click=go, args=(pid,),
                       type="primary" if st.session_state.page == pid else "secondary")


# ---------- Ligne de tâche (vue projet et planning) ----------
def task_row(p, t, suffix="", show_project=False):
    s = f"_{suffix}" if suffix else ""
    with st.container(key=f"task_{c.task_status(t)}_{t['id']}{s}"):
        col = st.columns(TASK_COLS, vertical_alignment="center")
        with col[0]:
            c.task_checkbox(p, t, s)
        sub = esc(p["name"]) if show_project else ""
        if t["done"] and t.get("by"):
            sub += (" · " if sub else "") + f'{esc(tr("fait par"))} {esc(t["by"])}'
        col[1].markdown(f'<div class="t-title{" done" if t["done"] else ""}">{esc(t["title"])}</div>'
                        + (f'<div class="t-sub">{sub}</div>' if sub else ""), unsafe_allow_html=True)
        col[2].markdown(f'<div class="t-owner"><span class="ini">{esc(c.owner_initial(t["owner"]))}</span>{esc(tr(t["owner"]))}</div>',
                        unsafe_allow_html=True)
        col[3].markdown(f'<div class="t-due">{c.parse(t["due"]):%d.%m.%Y}{tag(t["due"], t["done"])}</div>', unsafe_allow_html=True)
        col[4].markdown(f'<div class="t-dur">{c.format_duration(t.get("duration_minutes", 60))}</div>', unsafe_allow_html=True)
        with col[5].popover("⋯"):
            c.task_menu(p, t, s)


TASK_COLS = [0.35, 4, 1.5, 1.5, 0.8, 0.45]


def task_head(key):
    with st.container(key=key):
        cols = st.columns(TASK_COLS)
        for col, label in zip(cols[1:5], ("Tâche", "Responsable", "Deadline", "Durée")):
            col.markdown(f'<div class="thead">{tr(label)}</div>', unsafe_allow_html=True)


# ---------- Page Projets ----------
def board():
    projects = c.sorted_projects()
    left, right = st.columns([2.15, 1], gap="large")
    with left:
        h1, h2 = st.columns([3, 1.3], vertical_alignment="bottom")
        h1.markdown(f'<p class="kicker">{tr("Projets")} — {len(projects):02d}</p>'
                    f'<div class="h-sec">{tr("Index")} <em>{tr("des projets")}</em></div>', unsafe_allow_html=True)
        if h2.button("＋ " + tr("Nouveau projet"), type="primary", use_container_width=True, key="add_project"):
            c.open_new_project()
        st.markdown('<div style="border-top:1px solid var(--rule)"></div>', unsafe_allow_html=True)
        if not projects:
            st.markdown(f'<div class="empty">{tr(c.NO_PROJECT)}</div>', unsafe_allow_html=True)
        for i, p in enumerate(projects, 1):
            done, total = c.progress(p)
            with st.container(key=f"hit_{p['id']}"):
                st.markdown(
                    f'<div class="idx-row"><div class="idx-num">{i:02d}</div>'
                    f'<div><div class="idx-name"><i style="background:{p["color"]}"></i>{esc(p["name"])}</div>'
                    + (f'<div class="idx-desc">{esc(p["desc"])}</div>' if p.get("desc") else "")
                    + f'</div><div class="idx-prog">{tr("{done}/{total} tâches").format(done=done, total=total)} · {c.pct(p)}%'
                    f'<div class="bar"><div style="width:{c.pct(p)}%"></div></div></div>'
                    f'<div class="idx-due"><b>{esc(c.fmt_short(c.parse(p["due"])))}</b>{tag(p["due"], c.project_finished(p))}</div></div>',
                    unsafe_allow_html=True)
                st.button(tr("Ouvrir") + " " + p["name"], key=f"open_{p['id']}", on_click=c.set_open, args=(p["id"],))
    with right, st.container(key="aside"):
        mine_all = c.my_open_tasks()
        st.markdown(f'<div class="h-small">{tr("Mes tâches")}<span>{len(mine_all)}</span></div>', unsafe_allow_html=True)
        if not mine_all:
            st.markdown(f'<div class="mine-m" style="padding:.6rem 0 1rem">{tr("Tout est à jour.")}</div>', unsafe_allow_html=True)
        for p, t in mine_all[:10]:
            with st.container(key=f"mine_{t['id']}"):
                a, b = st.columns([0.12, 1])
                with a:
                    c.task_checkbox(p, t, "_mine")
                b.markdown(f'<div class="mine-t">{esc(t["title"])}</div><div class="mine-m"><span>{esc(p["name"])}</span>'
                           f'{tag(t["due"])}</div>', unsafe_allow_html=True)
        if len(mine_all) > 10:
            st.caption(tr("+ {n} autres tâches").format(n=len(mine_all) - 10))


# ---------- Vue projet ----------
def project_view(p):
    done, total = c.progress(p)
    with st.container(key="back"):
        st.button("← " + tr("Index des projets"), on_click=c.set_open, args=(None,))
    st.markdown(f'<div class="ph-title">{esc(p["name"])}</div>'
                + (f'<div class="ph-desc">{esc(p["desc"])}</div>' if p.get("desc") else ""), unsafe_allow_html=True)
    members = ", ".join(esc(m) for m in p["members"])
    st.markdown(
        '<div class="facts">'
        f'<div><small>{tr("Deadline")}</small><b>{c.parse(p["due"]):%d.%m.%Y}</b> {tag(p["due"], c.project_finished(p))}</div>'
        f'<div><small>{tr("Avancement")}</small><b>{c.pct(p)}%</b><div class="bar"><div style="width:{c.pct(p)}%"></div></div></div>'
        f'<div><small>{tr("Tâches")}</small><b>{done}/{total}</b></div>'
        f'<div><small>{tr("Membres")}</small><span class="who">{members}</span></div></div>', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns([1.2, 1.1, 0.9, 1.8])
    if a1.button("＋ " + tr("Nouvelle tâche"), type="primary", use_container_width=True, key="add_task"):
        c.open_new_task(p["id"])
    if a2.button(tr("Gérer le projet"), use_container_width=True, key=f"manage_{p['id']}"):
        c.open_edit_project(p["id"])
    if c.is_owner(p) and a3.button(tr("Supprimer"), use_container_width=True, key="del_project"):
        c.open_confirm_delete(p["id"])
    with a4:
        c.ics_button(p)
    todo = sorted((t for t in p["tasks"] if not t["done"]), key=lambda t: t["due"])
    finished = sorted((t for t in p["tasks"] if t["done"]), key=lambda t: t["due"])
    if not p["tasks"]:
        st.markdown(f'<div class="empty">{tr("Pas encore de tâche. Ajoute la première avec sa deadline.")}</div>', unsafe_allow_html=True)
        return
    for i, (label, items) in enumerate(((tr("À faire"), todo), (tr("Terminées"), finished))):
        if items:
            st.markdown(f'<div class="h-small">{label}<span>{len(items)}</span></div>', unsafe_allow_html=True)
            task_head(f"thead{i}")
            for t in items:
                task_row(p, t)


# ---------- Planning ----------
def item_row(item, suffix):
    p, t = c.find_task(item)
    if t:
        task_row(p, t, suffix, show_project=True)


def planning():
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    st.markdown(f'<p class="kicker">{tr("Charge basée sur les deadlines")}</p>'
                f'<div class="h-sec">{tr("Charge de travail")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpis">'
                f'<div><small>{tr("Heures restantes")}</small><b>{c.format_duration(summary["total"])}</b></div>'
                f'<div><small>{tr(c.TODAY)}</small><b>{c.format_duration(summary["today"]) if summary["today"] else "—"}</b></div>'
                f'<div><small>{tr("Cette semaine")}</small><b>{c.format_duration(summary["week"]) if summary["week"] else "—"}</b></div></div>',
                unsafe_allow_html=True)
    view, start, end, days, sel_key = c.workload_period()
    with st.container(key="period"):
        v1, v2, sp, prev, lab, nxt = st.columns([1, 1, 0.4, 0.5, 3, 0.5])
        v1.button(tr("Semaine"), key="pw", on_click=c.set_period, args=("Semaine",), use_container_width=True,
                  type="primary" if view == "Semaine" else "secondary")
        v2.button(tr("Mois"), key="pm", on_click=c.set_period, args=("Mois",), use_container_width=True,
                  type="primary" if view == "Mois" else "secondary")
        prev.button("‹", key="pprev", on_click=c.shift_period, args=(-1,), use_container_width=True,
                    help=tr("Semaine précédente" if view == "Semaine" else "Mois précédent"))
        lab.markdown(f'<div class="period-label">{esc(c.period_label(view, start, end))}</div>', unsafe_allow_html=True)
        nxt.button("›", key="pnext", on_click=c.shift_period, args=(1,), use_container_width=True,
                   help=tr("Semaine suivante" if view == "Semaine" else "Mois suivant"))
    period = [x for x in rows if start <= x["date"] <= end]
    o = sum(x["minutes"] for x in period if not x["done"])
    d = sum(x["minutes"] for x in period if x["done"])
    st.markdown(f'<div class="legend"><i class="o"></i>{tr("Ouvertes")} {c.format_duration(o) if o else "—"}'
                f'<i class="d"></i>{tr("Terminées")} {c.format_duration(d) if d else "—"}</div>', unsafe_allow_html=True)
    selected = st.session_state[sel_key]
    names = c.DAY_NAMES[c.lang()]
    today = date.today()
    if view == "Semaine":
        peak = max([sum(c.day_load(rows, day)) for day in days] + [60])
        with st.container(key="week"):
            cols = st.columns(7)
            for i, (col, day) in enumerate(zip(cols, days)):
                op, fi = c.day_load(rows, day)
                with col:
                    st.markdown(
                        f'<div class="wday{" sel" if day == selected else ""}{" today" if day == today else ""}">'
                        f'<div class="tot">{c.format_duration(op + fi) if op + fi else "·"}</div>'
                        f'<div class="col"><div class="d" style="height:{fi / peak * 100:.0f}%"></div>'
                        f'<div class="o" style="height:{op / peak * 100:.0f}%"></div></div>'
                        f'<div class="dt">{day:%d.%m}</div></div>', unsafe_allow_html=True)
                    st.button(names[i], key=f"wd_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day),
                              use_container_width=True, type="primary" if day == selected else "secondary")
    else:
        with st.container(key="month"):
            head = st.columns(7)
            for col, n in zip(head, names):
                col.markdown(f'<div class="mhead">{n}</div>', unsafe_allow_html=True)
            for w in range(0, len(days), 7):
                cols = st.columns(7)
                for col, day in zip(cols, days[w:w + 7]):
                    op, fi = c.day_load(rows, day)
                    state = "sel_" if day == selected else ""
                    with col, st.container(key=f"mcell_{state}{day.isoformat()}"):
                        with st.container(key=f"hit_m{day.isoformat()}"):
                            st.markdown(
                                f'<div class="mc{" out" if day.month != start.month else ""}{" today" if day == today else ""}">'
                                f'<b>{day.day}</b><span>{c.format_duration(op + fi) if op + fi else "&nbsp;"}</span>'
                                f'<div class="ink" style="width:{min(100, (op + fi) / 480 * 100):.0f}%"></div></div>',
                                unsafe_allow_html=True)
                            st.button(f"{day:%d/%m}", key=f"md_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day))
    sel_rows = sorted((x for x in rows if x["date"] == selected), key=lambda x: (x["done"], x["project"], x["title"]))
    st.markdown(f'<div class="h-small">{esc(c.fmt_long(selected).capitalize())}<span>{c.pl(len(sel_rows), "tâche", "tâches")}</span></div>',
                unsafe_allow_html=True)
    if sel_rows:
        for item in sel_rows:
            item_row(item, f"sel_{view}")
    else:
        st.caption(tr("Aucune tâche avec une échéance ce jour-là."))
    upcoming = sorted((x for x in rows if not x["done"] and x["date"] >= today), key=lambda x: (x["date"], x["project"]))
    st.markdown(f'<div class="h-small">{tr("Tâches ouvertes")}<span>{len(upcoming)}</span></div>', unsafe_allow_html=True)
    for item in upcoming[:30]:
        item_row(item, "up")
    if not upcoming:
        st.caption(tr("Aucune tâche ouverte à venir."))
    completed = sorted((x for x in rows if x["done"]), key=lambda x: (x["date"], x["project"]))
    st.markdown(f'<div class="h-small">{tr("Tâches terminées")}<span>{len(completed)}</span></div>', unsafe_allow_html=True)
    for item in completed[:30]:
        item_row(item, "done")
    if not completed:
        st.caption(tr("Aucune tâche terminée pour le moment."))


# ---------- Réglages ----------
def settings():
    st.markdown(f'<p class="kicker">{tr("Compte")} · Google Calendar · {tr("Sauvegarde")}</p>'
                f'<div class="h-sec">{tr("Réglages")}</div>', unsafe_allow_html=True)
    a, b, d = st.columns(3, gap="medium")
    with a, st.container(key="panel_account"):
        st.markdown(f'<div class="panel-t">{tr("Compte")}</div>'
                    f'<div class="status">● {esc(tr("Connecté : {name}").format(name=c.me()["name"]))}</div>', unsafe_allow_html=True)
        st.button(tr("Se déconnecter"), key="logout", on_click=st.logout, use_container_width=True)
    with b, st.container(key="panel_calendar"):
        st.markdown('<div class="panel-t">Google Calendar</div>', unsafe_allow_html=True)
        c.calendar_panel(cal_row, cal_err, link_style=(
            "display:block;text-align:center;padding:.6rem;background:#D9481E;color:#fff;"
            "font-family:sans-serif;font-weight:600;text-decoration:none"))
    with d, st.container(key="panel_backup"):
        st.markdown(f'<div class="panel-t">{tr("Sauvegarde")}</div>', unsafe_allow_html=True)
        st.caption("JSON · " + c.pl(len(st.session_state.projects), "projet", "projets"))
        c.export_button()


# ---------- Rendu ----------
masthead()
if cal_row and st.session_state.page != "settings":
    _, sync_col = st.columns([4, 1.3])
    if sync_col.button("↻ " + tr("Synchroniser Google Calendar"), key="calendar_sync_main", use_container_width=True):
        c.run_sync(tr("Calendrier synchronisé"))
if st.session_state.page == "planning":
    planning()
elif st.session_state.page == "settings":
    settings()
else:
    current = c.get_project(st.session_state.open) if st.session_state.open else None
    if current:
        project_view(current)
    else:
        board()
