"""Rappels par email des tâches importantes (anti gooner).

Chaque utilisateur choisit ses tâches importantes (⭐ dans l'app : champ `important_for`
de la tâche). Ce script, lancé une fois par jour (GitHub Actions, voir
.github/workflows/reminders.yml), envoie à chacun un récapitulatif de SES tâches
importantes non terminées qui sont en retard ou dont la deadline tombe dans les
REMIND_DAYS prochains jours. Aucun email n'est envoyé à qui n'a rien à faire.

Variables d'environnement :
  SUPABASE_URL, SUPABASE_KEY          mêmes valeurs que les Secrets de l'app
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
                                      serveur d'envoi (Gmail, Brevo, Resend, ...)
  MAIL_FROM                           expéditeur (par défaut SMTP_USER)
  APP_URL                             lien vers l'app dans l'email (facultatif)
  REMIND_DAYS                         jours d'avance (défaut 2 : J-2, J-1, jour J)
  TZ_NAME                             fuseau pour « aujourd'hui » (défaut Europe/Paris)

Usage :
  python reminders.py            envoie les emails
  python reminders.py --dry-run  affiche ce qui serait envoyé, sans rien envoyer
"""
import html
import os
import smtplib
import sys
from datetime import date, datetime
from email.message import EmailMessage
from email.utils import formataddr
from zoneinfo import ZoneInfo

import requests

EVERYONE = "Tout le monde"


def env(name, default=None, required=True):
    value = os.environ.get(name, default)
    if required and not value:
        sys.exit(f"Variable d'environnement manquante : {name}")
    return value


def rest_get(url, key, table, params):
    r = requests.get(f"{url}/rest/v1/{table}", params=params, timeout=20,
                     headers={"apikey": key, "Authorization": f"Bearer {key}"})
    r.raise_for_status()
    return r.json()


def when_label(days):
    if days < 0:
        return f"en retard de {-days} j"
    if days == 0:
        return "aujourd'hui"
    if days == 1:
        return "demain"
    return f"dans {days} j"


def collect(projects, profiles, today, remind_days):
    """{user_id: [(jours_restants, projet, tâche), ...]} pour les utilisateurs concernés."""
    known = {str(p["id"]) for p in profiles}
    out = {}
    for project in projects:
        for task in project.get("tasks", []):
            if task.get("done"):
                continue
            try:
                days = (date.fromisoformat(str(task["due"])[:10]) - today).days
            except (KeyError, TypeError, ValueError):
                continue
            if days > remind_days:
                continue
            members = {str(x) for x in project.get("member_ids", [])}
            for user_id in {str(x) for x in task.get("important_for", [])}:
                # Seulement les membres actuels du projet (quelqu'un retiré ne reçoit plus rien).
                if user_id in known and user_id in members:
                    out.setdefault(user_id, []).append((days, project, task))
    for items in out.values():
        items.sort(key=lambda x: (x[0], x[1].get("name", "")))
    return out


def build_email(name, items, app_url):
    late = sum(1 for d, _, _ in items if d < 0)
    subject = f"⭐ {len(items)} tâche{'s' if len(items) > 1 else ''} importante{'s' if len(items) > 1 else ''} à surveiller"
    if late:
        subject += f" (dont {late} en retard)"
    lines = [f"Salut {name},", "", "Voici tes tâches importantes qui arrivent :", ""]
    rows = []
    for days, project, task in items:
        owner = task.get("owner") or EVERYONE
        lines.append(f"- {task['title']} — {project.get('name', '')} — {when_label(days)} "
                     f"({date.fromisoformat(task['due'][:10]):%d/%m}) — responsable : {owner}")
        color = "#C2361B" if days < 0 else "#A86A12" if days <= 1 else "#2F6B4F"
        rows.append(
            f'<tr><td style="padding:10px 12px;border-bottom:1px solid #eee"><b>{html.escape(task["title"])}</b><br>'
            f'<span style="color:#777;font-size:13px">{html.escape(project.get("name", ""))} · {html.escape(owner)}</span></td>'
            f'<td style="padding:10px 12px;border-bottom:1px solid #eee;white-space:nowrap;color:{color};font-weight:700">'
            f'{when_label(days)}<br><span style="color:#777;font-weight:400;font-size:13px">'
            f'{date.fromisoformat(task["due"][:10]):%d/%m/%Y}</span></td></tr>')
    if app_url:
        lines += ["", f"Ouvrir anti gooner : {app_url}"]
    lines += ["", "Tu reçois ce message parce que tu as marqué ces tâches ⭐ importantes.",
              "Retire l'étoile dans l'app pour ne plus être rappelé."]
    button = (f'<p style="margin:22px 0"><a href="{html.escape(app_url, quote=True)}" style="background:#6C4DFF;color:#fff;'
              f'padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:700">Ouvrir anti gooner</a></p>'
              if app_url else "")
    body_html = (
        '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:auto;color:#20223A">'
        f'<h2 style="margin:0 0 6px">Salut {html.escape(name)} 👋</h2>'
        '<p style="color:#555;margin:0 0 16px">Voici tes tâches importantes qui arrivent :</p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:15px">{"".join(rows)}</table>'
        f'{button}<p style="color:#999;font-size:12px">Tu reçois ce message parce que tu as marqué ces tâches ⭐ '
        "importantes. Retire l'étoile dans l'app pour ne plus être rappelé.</p></div>")
    return subject, "\n".join(lines), body_html


def main():
    dry = "--dry-run" in sys.argv
    url = env("SUPABASE_URL").rstrip("/")
    key = env("SUPABASE_KEY")
    remind_days = int(env("REMIND_DAYS", "2"))
    today = datetime.now(ZoneInfo(env("TZ_NAME", "Europe/Paris"))).date()
    app_url = env("APP_URL", "", required=False)

    projects = [r["data"] for r in rest_get(url, key, "projects", {"select": "data"})]
    profiles = rest_get(url, key, "profiles", {"select": "id,name,email"})
    by_id = {str(p["id"]): p for p in profiles}
    todo = collect(projects, profiles, today, remind_days)
    print(f"{today} : {len(todo)} utilisateur(s) à rappeler.")
    if not todo:
        return

    smtp = None
    if not dry:
        host, port = env("SMTP_HOST"), int(env("SMTP_PORT", "587"))
        user, password = env("SMTP_USER"), env("SMTP_PASSWORD")
        sender = env("MAIL_FROM", user)
        smtp = smtplib.SMTP_SSL(host, port, timeout=30) if port == 465 else smtplib.SMTP(host, port, timeout=30)
        if port != 465:
            smtp.starttls()
        smtp.login(user, password)

    failed = 0
    for user_id, items in todo.items():
        profile = by_id[user_id]
        email = (profile.get("email") or "").strip()
        if not email:
            print(f"- {profile.get('name')} : pas d'email, ignoré.")
            continue
        subject, text, body_html = build_email(profile.get("name") or "", items, app_url)
        if dry:
            print(f"\n=== À : {email}\nObjet : {subject}\n{text}")
            continue
        msg = EmailMessage()
        msg["Subject"], msg["From"], msg["To"] = subject, formataddr(("anti gooner", sender)), email
        msg.set_content(text)
        msg.add_alternative(body_html, subtype="html")
        try:
            smtp.send_message(msg)
            print(f"- envoyé à {profile.get('name')} ({len(items)} tâche(s)).")
        except Exception as exc:  # on continue pour les autres
            failed += 1
            print(f"- échec pour {profile.get('name')} : {exc}")
    if smtp:
        smtp.quit()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
