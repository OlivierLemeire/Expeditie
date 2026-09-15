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
        "Extraversie gaat over de mate waarin iemand sociale contacten opzoekt "
        "en gemakkelijk contact legt. Een lage score betekent dat iemand eerder "
        "introvert is en minder behoefte heeft aan veel sociale interactie. "
        "Een hoge score betekent dat iemand gemakkelijk contact legt, graag praat "
        "en sociaal actief is. 1 = sterk introvert | 10 = sterk extravert",

    "Vriendelijkheid":
        "Vriendelijkheid gaat over de mate waarin iemand anderen helpt, vertrouwt "
        "en rekening houdt met anderen. Een lage score betekent dat iemand eerder "
        "afstandelijk, kritisch, wantrouwig of competitief is. Een hoge score betekent "
        "dat iemand behulpzaam, vriendelijk, vertrouwend en gericht op samenwerking is. "
        "1 = sterk afstandelijk | 10 = sterk vriendelijk",

    "Emotionele stabiliteit":
        "Emotionele stabiliteit gaat over hoe iemand reageert op stress, problemen "
        "en negatieve emoties. Een lage score betekent dat iemand sneller bezorgd, "
        "gespannen of emotioneel van slag raakt. Een hoge score betekent dat iemand "
        "meestal rustig blijft en goed met stress en tegenslagen omgaat. "
        "1 = sterk stressgevoelig/neurotisch | 10 = zeer emotioneel stabiel",

    "Zorgvuldigheid":
        "Zorgvuldigheid gaat over hoe georganiseerd, ordelijk en verantwoordelijk "
        "iemand is. Een lage score betekent dat iemand eerder chaotisch, impulsief "
        "of slordig werkt. Een hoge score betekent dat iemand plant, afspraken nakomt, "
        "taken afwerkt en georganiseerd te werk gaat. "
        "1 = sterk onzorgvuldig | 10 = zeer zorgvuldig",

    "Openheid voor ervaringen":
        "Openheid voor ervaringen gaat over de mate waarin iemand nieuwsgierig is "
        "en openstaat voor nieuwe ideeën en ervaringen. Een lage score betekent dat "
        "iemand liever vasthoudt aan bekende gewoontes en vertrouwde oplossingen. "
        "Een hoge score betekent dat iemand graag nieuwe dingen probeert, nieuwsgierig "
        "is en openstaat voor andere mogelijkheden. "
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
# HULPFUNCTIE
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


# ==================================================
# FASE 1 — INTRO
# ==================================================

if st.session_state.fase == "intro":

    st.title("🏝️ Expeditie Eiland")

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


# ==================================================
# FASE 2 — PERSOONLIJKHEDEN ANALYSEREN
# ==================================================

elif st.session_state.fase == "analyse":

    st.title("🧠 Analyseer de vijf jongeren")

    index = st.session_state.personage_index


    # --------------------------------------------------
    # ALLE PERSONAGES KLAAR
    # --------------------------------------------------

    if index >= len(personages):

        st.success("Jullie hebben alle vijf de persoonlijkheden geanalyseerd.")

        st.header("🏝️ Nu begint de echte test")

        st.markdown("""
Jullie hebben nu een persoonlijkheidsprofiel opgesteld voor elk lid van de groep.

Maar uiteindelijk draait alles om één vraag:

## Kunnen deze vijf jongeren samen zes maanden overleven?

De simulator laat zien hoe de groep omgaat met voedsel, onderdak,
stress, risico's, samenwerking en conflicten.

Wat er gebeurt, hangt af van de persoonlijkheidsprofielen die jullie hebben opgesteld.
""")

        if st.button("▶️ Start de eerste overlevingspoging"):

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
            f"Personage {index + 1} van {len(personages)}"
        )

        st.header(naam)

        afbeelding = Path(persoon["afbeelding"])

        if afbeelding.exists():
            st.image(str(afbeelding), width=350)

        st.markdown("### Wie is deze persoon?")
        st.write(persoon["beschrijving"])

        st.markdown("### 1. Schat de persoonlijkheid in")

        st.write(
            "Geef voor elke persoonlijkheidsdimensie een score van **1 tot 10**. "
            "Klik op het **?** als je niet meer precies weet wat een eigenschap betekent."
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


        # --------------------------------------------------
        # TWEE KEUZES VERANTWOORDEN
        # --------------------------------------------------

        st.markdown("### 2. Verantwoord twee van jullie keuzes")

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


        # --------------------------------------------------
        # FEEDBACK
        # --------------------------------------------------

        st.markdown("### 3. Controleer jullie analyse")

        if st.button(
            "🔎 Geef feedback",
            key=f"feedback_knop_{naam}"
        ):

            if len(gekozen_trekken) != 2:

                st.warning(
                    "Kies eerst precies twee persoonlijkheidsdimensies."
                )

            elif any(
                not motivaties[trek].strip()
                for trek in gekozen_trekken
            ):

                st.warning(
                    "Schrijf eerst bij beide gekozen eigenschappen een korte motivatie."
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
Je bent docent gedragswetenschappen voor leerlingen van ongeveer 17 jaar.

De leerlingen leren vijf persoonlijkheidsdimensies:

1. extraversie tegenover introversie
2. vriendelijkheid tegenover afstandelijkheid
3. emotionele stabiliteit tegenover neuroticisme
4. zorgvuldigheid tegenover onzorgvuldigheid
5. openheid voor ervaringen tegenover geslotenheid voor ervaringen

Een hoge score betekent een hoge score op de eerstgenoemde eigenschap.

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

REGELS:

- Er bestaat niet één exact correct getal.
- Beoordeel vooral laag, gemiddeld of hoog.
- Baseer je uitsluitend op de beschrijving.
- Geef feedback op alle vijf scores.
- Besteed extra aandacht aan de twee gemotiveerde eigenschappen.
- Gebruik uitsluitend de terminologie uit de opdracht.
- Houd het antwoord kort.

Structuur:

### Goed gezien
### Herbekijk dit
### Jullie argumentatie
### Advies
"""

                with st.spinner("Jullie analyse wordt nagekeken..."):

                    try:

                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )

                        st.session_state.feedback[naam] = response.text

                    except Exception as e:

                        st.error(
                            "Er ging iets mis bij het genereren van de feedback."
                        )

                        st.code(str(e))


        # --------------------------------------------------
        # FEEDBACK TONEN
        # --------------------------------------------------

        if naam in st.session_state.feedback:

            st.success("Feedback klaar!")

            st.markdown(
                st.session_state.feedback[naam]
            )

            st.info(
                "Jullie mogen de scores nog aanpassen als de feedback jullie overtuigt."
            )

            if st.button(
                "➡️ Ga verder",
                key=f"volgende_{naam}"
            ):

                st.session_state.resultaten[naam] = {
                    trek: st.session_state[f"{naam}_{trek}"]
                    for trek in TREKKEN
                }

                st.session_state.personage_index += 1

                st.rerun()


# ==================================================
# FASE 3 — OVERLEVINGSSIMULATIE
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = st.session_state.simulatieronde

    st.title("🏝️ De overlevingssimulatie")

    st.caption(
        f"Overlevingspoging {ronde} van 4"
    )

    # --------------------------------------------------
    # HUIDIGE PROFIELEN
    # --------------------------------------------------

    with st.expander("Bekijk de huidige persoonlijkheidsprofielen"):

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
    # SIMULATIE NOG NIET UITGEVOERD
    # --------------------------------------------------

    if ronde not in st.session_state.simulatieverhalen:

        if ronde == 1:

            st.markdown("""
De vijf jongeren zijn aangekomen op het eiland.

Hun persoonlijkheidsprofielen liggen vast.

### Zullen ze zes maanden kunnen overleven?
""")

        else:

            st.markdown(f"""
Jullie hebben het team aangepast.

Dit is **overlevingspoging {ronde}**.

### Heeft jullie nieuwe combinatie nu wel genoeg kans?
""")

        if st.button(
            "▶️ Laat de zes maanden beginnen",
            key=f"simuleer_{ronde}"
        ):

            profielen_tekst = profielen_naar_tekst(
                st.session_state.huidige_profielen
            )

            # Ronde 1-3 moeten mislukken.
            # Ronde 4 moet slagen.
            if ronde <= 3:
                uitkomst = "MISLUKT"
            else:
                uitkomst = "OVERLEEFT"

            eerdere_verhalen = ""

            for oude_ronde, verhaal in st.session_state.simulatieverhalen.items():

                eerdere_verhalen += f"""
EERDERE POGING {oude_ronde}:
{verhaal}

"""

            aanpassingen = ""

            if st.session_state.aanpassingsgeschiedenis:

                laatste = st.session_state.aanpassingsgeschiedenis[-1]

                aanpassingen += "\nLAATSTE AANPASSINGEN:\n"

                for wijziging in laatste["wijzigingen"]:

                    aanpassingen += (
                        f"- {wijziging['naam']}: "
                        f"{wijziging['trek']} van "
                        f"{wijziging['oud']} naar "
                        f"{wijziging['nieuw']}\n"
                    )

                aanpassingen += (
                    "\nWaarom de leerlingen dachten dat dit zou helpen:\n"
                    + laatste["reden"]
                )


            prompt = f"""
Je schrijft een fictief overlevingsverhaal voor een les gedragswetenschappen
voor leerlingen van ongeveer 17 jaar.

Vijf jongeren moeten zes maanden overleven op een onbewoond tropisch eiland.

Hun persoonlijkheidsprofielen zijn:

{profielen_tekst}

Dit is poging {ronde}.

De VASTSTAANDE UITKOMST van deze simulatie is:

{uitkomst}

Deze uitkomst mag je NIET veranderen.

Vertel nooit aan de leerlingen dat de uitkomst vooraf bepaald werd.

{aanpassingen}

{eerdere_verhalen}


BELANGRIJKE INHOUDELIJKE REGELS

- Baseer het verloop zoveel mogelijk op de actuele persoonlijkheidsprofielen.
- Persoonlijkheid bepaalt gedrag niet volledig. Formuleer probabilistisch.
- Laat zien dat eigenschappen zowel voordelen als nadelen kunnen hebben.
- Maak geen enkele Big Five-eigenschap simpelweg "goed" of "slecht".
- Problemen moeten ontstaan door een combinatie van persoonlijkheid,
  groepsdynamiek en de moeilijke omstandigheden op het eiland.
- Gebruik concrete situaties: water zoeken, voedsel verzamelen,
  onderdak, taakverdeling, risico's, stress, conflicten en samenwerking.
- Verzin geen nieuwe persoonlijkheidskenmerken die niet uit de scores volgen.
- Gebruik de termen:
  extraversie, vriendelijkheid, emotionele stabiliteit,
  zorgvuldigheid en openheid voor ervaringen.

ALS DIT POGING 2, 3 OF 4 IS:

- Laat duidelijk merken wat door de aanpassingen beter gaat.
- Respecteer dus de wijzigingen die de leerlingen gemaakt hebben.
- Gebruik niet gewoon opnieuw hetzelfde probleem als in de vorige ronde.


ALS DE UITKOMST "MISLUKT" IS:

- De groep haalt uiteindelijk de zes maanden niet.
- Geen van de vijf jongeren overleeft tot de redding.
- Beschrijf dit NIET grafisch.
- Focus op de opeenvolging van beslissingen, problemen,
  groepsdynamiek en omstandigheden.
- Leg duidelijk uit waarom de persoonlijkheidscombinatie
  in deze situatie onvoldoende bleek.


ALS DE UITKOMST "OVERLEEFT" IS:

- De groep slaagt erin zes maanden te overleven.
- Laat zien hoe hun verschillende persoonlijkheden elkaar aanvullen.
- Na zes maanden wordt de groep door een reddingsteam gevonden.
- Maak het einde positief, maar niet ongeloofwaardig.


SCHRIJF HET ANTWOORD IN DEZE STRUCTUUR:

## Poging {ronde}

### Wat gebeurt er?

Vertel een levendig maar beknopt verhaal van ongeveer 5 tot 7 korte alinea's.

### Waarom liep het mis?
OF, bij succes:
### Waarom lukte het deze keer?

Leg in 3 korte punten het verband met de persoonlijkheidsprofielen.

Houd het geschikt voor leerlingen van 17 jaar en vermijd grafische details.
"""

            with st.spinner(
                "Zes maanden op het eiland worden gesimuleerd..."
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
    # VERHAAL TONEN
    # --------------------------------------------------

    else:

        verhaal = st.session_state.simulatieverhalen[ronde]

        st.markdown(verhaal)


        # ==================================================
        # MISLUKT: PROFIELEN AANPASSEN
        # ==================================================

        if ronde <= 3:

            st.error(
                "❌ De groep heeft de zes maanden niet overleefd."
            )

            st.header("🔧 Bouw een betere groep")

            st.markdown("""
Jullie krijgen een nieuwe kans.

Je mag **2 of 3 persoonlijkheidsscores aanpassen**.

Een persoonlijkheid verandert natuurlijk niet zomaar in het echte leven.
Zie dit daarom als een experiment: jullie ontwerpen een **alternatieve versie**
van het team.

Per score mag je maximaal **3 punten omhoog of omlaag**.

Denk goed na: welke verandering zou het probleem uit de vorige poging kunnen oplossen?
""")


            aantal_wijzigingen = st.radio(
                "Hoeveel scores willen jullie aanpassen?",
                [2, 3],
                horizontal=True,
                key=f"aantal_{ronde}"
            )

            wijzigingen = []


            for i in range(aantal_wijzigingen):

                st.markdown(
                    f"### Aanpassing {i + 1}"
                )

                gekozen_naam = st.selectbox(
                    "Wie willen jullie aanpassen?",
                    list(st.session_state.huidige_profielen.keys()),
                    key=f"naam_{ronde}_{i}"
                )

                gekozen_trek = st.selectbox(
                    "Welke eigenschap?",
                    TREKKEN,
                    key=f"trek_{ronde}_{i}"
                )

                oude_score = (
                    st.session_state
                    .huidige_profielen[gekozen_naam][gekozen_trek]
                )

                st.write(
                    f"Huidige score: **{oude_score}/10**"
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
                    key=f"nieuw_{ronde}_{i}"
                )

                wijzigingen.append({
                    "naam": gekozen_naam,
                    "trek": gekozen_trek,
                    "oud": oude_score,
                    "nieuw": nieuwe_score
                })


            reden = st.text_area(
                "Waarom denken jullie dat deze aanpassingen de groep meer kans geven om te overleven?",
                placeholder=(
                    "Leg uit welk probleem uit de vorige poging "
                    "jullie hiermee proberen op te lossen..."
                ),
                key=f"reden_{ronde}"
            )


            if st.button(
                "✅ Test deze nieuwe groep",
                key=f"test_nieuw_{ronde}"
            ):

                paren = [
                    (w["naam"], w["trek"])
                    for w in wijzigingen
                ]

                if len(set(paren)) != len(paren):

                    st.warning(
                        "Jullie hebben dezelfde persoon en eigenschap "
                        "meer dan één keer gekozen."
                    )

                elif any(
                    w["nieuw"] == w["oud"]
                    for w in wijzigingen
                ):

                    st.warning(
                        "Bij elke gekozen eigenschap moet de score werkelijk veranderen."
                    )

                elif not reden.strip():

                    st.warning(
                        "Leg eerst kort uit waarom jullie denken "
                        "dat deze veranderingen zullen helpen."
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
                        "na_ronde": ronde,
                        "wijzigingen": wijzigingen,
                        "reden": reden
                    })

                    st.session_state.huidige_profielen = nieuwe_profielen

                    st.session_state.simulatieronde += 1

                    st.rerun()


        # ==================================================
        # RONDE 4: SUCCES
        # ==================================================

        else:

            st.success(
                "🎉 Ze hebben het gehaald!"
            )

            st.balloons()

            st.markdown("""
## Na zes maanden

Aan de horizon verschijnt een schip.

De vijf jongeren worden gevonden en veilig van het eiland gehaald.

Jullie hebben uiteindelijk een combinatie van persoonlijkheden ontworpen
die in deze omstandigheden voldoende goed kon samenwerken en zich aanpassen.
""")

            st.header("🧠 Tot slot")

            st.markdown("""
Denk nog even na:

- Welke veranderingen hebben volgens jullie het grootste verschil gemaakt?
- Was één persoonlijkheidseigenschap altijd goed of slecht?
- Waarom kan een groep baat hebben bij verschillende persoonlijkheden?
- Bestaat er volgens jullie eigenlijk één **ideale persoonlijkheid** om te overleven?
""")

            if st.button("🔄 Opnieuw spelen"):

                st.session_state.fase = "intro"
                st.session_state.personage_index = 0
                st.session_state.resultaten = {}
                st.session_state.feedback = {}
                st.session_state.huidige_profielen = {}
                st.session_state.simulatieronde = 1
                st.session_state.simulatieverhalen = {}
                st.session_state.aanpassingsgeschiedenis = []

                st.rerun()
