import streamlit as st
from PIL import Image

# --- BILD / LOGO LADEN ---
try:
    app_icon = Image.open("logo.png")
except Exception:
    app_icon = "🎓"

# --- 1. TITEL & DESIGN ---
st.set_page_config(page_title="Privater Notenrechner", page_icon=app_icon, layout="centered")

# Safari Apple-Icon Trick
st.markdown(
    """
    <link rel="apple-touch-icon" href="https://github.com/jonasfeneberg-sys/mein-notenrechner/blob/4208bde4c2bbc19ad09e454dc951a29eccc25212/logo.png">
    """,
    unsafe_allow_html=True
)

# --- NEUE FUNKTION: SCHNITTBERECHNUNG & SORTIER-WERT ---
def get_schnitt_wert(fach_daten):
    """
    Berechnet den Schnitt für ein Fach.
    Gibt die echte Note zurück oder 7.0, wenn keine Noten da sind.
    """
    grosse = fach_daten.get("gross", [])  # Angepasst an deinen Speicher ("gross")
    kleine = fach_daten.get("klein", [])  # Angepasst an deinen Speicher ("klein")
    ist_hauptfach = fach_daten.get("typ") == "ja"

    # Haben wir überhaupt Noten eingetragen?
    if not grosse and not kleine:
        return 7.0  # Fächer ohne Noten rutschen nach ganz hinten

    # Gewichtung berechnen
    if ist_hauptfach:
        if grosse and kleine:
            schnitt_gross = sum(grosse) / len(grosse)
            schnitt_klein = sum(kleine) / len(kleine)
            return round(((schnitt_gross * 2) + schnitt_klein) / 3, 2)
        elif grosse:
            return round(sum(grosse) / len(grosse), 2)
        else:
            return round(sum(kleine) / len(kleine), 2)
    else:
        if kleine:
            return round(sum(kleine) / len(kleine), 2)
        return 7.0


# --- 2. BEREICH: SPEICHER INITIALISIEREN ---
if "noten_buch" not in st.session_state:
    st.session_state.noten_buch = {}
if "active_subject" not in st.session_state:
    st.session_state.active_subject = None

# Lösch-Bestätigungs-Dialog
@st.dialog("Fach löschen?")
def loesch_bestaetigung(fach_name):
    st.write(f"Bist du dir wirklich sicher, dass du das Fach *'{fach_name}'* mit allen Noten löschen willst?")
    st.write("")
    col_ja, col_nein = st.columns(2)
    with col_ja:
        if st.button("Ja, löschen", type="primary", use_container_width=True):
            del st.session_state.noten_buch[fach_name]
            st.toast(f"Fach '{fach_name}' wurde gelöscht!")
            st.rerun()
    with col_nein:
        if st.button("Abbrechen", use_container_width=True):
            st.rerun()


# --- 3. BEREICH: NEUES FACH HINZUFÜGEN ---
st.header("+ Neues Fach hinzufügen")

with st.form("fach_formular", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        neues_fach = st.text_input("Name des Fachs", placeholder="z. B. Mathe, Deutsch...")
    with col2:
        ist_hauptfach = st.radio("Fach-Typ:", ["Hauptfach", "Nebenfach"])

    submit_button = st.form_submit_button("Fach hinzufügen", use_container_width=True)

if submit_button:
    sauberer_name = neues_fach.strip()
    if sauberer_name:
        if sauberer_name in st.session_state.noten_buch:
            st.error(f"Das Fach '{sauberer_name}' gibt es bereits!")
        else:
            typ = "ja" if ist_hauptfach == "Hauptfach" else "nein"
            st.session_state.noten_buch[sauberer_name] = {
                "typ": typ,
                "gross": [],
                "klein": []
            }
            st.success(f"Fach '{sauberer_name}' wurde hinzugefügt!")
            st.rerun()
    else:
        st.warning("Bitte gib zuerst einen Namen für das Fach ein!")

st.markdown("---")


# --- 4. BEREICH: NOTEN EINTRAGEN & FÄCHER VERWALTEN ---
if st.session_state.noten_buch:

    # Gesamtschnitt-Berechnung über alle Fächer, die Noten haben
    alle_schnitte = []
    for fach, daten in st.session_state.noten_buch.items():
        schnitt = get_schnitt_wert(daten)
        if schnitt != 7.0:
            alle_schnitte.append(schnitt)

    if alle_schnitte:
        gesamtschnitt_aller_faecher = sum(alle_schnitte) / len(alle_schnitte)
        with st.container(border=True):
            st.metric(label=" Aktueller Gesamtschnitt", value=f"{gesamtschnitt_aller_faecher:.2f}")
    else:
        st.info("Trage in mindestens einem Fach Noten ein, um deinen Gesamtschnitt zu sehen.")

    st.markdown("---")

    st.header(" Noten eintragen & Fächer verwalten")

    # In der Auswahlbox sortieren wir die Namen der Übersicht halber einfach alphabetisch
    facher_liste = sorted(list(st.session_state.noten_buch.keys()))
    ausgewaehltes_fach = st.selectbox(
        "Wähle ein Fach aus:",
        options=facher_liste,
        help="Wähle das Fach aus, für das du Noten eintragen oder löschen möchtest."
    )

    fach_daten = st.session_state.noten_buch[ausgewaehltes_fach]

    if fach_daten["typ"] == "ja":
        st.info(f"'{ausgewaehltes_fach}' ist ein Hauptfach. Klicke auf eine Note, um sie direkt hinzuzufügen.")
        st.write("*Große Note hinzufügen (Schulaufgabe):*")
        cols_g = st.columns(6)
        for note_wert in range(1, 7):
            if cols_g[note_wert - 1].button(f"*{note_wert}*", key=f"btn_g_{note_wert}", use_container_width=True):
                fach_daten["gross"].append(note_wert)
                st.success(f"Große Note {note_wert} hinzugefügt!")
                st.rerun()

        st.write("")
        st.write("*Kleine Note hinzufügen (Ex/Abfrage/mündliche Noten):*")
        cols_k = st.columns(6)
        for note_wert in range(1, 7):
            if cols_k[note_wert - 1].button(f"*{note_wert}*", key=f"btn_kh_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Kleine Note {note_wert} hinzugefügt!")
                st.rerun()
    else:
        st.info(f"'{ausgewaehltes_fach}' ist ein Nebenfach. Klicke auf eine Note, um sie direkt hinzuzufügen.")
        st.write("*Kleine Note hinzufügen:*")
        cols_n = st.columns(6)
        for note_wert in range(1, 7):
            if cols_n[note_wert - 1].button(f"*{note_wert}*", key=f"btn_kn_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Kleine Note {note_wert} hinzugefügt!")
                st.rerun()

    st.markdown("---")
    st.write("### Aktuelle Noten verwalten:")

    if fach_daten["typ"] == "ja":
        st.write("*Große Noten:*")
        if not fach_daten["gross"]:
            st.error("Keine großen Noten eingetragen.")
        else:
            for index, note in enumerate(fach_daten["gross"]):
                col_n, col_del = st.columns([4, 1])
                col_n.write(f"• Schulaufgabe: *{note}*")
                if col_del.button("🗑️", key=f"del_g_{index}"):
                    fach_daten["gross"].pop(index)
                    st.rerun()

    st.write("*Kleine Noten:*")
    if not fach_daten["klein"]:
        st.error("Keine kleinen Noten eingetragen.")
    else:
        for index, note in enumerate(fach_daten["klein"]):
            col_n, col_del = st.columns([4, 1])
            col_n.write(f"• Kleine Note: *{note}*")
            if col_del.button("🗑️", key=f"del_k_{index}"):
                fach_daten["klein"].pop(index)
                st.rerun()

    st.markdown("##### Gefahrzone:")
    if st.button(f" Ganzes Fach '{ausgewaehltes_fach}' löschen", use_container_width=True):
        loesch_bestaetigung(ausgewaehltes_fach)


    # --- 5. BEREICH: DIE AUSWERTUNG (Vom besten zum schlechtesten Fach sortiert) ---
    st.header(" Deine aktuellen Notenschnitte")

    # HIER SORTIEREN WIR DIE FÄCHER NACH IHREM SCHNITT
    sortierte_faecher = sorted(
        st.session_state.noten_buch.items(),
        key=lambda x: get_schnitt_wert(x[1])
    )

    # Jetzt gehen wir die Liste der Reihe nach durch
    for fach, daten in sortierte_faecher:
        schnitt = get_schnitt_wert(daten)

        if schnitt == 7.0:
            # Rote Meldung für Fächer ohne Noten ganz unten
            st.error(f"Für {fach} wurden noch keine Noten eingetragen. Schnitt: -.-")
        else:
            # Schicke grüne/blaue Box für berechnete Schnitte
            st.metric(label=f"Schnitt {fach}", value=f"{schnitt:.2f}")

else:
    st.info("Füge oben dein erstes Fach hinzu, um mit der Noteneingabe zu starten!")