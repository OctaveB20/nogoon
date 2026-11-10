"""Logique partagée par les 3 nouvelles versions de l'interface (v1_atelier, v2_console, v3_bento).

Tout ce qui touche aux données (Supabase), aux comptes, à Google Calendar, aux calculs
de charge de travail et aux actions sur les projets/tâches vit ici. Les fichiers de
version ne contiennent que l'interface : mise en page, navigation et direction artistique.
Le fonctionnement est identique à app.py.
"""
import hashlib
import hmac
import html
import json
import os
import secrets as py_secrets
import time
import uuid
from datetime import date, datetime, timedelta, timezone

import requests
import streamlit as st

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Évite l'erreur "Scope has changed" quand Google renvoie des scopes supplémentaires.
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

COLORS = ["#8B7BFF", "#FF8FA3", "#5CE1C6", "#FFC46B", "#6BB6FF", "#C48BFF"]
EVERYONE = "Tout le monde"
DURATION_OPTIONS = list(range(15, 481, 15))
DAY_NAMES = {"FR": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
             "EN": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
MONTHS = {"FR": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
                 "août", "septembre", "octobre", "novembre", "décembre"],
          "EN": ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"]}
WEEKDAYS_LONG = {"FR": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
                 "EN": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

# Libellés contenant une apostrophe, réutilisés dans des f-strings (compatibles Python < 3.12).
TAGLINE = "Les deadlines de l'équipe, au même endroit."
NO_PROJECT = "Aucun projet pour l'instant. Crée le premier."
TODAY = "Aujourd'hui"
TEAM_Q = "Qui est dans l'équipe ?"


def apply_theme(**opts):
    """Applique le thème de la version au démarrage (en plus de son .streamlit/config.toml)."""
    from streamlit import config as _config
    for k, v in opts.items():
        try:
            if _config.get_option(f"theme.{k}") != v:
                _config.set_option(f"theme.{k}", v)
        except Exception:
            pass


# ---------- Traductions ----------
EN = {
    "Les deadlines de l'équipe, au même endroit.": "Your team's deadlines, all in one place.",
    "projet": "project", "projets": "projects",
    "tâche à faire": "task to do", "tâches à faire": "tasks to do",
    "tâche": "task", "tâches": "tasks",
    "Connecte-toi pour retrouver tes projets.": "Log in to find your projects.",
    "Se connecter": "Log in",
    "Ton prénom (visible par tes amis)": "Your first name (visible to your friends)",
    "Code d'invitation": "Invitation code", "Créer mon compte": "Create my account",
    "Inscriptions fermées (INVITE_CODE absent des Secrets).": "Sign-ups are closed (INVITE_CODE missing from Secrets).",
    "Code d'invitation incorrect.": "Wrong invitation code.",
    "Ce nom est déjà pris.": "This name is already taken.",
    "Sauvegarde impossible, réessaie dans un instant.": "Could not save, try again in a moment.",
    "Suppression impossible, réessaie dans un instant.": "Could not delete, try again in a moment.",
    "Impossible de joindre la base de données (projet Supabase en pause, ou URL / clé incorrectes). Tes données ne sont pas perdues.": "Cannot reach the database (Supabase project paused, or wrong URL / key). Your data is not lost.",
    "terminé": "done", "aujourd'hui": "today", "demain": "tomorrow",
    "en retard de {n} j": "{n} d overdue", "dans {n} j": "in {n} d",
    "{done}/{total} tâches": "{done}/{total} tasks",
    "{done}/{total} tâches faites": "{done}/{total} tasks done",
    "Ouvrir": "Open", "Nouveau projet": "New project",
    "Aucun projet pour l'instant. Crée le premier.": "No projects yet. Create the first one.",
    "Mes tâches": "My tasks", "Retour": "Back",
    "Nouvelle tâche": "New task", "Gérer le projet": "Manage project",
    "Ajouter un membre": "Add a member", "Choisis un ami inscrit": "Pick a registered friend",
    "Ajouter": "Add", "Deadline du projet": "Project deadline", "Supprimer": "Delete",
    "Pas encore de tâche. Ajoute la première avec sa deadline.": "No tasks yet. Add the first one with its deadline.",
    "fait": "done", "fait par": "done by", "Tout le monde": "Everyone",
    "Nom du projet": "Project name",
    "Ex. Étude de cas marketing": "E.g. Marketing case study",
    "Description (facultatif)": "Description (optional)",
    "Qui est dans l'équipe ?": "Who's on the team?",
    "Ajoute des amis inscrits": "Add registered friends",
    "Créer le projet": "Create project", "Donne un nom au projet.": "Give the project a name.",
    "Tâche": "Task", "Ex. Rédiger l'introduction": "E.g. Write the introduction",
    "Responsable": "Owner", "Ajouter la tâche": "Add task",
    "Donne un nom à la tâche.": "Give the task a name.",
    "Supprimer ce projet ?": "Delete this project?",
    "« {name} » et ses {n} tâche(s) seront supprimés. Cette action est définitive.": "\"{name}\" and its {n} task(s) will be deleted. This cannot be undone.",
    "Annuler": "Cancel", "Oui, supprimer": "Yes, delete",
    "Avancement": "Progress",
    "L'avancement de chaque projet apparaîtra ici.": "Each project's progress will show up here.",
    "Sauvegarde": "Backup", "Exporter les données": "Export data",
    "Connecté : {name}": "Logged in: {name}", "Se déconnecter": "Log out",
    "Continuer avec Google": "Continue with Google",
    "Ton compte Google n'a pas d'email vérifié.": "Your Google account has no verified email.",
    "Première connexion avec {email}. Choisis ton prénom et entre le code d'invitation.": "First login with {email}. Pick your first name and enter the invitation code.",
    "Prénom trop court.": "First name too short.",
    "Création impossible, réessaie dans un instant.": "Could not create the account, try again in a moment.",
    "+ {n} autres tâches": "+ {n} more tasks",
    "À faire": "To do", "Terminées": "Done",
    "Supprimer la tâche": "Delete task", "Modifier": "Edit",
    "Ajouter à mon calendrier (.ics)": "Add to my calendar (.ics)",
    "Durée estimée": "Estimated duration", "Charge de travail": "Workload",
    "Projets": "Projects", "Planning": "Planning", "Aujourd'hui": "Today",
    "Cette semaine": "This week", "Heures restantes": "Hours remaining",
    "Aucune tâche planifiée sur cette période.": "No tasks due during this period.",
    "Modifier le projet": "Edit project", "Modifier la tâche": "Edit task",
    "Enregistrer les modifications": "Save changes",
    "Charge basée sur les deadlines": "Workload based on task due dates",
    "Tâches ouvertes": "Open tasks", "Tâches terminées": "Completed tasks",
    "Télécharge un fichier à ouvrir avec Google Agenda, Apple Calendrier ou Outlook : la deadline du projet et ses tâches non terminées y sont ajoutées.": "Downloads a file to open with Google Calendar, Apple Calendar or Outlook: the project deadline and its unfinished tasks get added.",
    "Semaine": "Week", "Mois": "Month",
    "Semaine précédente": "Previous week", "Semaine suivante": "Next week",
    "Mois précédent": "Previous month", "Mois suivant": "Next month",
    "Ouvertes": "Open", "Aucune tâche avec une échéance ce jour-là.": "No task due that day.",
    "Aucune tâche ouverte à venir.": "No upcoming open tasks.",
    "Aucune tâche terminée pour le moment.": "No completed tasks yet.",
    "Organise ton travail, fixe une échéance et invite ton équipe.": "Organise your work, set a deadline and invite your team.",
    "Informations du projet": "Project details", "Détails de la tâche": "Task details",
    "Quel est l'objectif de ce projet ?": "What is this project's goal?",
    "{n} membre(s) dans l'équipe": "{n} team member(s)",
    "Projet créé ✨": "Project created ✨", "Projet mis à jour ✨": "Project updated ✨",
    "Tâche mise à jour ✨": "Task updated ✨", "Tâche ajoutée ✨": "Task added ✨",
    "Ajoute les informations essentielles, puis estime le temps nécessaire.": "Add the essentials, then estimate the time needed.",
    "Modifie les informations du projet et les personnes qui y participent.": "Edit the project's details and who takes part.",
    "Ajuste les détails, la deadline et le temps nécessaire à cette tâche.": "Adjust the details, deadline and time needed for this task.",
    "Charge estimée : {d}": "Estimated load: {d}",
    "Synchroniser maintenant": "Sync now", "Synchroniser Google Calendar": "Sync Google Calendar",
    "Déconnecter Calendar": "Disconnect Calendar", "Confirmer la déconnexion": "Confirm disconnect",
    "Connecter Google Calendar": "Connect Google Calendar", "Continuer vers Google": "Continue to Google",
    "La déconnexion arrête la synchronisation. Les événements existants resteront dans Google Calendar.": "Disconnecting stops syncing. Existing events stay in Google Calendar.",
    "Google Calendar non connecté.": "Google Calendar not connected.",
    "Compte : {email}": "Account: {email}", "Compte": "Account",
    "Synchronisation en cours…": "Syncing…", "Calendrier synchronisé": "Calendar synced",
    "Membres": "Members", "Deadline": "Deadline", "Durée": "Duration",
    "Langue": "Language", "Réglages": "Settings", "Accueil": "Home",
    "Bonjour {name}": "Hi {name}", "À venir": "Upcoming", "En retard": "Overdue",
    "Bientôt": "Soon", "Plus tard": "Later", "Tout est à jour.": "All caught up.",
    "Rien pour toi ici. Profite 🌿": "Nothing for you here. Enjoy 🌿",
    "Ajout rapide": "Quick add", "Ce jour-là": "That day",
    "Total": "Total", "Libre": "Free", "Tâches": "Tasks",
    "Index": "Index", "des projets": "of projects", "Index des projets": "Project index",
    "Ton focus": "Your focus", "Tes projets": "Your projects", "Voir tout": "See all",
    "Reste à faire": "Left to do", "Équipe": "Team", "Prochaine deadline": "Next deadline",
    "Raccourcis": "Shortcuts", "Système": "System", "Statut": "Status", "Propriétaire": "Owner",
    "Progression": "Progress", "Ajouter une tâche…": "Add a task…",
}


def lang():
    return st.session_state.get("lang", "FR")


def tr(s):
    return EN.get(s, s) if lang() == "EN" else s


def pl(n, one, many):
    single = n == 1 or (n == 0 and lang() != "EN")
    return f"{n} {tr(one if single else many)}"


def fmt_long(d):
    """« mardi 10 novembre » / « Tuesday 10 November »."""
    return f"{WEEKDAYS_LONG[lang()][d.weekday()]} {d.day} {MONTHS[lang()][d.month - 1]}"


def fmt_month(d):
    return f"{MONTHS[lang()][d.month - 1]} {d.year}"


def fmt_short(d):
    return f"{d.day} {MONTHS[lang()][d.month - 1][:3]}"


# ---------- Supabase ----------
URL = KEY = None
H = {}


def init_backend():
    """Lit les secrets Supabase. À appeler après st.set_page_config."""
    global URL, KEY, H
    try:
        URL = st.secrets["SUPABASE_URL"].rstrip("/")
        KEY = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Secrets Supabase introuvables (SUPABASE_URL, SUPABASE_KEY, SUPABASE_ANON_KEY, INVITE_CODE).")
        st.stop()
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}


def rest(method, path, headers=None, **kw):
    r = requests.request(
        method, f"{URL}/rest/v1/{path}",
        headers={**H, "Content-Type": "application/json", **(headers or {})}, timeout=10, **kw,
    )
    if not r.ok:
        raise RuntimeError(f"Supabase {r.status_code} sur {path} : {r.text[:300]}")
    return r.json() if r.content else None


def me():
    return st.session_state.user


def profiles():
    return rest("GET", "profiles", params={"select": "id,name", "order": "name"})


def load():
    rows = rest("GET", "projects", params={"member_ids": f"cs.{{{me()['id']}}}", "select": "data"})
    return [r["data"] for r in rows]


def save():
    try:
        rows = [{"id": p["id"], "member_ids": p["member_ids"], "data": p} for p in st.session_state.projects]
        if rows:
            rest("POST", "projects", json=rows, headers={"Prefer": "resolution=merge-duplicates,return=minimal"})
    except Exception:
        st.toast(tr("Sauvegarde impossible, réessaie dans un instant."), icon="⚠️")


# ---------- Google Calendar ----------
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def calendar_redirect_uri():
    return st.secrets["GOOGLE_REDIRECT_URI"].strip()


def calendar_flow(state):
    config = {"web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [calendar_redirect_uri()],
    }}
    # Le Flow est recréé après la redirection : pas de PKCE auto-généré.
    flow = Flow.from_client_config(config, scopes=CALENDAR_SCOPES, state=state, autogenerate_code_verifier=False)
    flow.redirect_uri = calendar_redirect_uri()
    return flow


def calendar_fernet():
    return Fernet(st.secrets["GOOGLE_TOKEN_ENCRYPTION_KEY"].encode())


def calendar_connection():
    rows = rest("GET", "google_calendar_connections", params={
        "user_id": f"eq.{me()['id']}",
        "select": "user_id,refresh_token_encrypted,connected_email,scopes", "limit": "1",
    })
    return rows[0] if rows else None


def start_calendar_oauth():
    state = py_secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    rest("POST", "google_calendar_oauth_states", json={
        "state": state, "user_id": me()["id"], "expires_at": (now + timedelta(minutes=10)).isoformat(),
    }, headers={"Prefer": "return=minimal"})
    url, _ = calendar_flow(state).authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    st.session_state["calendar_auth_url"] = url


def handle_calendar_callback():
    params = st.query_params
    if params.get("error"):
        st.session_state["calendar_notice_err"] = "Autorisation Google Calendar refusée ou annulée."
        st.session_state.pop("calendar_auth_url", None)
        st.query_params.clear()
        st.rerun()
    code, state = params.get("code"), params.get("state")
    if not code or not state:
        return
    valid = rest("GET", "google_calendar_oauth_states", params={
        "state": f"eq.{state}", "user_id": f"eq.{me()['id']}",
        "expires_at": "gt." + datetime.now(timezone.utc).isoformat(), "select": "state", "limit": "1",
    })
    if not valid:
        st.session_state["calendar_notice_err"] = "Demande Google expirée ou invalide. Recommence la connexion."
        st.session_state.pop("calendar_auth_url", None)
        st.query_params.clear()
        st.rerun()
    flow = calendar_flow(state)
    flow.fetch_token(code=code)
    creds = flow.credentials
    google_email = build("oauth2", "v2", credentials=creds, cache_discovery=False).userinfo().get().execute()["email"]
    old = calendar_connection()
    refresh_token = creds.refresh_token
    if not refresh_token and old:
        refresh_token = calendar_fernet().decrypt(old["refresh_token_encrypted"].encode()).decode()
    if not refresh_token:
        raise RuntimeError("Google n'a pas renvoyé de jeton de renouvellement. Révoque l'accès existant à Anti Gooner dans ton compte Google, puis recommence.")
    saved = rest("POST", "google_calendar_connections", params={"on_conflict": "user_id"}, json={
        "user_id": me()["id"],
        "refresh_token_encrypted": calendar_fernet().encrypt(refresh_token.encode()).decode(),
        "connected_email": google_email, "scopes": CALENDAR_SCOPES,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }, headers={"Prefer": "resolution=merge-duplicates,return=representation"})
    if not saved:
        raise RuntimeError("Écriture dans google_calendar_connections sans effet (RLS ou contrainte ?)")
    rest("DELETE", "google_calendar_oauth_states", params={"state": f"eq.{state}"})
    st.session_state.pop("calendar_auth_url", None)
    st.session_state["calendar_notice"] = f"Google Calendar connecté : {google_email}"
    st.query_params.clear()
    st.rerun()


def calendar_service():
    connection = calendar_connection()
    if not connection:
        return None
    creds = Credentials(
        token=None,
        refresh_token=calendar_fernet().decrypt(connection["refresh_token_encrypted"].encode()).decode(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"], client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
        scopes=CALENDAR_SCOPES,
    )
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def gcal_exec(request, tries=5):
    for i in range(tries):
        try:
            return request.execute()
        except HttpError as exc:
            if i < tries - 1 and (exc.resp.status in (429, 500, 503) or "ratelimit" in str(exc).lower()):
                time.sleep(0.5 * 2 ** i)
                continue
            raise


def sync_google_calendar():
    service = calendar_service()
    if service is None:
        raise RuntimeError("Connecte d'abord ton compte Google Calendar.")
    user_id = str(me()["id"])
    desired, invalid = {}, []
    for project in st.session_state.projects:
        try:
            desired[("project", str(project["id"]))] = {
                "summary": f"Anti Gooner - Deadline : {project['name']}",
                "description": project.get("desc", ""), "due": str(project["due"]),
            }
        except (KeyError, TypeError) as exc:
            invalid.append(f"Projet sans deadline ou identifiant valide : {exc}")
        for task in project.get("tasks", []):
            if task.get("done"):
                continue
            try:
                desired[("task", str(task["id"]))] = {
                    "summary": f"{project['name']} : {task['title']}",
                    "description": f"Responsable : {task.get('owner', EVERYONE)}", "due": str(task["due"]),
                }
            except (KeyError, TypeError) as exc:
                invalid.append(f"Tâche sans deadline ou identifiant valide : {exc}")
    rows = rest("GET", "google_calendar_events", params={"user_id": f"eq.{user_id}", "select": "entity_type,entity_id,google_event_id"})
    existing = {(str(r["entity_type"]), str(r["entity_id"])): r["google_event_id"] for r in rows}
    created = updated = removed = failed = 0
    errors = list(invalid)
    for key, item in desired.items():
        entity_type, entity_id = key
        event_id = existing.get(key)
        try:
            due = date.fromisoformat(item["due"][:10])
            event = {"summary": item["summary"], "description": item["description"],
                     "start": {"date": due.isoformat()}, "end": {"date": (due + timedelta(days=1)).isoformat()}}
            stable_id = hashlib.sha256(f"{user_id}:{entity_type}:{entity_id}".encode()).hexdigest()
            if event_id:
                try:
                    gcal_exec(service.events().update(calendarId="primary", eventId=event_id, body=event))
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
                    event["status"] = "confirmed"
                    gcal_exec(service.events().update(calendarId="primary", eventId=stable_id, body=event))
                    updated += 1
                event_id = stable_id
            rest("POST", "google_calendar_events", params={"on_conflict": "user_id,entity_type,entity_id"}, json={
                "user_id": user_id, "entity_type": entity_type, "entity_id": entity_id,
                "google_event_id": event_id, "updated_at": datetime.now(timezone.utc).isoformat(),
            }, headers={"Prefer": "resolution=merge-duplicates,return=minimal"})
        except Exception as exc:
            failed += 1
            errors.append(f"{item.get('summary', entity_id)} : {type(exc).__name__}: {exc}")
        time.sleep(0.1)
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
                "user_id": f"eq.{user_id}", "entity_type": f"eq.{key[0]}", "entity_id": f"eq.{key[1]}"})
            removed += 1
        except Exception as exc:
            failed += 1
            errors.append(f"Suppression {key[0]} {key[1]} : {type(exc).__name__}: {exc}")
        time.sleep(0.1)
    return {"created": created, "updated": updated, "removed": removed,
            "failed": failed, "target": len(desired), "errors": errors}


def run_sync(prefix="Google Calendar"):
    with st.spinner(tr("Synchronisation en cours…")):
        try:
            report = sync_google_calendar()
        except Exception as exc:
            st.error(f"Synchronisation impossible : {type(exc).__name__}: {exc}")
            return
    st.success(f"{prefix} : {report['created']} créés, {report['updated']} mis à jour, {report['removed']} supprimés.")
    if report["failed"]:
        st.warning(f"{report['failed']} élément(s) en échec sur {report['target']} à synchroniser.")
    for message in report["errors"][:8]:
        st.caption(message)


def disconnect_calendar():
    rest("DELETE", "google_calendar_connections", params={"user_id": f"eq.{me()['id']}"})
    rest("DELETE", "google_calendar_events", params={"user_id": f"eq.{me()['id']}"})
    st.session_state.pop("calendar_disconnect_confirm", None)


def calendar_panel(cal_row, cal_err, link_style):
    """Bloc Google Calendar complet (connexion, synchro, déconnexion confirmée).

    `link_style` : CSS inline du lien « Continuer vers Google » (rendu dans une iframe,
    target=_top pour rester dans le même onglet)."""
    import streamlit.components.v1 as components
    if cal_err:
        st.error(f"Lecture de google_calendar_connections impossible : {cal_err}")
        return
    if cal_row:
        st.caption(tr("Compte : {email}").format(email=cal_row.get("connected_email") or "Google"))
        if st.button(tr("Synchroniser maintenant"), key="calendar_sync", use_container_width=True):
            run_sync()
        if st.button(tr("Déconnecter Calendar"), key="calendar_disconnect", use_container_width=True):
            st.session_state["calendar_disconnect_confirm"] = True
        if st.session_state.get("calendar_disconnect_confirm"):
            st.warning(tr("La déconnexion arrête la synchronisation. Les événements existants resteront dans Google Calendar."))
            if st.button(tr("Confirmer la déconnexion"), key="calendar_disconnect_yes", use_container_width=True):
                disconnect_calendar()
                st.rerun()
        return
    st.caption(tr("Google Calendar non connecté."))
    if st.button(tr("Connecter Google Calendar"), key="calendar_connect", use_container_width=True):
        try:
            start_calendar_oauth()
            st.rerun()
        except Exception as exc:
            st.error(f"Impossible de démarrer Google Calendar : {exc}")
    auth_url = st.session_state.get("calendar_auth_url")
    if auth_url:
        components.html(
            f'<a href="{html.escape(auth_url, quote=True)}" target="_top" style="{link_style}">'
            f'{esc(tr("Continuer vers Google"))}</a>', height=54)


# ---------- Comptes ----------
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
        rest("POST", "profiles", json={"id": str(uuid.uuid4()), "name": name, "email": email},
             headers={"Prefer": "return=minimal"})
    except Exception:
        return tr("Création impossible, réessaie dans un instant.")
    return None


def auth_gate(hero):
    """Connexion Google (st.login) puis onboarding. `hero(text)` affiche l'écran d'accueil de la version."""
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
    hero(tr("Première connexion avec {email}. Choisis ton prénom et entre le code d'invitation.").format(email=esc(email)))
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


def bootstrap():
    """Après connexion : retour OAuth Calendar, notifications, chargement des projets.

    Renvoie (cal_row, cal_err)."""
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
    st.session_state.setdefault("open", None)
    try:
        # Rechargé à chaque action : chacun voit les changements des autres.
        st.session_state.projects = load()
    except Exception:
        st.error(tr("Impossible de joindre la base de données (projet Supabase en pause, ou URL / clé incorrectes). Tes données ne sont pas perdues."))
        st.stop()
    try:
        return calendar_connection(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


# ---------- Utilitaires ----------
def uid():
    return uuid.uuid4().hex[:8]


def esc(s):
    return html.escape(s or "")


def parse(d):
    return date.fromisoformat(d)


def get_project(pid):
    return next((p for p in st.session_state.projects if p["id"] == pid), None)


def sorted_projects():
    return sorted(st.session_state.projects, key=lambda p: p["due"])


def progress(p):
    total = len(p["tasks"])
    done = sum(1 for t in p["tasks"] if t["done"])
    return done, total


def pct(p):
    done, total = progress(p)
    return round(done / total * 100) if total else 0


def project_finished(p):
    done, total = progress(p)
    return total > 0 and done == total


def due_info(d, done=False):
    """(classe, libellé) : late / soon / ok / done."""
    if done:
        return "done", tr("terminé")
    n = (parse(d) - date.today()).days
    if n < 0:
        return "late", tr("en retard de {n} j").format(n=-n)
    if n == 0:
        return "soon", tr("aujourd'hui")
    if n == 1:
        return "soon", tr("demain")
    return ("soon" if n <= 3 else "ok"), tr("dans {n} j").format(n=n)


def task_status(t):
    return due_info(t["due"], t["done"])[0]


def owner_color(owner):
    if owner == EVERYONE:
        return "#8E8FB5"
    return COLORS[sum(map(ord, owner)) % len(COLORS)]


def owner_initial(owner):
    return "👥" if owner == EVERYONE else (owner[:1].upper() or "?")


def open_count():
    return sum(1 for p in st.session_state.projects for t in p["tasks"] if not t["done"])


def my_open_tasks():
    """Tâches non faites qui me sont attribuées (ou à tout le monde), triées par deadline."""
    return sorted(
        ((p, t) for p in st.session_state.projects for t in p["tasks"]
         if not t["done"] and t["owner"] in (me()["name"], EVERYONE)),
        key=lambda x: (x[1]["due"], x[0]["name"]),
    )


def format_duration(minutes):
    minutes = int(minutes or 60)
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours} h {mins:02d}"
    if hours:
        return f"{hours} h"
    return f"{mins} min"


def export_json():
    return json.dumps(st.session_state.projects, ensure_ascii=False, indent=2)


def export_name():
    return f"anti_gooner_{date.today():%Y-%m-%d}.json"


def ics_name(p):
    return f"{''.join(ch if ch.isalnum() else '_' for ch in p['name'])}.ics"


def make_ics(p):
    def e(x):
        return str(x).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def event(uid_, day, summary, desc):
        d = parse(day)
        return ["BEGIN:VEVENT", f"UID:{uid_}@anti-gooner", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d + timedelta(days=1):%Y%m%d}",
                f"SUMMARY:{e(summary)}", f"DESCRIPTION:{e(desc)}", "END:VEVENT"]

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//anti gooner//FR", "CALSCALE:GREGORIAN"]
    lines += event(f"project-{p['id']}", p["due"], f"{tr('Deadline du projet')} : {p['name']}", p["desc"])
    for t in p["tasks"]:
        if not t["done"]:
            lines += event(f"task-{t['id']}", t["due"], f"{p['name']} : {t['title']}", f"{tr('Responsable')} : {tr(t['owner'])}")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def ics_button(p, label=None, key=None):
    st.download_button(
        label or tr("Ajouter à mon calendrier (.ics)"), data=make_ics(p), file_name=ics_name(p),
        mime="text/calendar", on_click="ignore", use_container_width=True, key=key,
        help=tr("Télécharge un fichier à ouvrir avec Google Agenda, Apple Calendrier ou Outlook : la deadline du projet et ses tâches non terminées y sont ajoutées."),
    )


def export_button(label=None, key=None):
    st.download_button(label or tr("Exporter les données"), data=export_json(), file_name=export_name(),
                       mime="application/json", on_click="ignore", use_container_width=True, key=key)


# ---------- Charge de travail ----------
def workload_data():
    rows = []
    for project in st.session_state.projects:
        for task in project.get("tasks", []):
            try:
                due = parse(task["due"])
            except (KeyError, TypeError, ValueError):
                continue
            rows.append({
                "date": due, "minutes": max(0, int(task.get("duration_minutes", 60) or 60)),
                "title": task.get("title", ""), "project": project.get("name", ""),
                "project_id": project.get("id"), "task_id": task.get("id"),
                "owner": task.get("owner", ""), "done": bool(task.get("done")),
            })
    return rows


def workload_summary(rows):
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    open_rows = [x for x in rows if not x["done"]]
    return {
        "total": sum(x["minutes"] for x in open_rows),
        "today": sum(x["minutes"] for x in open_rows if x["date"] == today),
        "week": sum(x["minutes"] for x in open_rows if monday <= x["date"] < monday + timedelta(days=7)),
    }


def workload_period():
    """Gère l'état Semaine/Mois + navigation. Renvoie (view, start, end, day_dates, selected_key)."""
    today = date.today()
    st.session_state.setdefault("workload_period", "Semaine")
    view = st.session_state.workload_period
    if view == "Semaine":
        st.session_state.setdefault("workload_week_start", today - timedelta(days=today.weekday()))
        start = st.session_state.workload_week_start
        end = start + timedelta(days=6)
        days = [start + timedelta(days=i) for i in range(7)]
        key = "workload_selected_day"
    else:
        st.session_state.setdefault("workload_month_start", today.replace(day=1))
        start = st.session_state.workload_month_start.replace(day=1)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        first = start - timedelta(days=start.weekday())
        days = [first + timedelta(days=i) for i in range(((end - first).days // 7 + 1) * 7)]
        key = "workload_selected_month_day"
    selected = st.session_state.get(key, today)
    if selected not in days:
        selected = start if view == "Semaine" else min(max(today, start), end)
    st.session_state[key] = selected
    return view, start, end, days, key


def set_period(view):
    st.session_state.workload_period = view


def shift_period(direction):
    if st.session_state.get("workload_period", "Semaine") == "Semaine":
        st.session_state.workload_week_start += timedelta(days=7 * direction)
    else:
        start = st.session_state.workload_month_start.replace(day=1)
        if direction < 0:
            st.session_state.workload_month_start = (start - timedelta(days=1)).replace(day=1)
        else:
            st.session_state.workload_month_start = (start.replace(day=28) + timedelta(days=4)).replace(day=1)


def select_day(key, day):
    st.session_state[key] = day


def period_label(view, start, end):
    if view == "Semaine":
        return f"{fmt_short(start)} – {fmt_short(end)} {end.year}"
    return fmt_month(start).capitalize()


def day_load(rows, day):
    opened = sum(x["minutes"] for x in rows if x["date"] == day and not x["done"])
    finished = sum(x["minutes"] for x in rows if x["date"] == day and x["done"])
    return opened, finished


def find_task(item):
    p = get_project(item["project_id"])
    if not p:
        return None, None
    t = next((t for t in p.get("tasks", []) if str(t.get("id")) == str(item["task_id"])), None)
    return p, t


# ---------- Actions ----------
def set_open(pid):
    st.session_state.open = pid


def toggle(pid, tid, key):
    """Coche/décoche une tâche. `key` = clé du widget checkbox qui a changé."""
    who = me()["name"]
    for t in get_project(pid)["tasks"]:
        if t["id"] == tid:
            t["done"] = bool(st.session_state[key])
            t["by"] = who if t["done"] else ""
    save()


def toggle_value(pid, tid, done):
    """Variante sans checkbox (bouton) : force l'état."""
    who = me()["name"]
    for t in get_project(pid)["tasks"]:
        if t["id"] == tid:
            t["done"] = done
            t["by"] = who if done else ""
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


def add_member(pid, name):
    p = get_project(pid)
    match = next((x for x in profiles() if x["name"] == name), None)
    if match and match["id"] not in p["member_ids"]:
        p["members"].append(match["name"])
        p["member_ids"].append(match["id"])
        save()
        return True
    return False


def create_project(name, desc, due, chosen, others):
    st.session_state.projects.append({
        "id": uid(), "name": name.strip(), "desc": desc.strip(), "due": due.isoformat(),
        "color": COLORS[len(st.session_state.projects) % len(COLORS)],
        "members": [me()["name"]] + chosen,
        "member_ids": [me()["id"]] + [x["id"] for x in others if x["name"] in chosen],
        "owner_id": me()["id"], "tasks": [],
    })
    save()


def add_task(pid, title, due, owner, duration):
    get_project(pid)["tasks"].append({
        "id": uid(), "title": title.strip(), "due": due.isoformat(), "owner": owner,
        "duration_minutes": int(duration), "done": False, "by": "",
    })
    save()


def is_owner(p):
    return p.get("owner_id") == me()["id"]


# ---------- Dialogues (communs aux 3 versions, restylés par chaque CSS) ----------
def _intro(n, text):
    st.markdown(f'<div class="dialog-intro"><b>{n}</b>{esc(text)}</div>', unsafe_allow_html=True)


def open_new_project():
    @st.dialog(tr("Nouveau projet"))
    def _dlg():
        st.caption(tr("Organise ton travail, fixe une échéance et invite ton équipe."))
        _intro("01", tr("Informations du projet"))
        name = st.text_input(tr("Nom du projet"), placeholder=tr("Ex. Étude de cas marketing"))
        desc = st.text_area(tr("Description (facultatif)"), height=90, placeholder=tr("Quel est l'objectif de ce projet ?"))
        due = st.date_input(tr("Deadline du projet"), value=date.today() + timedelta(days=14), format="DD/MM/YYYY")
        _intro("02", tr("Qui est dans l'équipe ?"))
        others = [x for x in profiles() if x["id"] != me()["id"]]
        chosen = st.multiselect(tr("Qui est dans l'équipe ?"), [x["name"] for x in others],
                                placeholder=tr("Ajoute des amis inscrits"), label_visibility="collapsed")
        st.caption("👥 " + tr("{n} membre(s) dans l'équipe").format(n=1 + len(chosen)))
        if st.button(tr("Créer le projet"), type="primary", use_container_width=True):
            if not name.strip():
                st.error(tr("Donne un nom au projet."))
                return
            create_project(name, desc, due, chosen, others)
            st.toast(tr("Projet créé ✨"))
            st.rerun()
    _dlg()


def open_new_task(pid):
    p = get_project(pid)

    @st.dialog(tr("Nouvelle tâche"))
    def _dlg():
        st.caption(tr("Ajoute les informations essentielles, puis estime le temps nécessaire."))
        _intro("01", tr("Détails de la tâche"))
        title = st.text_input(tr("Tâche"), placeholder=tr("Ex. Rédiger l'introduction"))
        c1, c2 = st.columns(2)
        due = c1.date_input(tr("Deadline"), value=date.today() + timedelta(days=3), format="DD/MM/YYYY")
        owner = c2.selectbox(tr("Responsable"), [EVERYONE] + p["members"], format_func=tr)
        duration = st.select_slider(tr("Durée estimée"), options=DURATION_OPTIONS, value=60,
                                    key=f"new_duration_{pid}", format_func=format_duration)
        st.caption(tr("Charge estimée : {d}").format(d=format_duration(duration)))
        if st.button(tr("Ajouter la tâche"), type="primary", use_container_width=True):
            if not title.strip():
                st.error(tr("Donne un nom à la tâche."))
                return
            add_task(pid, title, due, owner, duration)
            st.rerun()
    _dlg()


def open_edit_project(pid):
    p = get_project(pid)
    if not p:
        return

    @st.dialog(tr("Modifier le projet"))
    def _dlg():
        st.caption(tr("Modifie les informations du projet et les personnes qui y participent."))
        _intro("01", tr("Informations du projet"))
        with st.form(f"edit_project_dialog_{pid}", border=False):
            new_name = st.text_input(tr("Nom du projet"), value=p["name"])
            new_desc = st.text_area(tr("Description (facultatif)"), value=p.get("desc", ""), height=100)
            new_due = st.date_input(tr("Deadline du projet"), value=parse(p["due"]), format="DD/MM/YYYY")
            submitted = st.form_submit_button(tr("Enregistrer les modifications"), type="primary", use_container_width=True)
        if submitted:
            if not new_name.strip():
                st.error(tr("Donne un nom au projet."))
                return
            p["name"], p["desc"], p["due"] = new_name.strip(), new_desc.strip(), new_due.isoformat()
            save()
            st.toast(tr("Projet mis à jour ✨"))
            st.rerun()
        _intro("02", tr("Ajouter un membre"))
        avail = [x["name"] for x in profiles() if x["id"] not in p["member_ids"]]
        selected = st.selectbox(tr("Choisis un ami inscrit"), avail, index=None, key=f"edit_member_{pid}")
        if st.button(tr("Ajouter"), key=f"edit_member_add_{pid}", disabled=not selected, use_container_width=True):
            if add_member(pid, selected):
                st.rerun()
    _dlg()


def open_edit_task(pid, tid):
    p = get_project(pid)
    t = next((x for x in p.get("tasks", []) if x["id"] == tid), None) if p else None
    if not t:
        return

    @st.dialog(tr("Modifier la tâche"))
    def _dlg():
        st.caption(tr("Ajuste les détails, la deadline et le temps nécessaire à cette tâche."))
        _intro("01", tr("Détails de la tâche"))
        owners = [EVERYONE] + p["members"]
        current = t.get("owner", EVERYONE)
        with st.form(f"edit_task_dialog_{tid}", border=False):
            new_title = st.text_input(tr("Tâche"), value=t["title"])
            c1, c2 = st.columns(2)
            new_due = c1.date_input(tr("Deadline"), value=parse(t["due"]), format="DD/MM/YYYY")
            new_owner = c2.selectbox(tr("Responsable"), owners, index=owners.index(current) if current in owners else 0, format_func=tr)
            duration = st.select_slider(tr("Durée estimée"), options=DURATION_OPTIONS,
                                        value=max(15, min(480, int(t.get("duration_minutes", 60) or 60))),
                                        key=f"edit_duration_{tid}", format_func=format_duration)
            submitted = st.form_submit_button(tr("Enregistrer les modifications"), type="primary", use_container_width=True)
        if submitted:
            if not new_title.strip():
                st.error(tr("Donne un nom à la tâche."))
                return
            t.update({"title": new_title.strip(), "due": new_due.isoformat(), "owner": new_owner, "duration_minutes": int(duration)})
            save()
            st.toast(tr("Tâche mise à jour ✨"))
            st.rerun()
        st.divider()
        if st.button(tr("Supprimer la tâche"), key=f"delete_task_dialog_{tid}", use_container_width=True):
            delete_task(pid, tid)
            st.rerun()
    _dlg()


def open_confirm_delete(pid):
    p = get_project(pid)

    @st.dialog(tr("Supprimer ce projet ?"))
    def _dlg():
        st.write(tr("« {name} » et ses {n} tâche(s) seront supprimés. Cette action est définitive.").format(name=p["name"], n=len(p["tasks"])))
        c1, c2 = st.columns(2)
        if c1.button(tr("Annuler"), use_container_width=True):
            st.rerun()
        if c2.button(tr("Oui, supprimer"), type="primary", use_container_width=True):
            delete_project(pid)
            st.rerun()
    _dlg()


def task_menu(p, t, suffix):
    """Contenu du menu « … » d'une tâche : modifier / supprimer."""
    st.caption(f"⏱ {format_duration(t.get('duration_minutes', 60))}")
    if st.button(tr("Modifier"), key=f"edit_task_btn_{t['id']}{suffix}", use_container_width=True):
        open_edit_task(p["id"], t["id"])
    st.button(tr("Supprimer la tâche"), key=f"rm_{t['id']}{suffix}", on_click=delete_task,
              args=(p["id"], t["id"]), use_container_width=True)


def task_checkbox(p, t, suffix, label=None):
    key = f"chk_{t['id']}{suffix}"
    st.checkbox(label or tr("fait"), value=t["done"], key=key, on_change=toggle,
                args=(p["id"], t["id"], key), label_visibility="collapsed" if label is None else "visible")


def language_switch(key="lang"):
    # Libellé fixe : s'il changeait avec la langue, Streamlit recréerait le widget et reviendrait à FR.
    st.radio("Langue / Language", ["FR", "EN"], horizontal=True, key=key, label_visibility="collapsed")
