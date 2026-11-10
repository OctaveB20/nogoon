# nogoon (anti gooner)

Suivi des deadlines d'équipe (Streamlit + Supabase). Le site actuel est `app.py` ;
trois nouvelles interfaces sont dans `versions/` (voir `versions/README.md`).

## Rappels des tâches importantes ⭐

Chaque utilisateur choisit **ses** tâches importantes : interrupteur « ⭐ Importante pour moi »
dans la création / modification d'une tâche, ou « Marquer importante » dans le menu `⋯`.
L'étoile est personnelle (stockée dans `important_for` de la tâche) : la marquer ne
déclenche des rappels que pour toi.

Pour une tâche importante non terminée, en retard ou due dans les 2 jours :

1. **Email quotidien** (vers 7 h, heure de Paris) avec la liste de tes tâches concernées,
   envoyé par `reminders.py` via GitHub Actions (`.github/workflows/reminders.yml`).
2. **Notification Google Calendar** sur le téléphone (J-2 et veille à 9 h) pour ceux qui
   ont connecté Google Calendar ; l'événement prend un ⭐. Il faut cliquer « Synchroniser ».
3. **Bandeau dans l'app** en haut de page.

### Mise en place des emails (une fois)

Dans GitHub → Settings → Secrets and variables → Actions, ajoute ces **secrets** :

| Secret | Valeur |
|---|---|
| `SUPABASE_URL`, `SUPABASE_KEY` | les mêmes que dans les Secrets Streamlit |
| `SMTP_HOST`, `SMTP_PORT` | ex. Gmail : `smtp.gmail.com`, `587` |
| `SMTP_USER`, `SMTP_PASSWORD` | ex. Gmail : ton adresse + un **mot de passe d'application** (pas ton mot de passe) |
| `MAIL_FROM` | facultatif, adresse d'expéditeur |

Et en **variable** (onglet Variables) : `APP_URL` = l'adresse de l'app (lien dans l'email).

Pour tester : onglet Actions → « Rappels des tâches importantes » → Run workflow.
En local, sans rien envoyer :

```bash
SUPABASE_URL=... SUPABASE_KEY=... python reminders.py --dry-run
```

Note : GitHub met en pause les tâches planifiées d'un dépôt sans activité depuis 60 jours ;
il suffit de la réactiver dans l'onglet Actions.
