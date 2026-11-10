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
                   initial_sidebar_state="expanded")
c.init_backend()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&family=JetBrains+Mono:wght@400;500;700;800&display=swap');
:root {
  --bg:#0B0B0C; --panel:#111113; --panel2:#18181B; --line:#2A2A2F; --line2:#3A3A40;
  --text:#E8E8E3; --dim:#8D8D86; --acid:#C8FF2E; --late:#FF5A36; --soon:#FFB020; --ok:#C8FF2E; --info:#5AD7FF;
  --mono:'JetBrains Mono', ui-monospace, monospace; --cond:'Archivo', 'Arial Narrow', sans-serif;
}
.stApp { background:var(--bg); color:var(--text);
