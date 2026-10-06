import html
import json
import uuid
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="anti gooner", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = Path(__file__).with_name("anti_gooner_data.json")
COLORS = ["#8B7BFF", "#FF8FA3", "#5CE1C6", "#FFC46B", "#6BB6FF", "#C48BFF"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Manrope:wght@400;500;600;700&display=swap');

:root {
  --bg: #0D0E1C; --text: #ECEBFF; --muted: #8E8FB5;
  --line: rgba(255,255,255,.08); --accent: #8B7BFF;
}
.stApp {
  background:
    radial-gradient(900px 500px at 10% -10%, rgba(139,123,255,.22), transparent 60%),
    radial-gradient(700px 480px at 95% 5%, rgba(255,143,163,.14), transparent 60%),
    radial-gradient(800px 600px at 50% 110%, rgba(92,225,198,.10), transparent 60%),
    var(--bg);
  background-attachment: fixed;
}
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea { font-family: 'Manrope', sans-serif; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 2.5rem; }

/* Bannière */
.banner { padding: 1.5rem 0 2.2rem; animation: rise .8s cubic-bezier(.2,.8,.2,1) both; }
.banner h1 {
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: clamp(3.2rem, 9vw, 6.2rem); line-height: .95; letter-spacing: -0.045em; margin: 0;
  padding: 0; background: linear-gradient(100deg, #FFFFFF 10%, #B9AEFF 55%, #FF8FA3 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.banner p { color: var(--muted); font-size: 1.1rem; margin: .9rem 0 1.1rem; }
.pill {
  display: inline-block; padding: .3rem .85rem; margin-right: .5rem; border-radius: 999px;
  background: rgba(255,255,255,.06); border: 1px solid var(--line); color: var(--text);
  font-size: .85rem; font-weight: 600;
}
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }

/* Cartes projets, tâches, en-tête projet */
[class*="st-key-card_"], [class*="st-key-task_"], .st-key-ph {
  background: linear-gradient(160deg, rgba(255,255,255,.065), rgba(255,255,255,.02));
  border: 1px solid var(--line); border-radius: 22px; padding: 1.3rem 1.4rem;
  backdrop-filter: blur(12px);
  transition: transform .3s cubic-bezier(.2,.8,.2,1), border-color .3s ease, box-shadow .3s ease;
}
[class*="st-key-card_"]:hover {
  transform: translateY(-4px); border-color: rgba(139,123,255,.5);
  box-shadow: 0 22px 44px -22px rgba(139,123,255,.55);
}
[class*="st-key-task_"] { border-radius: 16px; padding: .55rem 1rem; }
[class*="st-key-task_"]:hover { border-color: rgba(255,255,255,.16); }
.st-key-ph { padding: 1.7rem 1.8rem; margin-bottom: .6rem; }

.pc-name, .ph-title {
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.35rem;
  letter-spacing: -0.02em; color: var(--text); display: flex; align-items: center; gap: .6rem;
}
.ph-title { font-size: 2.1rem; }
.dot { width: .7rem; height: .7rem; border-radius: 50%; flex: none; box-shadow: 0 0 14px currentColor; }
.pc-desc, .ph-desc { color: var(--muted); font-size: .92rem; margin: .5rem 0 1rem; min-height: 1.3rem; }
.pc-bar { height: 7px; border-radius: 99px; background: rgba(255,255,255,.08); overflow: hidden; }
.pc-bar > div { height: 100%; border-radius: 99px; transition: width .6s ease; }
.pc-meta { display: flex; justify-content: space-between; align-items: center; margin: .9rem 0 .2rem; color: var(--muted); font-size: .86rem; font-weight: 600; }

.badge { padding: .2rem .65rem; border-radius: 99px; font-size: .78rem; font-weight: 700; white-space: nowrap; }
.badge.late { background: rgba(255,107,129,.16); color: #FF8FA3; }
.badge.soon { background: rgba(255,196,107,.16); color: #FFC46B; }
.badge.ok { background: rgba(92,225,198,.14); color: #5CE1C6; }
.badge.done { background: rgba(255,255,255,.08); color: var(--muted); }

.t-title { font-weight: 600; color: var(--text); }
.t-title.done { text-decoration: line-through; color: var(--muted); }
.owner { color: var(--muted); font-size: .85rem; font-weight: 600; }
.date-small { color: var(--muted); font-size: .8rem; margin-left: .5rem; }
.chip { display: inline-block; padding: .2rem .7rem; margin: .8rem .4rem 0 0; border-radius: 99px; background: rgba(139,123,255,.14); color: #CFC8FF; font-size: .82rem; font-weight: 600; }
.empty { text-align: center; color: var(--muted); padding: 2.5rem 1rem; border: 1.5px dashed var(--line); border-radius: 20px; margin-top: 1rem; }

/* Boutons */
.stButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.05);
  color: var(--text); font-weight: 600; transition: all .25s ease;
}
.stButton > button:hover { border-color: var(--accent); background: rgba(139,123,255,.14); color: #fff; transform: translateY(-1px); }
.stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #8B7BFF, #6A58F0); border: none; color: #fff;
  box-shadow: 0 10px 24px -12px rgba(139,123,255,.9);
}
.stButton > button[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.1); }
.st-key-add_tile button {
  height: 100%; min-height: 200px; font-size: 1.15rem; border: 1.5px dashed rgba(139,123,255,.55);
  background: rgba(139,123,255,.05); border-radius: 22px;
}
.st-key-add_tile button:hover { background: rgba(139,123,255,.14); transform: translateY(-4px); }
.st-key-add_tile { height: 100%; }

[data-testid="stDialog"] div[role="dialog"] { border-radius: 24px; border: 1px solid var(--line); }

/* Sidebar : avancement des projets */
[data-testid="stSidebar"] { background: rgba(22,24,48,.65); border-right: 1px solid var(--line); backdrop-filter: blur(14px); }
.side-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.4rem; letter-spacing: -0.02em; color: var(--text); margin: .4rem 0 1.1rem; }
.ring-row { display: flex; align-items: center; gap: .9rem; padding: .7rem .8rem; margin-bottom: .6rem; border-radius: 18px; background: rgba(255,255,255,.04); border: 1px solid var(--line); }
.ring-row.active { border-color: rgba(139,123,255,.55); background: rgba(139,123,255,.09); }
.ring-row svg { flex: none; }
.ring-fg { transition: stroke-dasharray .8s ease; }
.ring-name { font-weight: 700; color: var(--text); font-size: .95rem; line-height: 1.2; }
.ring-sub { color: var(--muted); font-size: .8rem; margin-top: .15rem; }
.by { color: var(--muted); font-size: .76rem; margin-top: .1rem; }
</style>
"""


# ---------- Données ----------
def load():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text("utf-8"))
        except Exception:
            return []
    return []


def save():
    DATA_FILE.write_text(
        json.dumps(st.session_state.projects, ensure_ascii=False, indent=2), "utf-8"
    )


if "projects" not in st.session_state:
    st.session_state.projects = load()
    st.session_state.open = None


def uid():
    return uuid.uuid4().hex[:8]


def esc(s):
    return html.escape(s or "")


def parse(d):
    return date.fromisoformat(d)


def get_project(pid):
    return next((p for p in st.session_state.projects if p["id"] == pid), None)


def progress(p):
    total = len(p["tasks"])
    done = sum(1 for t in p["tasks"] if t["done"])
    return done, total


def due_badge(d, done=False):
    if done:
        return '<span class="badge done">terminé</span>'
    n = (parse(d) - date.today()).days
    if n < 0:
        txt, cls = f"en retard de {-n} j", "late"
    elif n == 0:
        txt, cls = "aujourd'hui", "soon"
    elif n == 1:
        txt, cls = "demain", "soon"
    else:
        txt, cls = f"dans {n} j", ("soon" if n <= 3 else "ok")
    return f'<span class="badge {cls}">{txt}</span>'


# ---------- Callbacks ----------
def set_open(pid):
    st.session_state.open = pid


def toggle(pid, tid):
    who = st.session_state.get(f"who_{pid}") or ""
    for t in get_project(pid)["tasks"]:
        if t["id"] == tid:
            t["done"] = st.session_state[f"chk_{tid}"]
            t["by"] = who if t["done"] else ""
    save()


def delete_task(pid, tid):
    p = get_project(pid)
    p["tasks"] = [t for t in p["tasks"] if t["id"] != tid]
    save()


def delete_project(pid):
    st.session_state.projects = [p for p in st.session_state.projects if p["id"] != pid]
    st.session_state.open = None
    save()


def add_member(pid):
    name = st.session_state.get("new_member", "").strip()
    p = get_project(pid)
    if name and name not in p["members"]:
        p["members"].append(name)
        save()
    st.session_state.new_member = ""


# ---------- Dialogues ----------
@st.dialog("Nouveau projet")
def new_project():
    name = st.text_input("Nom du projet", placeholder="Ex. Étude de cas marketing")
    desc = st.text_area("Description (facultatif)", height=80)
    due = st.date_input(
        "Deadline du projet", value=date.today() + timedelta(days=14), format="DD/MM/YYYY"
    )
    members = st.text_input("Qui est dans l'équipe ?", placeholder="Lina, Hugo, Sam")
    if st.button("Créer le projet", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Donne un nom au projet.")
            return
        st.session_state.projects.append(
            {
                "id": uid(),
                "name": name.strip(),
                "desc": desc.strip(),
                "due": due.isoformat(),
                "color": COLORS[len(st.session_state.projects) % len(COLORS)],
                "members": [m.strip() for m in members.split(",") if m.strip()],
                "tasks": [],
            }
        )
        save()
        st.rerun()


@st.dialog("Nouvelle tâche")
def new_task(pid):
    p = get_project(pid)
    title = st.text_input("Tâche", placeholder="Ex. Rédiger l'introduction")
    c1, c2 = st.columns(2)
    due = c1.date_input(
        "Deadline", value=date.today() + timedelta(days=3), format="DD/MM/YYYY"
    )
    owner = c2.selectbox("Responsable", ["Tout le monde"] + p["members"])
    if st.button("Ajouter la tâche", type="primary", use_container_width=True):
        if not title.strip():
            st.error("Donne un nom à la tâche.")
            return
        p["tasks"].append(
            {"id": uid(), "title": title.strip(), "due": due.isoformat(), "owner": owner, "done": False, "by": ""}
        )
        save()
        st.rerun()


# ---------- Vues ----------
def banner():
    projects = st.session_state.projects
    n_open = sum(1 for p in projects for t in p["tasks"] if not t["done"])
    st.markdown(
        f"""<div class="banner"><h1>anti gooner</h1>
<p>Les deadlines de l'équipe, au même endroit.</p>
<span class="pill">{len(projects)} projet{'s' if len(projects) > 1 else ''}</span>
<span class="pill">{n_open} tâche{'s' if n_open > 1 else ''} à faire</span></div>""",
        unsafe_allow_html=True,
    )


def card(p):
    done, total = progress(p)
    pct = int(done / total * 100) if total else 0
    with st.container(key=f"card_{p['id']}"):
        st.markdown(
            f"""<div class="pc-name"><span class="dot" style="background:{p['color']};color:{p['color']}"></span>{esc(p['name'])}</div>
<div class="pc-desc">{esc(p['desc']) or '&nbsp;'}</div>
<div class="pc-bar"><div style="width:{pct}%;background:{p['color']}"></div></div>
<div class="pc-meta"><span>{done}/{total} tâches</span>{due_badge(p['due'], total > 0 and done == total)}</div>""",
            unsafe_allow_html=True,
        )
        st.button(
            "Ouvrir", key=f"open_{p['id']}", on_click=set_open, args=(p["id"],), use_container_width=True
        )


def board():
    projects = sorted(st.session_state.projects, key=lambda p: p["due"])
    items = ["add"] + projects
    for r in range(0, len(items), 3):
        cols = st.columns(3, gap="medium")
        for col, item in zip(cols, items[r : r + 3]):
            with col:
                if item == "add":
                    if st.button("+  Nouveau projet", key="add_tile", use_container_width=True):
                        new_project()
                else:
                    card(item)
    if not projects:
        st.markdown(
            '<div class="empty">Aucun projet pour l\'instant. Clique sur le + pour créer le premier.</div>',
            unsafe_allow_html=True,
        )


def project_view(p):
    st.button("←  Retour au board", key="back", on_click=set_open, args=(None,))
    done, total = progress(p)
    pct = int(done / total * 100) if total else 0
    chips = "".join(f'<span class="chip">{esc(m)}</span>' for m in p["members"])
    with st.container(key="ph"):
        st.markdown(
            f"""<div class="ph-title"><span class="dot" style="background:{p['color']};color:{p['color']}"></span>{esc(p['name'])}</div>
<div class="ph-desc">{esc(p['desc'])}</div>
<div class="pc-bar"><div style="width:{pct}%;background:{p['color']}"></div></div>
<div class="pc-meta"><span>{done}/{total} tâches, deadline le {parse(p['due']):%d/%m/%Y}</span>{due_badge(p['due'], total > 0 and done == total)}</div>
{chips}""",
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns([1.2, 1.2, 2], vertical_alignment="center")
    if c1.button("+  Nouvelle tâche", type="primary", key="add_task", use_container_width=True):
        new_task(p["id"])
    with c2.popover("Gérer le projet", use_container_width=True):
        st.text_input("Ajouter un membre", key="new_member", placeholder="Prénom")
        st.button("Ajouter", key="add_member", on_click=add_member, args=(p["id"],))
        st.button("Supprimer ce projet", key="del_project", on_click=delete_project, args=(p["id"],))

    if p["members"]:
        c3.selectbox(
            "Je suis", p["members"], index=None, placeholder="Je suis… (choisis ton prénom)",
            key=f"who_{p['id']}", label_visibility="collapsed",
        )
    who = st.session_state.get(f"who_{p['id']}")
    locked = bool(p["members"]) and not who
    if locked:
        st.caption("Choisis ton prénom pour pouvoir marquer les tâches comme faites.")

    st.write("")
    tasks = sorted(p["tasks"], key=lambda t: (t["done"], t["due"]))
    if not tasks:
        st.markdown(
            '<div class="empty">Pas encore de tâche. Ajoute la première avec sa deadline.</div>',
            unsafe_allow_html=True,
        )
    for t in tasks:
        with st.container(key=f"task_{t['id']}"):
            c = st.columns([0.07, 1, 0.35, 0.42, 0.08], vertical_alignment="center")
            c[0].checkbox(
                "fait", value=t["done"], key=f"chk_{t['id']}", on_change=toggle,
                args=(p["id"], t["id"]), label_visibility="collapsed", disabled=locked,
            )
            cls = "t-title done" if t["done"] else "t-title"
            by = f'<div class="by">fait par {esc(t["by"])}</div>' if t["done"] and t.get("by") else ""
            c[1].markdown(f'<div class="{cls}">{esc(t["title"])}</div>{by}', unsafe_allow_html=True)
            c[2].markdown(f'<span class="owner">{esc(t["owner"])}</span>', unsafe_allow_html=True)
            c[3].markdown(
                f'{due_badge(t["due"], t["done"])}<span class="date-small">{parse(t["due"]):%d/%m}</span>',
                unsafe_allow_html=True,
            )
            c[4].button("✕", key=f"rm_{t['id']}", on_click=delete_task, args=(p["id"], t["id"]))


def ring(p, active):
    done, total = progress(p)
    pct = round(done / total * 100) if total else 0
    fg = (
        f'<circle class="ring-fg" cx="18" cy="18" r="15.9155" fill="none" stroke="{p["color"]}" '
        f'stroke-width="3.4" stroke-linecap="round" stroke-dasharray="{pct} {100 - pct}" '
        f'transform="rotate(-90 18 18)"/>'
        if pct
        else ""
    )
    return (
        f'<div class="ring-row{" active" if active else ""}">'
        f'<svg width="68" height="68" viewBox="0 0 36 36">'
        f'<circle cx="18" cy="18" r="15.9155" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="3.4"/>'
        f'{fg}'
        f'<text x="18" y="20.6" text-anchor="middle" font-size="8" font-weight="700" fill="#ECEBFF">{pct}%</text>'
        f'</svg>'
        f'<div><div class="ring-name">{esc(p["name"])}</div>'
        f'<div class="ring-sub">{done}/{total} tâches faites</div></div></div>'
    )


def sidebar():
    with st.sidebar:
        st.markdown('<div class="side-title">Avancement</div>', unsafe_allow_html=True)
        projects = sorted(st.session_state.projects, key=lambda p: p["due"])
        if not projects:
            st.caption("L'avancement de chaque projet apparaîtra ici.")
        for p in projects:
            st.markdown(ring(p, p["id"] == st.session_state.open), unsafe_allow_html=True)


# ---------- Main ----------
st.markdown(CSS, unsafe_allow_html=True)
sidebar()
banner()
current = get_project(st.session_state.open) if st.session_state.open else None
if current:
    project_view(current)
else:
    board()
