from datetime import datetime, time, timedelta, date
import streamlit as st

st.title("⏱️ Arbeitszeit- & Saldo-Rechner",
         help="Dieser Rechner ist nur für eine geleistete Arbeitszeit von max. 9:00 Stunden ausgelegt bei einer Regelarbeitszeit von 8 Stunden 12 Minten."
         )
st.write("Berechne deinen Feierabend oder dein Tagessaldo basierend auf deinen Zeiten.")


# Feste Vorgaben
REGEL_ARBEITSZEIT = timedelta(hours=8, minutes=12)


funktion = st.selectbox(
    "Was möchtest du berechnen?",
    (
        "Feierabendzeit bei Regelarbeitszeit berechnen",
        "Saldo für gewünschte Gehen-Zeit berechnen",
        "Saldo bei Abwesenheit (2 Mal Einstechen) berechnen",
        "Gehen-Zeit für gewünschten Saldo berechnen"
    ),
)


st.divider()


# --- FUNKTION 1: FEIERABEND BERECHNEN ---
if funktion == "Feierabendzeit bei Regelarbeitszeit berechnen":

    zeit_eingabe_ankunft = st.text_input(
        "Ankunftzeit (Format: HH:MM)", value="07:00"
    )
    try:
        ankunft_zeit = datetime.strptime(zeit_eingabe_ankunft.strip(), "%H:%M").time()
        ankunft_dt = datetime.combine(date.today(), ankunft_zeit)
    except ValueError:
        st.error("Bitte eine gültige Ankunftzeit eingeben (z.B. 07:00).")
        ankunft_dt = datetime.combine(date.today(), time(7, 0))

    # Berechnung für Funktion 1
    gesamte_pause = timedelta(minutes=30)
    feierabend_dt = ankunft_dt + REGEL_ARBEITSZEIT + gesamte_pause

    # Ausgabe für Funktion 1
    st.subheader("Dein Feierabend")
    st.metric(label="Berechneter Feierabend", value=feierabend_dt.strftime("%H:%M Uhr"))
    st.info(f"Bei einer Regelarbeitszeit von 8 Std. 12 Min. und 30 Min. Pause ist dein Feierabend um **{feierabend_dt.strftime('%H:%M')} Uhr**.")


# --- FUNKTION 2: SALDO BERECHNEN ---
elif funktion == "Saldo für gewünschte Gehen-Zeit berechnen":

    col1, col2 = st.columns(2)

    with col1:
        zeit_eingabe_ankunft = st.text_input(
            "Ankunftszeit (Format: HH:MM)", value="07:00"
        )
        try:
            ankunft_zeit = datetime.strptime(zeit_eingabe_ankunft.strip(), "%H:%M").time()
            ankunft_dt = datetime.combine(date.today(), ankunft_zeit)
        except ValueError:
            st.error("Bitte eine gültige Ankunftszeit eingeben (z.B. 07:00).")
            ankunft_dt = datetime.combine(date.today(), time(7, 0))

    with col2:
        zeit_eingabe_gehen = st.text_input(
            "Gewünschte Gehen-Zeit (Format: HH:MM)", value="15:42"
        )
        try:
            gehen_zeit = datetime.strptime(zeit_eingabe_gehen.strip(), "%H:%M").time()
            gehen_dt = datetime.combine(date.today(), gehen_zeit)
        except ValueError:
            st.error("Bitte eine gültige Gehen-Zeit eingeben (z.B. 15:42).")
            gehen_dt = datetime.combine(date.today(), time(15, 42))

    # Logik für das Saldo
    # 1. Gesamte Anwesenheit ermitteln
    anwesenheit_gesamt = gehen_dt - ankunft_dt

    # 2. Dynamische Mittagspausenermittlung basierend auf der ARBEITSZEIT
    # Grenzwerte bezogen auf die Gesamtanwesenheit:
    # 6h Arbeit + 15m Frühstück = 6h 15m Anwesenheit (Hier startet die Mittagspause)
    # 6h Arbeit + 15m Frühstück + 30m Mittag = 6h 45m Anwesenheit (Hier ist sie voll)

    if anwesenheit_gesamt <= timedelta(hours=6):
        # Noch keine 6 Stunden gearbeitet -> keine Pause
        mittag_pause = timedelta(minutes=0)

    elif timedelta(hours=6) < anwesenheit_gesamt <= timedelta(hours=6, minutes=30):
        mittag_pause = anwesenheit_gesamt - timedelta(hours=6)

    else:
        # Über 6h Anwesenheit -> 30 Minuten Mittagspause
        mittag_pause = timedelta(minutes=30)


    # 3. Tatsächliche Arbeitszeit und Saldo berechnen
    tatsaechliche_arbeitszeit = anwesenheit_gesamt - mittag_pause
    saldo = tatsaechliche_arbeitszeit - REGEL_ARBEITSZEIT

    # Gesamte Minuten des Saldos berechnen
    saldo_minuten_total = int(saldo.total_seconds() // 60)

    # Absolute Werte für die Formatierung nutzen
    abs_minuten_total = abs(saldo_minuten_total)
    saldo_stunden = abs_minuten_total // 60
    saldo_minuten = abs_minuten_total % 60
    saldo_formatiert = f"{saldo_stunden:02d}:{saldo_minuten:02d}"

    # Formatierung für die geleistete Arbeitszeit
    arb_sekunden = tatsaechliche_arbeitszeit.total_seconds()
    arb_formatiert = f"{int(arb_sekunden // 3600):02d}:{int((arb_sekunden % 3600) // 60):02d}"


    # 4. AUSGABE
    st.subheader("Dein Saldo-Ergebnis")

    if saldo_minuten_total >= 0:
        st.success(
            f"Du hast heute **{saldo_formatiert} Stunden Plus** gemacht. \n\n"
            f"Geleistete Arbeitszeit: `{arb_formatiert}` (Soll: 08:12)"
        )
    else:
        st.warning(
            f"Du hast heute **{saldo_formatiert} Stunden Minus** gemacht. \n\n"
            f"Geleistete Arbeitszeit: `{arb_formatiert}` (Soll: 08:12)"
        )

    # Pausenanzeige in Minuten
    min_mittag = int(mittag_pause.total_seconds() // 60)

    if anwesenheit_gesamt <= timedelta(hours=6):
        st.info("🥗 Pause: 0 Min.")

    elif timedelta(hours=6) < anwesenheit_gesamt <= timedelta(hours=6, minutes=30):

        frueheste_gehen_dt = gehen_dt - mittag_pause

        frueheste_gehen_zeit = (gehen_dt - mittag_pause).strftime("%H:%M")
        wiederbeginn_zeit = (frueheste_gehen_dt + timedelta(minutes=30)).strftime("%H:%M")

        st.warning(
            f"Wenn du gehst, läuft deine Pause seit {min_mittag} Min. \n\n"
            f"Du kannst deshalb schon um **{frueheste_gehen_zeit} Uhr** gehen. \n\n"
            f"Deine Zeiterfassung beginnt erst um {wiederbeginn_zeit} Uhr wieder."
        )

    else:
        st.info("🥗 Pause: 30 Min.")


# --- FUNKTION 3: SALDO BEI ABWESENHEIT (2 STEMPEL-BLÖCKE) ---
elif funktion == "Saldo bei Abwesenheit (2 Mal Einstechen) berechnen":

    st.subheader("Zeiten für 2 Stempel-Blöcke eingeben")

    st.html("""
        <style>
        [data-testid="stColumn"]:nth-child(1) {
            border-right: 1px solid #d6d6d6;
            padding-right: 1.5rem;
        }
        </style>
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**1. Arbeitsblock**")
        zeit_ankunft1 = st.text_input("Kommen 1 (HH:MM)", value="06:00", key="f4_ankunft1")
        zeit_gehen1 = st.text_input("Gehen 1 (HH:MM)", value="13:00", key="f4_gehen1")

    with col2:
        st.markdown("**2. Arbeitsblock**")
        zeit_ankunft2 = st.text_input("Kommen 2 (HH:MM)", value="13:45", key="f4_ankunft2")
        zeit_gehen2 = st.text_input("Gehen 2 (HH:MM)", value="14:57", key="f4_gehen2")

    # Time Parsing
    try:
        dt_ankunft1 = datetime.combine(date.today(), datetime.strptime(zeit_ankunft1.strip(), "%H:%M").time())
        dt_gehen1 = datetime.combine(date.today(), datetime.strptime(zeit_gehen1.strip(), "%H:%M").time())
        dt_ankunft2 = datetime.combine(date.today(), datetime.strptime(zeit_ankunft2.strip(), "%H:%M").time())
        dt_gehen2 = datetime.combine(date.today(), datetime.strptime(zeit_gehen2.strip(), "%H:%M").time())
        valid_times = True
    except ValueError:
        st.error("Bitte alle Zeiten im Format HH:MM eingeben.")
        valid_times = False


    if valid_times:
        if not (dt_ankunft1 < dt_gehen1 <= dt_ankunft2 < dt_gehen2):
            st.error("Bitte die chronologische Reihenfolge prüfen: Kommen 1 < Gehen 1 ≤ Kommen 2 < Gehen 2.")
        else:
            block1 = dt_gehen1 - dt_ankunft1
            block2 = dt_gehen2 - dt_ankunft2
            anwesenheit = block1 + block2
            abwesenheit = dt_ankunft2 - dt_gehen1


            if block1 <= timedelta(hours=6):
                if anwesenheit <= timedelta(hours=6):
                    gesetzliche_pause = timedelta(seconds=0)
                    tatsaechliche_arbeitszeit = anwesenheit
                elif timedelta (hours=6, minutes=0) < anwesenheit <= timedelta(hours=6, minutes=30):
                    gesetzliche_pause = timedelta(minutes=30)
                    pausenabzug = anwesenheit - timedelta(hours=6)
                    tatsaechliche_arbeitszeit = anwesenheit - pausenabzug
                elif anwesenheit > timedelta(hours=6, minutes=30):
                    gesetzliche_pause = timedelta(minutes=30)
                    tatsaechliche_arbeitszeit = anwesenheit - gesetzliche_pause
            else:
                gesetzliche_pause = timedelta(minutes=30)
                if timedelta (hours=6, minutes=0) < anwesenheit <= timedelta(hours=6, minutes=30):
                    if abwesenheit <= gesetzliche_pause:
                        rest_pause = gesetzliche_pause - abwesenheit
                        tatsaechliche_arbeitszeit = anwesenheit - rest_pause
                    else:
                        tatsaechliche_arbeitszeit = anwesenheit
                elif anwesenheit > timedelta(hours=6, minutes=30):
                    if abwesenheit <= gesetzliche_pause:
                        rest_pause = gesetzliche_pause - abwesenheit
                        tatsaechliche_arbeitszeit = anwesenheit - rest_pause
                    else:
                        zusaetzlicher_abzug = abwesenheit - gesetzliche_pause
                        tatsaechliche_arbeitszeit = anwesenheit

            saldo = tatsaechliche_arbeitszeit - REGEL_ARBEITSZEIT


            # Formatierung
            saldo_minuten_total = int(saldo.total_seconds() // 60)
            abs_minuten_total = abs(saldo_minuten_total)
            saldo_stunden = abs_minuten_total // 60
            saldo_minuten = abs_minuten_total % 60
            saldo_formatiert = f"{saldo_stunden:02d}:{saldo_minuten:02d}"

            arb_sekunden = tatsaechliche_arbeitszeit.total_seconds()
            arb_formatiert = f"{int(arb_sekunden // 3600):02d}:{int((arb_sekunden % 3600) // 60):02d}"

            min_abwesenheit = int(abwesenheit.total_seconds() // 60)
            min_erforderlich = int(gesetzliche_pause.total_seconds() // 60)


            # Ausgabe
            st.subheader("Dein Saldo-Ergebnis")


            if saldo_minuten_total >= 0:
                st.success(
                    f"Du hast heute **{saldo_formatiert} Stunden Plus** gemacht. \n\n"
                    f"Geleistete Arbeitszeit: `{arb_formatiert}` (Soll: 08:12)"
                )

            else:
                st.warning(
                    f"Du hast heute **{saldo_formatiert} Stunden Minus** gemacht. \n\n"
                    f"Geleistete Arbeitszeit: `{arb_formatiert}` (Soll: 08:12)"
                )


            hinweis_text = ""

            if block1 > timedelta (hours=6):
                if min_abwesenheit > min_erforderlich:
                    hinweis_text = (
                        f"Weil deine Abwesenheit von {min_abwesenheit} Min. die gesetzliche Pause von 30 Min. überschreitet, "
                        f"werden die übersteigenden **{min_abwesenheit - 30} Min.** als unterbrochene Arbeitszeit gewertet."
                    )
                else:
                    hinweis_text = (
                        f"Deine Abwesenheit befindet sich innerhalb der gesetzlichen Pause."
                    )
            else:
                hinweis_text = (
                    f"Du hast bei der ersten Gehen-Buchung noch nicht mehr als 6:00 Stunden gearbeitet, weshalb die Abwesenheit als "
                    f"unterbrochene Arbeitszeit erfasst wird. "
                )

            info_inhalt = (
                f"* 🕑 Abwesenheit: **{min_abwesenheit} Min.**\n"
                f"* 🥗 Pause: **{min_erforderlich} Min.**"
            )

            if hinweis_text:
                info_inhalt += f"\n\n{hinweis_text}"

            st.info(info_inhalt)


# --- FUNKTION 4: GEHEN-ZEIT FÜR WUNSCH-SALDO BERECHNEN ---
else:

    col1, col2 = st.columns(2)

    with col1:
        zeit_eingabe_ankunft = st.text_input(
            "Ankunftszeit (Format: HH:MM)", value="07:00", key="f3_ankunft"
        )
        try:
            ankunft_zeit = datetime.strptime(zeit_eingabe_ankunft.strip(), "%H:%M").time()
            ankunft_dt = datetime.combine(date.today(), ankunft_zeit)
        except ValueError:
            st.error("Bitte eine gültige Ankunftszeit eingeben (z.B. 07:00).")
            ankunft_dt = datetime.combine(date.today(), time(7, 0))

    with col2:
        # Ein Nummerneingabefeld für das Wunsch-Saldo in Minuten (z.B. +15 oder -10)
        wunsch_saldo_minuten = st.number_input(
            "Wunsch-Saldo (in Minuten)",
            value=0, step=5,
            help="Positive Zahl für Plusminuten, negative Zahl für Minusminuten."
        )

    # --- FÜR FUNKTION 4 ---
    wunsch_saldo = timedelta(minutes=wunsch_saldo_minuten)

    # 1. geplante reine Arbeitszeit
    geplante_arbeitszeit = REGEL_ARBEITSZEIT + wunsch_saldo


    # 2. Dynamische Mittagspause anhand der GEPLANTEN Arbeitszeit ermitteln
    # Die Mittagspause läuft ab 6 Stunden Arbeitszeit für maximal 30 Minuten an.
    if geplante_arbeitszeit <= timedelta(hours=6):
        mittag_pause = timedelta(minutes=0)

    else:
        # Ab 6,5 Stunden geplanter Arbeitszeit ist die Mittagspause voll
        mittag_pause = timedelta(minutes=30)


    # 3. Ziel-Gehen-Zeit berechnen
    ziel_gehen_dt = ankunft_dt + geplante_arbeitszeit + mittag_pause


    # --- AUSGABE ---
    st.subheader("Deine Ziel-Gehen-Zeit")
    st.metric(
        label="Berechnete Gehen-Zeit",
        value=ziel_gehen_dt.strftime("%H:%M Uhr")
    )

    # Vorzeichen-Text für die Info-Box vorbereiten
    saldo_text = f"+{wunsch_saldo_minuten}" if wunsch_saldo_minuten >= 0 else f"{wunsch_saldo_minuten}"

    st.info(
        f"Um ein Saldo von **{saldo_text} Minuten** zu erreichen, musst du um **{ziel_gehen_dt.strftime('%H:%M')} Uhr** Feierabend machen.\n\n"
        f"* 🕑 reine Arbeitszeit: `{int(geplante_arbeitszeit.total_seconds() // 3600):02d}:{int((geplante_arbeitszeit.total_seconds() % 3600) // 60):02d}`\n"
        f"* 🥗 Mittagspause: {int(mittag_pause.total_seconds() // 60)} Min."
    )
