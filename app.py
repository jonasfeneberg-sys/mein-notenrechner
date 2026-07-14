import streamlit as st
import json
import os

# Name der Speicherdatei auf dem Server/Computer
SPEICHER_DATEI = "noten_datenbank.json"


# --- FUNKTIONEN FÜR DIE DAUERHAFTE SPEICHERUNG ---
def daten_speichern():
    """Speichert das aktuelle Notenbuch dauerhaft in einer JSON-Datei."""
    with open(SPEICHER_DATEI, "w", encoding="utf-8") as f:
        json.dump(st.session_state.noten_buch, f, indent=4)


def daten_laden():
    """Lädt das Notenbuch aus der Datei, falls diese existiert."""
    if os.path.exists(SPEICHER_DATEI):
        try:
            with open(SPEICHER_DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}  # Falls die Datei beschädigt ist, fangen wir leer an
    return {}


# --- 1. TITEL & DESIGN ---
st.set_page_config(page_title="Dauerhafter Notenrechner", page_icon="🎓", layout="centered")
st.title("🎓 Mein Schul-Notenrechner")
st.write("Verwalte deine Fächer, trage deine Noten ein und behalte deinen Schnitt – für immer gespeichert!")

# --- 2. DAS LANGE GEDÄCHTNIS DER APP ---
if "noten_buch" not in st.session_state:
    st.session_state.noten_buch = daten_laden()

# --- 3. BEREICH: NEUES FACH HINZUFÜGEN ---
st.header("➕ Neues Fach hinzufügen")

col1, col2 = st.columns([2, 1])
with col1:
    neues_fach = st.text_input("Name des Fachs", placeholder="z. B. Mathe, Deutsch...")
with col2:
    ist_hauptfach = st.radio("Fach-Typ:", ["Hauptfach", "Nebenfach"])

if st.button("Fach speichern", use_container_width=True):
    if neues_fach:
        if neues_fach in st.session_state.noten_buch:
            st.error(f"Das Fach '{neues_fach}' gibt es bereits!")
        else:
            typ = "ja" if ist_hauptfach == "Hauptfach" else "nein"

            st.session_state.noten_buch[neues_fach] = {
                "typ": typ,
                "gross": [],
                "klein": []
            }
            daten_speichern()
            st.success(f"Fach '{neues_fach}' wurde erfolgreich hinzugefügt und gespeichert!")
            st.rerun()
    else:
        st.warning("Bitte gib zuerst einen Namen für das Fach ein!")

st.markdown("---")

# --- 4. BEREICH: VERWALTUNG & NOTEN (Nur wenn Fächer existieren) ---
if st.session_state.noten_buch:
    st.header("📝 Noten eintragen & Fächer verwalten")

    ausgewaehltes_fach = st.selectbox("Wähle ein Fach aus:", list(st.session_state.noten_buch.keys()))
    fach_daten = st.session_state.noten_buch[ausgewaehltes_fach]

    if fach_daten["typ"] == "ja":
        st.info(f"'{ausgewaehltes_fach}' ist ein Hauptfach. Du kannst Schulaufgaben (groß) und kleine Noten eintragen.")

        col_g, col_k = st.columns(2)
        with col_g:
            g_note = st.number_input("Große Note (Schulaufgabe):", min_value=1, max_value=6, step=1, key="g_note")
            if st.button("Große Note hinzufügen"):
                fach_daten["gross"].append(g_note)
                daten_speichern()
                st.success(f"Große Note {g_note} hinzugefügt!")
                st.rerun()

        with col_k:
            k_note = st.number_input("Kleine Note (Ex/Abfrage):", min_value=1, max_value=6, step=1, key="k_note_haupt")
            if st.button("Kleine Note hinzufügen (Hauptfach)"):
                fach_daten["klein"].append(k_note)
                daten_speichern()
                st.success(f"Kleine Note {k_note} hinzugefügt!")
                st.rerun()
    else:
        st.info(f"'{ausgewaehltes_fach}' ist ein Nebenfach. Du kannst nur kleine Noten eintragen.")
        k_note = st.number_input("Kleine Note:", min_value=1, max_value=6, step=1, key="k_note_neben")
        if st.button("Kleine Note hinzufügen (Nebenfach)"):
            fach_daten["klein"].append(k_note)
            daten_speichern()
            st.success(f"Kleine Note {k_note} hinzugefügt!")
            st.rerun()

    st.write("### Aktuelle Noten verwalten:")

    if fach_daten["typ"] == "ja":
        st.write("**Eingetragene große Noten:**")
        if not fach_daten["gross"]:
            st.write("*Keine großen Noten eingetragen.*")
        else:
            for index, note in enumerate(fach_daten["gross"]):
                col_n, col_del = st.columns([4, 1])
                col_n.write(f"• Schulaufgabe: **{note}**")
                if col_del.button("Löschen", key=f"del_g_{index}"):
                    fach_daten["gross"].pop(index)
                    daten_speichern()
                    st.rerun()

    st.write("**Eingetragene kleine Noten:**")
    if not fach_daten["klein"]:
        st.write("*Keine kleinen Noten eingetragen.*")
    else:
        for index, note in enumerate(fach_daten["klein"]):
            col_n, col_del = st.columns([4, 1])
            col_n.write(f"• Kleine Note: **{note}**")
            if col_del.button("Löschen", key=f"del_k_{index}"):
                fach_daten["klein"].pop(index)
                daten_speichern()
                st.rerun()

    st.markdown("##### Gefahrzone:")
    if st.button(f"🚨 Ganzes Fach '{ausgewaehltes_fach}' löschen", use_container_width=True):
        del st.session_state.noten_buch[ausgewaehltes_fach]
        daten_speichern()
        st.warning(f"Fach '{ausgewaehltes_fach}' wurde vollständig gelöscht!")
        st.rerun()

    st.markdown("---")

    # --- 5. BEREICH: DIE AUSWERTUNG ---
    st.header("📊 Deine aktuellen Notenschnitte")

    for fach, daten in list(st.session_state.noten_buch.items()):
        hat_kleine = len(daten["klein"]) > 0
        hat_grosse = len(daten["gross"]) > 0

        # --- FALL 1: HAUPTFACH ---
        if daten["typ"] == "ja":
            # Unterfall A: Beide Notentypen sind da (Spezialrechnung)
            if hat_grosse and hat_kleine:
                schnitt_gross = sum(daten["gross"]) / len(daten["gross"])
                schnitt_klein = sum(daten["klein"]) / len(daten["klein"])
                gesamtschnitt = ((schnitt_gross * 2) + schnitt_klein) / 3
                st.metric(label=f"Schnitt {fach} (Hauptfach)", value=f"{gesamtschnitt:.2f}")

            # Unterfall B: Nur große Noten vorhanden
            elif hat_grosse and not hat_kleine:
                gesamtschnitt = sum(daten["gross"]) / len(daten["gross"])
                st.metric(label=f"Schnitt {fach} (Hauptfach - nur Schulaufgaben)", value=f"{gesamtschnitt:.2f}")

            # Unterfall C: Nur kleine Noten vorhanden
            elif hat_kleine and not hat_grosse:
                gesamtschnitt = sum(daten["klein"]) / len(daten["klein"])
                st.metric(label=f"Schnitt {fach} (Hauptfach - nur kleine Noten)", value=f"{gesamtschnitt:.2f}")

            # Unterfall D: Noch gar keine Noten
            else:
                st.write(f"ℹ️ *Für {fach} wurden noch keine Noten eingetragen.*")

        # --- FALL 2: NEBENFACH ---
        else:
            if hat_kleine:
                gesamtschnitt = sum(daten["klein"]) / len(daten["klein"])
                st.metric(label=f"Schnitt {fach} (Nebenfach)", value=f"{gesamtschnitt:.2f}")
            else:
                st.write(f"ℹ️ *Für {fach} wurden noch keine Noten eingetragen.*")

else:
    st.info("Füge oben dein erstes Fach hinzu, um mit der Noteneingabe zu starten!")