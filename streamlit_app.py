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


def reset_spel():
    st.session_state.fase = "intro"
    st.session_state.groepsleden = ""
    st.session_state.analyse_intro_getoond = False
    st.session_state.personage_index = 0
    st.session_state.resultaten = {}
    st.session_state.feedback = {}
    st.session_state.simulatieronde = 1
    st.session_state.huidige_profielen = {}
    st.session_state.simulatieverhalen = {}
    st.session_state.aanpassingsgeschiedenis = []


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
**2.** ontdek of deze groep samen kan overleven  
**3.** als het misloopt, pas de persoonlijkheden aan om hun kans op overleven te verhogen  
**4.** probeer een combinatie te vinden die het eiland wél overleeft
""")

    st.info(
        "Op het einde maakt de app automatisch een overzicht van jullie antwoorden "
        "en aanpassingen. Dat overzicht moeten jullie indienen bij de leerkracht."
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
Voor jullie kunnen testen of deze groep het eiland overleeft,
moeten jullie eerst hun **persoonlijkheid inschatten**.

Gebruik daarvoor de **Big Five-persoonlijkheidstrekken**
uit het handboek, **pagina 157–158**.

Jullie analyseren **5 personen**.

Bij elke persoon:

- geven jullie voor alle 5 trekken een score;
- leggen jullie 2 scores kort uit;
- krijgen jullie feedback.

Zo oefenen jullie de Big Five in.

Daarna testen we:

### Kunnen deze vijf persoonlijkheden samen zes maanden overleven?
""")

        if st.button("Ga naar persoon 1"):

            st.session_state.analyse_intro_getoond = True

            st.rerun()


    else:

        index = st.session_state.personage_index

        st.title("Leer de groep kennen")

        st.progress(index / len(personages))


        # --------------------------------------------------
        # ALLE PERSONAGES KLAAR
        # --------------------------------------------------

        if index >= len(personages):

            st.success("Alle vijf persoonlijkheidsprofielen zijn klaar.")

            st.markdown("""
Nu begint de overlevingsproef.

### Kunnen deze vijf jongeren met deze persoonlijkheden zes maanden overleven?
""")

            if st.button("Test de groep"):

                st.session_state.huidige_profielen = copy.deepcopy(
                    st.session_state.resultaten
                )

                st.session_state.simulatieronde = 1
                st.session_state.simulatieverhalen = {}
                st.session_state.aanpassingsgeschiedenis = []
                st.session_state.fase = "simulatie"

                st.rerun()


        # --------------------------------------------------
        # ÉÉN PERSONAGE
        # --------------------------------------------------

        else:

            persoon = personages[index]
            naam = persoon["naam"]

            st.caption(
                f"Persoon {index + 1} van {len(personages)}"
            )

            st.header(naam)

            afbeelding = Path(persoon["afbeelding"])

            if afbeelding.exists():
                st.image(str(afbeelding), width=340)

            st.write(
                persoon["beschrijving"]
            )

            st.markdown("### Schat de persoonlijkheid in")

            st.info(
                "Zoek in de beschrijving naar concrete aanwijzingen over de persoonlijkheid. "
                "Welke gedragingen wijzen op hoge of lage extraversie, vriendelijkheid, "
                "emotionele stabiliteit, zorgvuldigheid en openheid voor ervaringen? "
                "Gebruik die aanwijzingen om de scores in te stellen."
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

            if st.button(
                "Vraag feedback",
                key=f"feedback_{naam}"
            ):

                if len(gekozen_trekken) != 2:

                    st.warning(
                        "Kies precies 2 eigenschappen."
                    )

                elif any(
                    not motivaties[trek].strip()
                    for trek in gekozen_trekken
                ):

                    st.warning(
                        "Schrijf bij beide eigenschappen een korte uitleg."
                    )

                else:

                    motivatie_tekst = ""

                    for trek in gekozen_trekken:

                        motivatie_tekst += f"""
{trek}
Score: {scores[trek]}/10
Motivatie:
{motivaties[trek]}

"""

                    prompt = f"""
Je bent docent gedragswetenschappen voor leerlingen van 17 jaar.

BELANGRIJK:
Schrijf je volledige antwoord uitsluitend in correct Nederlands.
Gebruik geen Engelse titels, woorden of zinnen.
Alle feedback moet in het Nederlands zijn.

De leerlingen analyseren een fictief personage aan de hand van:

- extraversie tegenover introversie
- vriendelijkheid tegenover afstandelijkheid
- emotionele stabiliteit tegenover neuroticisme
- zorgvuldigheid tegenover onzorgvuldigheid
- openheid voor ervaringen tegenover geslotenheid voor ervaringen

PERSONAGE:
{naam}

BESCHRIJVING:
{persoon["beschrijving"]}

SCORES:
Extraversie: {scores["Extraversie"]}/10
Vriendelijkheid: {scores["Vriendelijkheid"]}/10
Emotionele stabiliteit: {scores["Emotionele stabiliteit"]}/10
Zorgvuldigheid: {scores["Zorgvuldigheid"]}/10
Openheid voor ervaringen: {scores["Openheid voor ervaringen"]}/10

TWEE GEMOTIVEERDE KEUZES:
{motivatie_tekst}

Geef korte didactische feedback.

Regels:

- Er bestaat niet één exact juist cijfer.
- Beoordeel vooral laag, gemiddeld of hoog.
- Baseer je uitsluitend op de beschrijving.
- Geef feedback op alle vijf scores.
- Besteed extra aandacht aan de twee toegelichte keuzes.
- Houd het kort en duidelijk.
- SCHRIJF ALLES IN HET NEDERLANDS.

Gebruik deze structuur:

### Goed gezien
### Herbekijk dit
### Jullie uitleg
### Advies
"""

                    with st.spinner("Feedback wordt gemaakt..."):

                        try:

                            response = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=prompt
                            )

                            st.session_state.feedback[naam] = response.text

                        except Exception as e:

                            st.error("Er ging iets mis.")
                            st.code(str(e))


            if naam in st.session_state.feedback:

                st.markdown(
                    st.session_state.feedback[naam]
                )

                if st.button(
                    "Bewaar en ga verder",
                    key=f"volgende_{naam}"
                ):

                    st.session_state.resultaten[naam] = {
                        trek: st.session_state[f"{naam}_{trek}"]
                        for trek in TREKKEN
                    }

                    st.session_state.personage_index += 1

                    st.rerun()


# ==================================================
# OVERLEVINGSSIMULATIE
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = st.session_state.simulatieronde

    st.title("De overlevingsproef")

    if ronde == 1:
        st.caption("De groep arriveert op het eiland.")
    else:
        st.caption("De aangepaste groep probeert het opnieuw.")

    with st.expander("Bekijk de huidige persoonlijkheden"):

        for naam, profiel in st.session_state.huidige_profielen.items():

            st.markdown(f"**{naam}**")

            st.write(
                f"Extraversie {profiel['Extraversie']} | "
                f"Vriendelijkheid {profiel['Vriendelijkheid']} | "
                f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']} | "
                f"Zorgvuldigheid {profiel['Zorgvuldigheid']} | "
                f"Openheid {profiel['Openheid voor ervaringen']}"
            )


    # --------------------------------------------------
    # SIMULEREN
    # --------------------------------------------------

    if ronde not in st.session_state.simulatieverhalen:

        if ronde == 1:

            st.markdown(
                "Zullen ze de zes maanden halen?"
            )

        else:

            st.markdown(
                "Hebben jullie veranderingen hun kans op overleven verhoogd?"
            )

        if st.button(
            "Start de overlevingsproef",
            key=f"start_test_{ronde}"
        ):

            profielen_tekst = profielen_naar_tekst(
                st.session_state.huidige_profielen
            )

            if ronde <= 3:
                uitkomst = "MISLUKT"
            else:
                uitkomst = "SLAAGT"

            laatste_aanpassing = ""

            if st.session_state.aanpassingsgeschiedenis:

                laatste = st.session_state.aanpassingsgeschiedenis[-1]

                laatste_aanpassing += "Laatste aanpassingen:\n"

                for wijziging in laatste["wijzigingen"]:

                    laatste_aanpassing += (
                        f"- {wijziging['naam']}: "
                        f"{wijziging['trek']} van "
                        f"{wijziging['oud']} naar "
                        f"{wijziging['nieuw']}\n"
                    )

                laatste_aanpassing += (
                    f"\nReden van de leerlingen:\n"
                    f"{laatste['reden']}"
                )

            prompt = f"""
Je bent de verteller van een kort survivalspel voor leerlingen van 17 jaar.

BELANGRIJK:
Schrijf je volledige antwoord uitsluitend in correct Nederlands.
Gebruik geen Engelse titels, woorden of zinnen.
Ook alle tussenkopjes moeten in het Nederlands staan.
SCHRIJF ALLES IN HET NEDERLANDS.

Vijf jongeren moeten zes maanden overleven op een onbewoond eiland.

Hun persoonlijkheidsprofielen:

{profielen_tekst}

De verplichte uitkomst is:
{uitkomst}

{laatste_aanpassing}

REGELS:

- Bij MISLUKT haalt de groep de zes maanden niet en sterft voor de redding.
- Beschrijf overlijden niet grafisch.
- Bij SLAAGT overleeft de groep en wordt ze na zes maanden gered.
- Baseer gebeurtenissen duidelijk op de persoonlijkheidsprofielen.
- Persoonlijkheid bepaalt gedrag niet volledig.
- Persoonlijkheidstrekken kunnen zowel voordelen als nadelen hebben.
- Bij latere pogingen moet duidelijk zijn wat dankzij de aanpassingen beter gaat.
- Gebruik concrete problemen zoals water, voedsel, planning, stress,
  samenwerking, risico's en conflicten.
- Houd het kort.
- Gebruik uitsluitend Nederlands.

Gebruik exact:

### Maand 1-2
Maximaal 2 korte zinnen.

### Maand 3-4
Maximaal 2 korte zinnen.

### Maand 5-6
Maximaal 2 korte zinnen.

### Uitkomst
Maximaal 2 korte zinnen.

### Waarom?
- één kort punt
- één kort punt
"""

            with st.spinner(
                "De maanden op het eiland verstrijken..."
            ):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                    st.session_state.simulatieverhalen[ronde] = response.text

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Er ging iets mis bij de simulatie."
                    )

                    st.code(str(e))


    # --------------------------------------------------
    # RESULTAAT
    # --------------------------------------------------

    else:

        if ronde <= 3:

            mislukt_pad = Path(
                f"images/poging{ronde}_mislukt.png"
            )

            if mislukt_pad.exists():

                st.image(
                    str(mislukt_pad),
                    use_container_width=True
                )

        st.markdown(
            st.session_state.simulatieverhalen[ronde]
        )


        # --------------------------------------------------
        # MISLUKT
        # --------------------------------------------------

        if ronde <= 3:

            st.error(
                "De groep haalt de zes maanden niet."
            )

            st.markdown(
                "## Jullie beurt"
            )

            st.info(
                "Lees eerst goed wat er tijdens deze overlevingspoging is misgegaan. "
                "Pas daarna 2 persoonlijkheidsscores aan met als doel de kans te verhogen "
                "dat de groep de volgende keer wél zes maanden kan overleven."
            )

            st.markdown(
                "### Stap 1 — Kies wat jullie willen veranderen"
            )

            st.write(
                "Pas **2 persoonlijkheidsscores** aan. "
                "Per score mag je maximaal 3 punten omhoog of omlaag."
            )

            wijzigingen = []

            for i in range(2):

                st.markdown(
                    f"**Aanpassing {i + 1}**"
                )

                gekozen_naam = st.selectbox(
                    "Wie willen jullie aanpassen?",
                    list(
                        st.session_state.huidige_profielen.keys()
                    ),
                    key=f"aanp_naam_{ronde}_{i}"
                )

                gekozen_trek = st.selectbox(
                    "Welke persoonlijkheidstrek willen jullie aanpassen?",
                    TREKKEN,
                    key=f"aanp_trek_{ronde}_{i}"
                )

                oude_score = (
                    st.session_state
                    .huidige_profielen[gekozen_naam][gekozen_trek]
                )

                st.caption(
                    f"Huidige score: {oude_score}/10"
                )

                minimum = max(
                    1,
                    oude_score - 3
                )

                maximum = min(
                    10,
                    oude_score + 3
                )

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

            st.markdown(
                "### Stap 2 — Leg jullie strategie uit"
            )

            reden = st.text_area(
                "Waarom denken jullie dat deze veranderingen de kans op overleven verhogen?",
                placeholder=(
                    "Lees terug wat er misging. Leg uit hoe jullie veranderingen "
                    "dat probleem volgens jullie kunnen verkleinen."
                ),
                key=f"reden_{ronde}"
            )

            if st.button(
                "Test de aangepaste groep",
                key=f"volgende_poging_{ronde}"
            ):

                paren = [
                    (w["naam"], w["trek"])
                    for w in wijzigingen
                ]

                if len(set(paren)) != len(paren):

                    st.warning(
                        "Kies twee verschillende aanpassingen."
                    )

                elif any(
                    w["nieuw"] == w["oud"]
                    for w in wijzigingen
                ):

                    st.warning(
                        "Verander beide scores daadwerkelijk."
                    )

                elif not reden.strip():

                    st.warning(
                        "Leg eerst uit waarom deze veranderingen volgens jullie "
                        "de kans op overleven verhogen."
                    )

                else:

                    nieuwe_profielen = copy.deepcopy(
                        st.session_state.huidige_profielen
                    )

                    for wijziging in wijzigingen:

                        nieuwe_profielen[
                            wijziging["naam"]
                        ][
                            wijziging["trek"]
                        ] = wijziging["nieuw"]

                    st.session_state.aanpassingsgeschiedenis.append({
                        "wijzigingen": wijzigingen,
                        "reden": reden
                    })

                    st.session_state.huidige_profielen = nieuwe_profielen

                    st.session_state.simulatieronde += 1

                    st.rerun()


        # --------------------------------------------------
        # GERED
        # --------------------------------------------------

        else:

            st.success(
                "De groep heeft zes maanden overleefd en wordt gered."
            )

            st.header("Overzicht van jullie opdracht")

            st.markdown(
                f"**Groepsleden:** {st.session_state.groepsleden}"
            )

            st.write(
                "Jullie hebben eerst de persoonlijkheid van Noor, Elias, Aya, Mats en Lina "
                "ingeschat aan de hand van de vijf Big Five-persoonlijkheidstrekken."
            )

            st.write(
                "Daarna hebben jullie getest of deze combinatie van persoonlijkheden "
                "zes maanden kon overleven op een onbewoond eiland."
            )

            st.markdown("### Jullie aanpassingen")

            for nummer, ronde_data in enumerate(
                st.session_state.aanpassingsgeschiedenis,
                start=1
            ):

                st.markdown(
                    f"**Na mislukte overlevingsproef {nummer}:**"
                )

                for wijziging in ronde_data["wijzigingen"]:

                    st.write(
                        f"- {wijziging['naam']}: "
                        f"{wijziging['trek']} "
                        f"van {wijziging['oud']}/10 "
                        f"naar {wijziging['nieuw']}/10"
                    )

                st.write(
                    f"**Waarom jullie dachten dat dit de kans op overleven zou verhogen:** "
                    f"{ronde_data['reden']}"
                )

            st.markdown("### Eindresultaat")

            st.write(
                "Na de aanpassingen slaagde de groep erin zes maanden te overleven "
                "en werd ze uiteindelijk gered."
            )

            st.info(
                "Dit is het overzicht dat jullie moeten indienen bij de leerkracht."
            )

            if st.button("Opnieuw beginnen"):

                reset_spel()

                st.rerun()
