"""anti gooner — Version 3 « Bento ».

DA : douce et ludique. Fond pervenche, cartes blanches très arrondies, tuiles pastel,
typographie ronde (Outfit + Plus Jakarta Sans), dégradé corail → violet en accent.
UX : un tableau de bord « Accueil » en grille bento (focus du jour cochable, heures
du jour/semaine, mini-graphe de la semaine, projets en anneaux, statut Calendar),
une barre d'onglets flottante (Accueil · Projets · Planning · Compte) et une vue projet
à deux colonnes « À faire / Terminées ».
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st  # noqa: E402

import core as c  # noqa: E402
from core import esc, tr  # noqa: E402

c.apply_theme(base="light", primaryColor="#6C4DFF", backgroundColor="#EDEFFA",
              secondaryBackgroundColor="#FFFFFF", textColor="#20223A")
st.set_page_config(page_title="anti gooner", page_icon="🍱", layout="wide", initial_sidebar_state="collapsed")
c.init_backend()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
[data-testid="stMarkdownContainer"]:not(:has(> p)) { margin-bottom:0 !important; }
:root {
  --bg:#EDEFFA; --card:#FFFFFF; --ink:#20223A; --muted:#6B6F8E; --soft:#F5F6FD; --line:rgba(32,34,58,.08);
  --violet:#6C4DFF; --coral:#FF7A59; --grad:linear-gradient(120deg, #FF7A59, #C04CFD 55%, #6C4DFF);
  --mint:#D7F5E8; --mint-i:#127A55; --peach:#FFE4D6; --peach-i:#B4441D; --lilac:#E7E1FF; --lilac-i:#4A33C9;
  --butter:#FFF1C4; --butter-i:#8A6200; --sky:#DCEBFF; --sky-i:#1D5CB8; --rose:#FFE0E6; --rose-i:#B3264A;
  --r:28px; --shadow:0 1px 2px rgba(32,34,58,.04), 0 12px 32px -12px rgba(32,34,58,.14);
  --head:'Outfit', system-ui, sans-serif; --body:'Plus Jakarta Sans', system-ui, sans-serif;
}
.stApp { background:radial-gradient(1100px 600px at 100% -10%, rgba(192,76,253,.16), transparent 60%),
  radial-gradient(900px 500px at -10% 10%, rgba(255,122,89,.14), transparent 60%), var(--bg); background-attachment:fixed; }
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp li { font-family:var(--body); color:var(--ink); }
#MainMenu, footer, [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] { display:none !important; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1200px; padding:3.6rem 1.6rem 5rem; }

/* ---------- Barre supérieure ---------- */
.st-key-topbar { position:relative; z-index:5; background:rgba(255,255,255,.78); backdrop-filter:blur(16px);
  border:1px solid rgba(255,255,255,.9); border-radius:999px; padding:.4rem .5rem .4rem 1.1rem; box-shadow:var(--shadow); margin-bottom:1.6rem; }
.st-key-topbar [data-testid="stHorizontalBlock"] { align-items:center; gap:.4rem; }
.logo { font-family:var(--head); font-weight:800; font-size:1.3rem; letter-spacing:-.03em; white-space:nowrap; }
.logo span { background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
[class*="st-key-tab_"] button { border:0 !important; background:transparent !important; border-radius:999px !important; min-height:2.5rem; box-shadow:none !important; }
[class*="st-key-tab_"] button p { font-weight:600 !important; color:var(--muted) !important; font-size:.92rem !important; white-space:nowrap; }
[class*="st-key-tab_"] button:hover { background:var(--soft) !important; }
[class*="st-key-tab_"] button[data-testid="stBaseButton-primary"] { background:var(--ink) !important; }
[class*="st-key-tab_"] button[data-testid="stBaseButton-primary"] p { color:#fff !important; }
.avatar-me { width:2.4rem; height:2.4rem; border-radius:50%; background:var(--grad); color:#fff; font-family:var(--head); font-weight:700;
  display:flex; align-items:center; justify-content:center; margin-left:auto; box-shadow:0 6px 16px -6px rgba(108,77,255,.6); }
.st-key-lang [role="radiogroup"] { gap:.2rem; background:var(--soft); border-radius:999px; padding:.2rem; justify-content:center; flex-wrap:nowrap; }
.st-key-lang label { border-radius:999px; padding:.15rem .6rem; margin:0; cursor:pointer; }
.st-key-lang label > div:first-child { display:none; }
.st-key-lang label p { font-size:.78rem !important; font-weight:700; color:var(--muted) !important; }
.st-key-lang label:has(input:checked) { background:#fff; box-shadow:0 2px 6px rgba(32,34,58,.12); }
.st-key-lang label:has(input:checked) p { color:var(--ink) !important; }

/* ---------- Boutons ---------- */
.stButton button, .stDownloadButton button, .stFormSubmitButton button { border-radius:999px; border:1px solid var(--line); background:#fff;
  min-height:2.6rem; box-shadow:0 1px 2px rgba(32,34,58,.05); transition:transform .18s ease, box-shadow .18s ease, background .18s ease; }
.stButton button p, .stDownloadButton button p, .stFormSubmitButton button p { font-weight:600; }
.stButton button:hover, .stDownloadButton button:hover { transform:translateY(-1px); box-shadow:0 8px 18px -10px rgba(32,34,58,.35); border-color:rgba(108,77,255,.35); background:#fff; }
.stButton button[data-testid="stBaseButton-primary"], .stFormSubmitButton button { background:var(--grad); border:0; color:#fff; box-shadow:0 10px 22px -10px rgba(108,77,255,.7); }
.stButton button[data-testid="stBaseButton-primary"] p, .stFormSubmitButton button p { color:#fff !important; }
.stButton button[data-testid="stBaseButton-primary"]:hover { filter:saturate(1.15) brightness(1.04); }
button:focus-visible { outline:3px solid rgba(108,77,255,.45) !important; outline-offset:2px; }
button[data-testid="stPopoverButton"] > div:last-child { display:none; }

/* ---------- Tuiles bento ---------- */
[class*="st-key-b_"] { background:var(--card); border-radius:var(--r); padding:1.25rem 1.35rem; box-shadow:var(--shadow); height:100%; border:1px solid rgba(255,255,255,.7); }
[class*="st-key-b_"][class*="_peach"] { background:var(--peach); } [class*="st-key-b_"][class*="_lilac"] { background:var(--lilac); }
[class*="st-key-b_"][class*="_mint"] { background:var(--mint); } [class*="st-key-b_"][class*="_butter"] { background:var(--butter); }
.st-key-bento [data-testid="stHorizontalBlock"] { gap:1rem; align-items:stretch; }
.st-key-bento [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { gap:1rem; height:100%; }
.hello { font-family:var(--head); font-weight:800; font-size:clamp(2.2rem, 5.5vw, 3.6rem); letter-spacing:-.04em; line-height:1; margin:.4rem 0 .3rem; }
.hello span { background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hello-sub { color:var(--muted); font-size:1.02rem; margin-bottom:1.2rem; }
.t-label { font-family:var(--head); font-weight:600; font-size:.95rem; color:var(--muted); display:flex; align-items:center; justify-content:space-between; gap:.5rem; }
.t-label .ic { width:2.2rem; height:2.2rem; border-radius:14px; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem; background:rgba(255,255,255,.7); }
.t-big { font-family:var(--head); font-weight:800; font-size:clamp(2.2rem, 4vw, 3rem); letter-spacing:-.04em; line-height:1; margin:.7rem 0 .2rem; }
.t-foot { font-size:.82rem; color:var(--muted); }
.spark { display:flex; align-items:flex-end; gap:6px; height:64px; margin-top:.9rem; }
.spark div { flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; height:100%; justify-content:flex-end; }
.spark i { display:block; width:100%; border-radius:8px; background:rgba(74,51,201,.25); min-height:4px; }
.spark div.today i { background:var(--lilac-i); }
.spark small { font-size:.62rem; color:var(--lilac-i); font-weight:700; }
.h-tile { font-family:var(--head); font-weight:700; font-size:1.25rem; letter-spacing:-.02em; display:flex; justify-content:space-between; align-items:center; margin-bottom:.4rem; }
.h-tile span { font-family:var(--body); font-size:.78rem; font-weight:700; background:var(--soft); color:var(--muted); padding:.2rem .6rem; border-radius:999px; }
.h-page { font-family:var(--head); font-weight:800; font-size:clamp(2rem, 4.5vw, 2.8rem); letter-spacing:-.04em; margin:.2rem 0 .2rem; }
.sub { color:var(--muted); margin-bottom:1rem; }

/* Pastilles d'échéance */
.pill { display:inline-flex; align-items:center; gap:.3rem; font-size:.74rem; font-weight:700; padding:.22rem .62rem; border-radius:999px; white-space:nowrap; }
.pill.late { background:var(--rose); color:var(--rose-i); } .pill.soon { background:var(--butter); color:var(--butter-i); }
.pill.ok { background:var(--mint); color:var(--mint-i); } .pill.done { background:var(--soft); color:var(--muted); }

/* Listes de tâches */
[class*="st-key-task_"], [class*="st-key-focus_"] { background:var(--soft); border-radius:20px; padding:.55rem .7rem .55rem .8rem; margin-bottom:.1rem;
  transition:background .15s ease, transform .15s ease; }
[class*="st-key-task_"]:hover, [class*="st-key-focus_"]:hover { background:#fff; transform:translateY(-1px); box-shadow:0 8px 20px -14px rgba(32,34,58,.35); }
[class*="st-key-task_"] [data-testid="stHorizontalBlock"], [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] { gap:.5rem; }
[class*="st-key-task_done_"] { opacity:.65; }
.tt { font-weight:700; font-size:.96rem; line-height:1.3; }
.tt.done { text-decoration:line-through; color:var(--muted); }
.tm { display:flex; flex-wrap:wrap; align-items:center; gap:.35rem .5rem; margin-top:.3rem; font-size:.78rem; color:var(--muted); }
.dotp { width:.55rem; height:.55rem; border-radius:50%; display:inline-block; }
.av { width:1.6rem; height:1.6rem; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:.72rem; font-weight:800; color:#fff; flex:none; border:2px solid #fff; }
.avs { display:flex; } .avs .av + .av { margin-left:-.45rem; }
label[data-baseweb="checkbox"] > span:first-child { border-radius:50% !important; width:1.35rem; height:1.35rem; }
[class*="st-key-task_"] button[data-testid="stPopoverButton"], [class*="st-key-focus_"] button[data-testid="stPopoverButton"] { min-height:2rem; padding:0 .6rem; background:#fff; border:1px solid var(--line); }

/* Projets (anneaux) */
[class*="st-key-hit_"] { position:relative; gap:0 !important; }
[class*="st-key-hit_"] [data-testid="stElementContainer"]:has(button) { position:absolute; inset:0; z-index:3; margin:0; width:100% !important; height:100%; }
[class*="st-key-hit_"] .stButton, [class*="st-key-hit_"] .stButton button { width:100%; height:100%; min-height:0; }
[class*="st-key-hit_"] .stButton button { opacity:0; padding:0; border:0; cursor:pointer; }
.ring-mini { display:flex; align-items:center; gap:.75rem; padding:.55rem .6rem; border-radius:20px; transition:background .15s ease; }
[class*="st-key-hit_"]:hover .ring-mini { background:var(--soft); }
.ring-mini b { display:block; font-size:.92rem; } .ring-mini small { color:var(--muted); font-size:.76rem; }
.pcard { background:#fff; border-radius:var(--r); overflow:hidden; box-shadow:var(--shadow); transition:transform .2s ease, box-shadow .2s ease; }
[class*="st-key-hit_"]:hover .pcard { transform:translateY(-4px); box-shadow:0 24px 44px -20px rgba(32,34,58,.35); }
.pcard-top { height:84px; position:relative; }
.pcard-top .ringwrap { position:absolute; right:1.1rem; bottom:-30px; background:#fff; border-radius:50%; padding:5px; box-shadow:0 8px 20px -10px rgba(32,34,58,.4); }
.pcard-body { padding:1rem 1.2rem 1.2rem; }
.pcard-n { font-family:var(--head); font-weight:700; font-size:1.3rem; letter-spacing:-.02em; padding-right:4.2rem; line-height:1.15; }
.pcard-d { color:var(--muted); font-size:.86rem; margin:.35rem 0 .9rem; min-height:2.4rem; }
.pcard-f { display:flex; align-items:center; justify-content:space-between; gap:.5rem; }
.st-key-add_tile button { min-height:218px; border:2px dashed rgba(108,77,255,.35) !important; background:rgba(255,255,255,.45) !important; border-radius:var(--r) !important; }
.st-key-add_tile button p { font-family:var(--head) !important; font-size:1.15rem !important; color:var(--violet) !important; }
.st-key-grid [data-testid="stHorizontalBlock"] { gap:1.2rem; }
.st-key-grid [data-testid="stVerticalBlock"] { gap:1.2rem; }

/* Vue projet */
.st-key-phero { border-radius:var(--r); padding:1.6rem 1.7rem; box-shadow:var(--shadow); position:relative; overflow:hidden; }
.ph { display:flex; gap:1.4rem; align-items:center; }
.ph-n { font-family:var(--head); font-weight:800; font-size:clamp(1.9rem, 4.5vw, 2.8rem); letter-spacing:-.04em; line-height:1.02; }
.ph-d { color:var(--muted); margin:.4rem 0 .8rem; max-width:40rem; }
.ph-m { display:flex; flex-wrap:wrap; gap:.5rem .9rem; align-items:center; font-size:.85rem; color:var(--muted); }
.st-key-back button { background:rgba(255,255,255,.6) !important; }
.st-key-cols [data-testid="stHorizontalBlock"] { gap:1.2rem; }
.colh { font-family:var(--head); font-weight:700; font-size:1.1rem; display:flex; align-items:center; gap:.5rem; margin:.2rem 0 .5rem; }
.colh span { background:#fff; border-radius:999px; font-size:.76rem; padding:.1rem .55rem; color:var(--muted); }
.empty { text-align:center; color:var(--muted); padding:2rem 1rem; border:2px dashed rgba(108,77,255,.25); border-radius:var(--r); background:rgba(255,255,255,.4); }

/* Planning */
.seg { display:flex; gap:.3rem; }
.st-key-seg [data-testid="stHorizontalBlock"] { gap:.4rem; align-items:center; }
.period { font-family:var(--head); font-weight:700; font-size:1.3rem; text-align:center; letter-spacing:-.02em; }
.legend { display:flex; gap:1rem; justify-content:center; font-size:.8rem; color:var(--muted); margin:.3rem 0 .6rem; }
.legend i { display:inline-block; width:.7rem; height:.7rem; border-radius:50%; margin-right:.35rem; vertical-align:-1px; }
.st-key-week [data-testid="stHorizontalBlock"] { gap:.55rem; }
.wk { background:#fff; border-radius:22px; height:168px; padding:.6rem .4rem .5rem; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; box-shadow:var(--shadow); }
.wk.sel { background:var(--ink); } .wk.sel .t, .wk.sel .dt { color:#fff; }
.wk .t { font-size:.72rem; font-weight:700; margin-bottom:.4rem; color:var(--ink); }
.wk .bar { width:26px; height:96px; border-radius:13px; background:var(--soft); overflow:hidden; display:flex; flex-direction:column; justify-content:flex-end; }
.wk.sel .bar { background:rgba(255,255,255,.12); }
.wk .bar .o { background:var(--grad); } .wk .bar .d { background:#7BD8B3; }
.wk .dt { font-size:.72rem; color:var(--muted); margin-top:.45rem; font-weight:600; }
.wk.today .dt::after { content:" •"; color:var(--coral); }
.st-key-week .stButton button { min-height:2.1rem; }
.mh { text-align:center; font-size:.74rem; font-weight:700; color:var(--muted); }
.st-key-month [data-testid="stHorizontalBlock"] { gap:.4rem; }
.st-key-month [data-testid="stVerticalBlock"] { gap:.4rem; }
.mc { background:#fff; border-radius:16px; height:70px; padding:.4rem .5rem; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 1px 2px rgba(32,34,58,.05); }
.mc b { font-size:.86rem; } .mc span { font-size:.66rem; color:var(--muted); font-weight:600; }
.mc .dots { display:flex; gap:3px; } .mc .dots i { width:6px; height:6px; border-radius:50%; background:var(--violet); }
.mc .dots i.d { background:#7BD8B3; }
.mc.out { opacity:.35; } .mc.sel { background:var(--ink); } .mc.sel b, .mc.sel span { color:#fff; }
.mc.today b { color:var(--coral); }

/* Dialogues */
[data-testid="stDialog"] div[role="dialog"] { border-radius:32px; border:0; box-shadow:0 30px 80px -20px rgba(32,34,58,.45); }
[data-testid="stDialog"] h2 { font-family:var(--head) !important; font-weight:800 !important; letter-spacing:-.03em; }
.dialog-intro { display:flex; align-items:center; gap:.6rem; font-family:var(--head); font-weight:700; font-size:1rem; margin:1rem 0 .3rem; }
.dialog-intro b { background:var(--lilac); color:var(--lilac-i); border-radius:10px; padding:.1rem .45rem; font-size:.78rem; }
.stTextInput input, .stTextArea textarea, .stDateInput input { border-radius:14px !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { border-radius:14px !important; }
[data-testid="stForm"] { border:0; padding:0; }
[data-testid="stPopoverBody"] { border-radius:20px; }

/* Compte */
.acc { display:flex; align-items:center; gap:1rem; }
.acc .avatar-me { width:3.4rem; height:3.4rem; font-size:1.4rem; margin:0; }
.acc b { font-family:var(--head); font-size:1.3rem; } .acc small { display:block; color:var(--mint-i); font-weight:600; }
.login { text-align:center; margin:12vh auto 1.4rem; max-width:34rem; }
.login .hello { font-size:clamp(3rem, 10vw, 5rem); }
.login p { color:var(--muted); font-size:1.1rem; }

@media (max-width: 1024px) {
  .st-key-grid [data-testid="stHorizontalBlock"], .st-key-bento [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
  .st-key-grid [data-testid="stColumn"] { flex:1 1 calc(50% - 1.2rem) !important; min-width:calc(50% - 1.2rem) !important; }
  .st-key-bento [data-testid="stColumn"] { flex:1 1 100% !important; min-width:100% !important; }
}
@media (max-width: 760px) {
  .block-container { padding:3.4rem .8rem 4rem; }
  .st-key-topbar { border-radius:26px; padding:.5rem; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
  .st-key-topbar { position:relative; top:0; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { row-gap:.3rem !important; }
  .st-key-topbar [data-testid="stColumn"] { min-width:0 !important; flex:1 1 22% !important; width:auto !important; }
  .st-key-topbar [data-testid="stColumn"]:first-child { flex:1 1 55% !important; padding-left:.6rem; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(6) { order:-1; flex:0 0 auto !important; }
  .st-key-topbar [data-testid="stColumn"]:first-child { order:-2; }
  .st-key-topbar [data-testid="stColumn"]:has(.avatar-me) { display:none; }
  [class*="st-key-tab_"] button { padding:0 .2rem !important; min-height:2.3rem; }
  .stApp [class*="st-key-task_"] [data-testid="stHorizontalBlock"], .stApp [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
  .stApp [class*="st-key-task_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .stApp [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width:0 !important; }
  .stApp [class*="st-key-task_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child, .stApp [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { flex:0 0 1.8rem !important; }
  .stApp [class*="st-key-task_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child, .stApp [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child { flex:0 0 2.6rem !important; }
  .stApp [class*="st-key-task_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2), .stApp [class*="st-key-focus_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) { flex:1 1 auto !important; width:auto !important; }
  .st-key-bento [data-testid="stColumn"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
  .st-key-bento [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width:0 !important; }
  [class*="st-key-tab_"] button p { font-size:.8rem !important; }
  .st-key-grid [data-testid="stColumn"], .st-key-cols [data-testid="stColumn"] { flex:1 1 100% !important; min-width:100% !important; }
  .st-key-week [data-testid="stHorizontalBlock"], .st-key-month [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:.2rem; }
  .st-key-week [data-testid="stColumn"], .st-key-month [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; }
  .wk { height:118px; border-radius:14px; } .wk .bar { height:60px; width:14px; } .wk .t { font-size:.56rem; }
  .st-key-week .stButton button p { font-size:.66rem !important; }
  .mc { height:48px; padding:.2rem; border-radius:10px; } .mc span { display:none; }
  .ph { flex-direction:column; align-items:flex-start; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

TINTS = {"#8B7BFF": ("#E7E1FF", "#6C4DFF"), "#FF8FA3": ("#FFE0E6", "#E5486B"), "#5CE1C6": ("#D7F5E8", "#14A37A"),
         "#FFC46B": ("#FFF1C4", "#D79500"), "#6BB6FF": ("#DCEBFF", "#2C7BE5"), "#C48BFF": ("#F0E3FF", "#9B4DE0")}


def tint(color):
    return TINTS.get(color, ("#E7E1FF", color))


def hero(text):
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        c.language_switch()
    st.markdown(f'<div class="login"><div class="hello">anti <span>gooner</span></div><p>{text}</p></div>', unsafe_allow_html=True)


c.auth_gate(hero)
cal_row, cal_err = c.bootstrap()
st.session_state.setdefault("page", "home")


def go(page):
    st.session_state.page = page
    st.session_state.open = None


def open_project(pid):
    st.session_state.page = "projects"
    st.session_state.open = pid


def pill(d, done=False):
    cls, txt = c.due_info(d, done)
    icon = {"late": "⏰", "soon": "⚡", "ok": "📅", "done": "✓"}[cls]
    return f'<span class="pill {cls}">{icon} {esc(txt)}</span>'


def avatar(name):
    col = c.owner_color(name)
    return f'<span class="av" style="background:{col}">{esc(c.owner_initial(name))}</span>'


def ring(p, size=56, stroke=6):
    pct = c.pct(p)
    light, strong = tint(p["color"])
    r = 18 - stroke / 2 * 36 / size
    circ = 2 * 3.14159 * r
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 36 36">'
            f'<circle cx="18" cy="18" r="{r:.2f}" fill="none" stroke="{light}" stroke-width="{stroke * 36 / size:.2f}"/>'
            + (f'<circle cx="18" cy="18" r="{r:.2f}" fill="none" stroke="{strong}" stroke-width="{stroke * 36 / size:.2f}" stroke-linecap="round" '
               f'stroke-dasharray="{circ * pct / 100:.2f} {circ:.2f}" transform="rotate(-90 18 18)"/>' if pct else "")
            + f'<text x="18" y="21" text-anchor="middle" font-size="9" font-weight="800" fill="#20223A" font-family="Outfit, sans-serif">{pct}%</text></svg>')


# ---------- Barre supérieure ----------
def topbar():
    with st.container(key="topbar"):
        cols = st.columns([1.6, 1, 1, 1, 1, 1.05, 0.4], vertical_alignment="center")
        cols[0].markdown('<div class="logo">anti <span>gooner</span></div>', unsafe_allow_html=True)
        for col, (pid, label) in zip(cols[1:5], [("home", "🏠 " + tr("Accueil")), ("projects", "📁 " + tr("Projets")),
                                                  ("planning", "📅 " + tr("Planning")), ("account", "⚙️ " + tr("Compte"))]):
            with col, st.container(key=f"tab_{pid}"):
                st.button(label, on_click=go, args=(pid,), use_container_width=True,
                          type="primary" if st.session_state.page == pid else "secondary")
        with cols[5]:
            c.language_switch()
        cols[6].markdown(f'<div class="avatar-me">{esc(c.me()["name"][:1].upper())}</div>', unsafe_allow_html=True)


# ---------- Tâches ----------
def task_tile(p, t, suffix="", show_project=True, key_prefix="task"):
    s = f"_{suffix}" if suffix else ""
    status = c.task_status(t)
    with st.container(key=f"{key_prefix}_{status}_{t['id']}{s}"):
        a, b, m = st.columns([0.12, 1, 0.16], vertical_alignment="center")
        with a:
            c.task_checkbox(p, t, s)
        proj = f'<span><i class="dotp" style="background:{tint(p["color"])[1]}"></i> {esc(p["name"])}</span>' if show_project else ""
        by = f'<span>✓ {tr("fait par")} {esc(t["by"])}</span>' if t["done"] and t.get("by") else ""
        b.markdown(f'<div class="tt{" done" if t["done"] else ""}">{c.star(t)}{esc(t["title"])}</div>'
                   f'<div class="tm">{proj}{avatar(t["owner"])}<span>{esc(tr(t["owner"]))}</span>'
                   f'<span>⏱ {c.format_duration(t.get("duration_minutes", 60))}</span>{pill(t["due"], t["done"])}{by}</div>',
                   unsafe_allow_html=True)
        with m.popover("⋯"):
            c.task_menu(p, t, s)


# ---------- Accueil (bento) ----------
def home():
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    mine_all = c.my_open_tasks()
    late = sum(1 for p, t in mine_all if c.task_status(t) == "late")
    st.markdown(f'<div class="hello">{esc(tr("Bonjour {name}").format(name=c.me()["name"]))} <span>👋</span></div>'
                f'<div class="hello-sub">{esc(c.fmt_long(date.today()).capitalize())} · {esc(tr(c.TAGLINE))}</div>', unsafe_allow_html=True)
    if cal_row:
        if st.button("📅 " + tr("Synchroniser Google Calendar"), key="calendar_sync_main"):
            c.run_sync(tr("Calendrier synchronisé"))
    elif not cal_err:
        st.info("📅 " + tr("Google Calendar non connecté.") + " → " + tr("Compte"))
    with st.container(key="bento"):
        left, right = st.columns([1.55, 1])
        with left, st.container(key="b_focus"):
            st.markdown(f'<div class="h-tile">🎯 {tr("Ton focus")}<span>{len(mine_all)}</span></div>', unsafe_allow_html=True)
            if not mine_all:
                st.markdown(f'<div class="t-foot" style="padding:1rem 0">{tr("Rien pour toi ici. Profite 🌿")}</div>', unsafe_allow_html=True)
            for p, t in mine_all[:10]:
                task_tile(p, t, "focus", key_prefix="focus")
            if len(mine_all) > 10:
                st.caption(tr("+ {n} autres tâches").format(n=len(mine_all) - 10))
        with right:
            a, b = st.columns(2)
            with a, st.container(key="b_today_peach"):
                st.markdown(f'<div class="t-label">{tr(c.TODAY)}<span class="ic">☀️</span></div>'
                            f'<div class="t-big">{c.format_duration(summary["today"]) if summary["today"] else "0 h"}</div>'
                            f'<div class="t-foot">{c.pl(sum(1 for x in rows if x["date"] == date.today() and not x["done"]), "tâche", "tâches")}</div>',
                            unsafe_allow_html=True)
            with b, st.container(key="b_left_mint"):
                st.markdown(f'<div class="t-label">{tr("Reste à faire")}<span class="ic">✅</span></div>'
                            f'<div class="t-big">{c.open_count()}</div>'
                            f'<div class="t-foot">{c.format_duration(summary["total"])} · {late} {tr("En retard").lower()}</div>',
                            unsafe_allow_html=True)
            today = date.today()
            monday = today - timedelta(days=today.weekday())
            week = [monday + timedelta(days=i) for i in range(7)]
            loads = [c.day_load(rows, d)[0] for d in week]
            peak = max(loads + [60])
            bars = "".join(f'<div class="{"today" if d == today else ""}"><i style="height:{max(6, v / peak * 100):.0f}%"></i>'
                           f'<small>{c.DAY_NAMES[c.lang()][i][0]}</small></div>' for i, (d, v) in enumerate(zip(week, loads)))
            with st.container(key="b_week_lilac"):
                st.markdown(f'<div class="t-label">{tr("Cette semaine")}<span class="ic">📈</span></div>'
                            f'<div class="t-big">{c.format_duration(summary["week"]) if summary["week"] else "0 h"}</div>'
                            f'<div class="spark">{bars}</div>', unsafe_allow_html=True)
            with st.container(key="b_projects"):
                projects = c.sorted_projects()
                st.markdown(f'<div class="h-tile">📁 {tr("Tes projets")}<span>{len(projects)}</span></div>', unsafe_allow_html=True)
                for p in projects[:5]:
                    done, total = c.progress(p)
                    with st.container(key=f"hit_h{p['id']}"):
                        st.markdown(f'<div class="ring-mini">{ring(p, 46, 5)}<div><b>{esc(p["name"])}</b>'
                                    f'<small>{tr("{done}/{total} tâches faites").format(done=done, total=total)}</small></div>'
                                    f'<div style="margin-left:auto">{pill(p["due"], c.project_finished(p))}</div></div>', unsafe_allow_html=True)
                        st.button(p["name"], key=f"home_go_{p['id']}", on_click=open_project, args=(p["id"],))
                if not projects:
                    st.caption(tr("L'avancement de chaque projet apparaîtra ici."))
                st.button(tr("Voir tout") + " →", key="see_all", on_click=go, args=("projects",), use_container_width=True)


# ---------- Projets ----------
def board():
    projects = c.sorted_projects()
    st.markdown(f'<div class="h-page">{tr("Projets")}</div>'
                f'<div class="sub">{c.pl(len(projects), "projet", "projets")} · {c.pl(c.open_count(), "tâche à faire", "tâches à faire")}</div>',
                unsafe_allow_html=True)
    items = ["add"] + projects
    with st.container(key="grid"):
        for r in range(0, len(items), 3):
            cols = st.columns(3)
            for col, p in zip(cols, items[r:r + 3]):
                with col:
                    if p == "add":
                        if st.button("＋ " + tr("Nouveau projet"), key="add_tile", use_container_width=True):
                            c.open_new_project()
                        continue
                    light, strong = tint(p["color"])
                    done, total = c.progress(p)
                    avs = "".join(avatar(m) for m in p["members"][:5])
                    with st.container(key=f"hit_p{p['id']}"):
                        st.markdown(
                            f'<div class="pcard"><div class="pcard-top" style="background:linear-gradient(135deg,{light},{light} 40%,{strong}33)">'
                            f'<div class="ringwrap">{ring(p, 60, 6)}</div></div><div class="pcard-body">'
                            f'<div class="pcard-n">{esc(p["name"])}</div><div class="pcard-d">{esc(p.get("desc")) or "&nbsp;"}</div>'
                            f'<div class="pcard-f"><div class="avs">{avs}</div>{pill(p["due"], c.project_finished(p))}</div>'
                            f'<div class="t-foot" style="margin-top:.6rem">{tr("{done}/{total} tâches").format(done=done, total=total)}</div></div></div>',
                            unsafe_allow_html=True)
                        st.button(tr("Ouvrir") + " " + p["name"], key=f"open_{p['id']}", on_click=open_project, args=(p["id"],))
    if not projects:
        st.markdown(f'<div class="empty">{tr(c.NO_PROJECT)}</div>', unsafe_allow_html=True)


def project_view(p):
    light, strong = tint(p["color"])
    done, total = c.progress(p)
    with st.container(key="back"):
        st.button("← " + tr("Projets"), on_click=c.set_open, args=(None,))
    avs = "".join(avatar(m) for m in p["members"])
    st.markdown(f'<style>.st-key-phero {{ background:linear-gradient(135deg, {light}, #fff 70%); }}</style>', unsafe_allow_html=True)
    with st.container(key="phero"):
        st.markdown(
            f'<div class="ph">{ring(p, 104, 9)}<div><div class="ph-n">{esc(p["name"])}</div>'
            + (f'<div class="ph-d">{esc(p["desc"])}</div>' if p.get("desc") else '<div style="height:.6rem"></div>')
            + f'<div class="ph-m">{pill(p["due"], c.project_finished(p))}<span>📅 {c.parse(p["due"]):%d/%m/%Y}</span>'
            f'<span>✅ {tr("{done}/{total} tâches").format(done=done, total=total)}</span>'
            f'<span class="avs">{avs}</span><span>{", ".join(esc(m) for m in p["members"])}</span></div></div></div>',
            unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns([1.2, 1.2, 1, 1.9])
        if a1.button("＋ " + tr("Nouvelle tâche"), type="primary", key="add_task", use_container_width=True):
            c.open_new_task(p["id"])
        if a2.button("✏️ " + tr("Gérer le projet"), key=f"manage_{p['id']}", use_container_width=True):
            c.open_edit_project(p["id"])
        if c.is_owner(p) and a3.button("🗑 " + tr("Supprimer"), key="del_project", use_container_width=True):
            c.open_confirm_delete(p["id"])
        with a4:
            c.ics_button(p, "📆 " + tr("Ajouter à mon calendrier (.ics)"))
    st.write("")
    if not p["tasks"]:
        st.markdown(f'<div class="empty">{tr("Pas encore de tâche. Ajoute la première avec sa deadline.")}</div>', unsafe_allow_html=True)
        return
    todo = sorted((t for t in p["tasks"] if not t["done"]), key=lambda t: t["due"])
    fin = sorted((t for t in p["tasks"] if t["done"]), key=lambda t: t["due"])
    with st.container(key="cols"):
        l, r = st.columns([1.35, 1])
        with l, st.container(key="b_todo"):
            st.markdown(f'<div class="colh">📝 {tr("À faire")}<span>{len(todo)}</span></div>', unsafe_allow_html=True)
            for t in todo:
                task_tile(p, t, show_project=False)
            if not todo:
                st.markdown(f'<div class="t-foot">{tr("Tout est à jour.")} 🎉</div>', unsafe_allow_html=True)
        with r, st.container(key="b_done_mint"):
            st.markdown(f'<div class="colh">🎉 {tr("Terminées")}<span>{len(fin)}</span></div>', unsafe_allow_html=True)
            for t in fin:
                task_tile(p, t, show_project=False)


# ---------- Planning ----------
def item_tile(item, suffix):
    p, t = c.find_task(item)
    if t:
        task_tile(p, t, suffix)


def planning():
    rows = c.workload_data()
    summary = c.workload_summary(rows)
    st.markdown(f'<div class="h-page">{tr("Charge de travail")}</div><div class="sub">{tr("Charge basée sur les deadlines")}</div>',
                unsafe_allow_html=True)
    with st.container(key="bento"):
        k = st.columns(3)
        for col, (label, val, ic, tone) in zip(k, [("Heures restantes", summary["total"], "⏳", "lilac"),
                                                   (c.TODAY, summary["today"], "☀️", "peach"),
                                                   ("Cette semaine", summary["week"], "📈", "mint")]):
            with col, st.container(key=f"b_k{tone}_{tone}"):
                st.markdown(f'<div class="t-label">{tr(label)}<span class="ic">{ic}</span></div>'
                            f'<div class="t-big">{c.format_duration(val) if val else "0 h"}</div>', unsafe_allow_html=True)
    st.write("")
    view, start, end, days, sel_key = c.workload_period()
    with st.container(key="b_cal"):
        with st.container(key="seg"):
            s1, s2, _, prev, lab, nxt = st.columns([1, 1, 0.3, 0.5, 2.6, 0.5])
            s1.button(tr("Semaine"), key="pw", on_click=c.set_period, args=("Semaine",), use_container_width=True,
                      type="primary" if view == "Semaine" else "secondary")
            s2.button(tr("Mois"), key="pm", on_click=c.set_period, args=("Mois",), use_container_width=True,
                      type="primary" if view == "Mois" else "secondary")
            prev.button("‹", key="pprev", on_click=c.shift_period, args=(-1,), use_container_width=True,
                        help=tr("Semaine précédente" if view == "Semaine" else "Mois précédent"))
            lab.markdown(f'<div class="period">{esc(c.period_label(view, start, end))}</div>', unsafe_allow_html=True)
            nxt.button("›", key="pnext", on_click=c.shift_period, args=(1,), use_container_width=True,
                       help=tr("Semaine suivante" if view == "Semaine" else "Mois suivant"))
        period = [x for x in rows if start <= x["date"] <= end]
        o = sum(x["minutes"] for x in period if not x["done"])
        d = sum(x["minutes"] for x in period if x["done"])
        st.markdown(f'<div class="legend"><span><i style="background:var(--violet)"></i>{tr("Ouvertes")} <b>{c.format_duration(o) if o else "0 h"}</b></span>'
                    f'<span><i style="background:#7BD8B3"></i>{tr("Terminées")} <b>{c.format_duration(d) if d else "0 h"}</b></span></div>',
                    unsafe_allow_html=True)
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
                                    f'<div class="t">{c.format_duration(op + fi) if op + fi else "–"}</div>'
                                    f'<div class="bar"><div class="d" style="height:{fi / peak * 100:.0f}%"></div>'
                                    f'<div class="o" style="height:{op / peak * 100:.0f}%"></div></div>'
                                    f'<div class="dt">{day:%d/%m}</div></div>', unsafe_allow_html=True)
                        st.button(names[i], key=f"wd_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day),
                                  use_container_width=True, type="primary" if day == selected else "secondary")
        else:
            with st.container(key="month"):
                head = st.columns(7)
                for col, n in zip(head, names):
                    col.markdown(f'<div class="mh">{n}</div>', unsafe_allow_html=True)
                for w in range(0, len(days), 7):
                    cols = st.columns(7)
                    for col, day in zip(cols, days[w:w + 7]):
                        n_open = sum(1 for x in rows if x["date"] == day and not x["done"])
                        n_done = sum(1 for x in rows if x["date"] == day and x["done"])
                        op, fi = c.day_load(rows, day)
                        dots = "".join('<i></i>' for _ in range(min(n_open, 4))) + "".join('<i class="d"></i>' for _ in range(min(n_done, 3)))
                        with col, st.container(key=f"hit_m{day.isoformat()}"):
                            st.markdown(f'<div class="mc{" out" if day.month != start.month else ""}{" sel" if day == selected else ""}'
                                        f'{" today" if day == today else ""}"><b>{day.day}</b>'
                                        f'<span>{c.format_duration(op + fi) if op + fi else ""}</span><div class="dots">{dots}</div></div>',
                                        unsafe_allow_html=True)
                            st.button(f"{day:%d/%m}", key=f"md_{day.isoformat()}", on_click=c.select_day, args=(sel_key, day))
    st.write("")
    sel_rows = sorted((x for x in rows if x["date"] == selected), key=lambda x: (x["done"], x["project"], x["title"]))
    upcoming = sorted((x for x in rows if not x["done"] and x["date"] >= today), key=lambda x: (x["date"], x["project"]))
    completed = sorted((x for x in rows if x["done"]), key=lambda x: (x["date"], x["project"]))
    with st.container(key="cols"):
        l, r = st.columns([1, 1])
        with l:
            with st.container(key="b_sel"):
                st.markdown(f'<div class="colh">📍 {esc(c.fmt_long(selected).capitalize())}<span>{len(sel_rows)}</span></div>', unsafe_allow_html=True)
                for item in sel_rows:
                    item_tile(item, f"sel_{view}")
                if not sel_rows:
                    st.markdown(f'<div class="t-foot">{tr("Aucune tâche avec une échéance ce jour-là.")}</div>', unsafe_allow_html=True)
            st.write("")
            with st.container(key="b_completed_mint"):
                st.markdown(f'<div class="colh">🎉 {tr("Tâches terminées")}<span>{len(completed)}</span></div>', unsafe_allow_html=True)
                for item in completed[:30]:
                    item_tile(item, "done")
                if not completed:
                    st.markdown(f'<div class="t-foot">{tr("Aucune tâche terminée pour le moment.")}</div>', unsafe_allow_html=True)
        with r, st.container(key="b_upcoming"):
            st.markdown(f'<div class="colh">🚀 {tr("Tâches ouvertes")}<span>{len(upcoming)}</span></div>', unsafe_allow_html=True)
            for item in upcoming[:30]:
                item_tile(item, "up")
            if not upcoming:
                st.markdown(f'<div class="t-foot">{tr("Aucune tâche ouverte à venir.")}</div>', unsafe_allow_html=True)


# ---------- Compte ----------
def account():
    st.markdown(f'<div class="h-page">{tr("Compte")}</div><div class="sub">{tr("Réglages")} · Google Calendar · {tr("Sauvegarde")}</div>',
                unsafe_allow_html=True)
    with st.container(key="bento"):
        a, b, d = st.columns(3)
        with a, st.container(key="b_acc"):
            st.markdown(f'<div class="acc"><div class="avatar-me">{esc(c.me()["name"][:1].upper())}</div>'
                        f'<div><b>{esc(c.me()["name"])}</b><small>● {esc(tr("Connecté : {name}").format(name=c.me()["name"]))}</small></div></div>',
                        unsafe_allow_html=True)
            st.write("")
            st.button("👋 " + tr("Se déconnecter"), key="logout", on_click=st.logout, use_container_width=True)
        with b, st.container(key="b_gcal_lilac"):
            st.markdown('<div class="h-tile">📅 Google Calendar</div>', unsafe_allow_html=True)
            c.calendar_panel(cal_row, cal_err, link_style=(
                "display:block;text-align:center;padding:.65rem;border-radius:999px;"
                "background:linear-gradient(120deg,#FF7A59,#C04CFD 55%,#6C4DFF);color:#fff;"
                "font-family:sans-serif;font-weight:700;text-decoration:none"))
        with d, st.container(key="b_backup_butter"):
            st.markdown(f'<div class="h-tile">💾 {tr("Sauvegarde")}</div>'
                        f'<div class="t-foot" style="margin-bottom:.6rem">JSON · {c.pl(len(st.session_state.projects), "projet", "projets")}</div>',
                        unsafe_allow_html=True)
            c.export_button("⬇️ " + tr("Exporter les données"))


# ---------- Rendu ----------
topbar()
c.important_banner()
page = st.session_state.page
if page == "planning":
    planning()
elif page == "account":
    account()
elif page == "projects":
    current = c.get_project(st.session_state.open) if st.session_state.open else None
    if current:
        project_view(current)
    else:
        board()
else:
    home()
