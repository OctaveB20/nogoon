1281
1282
1283
1284
1285
1286
1287
1288
1289
1290
1291
1292
1293
1294
1295
1296
1297
1298
1299
1300
1301
1302
1303
1304
1305
1306
1307
1308
1309
1310
1311
1312
1313
1314
1315
1316
1317
1318
1319
1320
1321
1322
1323
1324
1325
1326
1327
1328
1329
1330
1331
1332
1333
1334
1335
1336
1337
1338
1339
1340
1341
1342
1343
1344
1345
1346
1347
1348
1349
1350
1351
1352
1353
1354
1355
1356
1357
1358
1359
1360
1361
1362
1363
1364
1365
1366
1367
1368
1369
1370
1371
1372
1373
1374
1375
1376
1377
1378
1379
1380
1381
1382
1383
1384
1385
1386
1387
1388
1389
1390
1391
1392
1393
1394
1395
1396
1397
1398
1399
1400
1401
1402
1403
1404
1405
1406
1407
1408
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

page = st.radio(
    "Navigation", [tr("Projets"), tr("Charge de travail")],
    horizontal=True, key="main_navigation", label_visibility="collapsed",
)
if page == tr("Charge de travail"):
    workload_view()
else:
