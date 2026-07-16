import streamlit as st

# --- 1. TITEL & DESIGN ---
st.set_page_config(page_title="Privater Notenrechner", page_icon="", layout="centered")
st.title("Schul-Notenrechner")
st.write("Verwalte deine Fächer, trage deine Noten ein – komplett privat in deinem Browser!")

# --- 2. ISOLIERTER SPEICHER FÜR DIESEN TAB ---
# Jedes Mal, wenn jemand die Seite neu öffnet, startet ein komplett eigener, frischer Speicherbereich.
if "noten_buch" not in st.session_state:
    st.session_state.noten_buch = {}


# --- NEUE FUNKTION FÜR DAS BESTÄTIGUNGS-FENSTER ---
@st.dialog("⚠️ Fach löschen?")
def loesch_bestaetigung(fach_name):
    st.write(
        f"Bist du dir wirklich sicher, dass du das Fach *'{fach_name}'* mit allen Noten löschen willst?")
    st.write("")  # Ein bisschen Abstand

    col_ja, col_nein = st.columns(2)
    with col_ja:
        if st.button("Ja, löschen", type="primary", use_container_width=True):
            del st.session_state.noten_buch[fach_name]
            st.toast(f"Fach '{fach_name}' wurde gelöscht!")  # Eine kleine, schicke Pop-up-Meldung unten rechts
            st.rerun()
    with col_nein:
        if st.button("Abbrechen", use_container_width=True):
            st.rerun()  # Schließt das Fenster einfach wieder

# --- 3. BEREICH: NEUES FACH HINZUFÜGEN ---
st.header("+ Neues Fach hinzufügen")

col1, col2 = st.columns([2, 1])
with col1:
    # Hier tippt man den Namen ein
    neues_fach = st.text_input("Name des Fachs", placeholder="z. B. Mathe, Deutsch...", key="neues_fach_input")
with col2:
    ist_hauptfach = st.radio("Fach-Typ:", ["Hauptfach", "Nebenfach"])

if st.button("Fach hinzufügen", use_container_width=True):
    # Wir entfernen eventuelle Leerzeichen am Anfang und Ende des Namens
    sauberer_name = neues_fach.strip()

    if sauberer_name:
        if sauberer_name in st.session_state.noten_buch:
            st.error(f"Das Fach '{sauberer_name}' gibt es bereits!")
        else:
            typ = "ja" if ist_hauptfach == "Hauptfach" else "nein"

            # Fach im privaten Speicher anlegen
            st.session_state.noten_buch[sauberer_name] = {
                "typ": typ,
                "gross": [],
                "klein": []
            }
            st.success(f"Fach '{sauberer_name}' wurde hinzugefügt!")
            st.rerun()  # Seite neu laden, damit das neue Fach unten erscheint
    else:
        st.warning("Bitte gib zuerst einen Namen für das Fach ein!")

st.markdown("---")


# --- 4. BEREICH: NOTEN EINTRAGEN & FÄCHER VERWALTEN (Nur wenn Fächer existieren) ---
if st.session_state.noten_buch:
    st.header(" Noten eintragen & Fächer verwalten")

    facher_liste = sorted(list(st.session_state.noten_buch.keys()))
    ausgewaehltes_fach = st.selectbox(
        "Wähle ein Fach aus:",
        options=facher_liste,
        help="Wähle das Fach aus, für das du Noten eintragen oder löschen möchtest."
    )

    fach_daten = st.session_state.noten_buch[ausgewaehltes_fach]

    if fach_daten["typ"] == "ja":
        st.info(f"'{ausgewaehltes_fach}' ist ein Hauptfach. Klicke auf eine Note, um sie direkt hinzuzufügen.")

        # --- GROSSE NOTEN (Schulaufgaben) ---
        st.write("*Große Note hinzufügen (Schulaufgabe):*")
        # Wir erstellen 6 Spalten nebeneinander für die Buttons 1 bis 6
        cols_g = st.columns(6)
        for note_wert in range(1, 7):
            if cols_g[note_wert - 1].button(f"*{note_wert}*", key=f"btn_g_{note_wert}", use_container_width=True):
                fach_daten["gross"].append(note_wert)
                st.success(f"Große Note {note_wert} hinzugefügt!")
                st.rerun()

        st.write("")  # Ein bisschen Abstand

        # --- KLEINE NOTEN (Hauptfach) ---
        st.write("*Kleine Note hinzufügen (Ex/Abfrage):*")
        cols_k = st.columns(6)
        for note_wert in range(1, 7):
            if cols_k[note_wert - 1].button(f"*{note_wert}*", key=f"btn_kh_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Kleine Note {note_wert} hinzugefügt!")
                st.rerun()
    else:
        st.info(f"'{ausgewaehltes_fach}' ist ein Nebenfach. Klicke auf eine Note, um sie direkt hinzuzufügen.")

        # --- KLEINE NOTEN (Nebenfach) ---
        st.write("*Kleine Note hinzufügen:*")
        cols_n = st.columns(6)
        for note_wert in range(1, 7):
            if cols_n[note_wert - 1].button(f"*{note_wert}*", key=f"btn_kn_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Kleine Note {note_wert} hinzugefügt!")
                st.rerun()

    st.markdown("---")
    st.write("### Aktuelle Noten verwalten:")

    # Große Noten anzeigen und löschen
    if fach_daten["typ"] == "ja":
        st.write("*Eingetragene große Noten:*")
        if not fach_daten["gross"]:
            st.write("Keine großen Noten eingetragen.")
        else:
            for index, note in enumerate(fach_daten["gross"]):
                col_n, col_del = st.columns([4, 1])
                col_n.write(f"• Schulaufgabe: *{note}*")
                if col_del.button("🗑️", key=f"del_g_{index}"):
                    fach_daten["gross"].pop(index)
                    st.rerun()

    # Kleine Noten anzeigen und löschen
    st.write("*Eingetragene kleine Noten:*")
    if not fach_daten["klein"]:
        st.write("Keine kleinen Noten eingetragen.")
    else:
        for index, note in enumerate(fach_daten["klein"]):
            col_n, col_del = st.columns([4, 1])
            col_n.write(f"• Kleine Note: *{note}*")
            if col_del.button("🗑️", key=f"del_k_{index}"):
                fach_daten["klein"].pop(index)
                st.rerun()

    st.markdown("##### Gefahrzone:")
    # Wenn man hier klickt, öffnet sich das Pop-up-Fenster von oben
    if st.button(f" Ganzes Fach '{ausgewaehltes_fach}' löschen", use_container_width=True):
        loesch_bestaetigung(ausgewaehltes_fach)

    # --- 5. BEREICH: DIE AUSWERTUNG ---
    st.header(" Deine aktuellen Notenschnitte")

    for fach, daten in list(st.session_state.noten_buch.items()):
        hat_kleine = len(daten["klein"]) > 0
        hat_grosse = len(daten["gross"]) > 0

        if daten["typ"] == "ja":
            if hat_grosse and hat_kleine:
                schnitt_gross = sum(daten["gross"]) / len(daten["gross"])
                schnitt_klein = sum(daten["klein"]) / len(daten["klein"])
                gesamtschnitt = ((schnitt_gross * 2) + schnitt_klein) / 3
                st.metric(label=f"Schnitt {fach}", value=f"{gesamtschnitt:.2f}")
            elif hat_grosse and not hat_kleine:
                gesamtschnitt = sum(daten["gross"]) / len(daten["gross"])
                st.metric(label=f"Schnitt {fach}", value=f"{gesamtschnitt:.2f}")
            elif hat_kleine and not hat_grosse:
                gesamtschnitt = sum(daten["klein"]) / len(daten["klein"])
                st.metric(label=f"Schnitt {fach}", value=f"{gesamtschnitt:.2f}")
            else:
                st.write(f"ℹ️ Für {fach} wurden noch keine Noten eingetragen.")

        else:
            if hat_kleine:
                gesamtschnitt = sum(daten["klein"]) / len(daten["klein"])
                st.metric(label=f"Schnitt {fach}", value=f"{gesamtschnitt:.2f}")
            else:
                st.write(f"ℹ️ Für {fach} wurden noch keine Noten eingetragen.")


        # --- 6. BEREICH: DER GESAMTSCHNITT ÜBER ALLE FÄCHER ---
        st.markdown("---")
        st.header(" Dein Gesamt-Notenschnitt")

        alle_schnitte = []

        # Wir gehen noch einmal durch alle Fächer und sammeln die berechneten Schnitte
        for fach, daten in st.session_state.noten_buch.items():
            hat_kleine = len(daten["klein"]) > 0
            hat_grosse = len(daten["gross"]) > 0

            fach_schnitt = None

            if daten["typ"] == "ja":  # Hauptfach
                if hat_grosse and hat_kleine:
                    schnitt_gross = sum(daten["gross"]) / len(daten["gross"])
                    schnitt_klein = sum(daten["klein"]) / len(daten["klein"])
                    fach_schnitt = ((schnitt_gross * 2) + schnitt_klein) / 3
                elif hat_grosse:
                    fach_schnitt = sum(daten["gross"]) / len(daten["gross"])
                elif hat_kleine:
                    fach_schnitt = sum(daten["klein"]) / len(daten["klein"])
            else:  # Nebenfach
                if hat_kleine:
                    fach_schnitt = sum(daten["klein"]) / len(daten["klein"])

            # Wenn das Fach einen gültigen Schnitt hat, packen wir ihn in unsere Liste
            if fach_schnitt is not None:
                alle_schnitte.append(fach_schnitt)

        # Wenn wir mindestens ein Fach mit Noten haben, berechnen wir den Gesamtschnitt
        if alle_schnitte:
            gesamtschnitt_aller_faecher = sum(alle_schnitte) / len(alle_schnitte)

            # Eine schöne große Anzeige für den Erfolg!
            st.subheader(f"Aktueller Zeugnisschnitt: {gesamtschnitt_aller_faecher:.2f}")
            st.progress(min(max((6.0 - gesamtschnitt_aller_faecher) / 5.0, 0.0), 1.0))  # Ein visueller Ladebalken
        else:
            st.info("Trage in mindestens einem Fach Noten ein, um deinen Gesamtschnitt zu sehen.")

else:
    st.info("Füge oben dein erstes Fach hinzu, um mit der Noteneingabe zu starten!")