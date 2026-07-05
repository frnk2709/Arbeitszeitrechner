from datetime import datetime, time, timedelta, date
import streamlit as st

st.title("⏱️ Arbeitszeit- & Saldo-Rechner")
st.write("Berechne deinen Feierabend oder dein Tagessaldo basierend auf deinen Zeiten.")

# Feste Vorgaben
REGEL_ARBEITSZEIT = timedelta(hours=8, minutes=12)

# -------------------------------------------------------------
# 1. FUNKTIONSAUSWAHL (Dropdown)
# -------------------------------------------------------------
funktion = st.selectbox(
    "Was möchtest du berechnen?",
    (
        "Feierabendzeit bei Regelarbeitszeit berechnen",
        "Saldo für gewünschte Gehen-Zeit berechnen",
        "Gehen-Zeit für gewünschten Saldo berechnen"
    ),
)

st.divider()

# -------------------------------------------------------------
# 2. EINGABE & VERARBEITUNG
# -------------------------------------------------------------

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
    gesamte_pause = timedelta(minutes=45)
    feierabend_dt = ankunft_dt + REGEL_ARBEITSZEIT + gesamte_pause

    # Ausgabe für Funktion 1
    st.subheader("Dein Feierabend")
    st.metric(label="Berechneter Feierabend", value=feierabend_dt.strftime("%H:%M Uhr"))
    st.info(f"Bei einer Regelarbeitszeit von 8 Std. 12 Min. und 45 Min. Pause ist dein Feierabend um **{feierabend_dt.strftime('%H:%M')} Uhr**.")


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
            "Gewünschte Gehen-Zeit (Format: HH:MM)", value="15:57"
        )
        try:
            gehen_zeit = datetime.strptime(zeit_eingabe_gehen.strip(), "%H:%M").time()
            gehen_dt = datetime.combine(date.today(), gehen_zeit)
        except ValueError:
            st.error("Bitte eine gültige Gehen-Zeit eingeben (z.B. 15:57).")
            gehen_dt = datetime.combine(date.today(), time(15, 57))

    # Logik für das Saldo
    # 1. Gesamte Anwesenheit ermitteln
    anwesenheit_gesamt = gehen_dt - ankunft_dt

    # Feste Frühstückspause (wird immer abgezogen)
    fruehstueck_pause = timedelta(minutes=15)


    # 2. Dynamische Mittagspausenermittlung basierend auf der ARBEITSZEIT
    # Grenzwerte bezogen auf die Gesamtanwesenheit:
    # 6h Arbeit + 15m Frühstück = 6h 15m Anwesenheit (Hier startet die Mittagspause)
    # 6h Arbeit + 15m Frühstück + 30m Mittag = 6h 45m Anwesenheit (Hier ist sie voll)

    if anwesenheit_gesamt <= timedelta(hours=6, minutes=15):
        # Noch keine 6 Stunden gearbeitet -> Nur Frühstückspause zählt
        mittag_pause = timedelta(minutes=0)

    elif timedelta(hours=6, minutes=15) < anwesenheit_gesamt <= timedelta(hours=6, minutes=45):
        # Man befindet sich mitten in der Mittagspause -> Wird anteilig berechnet
        mittag_pause = anwesenheit_gesamt - timedelta(hours=6, minutes=15)

    else:
        # Über 6h 45m Anwesenheit -> Volle 30 Minuten Mittagspause
        mittag_pause = timedelta(minutes=30)

    # Gesamte effektive Pause berechnen
    effektive_pause = fruehstueck_pause + mittag_pause


    # 3. Tatsächliche Arbeitszeit und Saldo berechnen
    tatsaechliche_arbeitszeit = anwesenheit_gesamt - effektive_pause
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

    # Aufgeteilte Pausenanzeige in Minuten
    min_fruehstueck = int(fruehstueck_pause.total_seconds() // 60)
    min_mittag = int(mittag_pause.total_seconds() // 60)
    min_gesamt = int(effektive_pause.total_seconds() // 60)

    st.info(
        f"**Pausenzeiten:**\n"
        f"* 🥐 Frühstückspause: {min_fruehstueck} Min.\n"
        f"* 🥗 Mittagspause: {min_mittag} Min.\n"
        f"\n➡️ **Gesamtpause: {min_gesamt} Min.**"
    )


# --- FUNKTION 3: GEHEN-ZEIT FÜR WUNSCH-SALDO BERECHNEN ---
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

    # --- FÜR FUNKTION 3 ---
    wunsch_saldo = timedelta(minutes=wunsch_saldo_minuten)

    # 1. geplante reine Arbeitszeit
    geplante_arbeitszeit = REGEL_ARBEITSZEIT + wunsch_saldo

    # Feste Frühstückspause gilt immer
    fruehstueck_pause = timedelta(minutes=15)

    # 2. Dynamische Mittagspause anhand der GEPLANTEN Arbeitszeit ermitteln
    # Die Mittagspause läuft ab 6 Stunden Arbeitszeit für maximal 30 Minuten an.
    if geplante_arbeitszeit <= timedelta(hours=6):
        mittag_pause = timedelta(minutes=0)
    elif timedelta(hours=6) < geplante_arbeitszeit <= timedelta(hours=6, minutes=30):
        # Befindet sich der Wunsch genau in der anlaufenden Mittagspause,
        # muss die Mittagspause 1:1 auf die Anwesenheit aufgeschlagen werden
        mittag_pause = geplante_arbeitszeit - timedelta(hours=6)
    else:
        # Ab 6,5 Stunden geplanter Arbeitszeit ist die Mittagspause voll
        mittag_pause = timedelta(minutes=30)

    gesamt_pause = fruehstueck_pause + mittag_pause

    # 3. Ziel-Gehen-Zeit berechnen
    ziel_gehen_dt = ankunft_dt + geplante_arbeitszeit + gesamt_pause

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
        f"**Aufschlüsselung der Zeiten:**\n"
        f"* 🕑 reine Arbeitszeit: `{int(geplante_arbeitszeit.total_seconds() // 3600):02d}:{int((geplante_arbeitszeit.total_seconds() % 3600) // 60):02d}`\n"
        f"* 🥐 Frühstückspause: {int(fruehstueck_pause.total_seconds() // 60)} Min.\n"
        f"* 🥗 Mittagspause: {int(mittag_pause.total_seconds() // 60)} Min."
    )
