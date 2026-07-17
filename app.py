import streamlit as st
from PIL import Image

try:
    app_icon = Image.open("logo.png")
except Exception:
    app_icon = "🎓"

st.set_page_config(page_title="Privater Notenrechner", page_icon=app_icon, layout="centered")

st.markdown(
    """
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/jonasfeneberg-sys/mein-notenrechner/main/logo.png">
    <style>
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }

    p, span, label, .stMetric label {
        color: #f8fafc !important;
    }

    div.stButton > button {
        border-radius: 16px !important;
        padding: 20px 15px !important;
        font-weight: bold !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        transition: all 0.2s ease-in-out !important;
        min-height: 100px !important;
        white-space: pre-line !important;
    }

    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        border-color: #10b981 !important;
        background-color: #0f172a !important;
        color: #10b981 !important;
    }

    div[data-baseweb="input"] input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }

    div[data-testid="stForm"] {
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        background-color: #0f172a !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def get_schnitt_wert(fach_daten):
    grosse = fach_daten.get("gross", [])
    kleine = fach_daten.get("klein", [])
    ist_hauptfach = fach_daten.get("typ") == "ja"

    if not grosse and not kleine:
        return 7.0

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


if "noten_buch" not in st.session_state:
    st.session_state.noten_buch = {}
if "active_subject" not in st.session_state:
    st.session_state.active_subject = None


@st.dialog("Fach löschen?")
def loesch_bestaetigung(fach_name):
    st.write(f"Bist du dir wirklich sicher, dass du das Fach *'{fach_name}'* mit allen Noten löschen willst?")
    st.write("")
    col_ja, col_nein = st.columns(2)
    with col_ja:
        if st.button("Ja, löschen", type="primary", use_container_width=True):
            del st.session_state.noten_buch[fach_name]
            st.session_state.active_subject = None
            st.toast(f"Fach '{fach_name}' wurde gelöscht!")
            st.rerun()
    with col_nein:
        if st.button("Abbrechen", use_container_width=True):
            st.rerun()


if st.session_state.active_subject is None:
    st.title("🎓 Mein Notenrechner")

    alle_schnitte = []
    for fach, daten in st.session_state.noten_buch.items():
        schnitt = get_schnitt_wert(daten)
        if schnitt != 7.0:
            alle_schnitte.append(schnitt)

    if alle_schnitte:
        gesamtschnitt_aller_faecher = sum(alle_schnitte) / len(alle_schnitte)
        with st.container(border=True):
            st.metric(label="📊 Aktueller Gesamtschnitt", value=f"{gesamtschnitt_aller_faecher:.2f}")
    else:
        st.info("Trage in mindestens einem Fach Noten ein, um deinen Gesamtschnitt zu sehen.")

    st.markdown("---")
    st.subheader("📚 Meine Fächer")

    if not st.session_state.noten_buch:
        st.info("Noch keine Fächer angelegt. Erstelle dein erstes Fach weiter unten!")
    else:
        sortierte_faecher = sorted(
            st.session_state.noten_buch.items(),
            key=lambda x: get_schnitt_wert(x[1])
        )

        cols = st.columns(2)
        for index, (fach_name, daten) in enumerate(sortierte_faecher):
            col = cols[index % 2]
            schnitt = get_schnitt_wert(daten)

            if schnitt == 7.0:
                anzeige_schnitt = "-.-"
                emoji = "📖"
            else:
                anzeige_schnitt = f"{schnitt:.2f}"
                emoji = "⭐" if schnitt <= 2.0 else "📝"

            kachel_text = f"{emoji} {fach_name}\nSchnitt: {anzeige_schnitt}"

            with col:
                if st.button(kachel_text, key=f"kachel_{fach_name}", use_container_width=True):
                    st.session_state.active_subject = fach_name
                    st.rerun()

    st.markdown("---")
    st.subheader("➕ Neues Fach hinzufügen")
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


else:
    fach_name = st.session_state.active_subject
    fach_daten = st.session_state.noten_buch[fach_name]
    schnitt = get_schnitt_wert(fach_daten)
    anzeige_schnitt = "-.-" if schnitt == 7.0 else f"{schnitt:.2f}"

    if st.button("⬅ Zurück zur Übersicht", use_container_width=True):
        st.session_state.active_subject = None
        st.rerun()

    st.markdown("---")
    col_titel, col_schnitt = st.columns([2, 1])
    with col_titel:
        st.title(f"📖 {fach_name}")
        typ_text = "Hauptfach" if fach_daten["typ"] == "ja" else "Nebenfach"
        st.write(f"Fach-Typ: **{typ_text}**")
    with col_schnitt:
        st.metric(label="Aktueller Schnitt", value=anzeige_schnitt)

    st.markdown("---")
    st.subheader("📝 Note hinzufügen")

    if fach_daten["typ"] == "ja":
        st.write("*Große Note hinzufügen (Schulaufgabe):*")
        cols_g = st.columns(6)
        for note_wert in range(1, 7):
            if cols_g[note_wert - 1].button(f"*{note_wert}*", key=f"detail_g_{note_wert}", use_container_width=True):
                fach_daten["gross"].append(note_wert)
                st.success(f"Große Note {note_wert} hinzugefügt!")
                st.rerun()

        st.write("")
        st.write("*Kleine Note hinzufügen (Ex/Abfrage/Mündlich):*")
        cols_k = st.columns(6)
        for note_wert in range(1, 7):
            if cols_k[note_wert - 1].button(f"*{note_wert}*", key=f"detail_k_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Kleine Note {note_wert} hinzugefügt!")
                st.rerun()
    else:
        st.write("*Kleine Note hinzufügen:*")
        cols_n = st.columns(6)
        for note_wert in range(1, 7):
            if cols_n[note_wert - 1].button(f"*{note_wert}*", key=f"detail_n_{note_wert}", use_container_width=True):
                fach_daten["klein"].append(note_wert)
                st.success(f"Note {note_wert} hinzugefügt!")
                st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Eingetragene Noten verwalten")

    if fach_daten["typ"] == "ja":
        st.write("**Große Noten:**")
        if not fach_daten["gross"]:
            st.info("Keine großen Noten eingetragen.")
        else:
            for index, note in enumerate(fach_daten["gross"]):
                col_n, col_del = st.columns([4, 1])
                col_n.write(f"• Schulaufgabe: *{note}*")
                if col_del.button("🗑️", key=f"del_g_{index}"):
                    fach_daten["gross"].pop(index)
                    st.rerun()

    st.write("**Kleine Noten:**")
    if not fach_daten["klein"]:
        st.info("Keine kleinen Noten eingetragen.")
    else:
        for index, note in enumerate(fach_daten["klein"]):
            col_n, col_del = st.columns([4, 1])
            col_n.write(f"• Kleine Note: *{note}*")
            if col_del.button("🗑️", key=f"del_k_{index}"):
                fach_daten["klein"].pop(index)
                st.rerun()

    st.markdown("---")
    st.markdown("##### ⚠️ Gefahrzone")
    if st.button(f"Ganzes Fach '{fach_name}' unwiderruflich löschen", use_container_width=True, type="secondary"):
        loesch_bestaetigung(fach_name)