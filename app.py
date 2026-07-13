import streamlit as st

# --- 1. TITEL & DESIGN ---
st.set_page_config(page_title="Notenrechner", page_icon="🎓", layout="centered")
st.title("🎓 Mein Schul-Notenrechner")
st.write("Verwalte deine Fächer, trage deine Noten ein und berechne deinen exakten Schnitt!")

# --- 2. DAS GEDÄCHTNIS DER APP (Session State) ---
# Hier erstellen wir unser 'noten_buch', falls es noch nicht existiert
if "noten_buch" not in st.session_state:
    st.session_state.noten_buch = {}

# --- 3. BEREICH: NEUES FACH HINZUFÜGEN ---
st.header("➕ Neues Fach hinzufügen")

# Eingabefelder nebeneinander platzieren
col1, col2 = st.columns([2, 1])
with col1:
    neues_fach = st.text_input("Name des Fachs", placeholder="z. B. Mathe, Deutsch...")
with col2:
    ist_hauptfach = st.radio("Fach-Typ:", ["Hauptfach", "Nebenfach"])

if st.button("Fach speichern", use_container_width=True):
    if neues_fach:
        # Fachtyp übersetzen ("Hauptfach" -> "ja", "Nebenfach" -> "nein")
        typ = "ja" if ist_hauptfach == "Hauptfach" else "nein"

        # Fach im Speicher anlegen
        st.session_state.noten_buch[neues_fach] = {
            "typ": typ,
            "gross": [],
            "klein": []
        }
        st.success(f"Fach '{neues_fach}' wurde erfolgreich hinzugefügt!")
    else:
        st.warning("Bitte gib zuerst einen Namen für das Fach ein!")

st.markdown("---")

# --- 4. BEREICH: NOTEN EINTRAGEN & BERECHNEN ---
if st.session_state.noten_buch:
    st.header("📝 Noten eintragen")

    # Dropdown-Menü, um das Fach auszuwählen
    ausgewaehltes_fach = st.selectbox("Wähle ein Fach aus:", list(st.session_state.noten_buch.keys()))
    fach_daten = st.session_state.noten_buch[ausgewaehltes_fach]

    # Weiche: Hauptfach oder Nebenfach?
    if fach_daten["typ"] == "ja":
        st.info(f"'{ausgewaehltes_fach}' ist ein Hauptfach. Du kannst Schulaufgaben (groß) und kleine Noten eintragen.")

        col_g, col_k = st.columns(2)
        with col_g:
            g_note = st.number_input("Große Note (Schulaufgabe):", min_value=1, max_value=6, step=1, key="g_note")
            if st.button("Große Note hinzufügen"):
                fach_daten["gross"].append(g_note)
                st.success(f"Große Note {g_note} hinzugefügt!")

        with col_k:
            k_note = st.number_input("Kleine Note (Ex/Abfrage):", min_value=1, max_value=6, step=1, key="k_note_haupt")
            if st.button("Kleine Note hinzufügen (Hauptfach)"):
                fach_daten["klein"].append(k_note)
                st.success(f"Kleine Note {k_note} hinzugefügt!")
    else:
        st.info(f"'{ausgewaehltes_fach}' ist ein Nebenfach. Du kannst nur kleine Noten eintragen.")
        k_note = st.number_input("Kleine Note:", min_value=1, max_value=6, step=1, key="k_note_neben")
        if st.button("Kleine Note hinzufügen (Nebenfach)"):
            fach_daten["klein"].append(k_note)
            st.success(f"Kleine Note {k_note} hinzugefügt!")

    # Eingetragene Noten anzeigen
    st.write("**Eingetragene große Noten:**", fach_daten["gross"])
    st.write("**Eingetragene kleine Noten:**", fach_daten["klein"])

    st.markdown("---")

    # --- 5. BEREICH: DIE AUSWERTUNG (DEINE BERECHNUNG!) ---
    st.header("📊 Deine aktuellen Notenschnitte")

    for fach, daten in st.session_state.noten_buch.items():
        # Verhindern, dass wir durch 0 teilen (falls noch keine Noten eingetragen sind)
        hat_kleine = len(daten["klein"]) > 0
        hat_grosse = len(daten["gross"]) > 0

        if daten["typ"] == "ja":  # Hauptfach
            if hat_grosse and hat_kleine:
                schnitt_gross = sum(daten["gross"]) / len(daten["gross"])
                schnitt_klein = sum(daten["klein"]) / len(daten["klein"])
                gesamtschnitt = ((schnitt_gross * 2) + schnitt_klein) / 3
                st.metric(label=f"Schnitt {fach} (Hauptfach)", value=f"{gesamtschnitt:.2f}")
            else:
                st.write(f"ℹ️ *Für {fach} fehlen noch Noten in beiden Kategorien für den Gesamtschnitt.*")
        else:  # Nebenfach
            if hat_kleine:
                gesamtschnitt = sum(daten["klein"]) / len(daten["klein"])
                st.metric(label=f"Schnitt {fach} (Nebenfach)", value=f"{gesamtschnitt:.2f}")
            else:
                st.write(f"ℹ️ *Für {fach} wurden noch keine Noten eingetragen.*")

else:
    st.info("Füge oben dein erstes Fach hinzu, um mit der Noteneingabe zu starten!")