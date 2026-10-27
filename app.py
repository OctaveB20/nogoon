import hashlib
import hmac
import html
import json
import os
import secrets as py_secrets
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Évite l'erreur "Scope has changed" quand Google renvoie des scopes supplémentaires.
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

st.set_page_config(page_title="anti gooner", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = Path(__file__).with_name("anti_gooner_data.json")
COLORS = ["#8B7BFF", "#FF8FA3", "#5CE1C6", "#FFC46B", "#6BB6FF", "#C48BFF"]

LANG = st.session_state.get("lang", "FR")

EN = {
    "Les deadlines de l'équipe, au même endroit.": "Your team's deadlines, all in one place.",
    "projet": "project", "projets": "projects",
    "tâche à faire": "task to do", "tâches à faire": "tasks to do",
    "Connecte-toi pour retrouver tes projets.": "Log in to find your projects.",
    "Connexion": "Log in", "Créer un compte": "Sign up", "Mot de passe": "Password",
    "Se connecter": "Log in", "Email ou mot de passe incorrect.": "Wrong email or password.",
    "Ton prénom (visible par tes amis)": "Your first name (visible to your friends)",
    "Mot de passe (6 caractères minimum)": "Password (6 characters minimum)",
    "Code d'invitation": "Invitation code", "Créer mon compte": "Create my account",
    "Inscriptions fermées (INVITE_CODE absent des Secrets).": "Sign-ups are closed (INVITE_CODE missing from Secrets).",
    "Code d'invitation incorrect.": "Wrong invitation code.",
    "Vérifie le nom, l'email et le mot de passe (6 caractères minimum).": "Check the name, email and password (6 characters minimum).",
    "Ce nom est déjà pris.": "This name is already taken.",
    "Création impossible (cet email est peut-être déjà utilisé).": "Could not create the account (this email may already be in use).",
    "Sauvegarde impossible, réessaie dans un instant.": "Could not save, try again in a moment.",
    "Suppression impossible, réessaie dans un instant.": "Could not delete, try again in a moment.",
    "Impossible de joindre la base de données (projet Supabase en pause, ou URL / clé incorrectes). Tes données ne sont pas perdues.": "Cannot reach the database (Supabase project paused, or wrong URL / key). Your data is not lost.",
    "terminé": "done", "aujourd'hui": "today", "demain": "tomorrow",
    "en retard de {n} j": "{n} d overdue", "dans {n} j": "in {n} d",
    "{done}/{total} tâches": "{done}/{total} tasks",
    "{done}/{total} tâches faites": "{done}/{total} tasks done",
    "{done}/{total} tâches, deadline le {d}": "{done}/{total} tasks, deadline {d}",
    "Ouvrir": "Open", "+  Nouveau projet": "+  New project",
    "Aucun projet pour l'instant. Clique sur le + pour créer le premier.": "No projects yet. Click the + to create the first one.",
    "Mes tâches": "My tasks", "←  Retour au board": "←  Back to board",
    "+  Nouvelle tâche": "+  New task", "Gérer le projet": "Manage project",
    "Ajouter un membre": "Add a member", "Choisis un ami inscrit": "Pick a registered friend",
    "Ajouter": "Add", "Deadline du projet": "Project deadline", "Supprimer": "Delete",
    "Pas encore de tâche. Ajoute la première avec sa deadline.": "No tasks yet. Add the first one with its deadline.",
    "fait": "done", "fait par": "done by", "Tout le monde": "Everyone",
    "Nouveau projet": "New project", "Nom du projet": "Project name",
    "Ex. Étude de cas marketing": "E.g. Marketing case study",
    "Description (facultatif)": "Description (optional)",
    "Qui est dans l'équipe ?": "Who's on the team?",
    "Ajoute des amis inscrits": "Add registered friends",
    "Créer le projet": "Create project", "Donne un nom au projet.": "Give the project a name.",
    "Nouvelle tâche": "New task", "Tâche": "Task",
    "Ex. Rédiger l'introduction": "E.g. Write the introduction",
    "Responsable": "Owner", "Ajouter la tâche": "Add task",
    "Donne un nom à la tâche.": "Give the task a name.",
    "Supprimer ce projet ?": "Delete this project?",
    "« {name} » et ses {n} tâche(s) seront supprimés. Cette action est définitive.": "\"{name}\" and its {n} task(s) will be deleted. This cannot be undone.",
    "Annuler": "Cancel", "Oui, supprimer": "Yes, delete",
    "Avancement": "Progress",
    "L'avancement de chaque projet apparaîtra ici.": "Each project's progress will show up here.",
    "Sauvegarde": "Backup", "Exporter les données": "Export data",
    "Connecté : {name}": "Logged in: {name}", "Se déconnecter": "Log out",
    "Rester connecté sur cet appareil (cookie de 30 jours)": "Stay logged in on this device (30-day cookie)",
    "Reconnexion automatique indisponible sur ce navigateur.": "Auto-login unavailable in this browser.",
    "Reconnexion automatique activée.": "Auto-login enabled.",
    "Reconnexion automatique désactivée.": "Auto-login turned off.",
    "Désactiver": "Turn off",
    "Rester connecté sur cet appareil": "Stay logged in on this device",
    "Enregistre un cookie de 30 jours pour te reconnecter automatiquement.": "Saves a 30-day cookie to log you back in automatically.",
    "Continuer avec Google": "Continue with Google",
    "Ton compte Google n'a pas d'email vérifié.": "Your Google account has no verified email.",
    "Première connexion avec {email}. Choisis ton prénom et entre le code d'invitation.": "First login with {email}. Pick your first name and enter the invitation code.",
    "Prénom trop court.": "First name too short.",
    "Création impossible, réessaie dans un instant.": "Could not create the account, try again in a moment.",
    "Enregistrer": "Save",
    "+ {n} autres tâches": "+ {n} more tasks",
    "À faire": "To do", "Terminées": "Done",
    "Supprimer la tâche": "Delete task",
    "Ajouter à mon calendrier (.ics)": "Add to my calendar (.ics)",
    "Télécharge un fichier à ouvrir avec Google Agenda, Apple Calendrier ou Outlook : la deadline du projet et ses tâches non terminées y sont ajoutées.": "Downloads a file to open with Google Calendar, Apple Calendar or Outlook: the project deadline and its unfinished tasks get added.",
}


def tr(s):
    return EN.get(s, s) if LANG == "EN" else s


def pl(n, one, many):
    single = n == 1 or (n == 0 and LANG != "EN")
    return f"{n} {tr(one if single else many)}"


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
[class*="st-key-task_"] {
  border-radius: 16px; padding: .6rem 1rem .6rem 1.1rem; border-left: 4px solid rgba(255,255,255,.14);
  margin-bottom: .15rem;
}
[class*="st-key-task_"]:hover { transform: translateX(3px); box-shadow: 0 14px 30px -20px rgba(0,0,0,.8); }
[class*="st-key-task_late_"] { border-left-color: #FF8FA3; background: linear-gradient(90deg, rgba(255,107,129,.10), rgba(255,255,255,.02) 45%); }
[class*="st-key-task_soon_"] { border-left-color: #FFC46B; }
[class*="st-key-task_ok_"] { border-left-color: #5CE1C6; }
[class*="st-key-task_done_"] { border-left-color: rgba(255,255,255,.14); opacity: .6; }
[class*="st-key-task_done_"]:hover { opacity: 1; }
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
.stDownloadButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.05);
  color: var(--text); font-weight: 600; transition: all .25s ease;
}
.stDownloadButton > button:hover { border-color: var(--accent); background: rgba(139,123,255,.14); color: #fff; transform: translateY(-1px); }
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
.ring-row { display: flex; align-items: center; gap: .9rem; padding: .7rem .8rem; margin-bottom: 0; border-radius: 18px; transition: all .25s ease; background: rgba(255,255,255,.04); border: 1px solid var(--line); }
.ring-row.active { border-color: rgba(139,123,255,.55); background: rgba(139,123,255,.09); }
.ring-row svg { flex: none; }
.ring-fg { transition: stroke-dasharray .8s ease; }
.ring-name { font-weight: 700; color: var(--text); font-size: .95rem; line-height: 1.2; }
.ring-sub { color: var(--muted); font-size: .8rem; margin-top: .15rem; }
.by { color: var(--muted); font-size: .76rem; margin-top: .1rem; }

/* Projets cliquables dans la sidebar : superposition du bouton sur toute la carte */
[class*="st-key-navc_"] {
  position: relative;
  display: grid;
  margin-bottom: .6rem;
  isolation: isolate;
}
[class*="st-key-navc_"] > [data-testid="stElementContainer"] {
  grid-area: 1 / 1;
  min-width: 0;
}
[class*="st-key-navc_"] [data-testid="stElementContainer"]:has(button) {
  position: relative;
  z-index: 3;
  align-self: stretch;
  min-height: 100%;
}
[class*="st-key-navc_"] [data-testid="stElementContainer"]:has(button) .stButton,
[class*="st-key-navc_"] [data-testid="stElementContainer"]:has(button) .stButton > button {
  width: 100%;
  height: 100%;
  min-height: 100%;
}
[class*="st-key-navc_"] .stButton > button {
  opacity: 0;
  cursor: pointer;
  padding: 0;
  border: 0;
}
[class*="st-key-navc_"]:hover .ring-row,
[class*="st-key-navc_"]:focus-within .ring-row {
  border-color: rgba(139,123,255,.7);
  background: rgba(139,123,255,.12);
  transform: translateX(3px);
}
[class*="st-key-navc_"] .stButton > button:focus-visible {
  opacity: .01;
  outline: 2px solid #8B7BFF;
  outline-offset: -3px;
}
.mt-row { display: flex; align-items: center; gap: .8rem; padding: .7rem 1rem; margin-bottom: .5rem; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid var(--line); }
.mt-row .t-title { flex: 1; }

/* Lignes de tâches */
.sec { display: flex; align-items: center; gap: .6rem; color: var(--muted); font-size: .9rem; font-weight: 700; margin: 1.5rem 0 .6rem; }
.sec span { background: rgba(255,255,255,.08); border-radius: 99px; padding: .05rem .6rem; font-size: .78rem; }
.avatar { display: inline-flex; align-items: center; justify-content: center; width: 1.7rem; height: 1.7rem; border-radius: 50%; font-size: .78rem; font-weight: 700; margin-right: .55rem; vertical-align: middle; }
[class*="st-key-task_"] .t-title { font-size: 1rem; }
[class*="st-key-task_"] label[data-baseweb="checkbox"] > span:first-child { border-radius: 50%; width: 1.4rem; height: 1.4rem; }
[class*="st-key-task_"] button[data-testid="stPopoverButton"] {
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.18); color: var(--text);
  min-height: 2.2rem; min-width: 3rem; padding: 0 .6rem; justify-content: center; border-radius: 10px; box-shadow: none;
}
[class*="st-key-task_"] button[data-testid="stPopoverButton"]:hover { background: rgba(139,123,255,.22); border-color: rgba(139,123,255,.7); color: #fff; transform: none; }

/* Sélecteur de langue */
.st-key-lang [role="radiogroup"] { gap: .35rem; justify-content: flex-end; }
.st-key-lang label { background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.28); border-radius: 999px; padding: .2rem .95rem; transition: all .25s ease; cursor: pointer; }
.st-key-lang label p, .st-key-lang label div { color: #ECEBFF !important; font-weight: 700; font-size: .85rem; }
.st-key-lang label:hover { border-color: rgba(139,123,255,.85); }
.st-key-lang label:has(input:checked) { background: linear-gradient(135deg, #8B7BFF, #6A58F0); border-color: transparent; box-shadow: 0 8px 20px -10px rgba(139,123,255,.9); }
.st-key-lang label:has(input:checked) p, .st-key-lang label:has(input:checked) div { color: #fff !important; }
.st-key-lang label > div:first-child { display: none; }
[data-testid="stForm"] { border: none; padding: 0; }
.stFormSubmitButton > button {
  border-radius: 12px; border: none; background: linear-gradient(135deg, #8B7BFF, #6A58F0); color: #fff;
  font-weight: 600; box-shadow: 0 10px 24px -12px rgba(139,123,255,.9); transition: all .25s ease;
}
.stFormSubmitButton > button:hover { filter: brightness(1.1); transform: translateY(-1px); }
</style>
"""


# ---------- Données ----------
URL = KEY = ANON = None
_cfg_ok = True
try:
    URL = st.secrets["SUPABASE_URL"].rstrip("/")
    KEY = st.secrets["SUPABASE_KEY"]
    ANON = st.secrets.get("SUPABASE_ANON_KEY", KEY)
except Exception:
    _cfg_ok = False
if not _cfg_ok:
    st.error("Secrets Supabase introuvables (SUPABASE_URL, SUPABASE_KEY, SUPABASE_ANON_KEY, INVITE_CODE).")
    st.stop()

H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
COOKIE = "ag_rt"


def rest(method, path, headers=None, **kw):
    r = requests.request(
        method, f"{URL}/rest/v1/{path}",
        headers={**H, "Content-Type": "application/json", **(headers or {})}, timeout=10, **kw,
    )
    if not r.ok:
        # Montre le vrai message d'erreur de Supabase (table manquante, RLS, etc.)
        raise RuntimeError(f"Supabase {r.status_code} sur {path} : {r.text[:300]}")
    return r.json() if r.content else None


def me():
    return st.session_state.user


# ---------- Google Calendar OAuth & synchronisation ----------
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def calendar_redirect_uri():
    return st.secrets["GOOGLE_REDIRECT_URI"].strip()


def calendar_client_config():
    return {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [calendar_redirect_uri()],
        }
    }


def calendar_flow(state):
    # autogenerate_code_verifier=False : le Flow est recréé après la redirection,
    # donc le code_verifier PKCE serait perdu et fetch_token échouerait.
    flow = Flow.from_client_config(
        calendar_client_config(), scopes=CALENDAR_SCOPES, state=state,
        autogenerate_code_verifier=False,
    )
    flow.redirect_uri = calendar_redirect_uri()
    return flow


def calendar_fernet():
    return Fernet(st.secrets["GOOGLE_TOKEN_ENCRYPTION_KEY"].encode())


def calendar_connection():
    rows = rest(
        "GET", "google_calendar_connections",
        params={
            "user_id": f"eq.{me()['id']}",
            "select": "user_id,refresh_token_encrypted,connected_email,scopes",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


def start_calendar_oauth():
    state = py_secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    rest(
        "POST", "google_calendar_oauth_states",
        json={
            "state": state,
            "user_id": me()["id"],
            "expires_at": (now + timedelta(minutes=10)).isoformat(),
        },
        headers={"Prefer": "return=minimal"},
    )
    flow = calendar_flow(state)
    url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    st.session_state["calendar_auth_url"] = url


def handle_calendar_callback():
    params = st.query_params
    error = params.get("error")
    if error:
        st.session_state["calendar_notice_err"] = "Autorisation Google Calendar refusée ou annulée."
        st.session_state.pop("calendar_auth_url", None)
        st.query_params.clear()
        st.rerun()

    code = params.get("code")
    state = params.get("state")
    if not code or not state:
        return

    valid_states = rest(
        "GET", "google_calendar_oauth_states",
        params={
            "state": f"eq.{state}",
            "user_id": f"eq.{me()['id']}",
            "expires_at": "gt." + datetime.now(timezone.utc).isoformat(),
            "select": "state",
            "limit": "1",
        },
    )
    if not valid_states:
        st.session_state["calendar_notice_err"] = "Demande Google expirée ou invalide. Recommence la connexion."
        st.session_state.pop("calendar_auth_url", None)
        st.query_params.clear()
        st.rerun()

    flow = calendar_flow(state)
    flow.fetch_token(code=code)
    creds = flow.credentials

    oauth_service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
    google_email = oauth_service.userinfo().get().execute()["email"]

    old = calendar_connection()
    refresh_token = creds.refresh_token
    if not refresh_token and old:
        refresh_token = calendar_fernet().decrypt(
            old["refresh_token_encrypted"].encode()
        ).decode()
    if not refresh_token:
        raise RuntimeError(
            "Google n'a pas renvoyé de jeton de renouvellement. Révoque l'accès existant à Anti Gooner dans ton compte Google, puis recommence."
        )

    encrypted = calendar_fernet().encrypt(refresh_token.encode()).decode()
    saved_rows = rest(
        "POST", "google_calendar_connections",
        params={"on_conflict": "user_id"},
        json={
            "user_id": me()["id"],
            "refresh_token_encrypted": encrypted,
            "connected_email": google_email,
            "scopes": CALENDAR_SCOPES,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        headers={"Prefer": "resolution=merge-duplicates,return=representation"},
    )
    if not saved_rows:
        raise RuntimeError("Écriture dans google_calendar_connections sans effet (RLS ou contrainte ?)")
    rest("DELETE", "google_calendar_oauth_states", params={"state": f"eq.{state}"})
    st.session_state.pop("calendar_auth_url", None)
    st.session_state["calendar_notice"] = f"Google Calendar connecté : {google_email}"
    st.query_params.clear()
    st.rerun()


def calendar_credentials():
    connection = calendar_connection()
    if not connection:
        return None
    refresh_token = calendar_fernet().decrypt(
        connection["refresh_token_encrypted"].encode()
    ).decode()
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
        scopes=CALENDAR_SCOPES,
    )
    creds.refresh(Request())
    return creds


def calendar_service():
    creds = calendar_credentials()
    if creds is None:
        return None
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def gcal_exec(request, tries=5):
    """Exécute une requête Google avec nouvel essai en cas de limite de débit."""
    for i in range(tries):
        try:
            return request.execute()
        except HttpError as exc:
            msg = str(exc).lower()
            if i < tries - 1 and (exc.resp.status in (429, 500, 503) or "ratelimit" in msg):
                time.sleep(0.5 * 2 ** i)
                continue
            raise


def sync_google_calendar():
    """Synchronise les deadlines et renvoie un bilan détaillé."""
    service = calendar_service()
    if service is None:
        raise RuntimeError("Connecte d'abord ton compte Google Calendar.")

    user_id = str(me()["id"])
    desired = {}
    invalid = []
    for project in st.session_state.projects:
        try:
            desired[("project", str(project["id"]))] = {
                "summary": f"Anti Gooner - Deadline : {project['name']}",
                "description": project.get("desc", ""),
                "due": str(project["due"]),
            }
        except (KeyError, TypeError) as exc:
            invalid.append(f"Projet sans deadline ou identifiant valide : {exc}")
        for task in project.get("tasks", []):
            if task.get("done"):
                continue
            try:
                desired[("task", str(task["id"]))] = {
                    "summary": f"{project['name']} : {task['title']}",
                    "description": f"Responsable : {task.get('owner', 'Tout le monde')}",
                    "due": str(task["due"]),
                }
            except (KeyError, TypeError) as exc:
                invalid.append(f"Tâche sans deadline ou identifiant valide : {exc}")

    rows = rest(
        "GET", "google_calendar_events",
        params={"user_id": f"eq.{user_id}", "select": "entity_type,entity_id,google_event_id"},
    )
    existing = {
        (str(r["entity_type"]), str(r["entity_id"])): r["google_event_id"]
        for r in rows
    }
    created = updated = removed = failed = 0
    errors = list(invalid)

    for key, item in desired.items():
        entity_type, entity_id = key
        event_id = existing.get(key)
        try:
            due = date.fromisoformat(item["due"][:10])
            event = {
                "summary": item["summary"],
                "description": item["description"],
                "start": {"date": due.isoformat()},
                "end": {"date": (due + timedelta(days=1)).isoformat()},
            }
            stable_id = hashlib.sha256(
                f"{user_id}:{entity_type}:{entity_id}".encode()
            ).hexdigest()

            if event_id:
                try:
                    gcal_exec(service.events().update(
                        calendarId="primary", eventId=event_id, body=event
                    ))
                    updated += 1
                except HttpError as exc:
                    if exc.resp.status != 404:
                        raise
                    event_id = None

            if not event_id:
                event["id"] = stable_id
                try:
                    gcal_exec(service.events().insert(calendarId="primary", body=event))
                    created += 1
                except HttpError as exc:
                    if exc.resp.status != 409:
                        raise
                    # L'événement existe déjà (ou a été supprimé : on le ressuscite).
                    event["status"] = "confirmed"
                    gcal_exec(service.events().update(
                        calendarId="primary", eventId=stable_id, body=event
                    ))
                    updated += 1
                event_id = stable_id

            rest(
                "POST", "google_calendar_events",
                params={"on_conflict": "user_id,entity_type,entity_id"},
                json={
                    "user_id": user_id, "entity_type": entity_type,
                    "entity_id": entity_id, "google_event_id": event_id,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
            )
        except Exception as exc:
            failed += 1
            errors.append(f"{item.get('summary', entity_id)} : {type(exc).__name__}: {exc}")
        time.sleep(0.1)

    # Supprime les événements devenus inutiles seulement si leur suppression réussit.
    for key, event_id in existing.items():
        if key in desired:
            continue
        try:
            try:
                gcal_exec(service.events().delete(calendarId="primary", eventId=event_id))
            except HttpError as exc:
                if exc.resp.status not in (404, 410):
                    raise
            rest("DELETE", "google_calendar_events", params={
                "user_id": f"eq.{user_id}",
                "entity_type": f"eq.{key[0]}",
                "entity_id": f"eq.{key[1]}",
            })
            removed += 1
        except Exception as exc:
            failed += 1
            errors.append(f"Suppression {key[0]} {key[1]} : {type(exc).__name__}: {exc}")
        time.sleep(0.1)

    return {
        "created": created, "updated": updated, "removed": removed,
        "failed": failed, "target": len(desired), "errors": errors,
    }


def show_sync_report(report, prefix="Google Calendar"):
    st.success(
        f"{prefix} : {report['created']} créés, "
        f"{report['updated']} mis à jour, {report['removed']} supprimés."
    )
    if report["failed"]:
        st.warning(f"{report['failed']} élément(s) en échec sur {report['target']} à synchroniser.")
    for message in report["errors"][:8]:
        st.caption(message)


def run_sync(prefix="Google Calendar"):
    with st.spinner("Synchronisation en cours…"):
        try:
            show_sync_report(sync_google_calendar(), prefix)
        except Exception as exc:
            st.error(f"Synchronisation impossible : {type(exc).__name__}: {exc}")


def profiles():
    return rest("GET", "profiles", params={"select": "id,name", "order": "name"})


def load():
    """Projets dont l'utilisateur connecté est membre."""
    rows = rest("GET", "projects", params={"member_ids": f"cs.{{{me()['id']}}}", "select": "data"})
    return [r["data"] for r in rows]


def save():
    try:
        rows = [
            {"id": p["id"], "member_ids": p["member_ids"], "data": p}
            for p in st.session_state.projects
        ]
        if rows:
            rest("POST", "projects", json=rows, headers={"Prefer": "resolution=merge-duplicates,return=minimal"})
    except Exception:
        st.toast(tr("Sauvegarde impossible, réessaie dans un instant."), icon="⚠️")


# ---------- Comptes (connexion Google via st.login) ----------
def register(name, code, email):
    invite = str(st.secrets.get("INVITE_CODE", ""))
    if not invite:
        return tr("Inscriptions fermées (INVITE_CODE absent des Secrets).")
    if not hmac.compare_digest(code.strip().encode(), invite.encode()):
        return tr("Code d'invitation incorrect.")
    name = name.strip()
    if len(name) < 2:
        return tr("Prénom trop court.")
    if any(x["name"].lower() == name.lower() for x in profiles()):
        return tr("Ce nom est déjà pris.")
    try:
        rest(
            "POST", "profiles",
            json={"id": str(uuid.uuid4()), "name": name, "email": email},
            headers={"Prefer": "return=minimal"},
        )
    except Exception:
        return tr("Création impossible, réessaie dans un instant.")
    return None


def hero(text):
    st.markdown(
        '<div class="banner"><h1>anti gooner</h1><p>' + text + "</p></div>", unsafe_allow_html=True
    )


def auth_gate():
    if "user" in st.session_state:
        return
    if not getattr(st.user, "is_logged_in", False):
        hero(tr("Connecte-toi pour retrouver tes projets."))
        st.button(tr("Continuer avec Google"), type="primary", on_click=st.login, key="google_login")
        st.stop()

    email = (getattr(st.user, "email", "") or "").strip().lower()
    if not email or getattr(st.user, "email_verified", True) is False:
        hero(tr("Ton compte Google n'a pas d'email vérifié."))
        st.button(tr("Se déconnecter"), on_click=st.logout, key="logout_err")
        st.stop()

    try:
        rows = rest("GET", "profiles", params={"email": f"eq.{email}", "select": "id,name"})
    except Exception:
        st.error(tr("Impossible de joindre la base de données (projet Supabase en pause, ou URL / clé incorrectes). Tes données ne sont pas perdues."))
        st.stop()
    if rows:
        st.session_state.user = {"id": rows[0]["id"], "name": rows[0]["name"]}
        return

    # Première connexion : prénom + code d'invitation
    hero(tr("Première connexion avec {email}. Choisis ton prénom et entre le code d'invitation.").format(email=email))
    with st.form("onboarding", border=False):
        name = st.text_input(tr("Ton prénom (visible par tes amis)"), key="ob_name", autocomplete="given-name")
        code = st.text_input(tr("Code d'invitation"), type="password", key="ob_code", autocomplete="off")
        go = st.form_submit_button(tr("Créer mon compte"), type="primary")
    st.button(tr("Se déconnecter"), on_click=st.logout, key="logout_ob")
    if go:
        err = register(name, code, email)
        if err:
            st.error(err)
        else:
            st.rerun()
    st.stop()


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
        return f'<span class="badge done">{tr("terminé")}</span>'
    n = (parse(d) - date.today()).days
    if n < 0:
        txt, cls = tr("en retard de {n} j").format(n=-n), "late"
    elif n == 0:
        txt, cls = tr("aujourd'hui"), "soon"
    elif n == 1:
        txt, cls = tr("demain"), "soon"
    else:
        txt, cls = tr("dans {n} j").format(n=n), ("soon" if n <= 3 else "ok")
    return f'<span class="badge {cls}">{txt}</span>'


# ---------- Callbacks ----------
def set_open(pid):
    st.session_state.open = pid


def toggle(pid, tid):
    who = me()["name"]
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
    try:
        rest("DELETE", "projects", params={"id": f"eq.{pid}"})
    except Exception:
        st.toast(tr("Suppression impossible, réessaie dans un instant."), icon="⚠️")
        return
    st.session_state.projects = [p for p in st.session_state.projects if p["id"] != pid]
    st.session_state.open = None


def add_member(pid):
    name = st.session_state.get("new_member")
    p = get_project(pid)
    match = next((x for x in profiles() if x["name"] == name), None)
    if match and match["id"] not in p["member_ids"]:
        p["members"].append(match["name"])
        p["member_ids"].append(match["id"])
        save()
    st.session_state.new_member = None


def set_project_due(pid):
    get_project(pid)["due"] = st.session_state[f"pdue_{pid}"].isoformat()
    save()


def set_task_due(pid, tid):
    for t in get_project(pid)["tasks"]:
        if t["id"] == tid:
            t["due"] = st.session_state[f"due_{tid}"].isoformat()
    save()


# ---------- Dialogues ----------
@st.dialog(tr("Nouveau projet"))
def new_project():
    name = st.text_input(tr("Nom du projet"), placeholder=tr("Ex. Étude de cas marketing"))
    desc = st.text_area(tr("Description (facultatif)"), height=80)
    due = st.date_input(
        tr("Deadline du projet"), value=date.today() + timedelta(days=14), format="DD/MM/YYYY"
    )
    others = [x for x in profiles() if x["id"] != me()["id"]]
    chosen = st.multiselect(
        tr("Qui est dans l'équipe ?"), [x["name"] for x in others], placeholder=tr("Ajoute des amis inscrits")
    )
    if st.button(tr("Créer le projet"), type="primary", use_container_width=True):
        if not name.strip():
            st.error(tr("Donne un nom au projet."))
            return
        st.session_state.projects.append(
            {
                "id": uid(),
                "name": name.strip(),
                "desc": desc.strip(),
                "due": due.isoformat(),
                "color": COLORS[len(st.session_state.projects) % len(COLORS)],
                "members": [me()["name"]] + chosen,
                "member_ids": [me()["id"]] + [x["id"] for x in others if x["name"] in chosen],
                "owner_id": me()["id"],
                "tasks": [],
            }
        )
        save()
        st.rerun()


@st.dialog(tr("Nouvelle tâche"))
def new_task(pid):
    p = get_project(pid)
    title = st.text_input(tr("Tâche"), placeholder=tr("Ex. Rédiger l'introduction"))
    c1, c2 = st.columns(2)
    due = c1.date_input(
        "Deadline", value=date.today() + timedelta(days=3), format="DD/MM/YYYY"
    )
    owner = c2.selectbox(tr("Responsable"), ["Tout le monde"] + p["members"], format_func=tr)
    if st.button(tr("Ajouter la tâche"), type="primary", use_container_width=True):
        if not title.strip():
            st.error(tr("Donne un nom à la tâche."))
            return
        p["tasks"].append(
            {"id": uid(), "title": title.strip(), "due": due.isoformat(), "owner": owner, "done": False, "by": ""}
        )
        save()
        st.rerun()


@st.dialog(tr("Supprimer ce projet ?"))
def confirm_delete(pid):
    p = get_project(pid)
    st.write(tr("« {name} » et ses {n} tâche(s) seront supprimés. Cette action est définitive.").format(name=p["name"], n=len(p["tasks"])))
    c1, c2 = st.columns(2)
    if c1.button(tr("Annuler"), use_container_width=True):
        st.rerun()
    if c2.button(tr("Oui, supprimer"), type="primary", use_container_width=True):
        delete_project(pid)
        st.rerun()


# ---------- Vues ----------
def banner():
    projects = st.session_state.projects
    n_open = sum(1 for p in projects for t in p["tasks"] if not t["done"])
    st.markdown(
        f"""<div class="banner"><h1>anti gooner</h1>
<p>{tr("Les deadlines de l'équipe, au même endroit.")}</p>
<span class="pill">{pl(len(projects), "projet", "projets")}</span>
<span class="pill">{pl(n_open, "tâche à faire", "tâches à faire")}</span></div>""",
        unsafe_allow_html=True,
    )


def card(p):
    done, total = progress(p)
    pct = int(done / total * 100) if total else 0
    cnt = tr("{done}/{total} tâches").format(done=done, total=total)
    with st.container(key=f"card_{p['id']}"):
        st.markdown(
            f"""<div class="pc-name"><span class="dot" style="background:{p['color']};color:{p['color']}"></span>{esc(p['name'])}</div>
<div class="pc-desc">{esc(p['desc']) or '&nbsp;'}</div>
<div class="pc-bar"><div style="width:{pct}%;background:{p['color']}"></div></div>
<div class="pc-meta"><span>{cnt}</span>{due_badge(p['due'], total > 0 and done == total)}</div>""",
            unsafe_allow_html=True,
        )
        st.button(
            tr("Ouvrir"), key=f"open_{p['id']}", on_click=set_open, args=(p["id"],), use_container_width=True
        )


def board():
    projects = sorted(st.session_state.projects, key=lambda p: p["due"])
    items = ["add"] + projects
    for r in range(0, len(items), 3):
        cols = st.columns(3, gap="medium")
        for col, item in zip(cols, items[r : r + 3]):
            with col:
                if item == "add":
                    if st.button(tr("+  Nouveau projet"), key="add_tile", use_container_width=True):
                        new_project()
                else:
                    card(item)
    if not projects:
        st.markdown(
            '<div class="empty">' + tr("Aucun projet pour l'instant. Clique sur le + pour créer le premier.") + "</div>",
            unsafe_allow_html=True,
        )
    mine_all = sorted(
        ((p, t) for p in projects for t in p["tasks"] if not t["done"] and t["owner"] in (me()["name"], "Tout le monde")),
        key=lambda x: (x[1]["due"], x[0]["name"]),
    )
    mine = mine_all[:10]
    if mine:
        st.markdown(
            '<div class="side-title" style="margin-top:2.2rem">' + tr("Mes tâches") + "</div>", unsafe_allow_html=True
        )
        for p, t in mine:
            st.markdown(
                f'<div class="mt-row"><span class="dot" style="background:{p["color"]};color:{p["color"]}"></span>'
                f'<span class="t-title">{esc(t["title"])}</span><span class="owner">{esc(p["name"])}</span>'
                f'{due_badge(t["due"])}</div>',
                unsafe_allow_html=True,
            )
        if len(mine_all) > 10:
            st.caption(tr("+ {n} autres tâches").format(n=len(mine_all) - 10))


def make_ics(p):
    def e(x):
        return str(x).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def event(uid_, day, summary, desc):
        d = parse(day)
        return [
            "BEGIN:VEVENT", f"UID:{uid_}@anti-gooner", f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{e(summary)}", f"DESCRIPTION:{e(desc)}", "END:VEVENT",
        ]

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//anti gooner//FR", "CALSCALE:GREGORIAN"]
    lines += event(f"project-{p['id']}", p["due"], f"{tr('Deadline du projet')} : {p['name']}", p["desc"])
    for t in p["tasks"]:
        if not t["done"]:
            lines += event(
                f"task-{t['id']}", t["due"], f"{p['name']} : {t['title']}",
                f"{tr('Responsable')} : {tr(t['owner'])}",
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def task_status(t):
    if t["done"]:
        return "done"
    n = (parse(t["due"]) - date.today()).days
    return "late" if n < 0 else ("soon" if n <= 3 else "ok")


def owner_chip(owner):
    if owner == "Tout le monde":
        letter, color = "👥", "#8E8FB5"
    else:
        letter = owner[:1].upper() or "?"
        color = COLORS[sum(map(ord, owner)) % len(COLORS)]
    return (
        f'<span class="avatar" style="background:{color}22;color:{color};border:1px solid {color}55">'
        f'{esc(letter)}</span><span class="owner">{esc(tr(owner))}</span>'
    )


def project_view(p):
    st.button(tr("←  Retour au board"), key="back", on_click=set_open, args=(None,))
    done, total = progress(p)
    pct = int(done / total * 100) if total else 0
    chips = "".join(f'<span class="chip">{esc(m)}</span>' for m in p["members"])
    meta = tr("{done}/{total} tâches, deadline le {d}").format(done=done, total=total, d=f"{parse(p['due']):%d/%m/%Y}")
    with st.container(key="ph"):
        st.markdown(
            f"""<div class="ph-title"><span class="dot" style="background:{p['color']};color:{p['color']}"></span>{esc(p['name'])}</div>
<div class="ph-desc">{esc(p['desc'])}</div>
<div class="pc-bar"><div style="width:{pct}%;background:{p['color']}"></div></div>
<div class="pc-meta"><span>{meta}</span>{due_badge(p['due'], total > 0 and done == total)}</div>
{chips}""",
            unsafe_allow_html=True,
        )

    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 2], vertical_alignment="center")
    if c1.button(tr("+  Nouvelle tâche"), type="primary", key="add_task", use_container_width=True):
        new_task(p["id"])
    with c2.popover(tr("Gérer le projet"), use_container_width=True):
        with st.form(f"edit_project_{p['id']}", border=False):
            new_name = st.text_input(tr("Nom du projet"), value=p["name"], key=f"pn_{p['id']}")
            new_desc = st.text_area(
                tr("Description (facultatif)"), value=p["desc"], height=90, key=f"pd_{p['id']}"
            )
            saved = st.form_submit_button(tr("Enregistrer"))
        if saved and new_name.strip():
            p["name"] = new_name.strip()
            p["desc"] = new_desc.strip()
            save()
            st.rerun()
        st.divider()
        avail = [x["name"] for x in profiles() if x["id"] not in p["member_ids"]]
        st.selectbox(
            tr("Ajouter un membre"), avail, index=None, key="new_member", placeholder=tr("Choisis un ami inscrit")
        )
        st.button(tr("Ajouter"), key="add_member", on_click=add_member, args=(p["id"],))
        st.date_input(
            tr("Deadline du projet"), value=parse(p["due"]), format="DD/MM/YYYY",
            key=f"pdue_{p['id']}", on_change=set_project_due, args=(p["id"],),
        )
    if p.get("owner_id") == me()["id"] and c3.button(tr("Supprimer"), key="del_project", use_container_width=True):
        confirm_delete(p["id"])
    c4.download_button(
        tr("Ajouter à mon calendrier (.ics)"),
        data=make_ics(p),
        file_name=f"{''.join(ch if ch.isalnum() else '_' for ch in p['name'])}.ics",
        mime="text/calendar",
        on_click="ignore",
        use_container_width=True,
        help=tr("Télécharge un fichier à ouvrir avec Google Agenda, Apple Calendrier ou Outlook : la deadline du projet et ses tâches non terminées y sont ajoutées."),
    )

    locked = False

    st.write("")
    tasks = sorted(p["tasks"], key=lambda t: (t["done"], t["due"]))
    if not tasks:
        st.markdown(
            '<div class="empty">' + tr("Pas encore de tâche. Ajoute la première avec sa deadline.") + "</div>",
            unsafe_allow_html=True,
        )
    last_grp = None
    for t in tasks:
        grp = "done" if t["done"] else "todo"
        if grp != last_grp:
            last_grp = grp
            label, count = (tr("Terminées"), done) if t["done"] else (tr("À faire"), total - done)
            st.markdown(f'<div class="sec">{label}<span>{count}</span></div>', unsafe_allow_html=True)
        with st.container(key=f"task_{task_status(t)}_{t['id']}"):
            c = st.columns([0.08, 1.5, 0.65, 0.6, 0.22], vertical_alignment="center")
            c[0].checkbox(
                tr("fait"), value=t["done"], key=f"chk_{t['id']}", on_change=toggle,
                args=(p["id"], t["id"]), label_visibility="collapsed", disabled=locked,
            )
            cls = "t-title done" if t["done"] else "t-title"
            by = f'<div class="by">{tr("fait par")} {esc(t["by"])}</div>' if t["done"] and t.get("by") else ""
            c[1].markdown(f'<div class="{cls}">{esc(t["title"])}</div>{by}', unsafe_allow_html=True)
            c[2].markdown(owner_chip(t["owner"]), unsafe_allow_html=True)
            c[3].markdown(
                f'{due_badge(t["due"], t["done"])}<span class="date-small">{parse(t["due"]):%d/%m}</span>',
                unsafe_allow_html=True,
            )
            with c[4].popover(":material/more_horiz:"):
                with st.form(f"edit_task_{t['id']}", border=False):
                    new_title = st.text_input(tr("Tâche"), value=t["title"], key=f"tt_{t['id']}")
                    saved_t = st.form_submit_button(tr("Enregistrer"))
                if saved_t and new_title.strip():
                    t["title"] = new_title.strip()
                    save()
                    st.rerun()
                st.date_input(
                    "Deadline", value=parse(t["due"]), format="DD/MM/YYYY",
                    key=f"due_{t['id']}", on_change=set_task_due, args=(p["id"], t["id"]),
                )
                st.divider()
                st.button(
                    tr("Supprimer la tâche"), key=f"rm_{t['id']}", on_click=delete_task,
                    args=(p["id"], t["id"]), use_container_width=True,
                )


def ring(p, active):
    done, total = progress(p)
    pct = round(done / total * 100) if total else 0
    sub = tr("{done}/{total} tâches faites").format(done=done, total=total)
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
        f'<div class="ring-sub">{sub}</div></div></div>'
    )


def sidebar(calendar_connection_row, calendar_error):
    with st.sidebar:
        st.markdown('<div class="side-title">' + tr("Avancement") + "</div>", unsafe_allow_html=True)
        projects = sorted(st.session_state.projects, key=lambda p: p["due"])
        if not projects:
            st.caption(tr("L'avancement de chaque projet apparaîtra ici."))
        for p in projects:
            with st.container(key=f"navc_{p['id']}"):
                st.markdown(ring(p, p["id"] == st.session_state.open), unsafe_allow_html=True)
                st.button(p["name"], key=f"go_{p['id']}", on_click=set_open, args=(p["id"],), use_container_width=True)
        st.markdown(
            '<div class="side-title" style="font-size:1.05rem;margin-top:1.8rem">' + tr("Sauvegarde") + "</div>",
            unsafe_allow_html=True,
        )
        st.download_button(
            tr("Exporter les données"),
            data=json.dumps(st.session_state.projects, ensure_ascii=False, indent=2),
            file_name=f"anti_gooner_{date.today():%Y-%m-%d}.json",
            mime="application/json",
            on_click="ignore",
            use_container_width=True,
        )
        st.caption(tr("Connecté : {name}").format(name=me()["name"]))
        st.markdown('<div class="side-title" style="font-size:1.05rem;margin-top:1.4rem">Google Calendar</div>', unsafe_allow_html=True)

        if calendar_error:
            st.error(f"Lecture de google_calendar_connections impossible : {calendar_error}")
        elif calendar_connection_row:
            st.caption(f"Compte : {calendar_connection_row.get('connected_email') or 'Google'}")
            if st.button("Synchroniser maintenant", key="calendar_sync", use_container_width=True):
                run_sync()
            if st.button("Déconnecter Calendar", key="calendar_disconnect", use_container_width=True):
                st.session_state["calendar_disconnect_confirm"] = True
            if st.session_state.get("calendar_disconnect_confirm"):
                st.warning("La déconnexion arrête la synchronisation. Les événements existants resteront dans Google Calendar.")
                if st.button("Confirmer la déconnexion", key="calendar_disconnect_yes", use_container_width=True):
                    rest("DELETE", "google_calendar_connections", params={"user_id": f"eq.{me()['id']}"})
                    rest("DELETE", "google_calendar_events", params={"user_id": f"eq.{me()['id']}"})
                    st.session_state.pop("calendar_disconnect_confirm", None)
                    st.rerun()
        else:
            if st.button("Connecter Google Calendar", key="calendar_connect", use_container_width=True):
                try:
                    start_calendar_oauth()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Impossible de démarrer Google Calendar : {exc}")
            auth_url = st.session_state.get("calendar_auth_url")
            if auth_url:
                # target="_top" : ouvre Google dans le même onglet (st.link_button ouvre un nouvel onglet)
                components.html(
                    f'''<a href="{html.escape(auth_url, quote=True)}" target="_top"
                    style="display:block;text-align:center;padding:.5rem;border-radius:12px;
                    background:linear-gradient(135deg,#8B7BFF,#6A58F0);color:#fff;
                    font-family:sans-serif;font-weight:600;text-decoration:none">Continuer vers Google</a>''',
                    height=50,
                )

        st.button("Se déconnecter", key="logout", on_click=st.logout, use_container_width=True)


# ---------- Main ----------
st.markdown(CSS, unsafe_allow_html=True)
_, _lang_col = st.columns([5, 1])
with _lang_col:
    st.radio("Langue / Language", ["FR", "EN"], horizontal=True, key="lang", label_visibility="collapsed")
auth_gate()
try:
    handle_calendar_callback()
except Exception as exc:
    st.session_state.pop("calendar_auth_url", None)
    st.query_params.clear()
    st.error(f"Erreur Google Calendar : {type(exc).__name__}: {exc}")
notice = st.session_state.pop("calendar_notice", None)
if notice:
    st.success(notice)
notice_err = st.session_state.pop("calendar_notice_err", None)
if notice_err:
    st.error(notice_err)
if "open" not in st.session_state:
    st.session_state.open = None
try:
    # Rechargé à chaque action : chacun voit les changements des autres
    st.session_state.projects = load()
except Exception:
    st.error(tr("Impossible de joindre la base de données (projet Supabase en pause, ou URL / clé incorrectes). Tes données ne sont pas perdues."))
    st.stop()

# État de la connexion Google Calendar (lu une seule fois par exécution)
try:
    _cal_row = calendar_connection()
    _cal_err = None
except Exception as exc:
    _cal_row, _cal_err = None, f"{type(exc).__name__}: {exc}"

sidebar(_cal_row, _cal_err)
banner()

# Bloc toujours visible, même si la barre latérale est repliée.
if _cal_err:
    st.error(f"Lecture de google_calendar_connections impossible : {_cal_err}")
elif _cal_row:
    if st.button("📅 Synchroniser Google Calendar", key="calendar_sync_main"):
        run_sync("Calendrier synchronisé")
else:
    st.info("Google Calendar non connecté : utilise le bouton « Connecter Google Calendar » dans la barre latérale.")

with st.expander("Diagnostic Google Calendar"):
    st.write({
        "user_id": me()["id"],
        "connexion_trouvee": bool(_cal_row),
        "erreur_lecture": _cal_err,
        "redirect_uri": st.secrets.get("GOOGLE_REDIRECT_URI"),
        "params_url": list(st.query_params.keys()),
    })

current = get_project(st.session_state.open) if st.session_state.open else None
if current:
    project_view(current)
else:
    board()
