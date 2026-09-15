import streamlit as st
from google import genai
from pathlib import Path


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
        "De mate waarin iemand nieuwe sociale contacten legt. "
        "1 = eerder introvert | 10 = sterk extravert",

    "Vriendelijkheid":
        "De mate waarin iemand bereid is anderen te helpen en te vertrouwen. "
        "1 = eerder afstandelijk | 10 = sterk vriendelijk",

    "Emotionele stabiliteit":
        "De mate waarin iemand goed omgaat met stress en problemen. "
        "1 = eerder neurotisch/stressgevoelig | 10 = emotioneel stabiel",

    "Zorgvuldigheid":
        "De mate waarin iemand georganiseerd en ordelijk is. "
        "1 = eerder onzorgvuldig | 10 = sterk zorgvuldig",

    "Openheid voor ervaringen":
        "De mate waarin iemand openstaat voor nieuwe ervaringen. "
        "1 = eerder gesloten | 10 = sterk open voor nieuwe ervaringen"
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
# SESSION STATE
# --------------------------------------------------

if "fase" not in st.session_state:
    st.session_state.fase = "intro"

if "personage_index" not in st.session_state:
    st.session_state.personage_index = 0

if "resultaten" not in st.session_state:
    st.session_state.resultaten = {}

if "feedback" not in st.session_state:
    st.session_state.feedback = {}


# --------------------------------------------------
# TITEL
# --------------------------------------------------

st.title("🏝️ Expeditie Eiland")


# --------------------------------------------------
# INTRO-PAGINA
# --------------------------------------------------

if st.session_state.fase == "intro":

    eiland_pad = Path("images/eiland.png")

    if eiland_pad.exists():
        st.image(str(eiland_pad), use_container_width=True)

    st.markdown("""
Een groep jongeren is met een klein vliegtuig neergestort op een afgelegen,
onbewoond eiland.

Er is geen gsm-bereik en hulp is voorlopig niet onderweg.

Ze zullen **zes maanden lang zelf moeten zien te overleven**.

Ze moeten voedsel vinden, drinkbaar water zoeken, een schuilplaats bouwen,
taken verdelen, samenwerken en omgaan met stress en conflicten.

## Welke persoonlijkheden zouden hier het best kunnen overleven?

Ontdek het door de vijf jongeren te leren kennen en hun persoonlijkheid te analyseren.
""")

    if st.button("➡️ Ontdek de vijf jongeren"):
        st.session_state.fase = "analyse"
        st.rerun()

# --------------------------------------------------
# ANALYSEFASE
# --------------------------------------------------

elif st.session_state.fase == "analyse":

    with st.expander("🧠 Herhaal de vijf persoonlijkheidsdimensies"):
        for trek in TREKKEN:
            st.markdown(f"**{trek}**")
            st.write(UITLEG[trek])

    index = st.session_state.personage_index

    # EINDSCHERM
    if index >= len(personages):

        st.success("🎉 Jullie hebben alle vijf de personages geanalyseerd!")

        st.header("Jullie expeditieteam")

        for naam, profiel in st.session_state.resultaten.items():

            st.subheader(naam)

            st.write(
                f"**Extraversie:** {profiel['Extraversie']}/10  \n"
                f"**Vriendelijkheid:** {profiel['Vriendelijkheid']}/10  \n"
                f"**Emotionele stabiliteit:** {profiel['Emotionele stabiliteit']}/10  \n"
                f"**Zorgvuldigheid:** {profiel['Zorgvuldigheid']}/10  \n"
                f"**Openheid voor ervaringen:** {profiel['Openheid voor ervaringen']}/10"
            )

        st.info(
            "De persoonlijkheidsprofielen zijn klaar. "
            "In de volgende fase kunnen jullie onderzoeken hoe deze vijf jongeren "
            "het samen op het eiland zouden doen."
        )

        if st.button("🔄 Opnieuw beginnen"):
            st.session_state.fase = "intro"
            st.session_state.personage_index = 0
            st.session_state.resultaten = {}
            st.session_state.feedback = {}
            st.rerun()

    # PERSONAGE
    else:

        persoon = personages[index]
        naam = persoon["naam"]

        st.caption(f"Personage {index + 1} van {len(personages)}")
        st.header(naam)

        afbeelding = Path(persoon["afbeelding"])
        if afbeelding.exists():
            st.image(str(afbeelding), width=350)

        st.markdown("### Wie is deze persoon?")
        st.write(persoon["beschrijving"])

        st.markdown("### 1. Schat de persoonlijkheid in")
        st.write("Geef voor elke persoonlijkheidsdimensie een score van **1 tot 10**.")

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

        st.markdown("### 2. Verantwoord twee van jullie keuzes")
        st.write(
            "Kies **twee persoonlijkheidsdimensies** waarvan jullie de score willen uitleggen."
        )

        gekozen_trekken = st.multiselect(
            "Welke twee eigenschappen willen jullie verantwoorden?",
            TREKKEN,
            max_selections=2,
            key=f"{naam}_gekozen_trekken"
        )

        motivaties = {}

        for trek in gekozen_trekken:
            motivaties[trek] = st.text_area(
                f"Waarom gaven jullie {naam} deze score voor {trek}?",
                placeholder="Verwijs naar concrete informatie uit de beschrijving...",
                key=f"{naam}_motivatie_{trek}"
            )

        st.markdown("### 3. Controleer jullie analyse")

        if st.button("🔎 Geef feedback", key=f"feedback_knop_{naam}"):

            if len(gekozen_trekken) != 2:
                st.warning(
                    "Kies eerst precies twee persoonlijkheidsdimensies die jullie willen verantwoorden."
                )

            elif any(not motivaties[trek].strip() for trek in gekozen_trekken):
                st.warning(
                    "Schrijf eerst bij beide gekozen eigenschappen een korte motivatie."
                )

            else:

                motivatie_tekst = ""

                for trek in gekozen_trekken:
                    motivatie_tekst += f"""
{trek}
Score: {scores[trek]}/10
Motivatie van de leerlingen:
{motivaties[trek]}

"""

                prompt = f"""
Je bent docent gedragswetenschappen voor leerlingen van ongeveer 17 jaar.

De leerlingen leren deze vijf persoonlijkheidsdimensies:

1. extraversie tegenover introversie
2. vriendelijkheid tegenover afstandelijkheid
3. emotionele stabiliteit tegenover neuroticisme
4. zorgvuldigheid tegenover onzorgvuldigheid
5. openheid voor ervaringen tegenover geslotenheid voor ervaringen

Een hoge score betekent steeds een hoge score op de eerstgenoemde eigenschap.

De leerling analyseert dit fictieve personage:

NAAM:
{naam}

BESCHRIJVING:
{persoon["beschrijving"]}

DE SCORES VAN DE LEERLINGEN:

Extraversie: {scores["Extraversie"]}/10
Vriendelijkheid: {scores["Vriendelijkheid"]}/10
Emotionele stabiliteit: {scores["Emotionele stabiliteit"]}/10
Zorgvuldigheid: {scores["Zorgvuldigheid"]}/10
Openheid voor ervaringen: {scores["Openheid voor ervaringen"]}/10

Voor twee eigenschappen hebben de leerlingen hun keuze verantwoord:

{motivatie_tekst}

Geef korte, didactische feedback.

BELANGRIJKE REGELS:

- Doe niet alsof er één exact juist getal bestaat.
- Beoordeel vooral of een lage, gemiddelde of hoge score past.
- Een verschil zoals 7 tegenover 8 is niet belangrijk.
- Baseer je uitsluitend op de beschrijving.
- Verzin geen eigenschappen die niet in de tekst staan.
- Als er weinig informatie is over een trek, zeg dat expliciet.
- Geef feedback op ALLE vijf scores.
- Besteed extra aandacht aan de twee eigenschappen die de leerlingen motiveerden.
- Zeg bij die twee ook of hun redenering klopt.
- Gebruik uitsluitend de termen uit deze opdracht.
- Gebruik dus geen woorden als consciëntieusheid, altruïsme of agreeableness.
- Wees kritisch maar behulpzaam.
- Houd het antwoord kort.

Gebruik deze structuur:

### Goed gezien
Noem kort welke inschattingen goed passen.

### Herbekijk dit
Noem alleen scores die moeilijk te verdedigen zijn en leg kort uit waarom.

### Jullie argumentatie
Geef specifiek feedback op de twee geschreven motivaties.

### Advies
Geef maximaal twee concrete veranderingen die de leerlingen eventueel kunnen maken.
"""

                with st.spinner("Jullie analyse wordt nagekeken..."):

                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )

                        st.session_state.feedback[naam] = response.text

                    except Exception as e:
                        st.error("Er ging iets mis bij het genereren van de feedback.")
                        st.code(str(e))

        if naam in st.session_state.feedback:

            st.success("Feedback klaar!")
            st.markdown(st.session_state.feedback[naam])

            st.info(
                "Bekijk jullie scores opnieuw. "
                "Jullie mogen ze aanpassen als de feedback jullie overtuigt."
            )

            st.markdown("### 4. Klaar? Ga verder")

            if st.button(f"➡️ Ga verder naar het volgende personage", key=f"volgende_{naam}"):

                st.session_state.resultaten[naam] = {
                    trek: st.session_state[f"{naam}_{trek}"]
                    for trek in TREKKEN
                }

                st.session_state.personage_index += 1
                st.rerun()
