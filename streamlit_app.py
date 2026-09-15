import streamlit as st
from google import genai
from pathlib import Path
import copy


# --------------------------------------------------
# INSTELLINGEN
# --------------------------------------------------

st.set_page_config(
    page_title="Expeditie Eiland",
    page_icon="🏝️",
    layout="centered"
)

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


# --------------------------------------------------
# BIG FIVE
# --------------------------------------------------

TREKKEN = [
    "Extraversie",
    "Vriendelijkheid",
    "Emotionele stabiliteit",
    "Zorgvuldigheid",
    "Openheid voor ervaringen"
]

UITLEG = {
    "Extraversie":
        "Extraversie gaat over de mate waarin iemand sociale contacten opzoekt en gemakkelijk contact legt. "
        "Lage score = eerder introvert en stiller in groepen. "
        "Hoge score = sociaal, actief en vlot in contact. "
        "1 = sterk introvert | 10 = sterk extravert",

    "Vriendelijkheid":
        "Vriendelijkheid gaat over de mate waarin iemand anderen helpt, vertrouwt en rekening houdt met anderen. "
        "Lage score = eerder afstandelijk, kritisch of competitief. "
        "Hoge score = behulpzaam, vriendelijk en gericht op samenwerking. "
        "1 = sterk afstandelijk | 10 = sterk vriendelijk",

    "Emotionele stabiliteit":
        "Emotionele stabiliteit gaat over hoe iemand omgaat met stress, problemen en tegenslagen. "
        "Lage score = sneller bezorgd, gespannen of emotioneel van slag. "
        "Hoge score = rustig en veerkrachtig onder druk. "
        "1 = sterk stressgevoelig | 10 = zeer emotioneel stabiel",

    "Zorgvuldigheid":
        "Zorgvuldigheid gaat over hoe georganiseerd, ordelijk en verantwoordelijk iemand is. "
        "Lage score = eerder slordig, chaotisch of impulsief. "
        "Hoge score = plant, werkt nauwkeurig en maakt dingen af. "
        "1 = sterk onzorgvuldig | 10 = zeer zorgvuldig",

    "Openheid voor ervaringen":
        "Openheid voor ervaringen gaat over de mate waarin iemand nieuwsgierig is en openstaat voor nieuwe ideeën en ervaringen. "
        "Lage score = liever bekende oplossingen en gewoontes. "
        "Hoge score = nieuwsgierig, creatief en bereid om iets nieuws te proberen. "
        "1 = sterk gesloten | 10 = zeer open voor nieuwe ervaringen"
}


# --------------------------------------------------
# PERSONAGES
# --------------------------------------------------

personages = [
    {
        "naam": "Noor",
        "afbeelding": "images/noor.png",
        "beschrijving": """
Noor probeert graag onbekende dingen uit en bedenkt vaak originele oplossingen.
In een groep neemt ze gemakkelijk het woord en krijgt ze anderen enthousiast.
Ze begint echter regelmatig aan iets nieuws voordat het vorige af is.
Als iets mislukt, maakt ze zich daar meestal niet lang druk over.
"""
    },
    {
        "naam": "Elias",
        "afbeelding": "images/elias.png",
        "beschrijving": """
Elias houdt van duidelijke afspraken en maakt graag vooraf een planning.
Hij voert taken nauwkeurig uit en merkt snel wanneer anderen zich niet aan afspraken houden.
Hij praat niet veel in grote groepen en kiest liever voor een aanpak waarvan bewezen is
dat die werkt. Als anderen slordig werken, kan hij nogal kritisch reageren.
"""
    },
    {
        "naam": "Aya",
        "afbeelding": "images/aya.png",
        "beschrijving": """
Aya merkt snel wanneer iemand zich niet goed voelt en probeert conflicten te vermijden.
Ze helpt anderen vaak zonder dat ze daarom vragen.
Zelf neemt ze niet snel de leiding en vindt ze het lastig om iemand tegen te spreken.
In nieuwe situaties is ze aanvankelijk onzeker en piekert ze gemakkelijk over wat er mis kan gaan.
"""
    },
    {
        "naam": "Mats",
        "afbeelding": "images/mats.png",
        "beschrijving": """
Mats blijft meestal kalm, ook wanneer anderen in paniek raken.
Hij neemt snel beslissingen en durft risico's te nemen.
Hij vindt discussies niet erg en zegt rechtstreeks wat hij denkt,
ook wanneer anderen dat onaangenaam vinden.
Hij heeft weinig geduld voor lange vergaderingen of uitgebreide plannen.
"""
    },
    {
        "naam": "Lina",
        "afbeelding": "images/lina.png",
        "beschrijving": """
Lina is nieuwsgierig en observeert eerst goed voordat ze iets doet.
Ze vindt het interessant om uit te zoeken hoe dingen werken
en kan lang geconcentreerd aan een probleem werken.
Ze heeft weinig behoefte om voortdurend met anderen bezig te zijn.
Wanneer iets belangrijk is, kan ze zich er wel behoorlijk zorgen over maken.
"""
    }
]


# --------------------------------------------------
# VERWACHTE PROFIELEN VOOR SNELLE FEEDBACK
# --------------------------------------------------

VERWACHT = {
    "Noor": {
        "Extraversie": {"min": 7, "max": 10, "uitleg": "ze neemt gemakkelijk het woord en krijgt anderen enthousiast"},
        "Vriendelijkheid": {"min": 5, "max": 8, "uitleg": "ze werkt in groep enthousiasmerend, maar de tekst zegt weinig expliciet over helpen of meegaandheid"},
        "Emotionele stabiliteit": {"min": 7, "max": 10, "uitleg": "als iets mislukt, maakt ze zich daar meestal niet lang druk over"},
        "Zorgvuldigheid": {"min": 2, "max": 4, "uitleg": "ze begint vaak aan iets nieuws voordat het vorige af is"},
        "Openheid voor ervaringen": {"min": 8, "max": 10, "uitleg": "ze probeert graag onbekende dingen uit en bedenkt originele oplossingen"}
    },
    "Elias": {
        "Extraversie": {"min": 2, "max": 4, "uitleg": "hij praat niet veel in grote groepen"},
        "Vriendelijkheid": {"min": 3, "max": 6, "uitleg": "hij kan kritisch reageren als anderen slordig werken"},
        "Emotionele stabiliteit": {"min": 5, "max": 7, "uitleg": "de tekst toont geen sterke stressgevoeligheid, maar ook geen uitgesproken kalmte onder druk"},
        "Zorgvuldigheid": {"min": 8, "max": 10, "uitleg": "hij houdt van duidelijke afspraken, plant graag en werkt nauwkeurig"},
        "Openheid voor ervaringen": {"min": 2, "max": 5, "uitleg": "hij kiest liever voor een aanpak waarvan bewezen is dat die werkt"}
    },
    "Aya": {
        "Extraversie": {"min": 2, "max": 5, "uitleg": "ze neemt niet snel de leiding en spreekt anderen moeilijk tegen"},
        "Vriendelijkheid": {"min": 8, "max": 10, "uitleg": "ze helpt anderen vaak spontaan en probeert conflicten te vermijden"},
        "Emotionele stabiliteit": {"min": 2, "max": 4, "uitleg": "in nieuwe situaties is ze onzeker en ze piekert gemakkelijk"},
        "Zorgvuldigheid": {"min": 4, "max": 7, "uitleg": "de tekst zegt niet heel veel over planning of ordelijkheid"},
        "Openheid voor ervaringen": {"min": 3, "max": 5, "uitleg": "in nieuwe situaties is ze aanvankelijk onzeker"}
    },
    "Mats": {
        "Extraversie": {"min": 6, "max": 8, "uitleg": "hij zegt rechtstreeks wat hij denkt en neemt snel beslissingen"},
        "Vriendelijkheid": {"min": 2, "max": 4, "uitleg": "hij zegt dingen ook wanneer anderen dat onaangenaam vinden en heeft weinig geduld"},
        "Emotionele stabiliteit": {"min": 8, "max": 10, "uitleg": "hij blijft meestal kalm, ook wanneer anderen in paniek raken"},
        "Zorgvuldigheid": {"min": 2, "max": 4, "uitleg": "hij heeft weinig geduld voor lange vergaderingen of uitgebreide plannen"},
        "Openheid voor ervaringen": {"min": 6, "max": 8, "uitleg": "hij durft risico's te nemen en kiest snel voor actie"}
    },
    "Lina": {
        "Extraversie": {"min": 2, "max": 4, "uitleg": "ze heeft weinig behoefte om voortdurend met anderen bezig te zijn"},
        "Vriendelijkheid": {"min": 4, "max": 7, "uitleg": "de tekst toont geen sterke afstandelijkheid maar ook geen uitgesproken hulpgerichtheid"},
        "Emotionele stabiliteit": {"min": 3, "max": 5, "uitleg": "wanneer iets belangrijk is, kan ze zich er behoorlijk zorgen over maken"},
        "Zorgvuldigheid": {"min": 7, "max": 9, "uitleg": "ze observeert eerst goed en kan lang geconcentreerd aan een probleem werken"},
        "Openheid voor ervaringen": {"min": 8, "max": 10, "uitleg": "ze is nieuwsgierig en wil uitzoeken hoe dingen werken"}
    }
}


# --------------------------------------------------
# EXPEDITIEROLLEN
# --------------------------------------------------

ROLLEN = {
    "Verkenner": "verkent onbekend terrein en zoekt nieuwe routes of kansen",
    "Planner / voorraadbeheerder": "houdt overzicht over voedsel, water en materiaal",
    "Kampbouwer": "helpt bij het opzetten en onderhouden van een veilige kampplaats",
    "Onderzoeker": "observeert het terrein, planten, weer en mogelijke gevaren",
    "Groepscoördinator": "probeert de groep te organiseren en conflicten te beperken"
}


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "fase" not in st.session_state:
    st.session_state.fase = "intro"

if "groepsleden" not in st.session_state:
    st.session_state.groepsleden = ""

if "analyse_intro_getoond" not in st.session_state:
    st.session_state.analyse_intro_getoond = False

if "personage_index" not in st.session_state:
    st.session_state.personage_index = 0

if "resultaten" not in st.session_state:
    st.session_state.resultaten = {}

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "rollen" not in st.session_state:
    st.session_state.rollen = {}

if "rolredenen" not in st.session_state:
    st.session_state.rolredenen = {}

if "simulatieronde" not in st.session_state:
    st.session_state.simulatieronde = 1

if "huidige_profielen" not in st.session_state:
    st.session_state.huidige_profielen = {}

if "simulatieverhalen" not in st.session_state:
    st.session_state.simulatieverhalen = {}

if "aanpassingsgeschiedenis" not in st.session_state:
    st.session_state.aanpassingsgeschiedenis = []


# --------------------------------------------------
# HULPFUNCTIES
# --------------------------------------------------

def profielen_naar_tekst(profielen):
    tekst = ""

    for naam, profiel in profielen.items():
        tekst += f"""
{naam}
- Extraversie: {profiel['Extraversie']}/10
- Vriendelijkheid: {profiel['Vriendelijkheid']}/10
- Emotionele stabiliteit: {profiel['Emotionele stabiliteit']}/10
- Zorgvuldigheid: {profiel['Zorgvuldigheid']}/10
- Openheid voor ervaringen: {profiel['Openheid voor ervaringen']}/10

"""

    return tekst


def rollen_naar_tekst(rollen, rolredenen):
    tekst = ""

    for rol, persoon in rollen.items():
        reden = rolredenen.get(rol, "")
        tekst += f"- {rol}: {persoon}. Reden: {reden}\n"

    return tekst


def reset_spel():
    st.session_state.fase = "intro"
    st.session_state.groepsleden = ""
    st.session_state.analyse_intro_getoond = False
    st.session_state.personage_index = 0
    st.session_state.resultaten = {}
    st.session_state.feedback = {}
    st.session_state.rollen = {}
    st.session_state.rolredenen = {}
    st.session_state.simulatieronde = 1
    st.session_state.huidige_profielen = {}
    st.session_state.simulatieverhalen = {}
    st.session_state.aanpassingsgeschiedenis = []


def score_feedback(score, minimum, maximum, uitleg):
    if minimum <= score <= maximum:
        return "goed", f"Deze score past goed bij de beschrijving: {uitleg}."
    elif minimum - 1 <= score <= maximum + 1:
        return "twijfel", f"Deze score is nog verdedigbaar, maar kijk goed naar: {uitleg}."
    elif score < minimum:
        return "laag", f"Deze score lijkt wat te laag. Op basis van de beschrijving zou eerder ongeveer {minimum}–{maximum}/10 passen, omdat {uitleg}."
    else:
        return "hoog", f"Deze score lijkt wat te hoog. Op basis van de beschrijving zou eerder ongeveer {minimum}–{maximum}/10 passen, omdat {uitleg}."


def maak_feedback_persoon(naam, scores, gekozen_trekken):
    profiel = VERWACHT[naam]

    goed_gezien = []
    herbekijk = []
    uitleg_feedback = []

    for trek in TREKKEN:
        verwacht = profiel[trek]
        status, tekst = score_feedback(
            scores[trek],
            verwacht["min"],
            verwacht["max"],
            verwacht["uitleg"]
        )

        if status in ["goed", "twijfel"]:
            goed_gezien.append(f"**{trek}:** {tekst}")
        else:
            herbekijk.append(f"**{trek}:** {tekst}")

    for trek in gekozen_trekken:
        verwacht = profiel[trek]
        status, _ = score_feedback(
            scores[trek],
            verwacht["min"],
            verwacht["max"],
            verwacht["uitleg"]
        )

        if status in ["goed", "twijfel"]:
            uitleg_feedback.append(
                f"**{trek}:** Jullie gekozen score is verdedigbaar. Een sterke uitleg verwijst expliciet naar het feit dat {verwacht['uitleg']}."
            )
        else:
            uitleg_feedback.append(
                f"**{trek}:** Deze score is moeilijker te verdedigen. Kijk opnieuw naar het feit dat {verwacht['uitleg']} en pas eventueel de score of jullie uitleg aan."
            )

    advies = []
    if herbekijk:
        advies.append("Herbekijk eerst de scores die duidelijk te laag of te hoog lijken.")
    advies.append("Verwijs in jullie uitleg altijd naar concreet gedrag uit de beschrijving.")
    advies.append("Denk niet in exacte cijfers, maar vooral in laag, gemiddeld of hoog.")

    tekst = "### Goed gezien\n"
    if goed_gezien:
        tekst += "\n".join([f"- {x}" for x in goed_gezien[:3]])
    else:
        tekst += "- Er zijn nog weinig scores die echt overtuigen."

    tekst += "\n\n### Herbekijk dit\n"
    if herbekijk:
        tekst += "\n".join([f"- {x}" for x in herbekijk[:4]])
    else:
        tekst += "- De meeste scores zijn goed verdedigbaar."

    tekst += "\n\n### Jullie uitleg\n"
    if uitleg_feedback:
        tekst += "\n".join([f"- {x}" for x in uitleg_feedback])
    else:
        tekst += "- Jullie hebben nog geen twee eigenschappen gekozen."

    tekst += "\n\n### Advies\n"
    tekst += "\n".join([f"- {x}" for x in advies[:2]])

    return tekst


def maak_verslag():
    lijnen = []
    lijnen.append("OVERZICHT EXPEDITIE EILAND")
    lijnen.append("")
    lijnen.append(f"Groepsleden: {st.session_state.groepsleden}")
    lijnen.append("")
    lijnen.append("1. Persoonlijkheidsanalyse")
    lijnen.append("We analyseerden Noor, Elias, Aya, Mats en Lina met de Big Five-persoonlijkheidstrekken.")
    lijnen.append("")

    lijnen.append("2. Expeditierollen")
    for rol, persoon in st.session_state.rollen.items():
        reden = st.session_state.rolredenen.get(rol, "")
        lijnen.append(f"- {rol}: {persoon}")
        lijnen.append(f"  Reden: {reden}")
    lijnen.append("")

    lijnen.append("3. Aanpassingen tijdens de overlevingsproeven")
    if st.session_state.aanpassingsgeschiedenis:
        for i, ronde_data in enumerate(st.session_state.aanpassingsgeschiedenis, start=1):
            lijnen.append(f"Na mislukte expeditie {i}:")
            for wijziging in ronde_data["wijzigingen"]:
                lijnen.append(
                    f"- {wijziging['naam']}: {wijziging['trek']} van "
                    f"{wijziging['oud']}/10 naar {wijziging['nieuw']}/10"
                )
            lijnen.append(f"  Waarom: {ronde_data['reden']}")
            lijnen.append("")
    else:
        lijnen.append("- Er waren geen aanpassingen nodig.")
        lijnen.append("")

    lijnen.append("4. Eindresultaat")
    lijnen.append("We bleven de persoonlijkheden aanpassen tot we een groep hadden gemaakt die zes maanden kon overleven op het eiland.")
    lijnen.append("Daarna werd de groep gered.")
    lijnen.append("")

    return "\n".join(lijnen)


# ==================================================
# INTRO
# ==================================================

if st.session_state.fase == "intro":

    st.title("Expeditie Eiland")

    eiland_pad = Path("images/eiland.png")
    if eiland_pad.exists():
        st.image(str(eiland_pad), use_container_width=True)

    st.markdown("""
Een groep jongeren is neergestort op een onbewoond eiland.

Redding kan pas over **zes maanden** komen.

Jullie missie:

**1.** schat hun persoonlijkheid in  
**2.** stel een expeditieteam samen  
**3.** ontdek of deze groep kan overleven  
**4.** als het misloopt, pas persoonlijkheden aan om hun overlevingskans te verhogen  
**5.** blijf proberen tot jullie een groep hebben gemaakt die het eiland wél overleeft
""")

    st.info(
        "Op het einde maakt de app automatisch een overzicht van jullie antwoorden en aanpassingen. "
        "Dat overzicht moeten jullie indienen bij de leerkracht."
    )

    groepsleden = st.text_input(
        "Namen van de groepsleden",
        placeholder="bv. Nora, Yassine, Marie"
    )

    if st.button("Start de expeditie"):
        if not groepsleden.strip():
            st.warning("Vul eerst jullie namen in.")
        else:
            st.session_state.groepsleden = groepsleden
            st.session_state.fase = "analyse"
            st.session_state.analyse_intro_getoond = False
            st.rerun()


# ==================================================
# PERSOONLIJKHEDEN ANALYSEREN
# ==================================================

elif st.session_state.fase == "analyse":

    if not st.session_state.analyse_intro_getoond:

        st.title("Fase 1 — Leer de groep kennen")

        st.markdown("""
Voor jullie de expeditie kunnen testen, moeten jullie eerst de persoonlijkheid van de vijf jongeren inschatten.

Gebruik daarvoor de **Big Five-persoonlijkheidstrekken** uit het handboek, **pagina 157–158**.

Bij elke persoon:

- geef je voor alle 5 trekken een score;
- leg je 2 scores kort uit;
- krijg je meteen feedback.

Daarna gebruiken jullie die profielen om een **expeditieteam** op te bouwen.
""")

        if st.button("Ga naar persoon 1"):
            st.session_state.analyse_intro_getoond = True
            st.rerun()

    else:

        index = st.session_state.personage_index

        st.title("Fase 1 — Leer de groep kennen")
        st.progress(index / len(personages))

        if index >= len(personages):

            st.success("Alle vijf persoonlijkheidsprofielen zijn klaar.")

            st.markdown("""
Jullie weten nu beter hoe de vijf jongeren in elkaar zitten.

De volgende stap is om hen **expeditierollen** te geven.
""")

            if st.button("Ga naar de expeditierollen"):
                st.session_state.fase = "rollen"
                st.rerun()

        else:

            persoon = personages[index]
            naam = persoon["naam"]

            st.caption(f"Persoon {index + 1} van {len(personages)}")
            st.header(naam)

            afbeelding = Path(persoon["afbeelding"])
            if afbeelding.exists():
                st.image(str(afbeelding), width=340)

            st.write(persoon["beschrijving"])

            st.markdown("### Schat de persoonlijkheid in")

            st.info(
                "Zoek in de beschrijving naar concrete aanwijzingen. "
                "Welke gedragingen wijzen op hoge of lage extraversie, vriendelijkheid, "
                "emotionele stabiliteit, zorgvuldigheid en openheid voor ervaringen?"
            )

            scores = {}

            for trek in TREKKEN:
                scores[trek] = st.slider(
                    trek,
                    min_value=1,
                    max_value=10,
                    value=5,
                    key=f"{naam}_{trek}",
                    help=UITLEG[trek]
                )

            st.markdown("### Licht 2 keuzes toe")

            gekozen_trekken = st.multiselect(
                "Welke 2 eigenschappen willen jullie uitleggen?",
                TREKKEN,
                max_selections=2,
                key=f"{naam}_gekozen_trekken"
            )

            motivaties = {}

            for trek in gekozen_trekken:
                motivaties[trek] = st.text_area(
                    f"Waarom gaven jullie {naam} deze score voor {trek}?",
                    placeholder="Verwijs naar concrete aanwijzingen uit de beschrijving...",
                    key=f"{naam}_motivatie_{trek}"
                )

            if st.button("Geef feedback", key=f"feedback_{naam}"):

                if len(gekozen_trekken) != 2:
                    st.warning("Kies precies 2 eigenschappen.")
                elif any(not motivaties[trek].strip() for trek in gekozen_trekken):
                    st.warning("Schrijf bij beide eigenschappen een korte uitleg.")
                else:
                    st.session_state.feedback[naam] = maak_feedback_persoon(
                        naam,
                        scores,
                        gekozen_trekken
                    )

            if naam in st.session_state.feedback:
                st.markdown(st.session_state.feedback[naam])

                if st.button("Bewaar en ga verder", key=f"volgende_{naam}"):
                    st.session_state.resultaten[naam] = {
                        trek: st.session_state[f"{naam}_{trek}"]
                        for trek in TREKKEN
                    }
                    st.session_state.personage_index += 1
                    st.rerun()


# ==================================================
# EXPEDITIEROLLEN
# ==================================================

elif st.session_state.fase == "rollen":

    st.title("Fase 2 — Stel de expeditie samen")

    kaart_pad = Path("images/eilandkaart.png")
    if kaart_pad.exists():
        st.image(str(kaart_pad), use_container_width=True)

    st.markdown("""
Jullie gaan nu een echte expeditie opzetten.

Een ontdekkingsreis draait niet alleen om overleven, maar ook om:

- onbekend terrein verkennen
- materiaal en voedsel beheren
- gevaren observeren
- samenwerken in moeilijke omstandigheden

Geef daarom elk van de vijf jongeren een **expeditierol**.
""")

    gekozen_rollen = {}
    gekozen_redenen = {}

    for rol, beschrijving in ROLLEN.items():
        st.markdown(f"### {rol}")
        st.caption(beschrijving)

        gekozen_rollen[rol] = st.selectbox(
            f"Wie kiezen jullie als {rol}?",
            [p["naam"] for p in personages],
            key=f"rol_{rol}"
        )

        gekozen_redenen[rol] = st.text_area(
            f"Waarom past deze persoon volgens jullie bij de rol van {rol}?",
            placeholder="Verbind de rol met de persoonlijkheid van deze persoon...",
            key=f"reden_rol_{rol}"
        )

    st.info(
        "Hierna begint de echte overlevingsproef. "
        "Als de groep het niet haalt, blijven jullie persoonlijkheden aanpassen "
        "tot jullie een groep hebben gemaakt die kan overleven."
    )

    if st.button("Start de expeditie"):

        if len(set(gekozen_rollen.values())) != len(gekozen_rollen.values()):
            st.warning("Geef elke rol aan een andere persoon.")
        elif any(not tekst.strip() for tekst in gekozen_redenen.values()):
            st.warning("Leg bij elke rol kort uit waarom die persoon daarbij past.")
        else:
            st.session_state.rollen = gekozen_rollen
            st.session_state.rolredenen = gekozen_redenen
            st.session_state.huidige_profielen = copy.deepcopy(st.session_state.resultaten)
            st.session_state.simulatieronde = 1
            st.session_state.simulatieverhalen = {}
            st.session_state.aanpassingsgeschiedenis = []
            st.session_state.fase = "simulatie"
            st.rerun()


# ==================================================
# OVERLEVINGSSIMULATIE
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = st.session_state.simulatieronde

    st.title("Fase 3 — De expeditie")

    kaart_pad = Path("images/eilandkaart.png")
    if kaart_pad.exists():
        st.image(str(kaart_pad), use_container_width=True)

    if ronde == 1:
        st.caption("De expeditie begint aan de kust van het eiland.")
    else:
        st.caption("De aangepaste expeditie probeert het opnieuw.")

    st.info(
        "Jullie doel is nu duidelijk: blijf de persoonlijkheden aanpassen tot jullie "
        "een groep hebben gemaakt die zes maanden kan overleven."
    )

    with st.expander("Bekijk de huidige groep"):

        st.markdown("**Persoonlijkheden**")
        for naam, profiel in st.session_state.huidige_profielen.items():
            st.write(
                f"{naam}: "
                f"Extraversie {profiel['Extraversie']} | "
                f"Vriendelijkheid {profiel['Vriendelijkheid']} | "
                f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']} | "
                f"Zorgvuldigheid {profiel['Zorgvuldigheid']} | "
                f"Openheid {profiel['Openheid voor ervaringen']}"
            )

        st.markdown("**Expeditierollen**")
        for rol, persoon in st.session_state.rollen.items():
            st.write(f"{rol}: {persoon}")

    if ronde not in st.session_state.simulatieverhalen:

        if ronde == 1:
            st.markdown("Zijn deze vijf jongeren, met deze persoonlijkheden en rollen, in staat om te overleven?")
        else:
            st.markdown("Hebben jullie aanpassingen de overlevingskans voldoende verhoogd?")

        if st.button("Start de overlevingsproef", key=f"start_test_{ronde}"):

            profielen_tekst = profielen_naar_tekst(st.session_state.huidige_profielen)
            rollen_tekst = rollen_naar_tekst(st.session_state.rollen, st.session_state.rolredenen)

            if ronde <= 3:
                uitkomst = "MISLUKT"
            else:
                uitkomst = "SLAAGT"

            laatste_aanpassing = ""

            if st.session_state.aanpassingsgeschiedenis:
                laatste = st.session_state.aanpassingsgeschiedenis[-1]
                laatste_aanpassing += "Laatste persoonlijkheidsaanpassingen:\n"
                for wijziging in laatste["wijzigingen"]:
                    laatste_aanpassing += (
                        f"- {wijziging['naam']}: "
                        f"{wijziging['trek']} van {wijziging['oud']} naar {wijziging['nieuw']}\n"
                    )
                laatste_aanpassing += f"\nWaarom de leerlingen dachten dat dit zou helpen:\n{laatste['reden']}\n"

            prompt = f"""
Je bent de verteller van een kort survivalverhaal voor leerlingen van 17 jaar.

BELANGRIJK:
- Schrijf ALLES volledig in het Nederlands.
- Gebruik geen Engelse woorden of Engelse tussenkopjes.
- Alle titels moeten in het Nederlands zijn.

Context:
Vijf jongeren zijn gestrand op een onbewoond eiland en moeten zes maanden overleven.
Ze ondernemen tegelijk een soort ontdekkingsreis door onbekend terrein.

Hun persoonlijkheidsprofielen zijn:

{profielen_tekst}

Hun expeditierollen zijn:

{rollen_tekst}

{laatste_aanpassing}

De verplichte uitkomst van deze simulatie is:
{uitkomst}

Regels:
- Bij MISLUKT haalt de groep de zes maanden niet en sterft voor de redding.
- Beschrijf dat niet grafisch.
- Bij SLAAGT overleeft de groep zes maanden en wordt de groep gered.
- Baseer het verhaal duidelijk op de persoonlijkheden én de expeditierollen.
- Laat de expeditie verlopen in drie fasen: kust, binnenland en hoogtepunt / uitkijkpunt.
- Laat zien dat eigenschappen voordelen én nadelen hebben.
- Laat bij latere pogingen duidelijk zien wat door de aanpassingen beter gaat.
- Houd het kort, levendig en leesbaar.
- Gebruik concrete problemen: kamp bouwen, water vinden, voedsel bewaren, verkennen, risico's, conflicten, taakverdeling.

Gebruik exact deze structuur:

### Fase 1 — De kust
Maximaal 2 korte zinnen.

### Fase 2 — Het binnenland
Maximaal 2 korte zinnen.

### Fase 3 — Het hoogtepunt
Maximaal 2 korte zinnen.

### Uitkomst
Maximaal 2 korte zinnen.

### Waarom?
- één kort punt
- één kort punt
"""

            with st.spinner("De expeditie wordt gesimuleerd..."):

                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                    st.session_state.simulatieverhalen[ronde] = response.text
                    st.rerun()

                except Exception as e:
                    st.error("Er ging iets mis bij de simulatie.")
                    st.code(str(e))

    else:

        if ronde <= 3:
            mislukt_pad = Path(f"images/poging{ronde}_mislukt.png")
            if mislukt_pad.exists():
                st.image(str(mislukt_pad), use_container_width=True)

        st.markdown(st.session_state.simulatieverhalen[ronde])

        if ronde <= 3:

            st.error("Deze expeditie overleeft de zes maanden niet.")

            st.markdown("## Jullie opdracht")
            st.info(
                "Lees eerst goed wat er tijdens de expeditie is gebeurd. "
                "Pas daarna 2 persoonlijkheidsscores aan om de kans te verhogen "
                "dat de groep de volgende keer wél kan overleven."
            )

            st.markdown("### Stap 1 — Kies 2 aanpassingen")

            wijzigingen = []

            for i in range(2):

                st.markdown(f"**Aanpassing {i + 1}**")

                gekozen_naam = st.selectbox(
                    "Wie willen jullie aanpassen?",
                    list(st.session_state.huidige_profielen.keys()),
                    key=f"aanp_naam_{ronde}_{i}"
                )

                gekozen_trek = st.selectbox(
                    "Welke persoonlijkheidstrek willen jullie aanpassen?",
                    TREKKEN,
                    key=f"aanp_trek_{ronde}_{i}"
                )

                oude_score = st.session_state.huidige_profielen[gekozen_naam][gekozen_trek]

                st.caption(f"Huidige score: {oude_score}/10")

                minimum = max(1, oude_score - 3)
                maximum = min(10, oude_score + 3)

                nieuwe_score = st.slider(
                    "Nieuwe score",
                    min_value=minimum,
                    max_value=maximum,
                    value=oude_score,
                    key=f"aanp_nieuw_{ronde}_{i}",
                    help=UITLEG[gekozen_trek]
                )

                wijzigingen.append({
                    "naam": gekozen_naam,
                    "trek": gekozen_trek,
                    "oud": oude_score,
                    "nieuw": nieuwe_score
                })

            st.markdown("### Stap 2 — Leg jullie strategie uit")

            reden = st.text_area(
                "Waarom denken jullie dat deze veranderingen de kans op overleven verhogen?",
                placeholder=(
                    "Lees wat er misging en leg uit hoe jullie aanpassingen dat probleem volgens jullie kunnen verkleinen."
                ),
                key=f"reden_{ronde}"
            )

            st.info(
                "Jullie blijven op deze manier persoonlijkheden aanpassen en opnieuw testen, "
                "tot jullie een groep hebben gemaakt die het eiland kan overleven."
            )

            if st.button("Test de aangepaste expeditie", key=f"volgende_poging_{ronde}"):

                paren = [(w["naam"], w["trek"]) for w in wijzigingen]

                if len(set(paren)) != len(paren):
                    st.warning("Kies twee verschillende aanpassingen.")
                elif any(w["nieuw"] == w["oud"] for w in wijzigingen):
                    st.warning("Verander beide scores daadwerkelijk.")
                elif not reden.strip():
                    st.warning(
                        "Leg eerst uit waarom deze veranderingen volgens jullie de kans op overleven verhogen."
                    )
                else:
                    nieuwe_profielen = copy.deepcopy(st.session_state.huidige_profielen)

                    for wijziging in wijzigingen:
                        nieuwe_profielen[wijziging["naam"]][wijziging["trek"]] = wijziging["nieuw"]

                    st.session_state.aanpassingsgeschiedenis.append({
                        "wijzigingen": wijzigingen,
                        "reden": reden
                    })

                    st.session_state.huidige_profielen = nieuwe_profielen
                    st.session_state.simulatieronde += 1
                    st.rerun()

        else:

            gered_pad = Path("images/gered.png")
            if gered_pad.exists():
                st.image(str(gered_pad), use_container_width=True)

            st.success("De expeditie heeft zes maanden overleefd en wordt gered.")

            st.markdown("""
De combinatie van persoonlijkheden en rollen werkte uiteindelijk goed genoeg.

Jullie hebben dus stap voor stap een groep gebouwd die:
- kon samenwerken,
- onbekend terrein kon verkennen,
- en lang genoeg kon overleven tot de redding arriveerde.
""")

            st.header("Overzicht om in te dienen")

            verslag = maak_verslag()

            st.text_area(
                "Kopieer dit overzicht en dien het in bij de leerkracht",
                value=verslag,
                height=380
            )

            if st.button("Opnieuw beginnen"):
                reset_spel()
                st.rerun()
