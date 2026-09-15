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
    st.session_state.personage_index = 0
    st.session_state.resultaten = {}
    st.session_state.feedback = {}
    st.session_state.simulatieronde = 1
    st.session_state.huidige_profielen = {}
    st.session_state.simulatieverhalen = {}
    st.session_state.aanpassingsgeschiedenis = []


# ==================================================
# FASE 1 — INTRO
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
**2.** test of deze groep kan overleven  
**3.** pas na elke mislukking enkele scores aan  
**4.** probeer uiteindelijk een groep te bouwen die de zes maanden haalt
""")

    st.info("Doel: bouw stap voor stap een team dat lang genoeg overleeft om gered te worden.")

    if st.button("Start de expeditie"):
        st.session_state.fase = "analyse"
        st.rerun()


# ==================================================
# FASE 2 — PERSOONLIJKHEDEN ANALYSEREN
# ==================================================

elif st.session_state.fase == "analyse":

    index = st.session_state.personage_index

    st.title("Fase 1 — Ken de groep")
    st.progress(index / len(personages))

    if index >= len(personages):

        st.success("Alle vijf persoonlijkheidsprofielen zijn klaar.")

        st.markdown("""
Nu gaan we zien of deze groep het echt redt op het eiland.

Er zijn **maximaal 4 pogingen**.

Na elke mislukking mogen jullie **2 scores aanpassen** en opnieuw testen.
""")

        for naam, profiel in st.session_state.resultaten.items():
            st.markdown(f"**{naam}**")
            st.write(
                f"Extraversie {profiel['Extraversie']} | "
                f"Vriendelijkheid {profiel['Vriendelijkheid']} | "
                f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']} | "
                f"Zorgvuldigheid {profiel['Zorgvuldigheid']} | "
                f"Openheid {profiel['Openheid voor ervaringen']}"
            )

        if st.button("Start poging 1"):
            st.session_state.huidige_profielen = copy.deepcopy(st.session_state.resultaten)
            st.session_state.simulatieronde = 1
            st.session_state.simulatieverhalen = {}
            st.session_state.aanpassingsgeschiedenis = []
            st.session_state.fase = "simulatie"
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

        st.markdown("### Geef scores")

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
                placeholder="Verwijs naar de beschrijving...",
                key=f"{naam}_motivatie_{trek}"
            )

        if st.button("Vraag feedback", key=f"feedback_{naam}"):

            if len(gekozen_trekken) != 2:
                st.warning("Kies precies 2 eigenschappen.")
            elif any(not motivaties[trek].strip() for trek in gekozen_trekken):
                st.warning("Schrijf bij beide gekozen eigenschappen een korte uitleg.")
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

De leerlingen analyseren een fictief personage op 5 dimensies:
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
- Er is niet 1 exact juist getal.
- Beoordeel vooral laag / gemiddeld / hoog.
- Baseer je alleen op de beschrijving.
- Geef feedback op alle 5 scores.
- Besteed extra aandacht aan de 2 toegelichte keuzes.
- Houd het kort en duidelijk.

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
            st.markdown(st.session_state.feedback[naam])

            if st.button("Bewaar en ga verder", key=f"volgende_{naam}"):
                st.session_state.resultaten[naam] = {
                    trek: st.session_state[f"{naam}_{trek}"]
                    for trek in TREKKEN
                }
                st.session_state.personage_index += 1
                st.rerun()


# ==================================================
# FASE 3 — SURVIVALGAME
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = st.session_state.simulatieronde

    st.title("Fase 2 — Overleef het eiland")
    st.progress(ronde / 4)
    st.caption(f"Poging {ronde} van 4")

    with st.expander("Huidige groep bekijken"):
        for naam, profiel in st.session_state.huidige_profielen.items():
            st.markdown(f"**{naam}**")
            st.write(
                f"Extraversie {profiel['Extraversie']} | "
                f"Vriendelijkheid {profiel['Vriendelijkheid']} | "
                f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']} | "
                f"Zorgvuldigheid {profiel['Zorgvuldigheid']} | "
                f"Openheid {profiel['Openheid voor ervaringen']}"
            )

    # ----------------------------------------------
    # NOG NIET GESIMULEERD
    # ----------------------------------------------

    if ronde not in st.session_state.simulatieverhalen:

        if ronde == 1:
            st.markdown("Test nu of jullie eerste groep de zes maanden haalt.")
        else:
            st.markdown("Jullie hebben het team aangepast. Test nu deze nieuwe versie.")

        if st.button("Test deze groep", key=f"start_test_{ronde}"):

            profielen_tekst = profielen_naar_tekst(st.session_state.huidige_profielen)

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
                        f"- {wijziging['naam']}: {wijziging['trek']} van "
                        f"{wijziging['oud']} naar {wijziging['nieuw']}\n"
                    )
                laatste_aanpassing += f"\nWaarom de leerlingen dit deden:\n{laatste['reden']}"

            prompt = f"""
Je bent de verteller van een survivalspel voor leerlingen van 17 jaar.

Vijf jongeren moeten 6 maanden overleven op een onbewoond eiland.

Hun persoonlijkheidsprofielen zijn:
{profielen_tekst}

Dit is poging {ronde}.
De verplichte uitkomst is: {uitkomst}

{laatste_aanpassing}

BELANGRIJKE REGELS:
- Als de uitkomst MISLUKT is, haalt de groep de 6 maanden niet en sterft voor de redding.
- Beschrijf dat niet grafisch.
- Als de uitkomst SLAAGT is, overleeft de groep 6 maanden en wordt gered.
- Baseer gebeurtenissen op de persoonlijkheidsprofielen.
- Toon dat eigenschappen voordelen én nadelen hebben.
- Houd het kort, levendig en licht speels.
- Bij latere pogingen moet duidelijk zijn wat door de aanpassingen beter ging.
- Gebruik concrete dingen: water, voedsel, schuilplaats, planning, stress, ruzie, samenwerking.

Schrijf in het Nederlands.

Gebruik exact deze structuur:

### Maand 1-2
maximaal 2 korte zinnen

### Maand 3-4
maximaal 2 korte zinnen

### Maand 5-6
maximaal 2 korte zinnen

### Uitkomst
1 korte alinea

### Waarom?
- punt 1
- punt 2
"""

            with st.spinner("De simulatie loopt..."):
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

    # ----------------------------------------------
    # RESULTAAT TONEN
    # ----------------------------------------------

    else:

        if ronde <= 3:
            mislukt_pad = Path(f"images/poging{ronde}_mislukt.png")
            if mislukt_pad.exists():
                st.image(str(mislukt_pad), use_container_width=True)

        st.markdown(st.session_state.simulatieverhalen[ronde])

        # ------------------------------------------
        # MISLUKT -> AANPASSEN
        # ------------------------------------------

        if ronde <= 3:

            st.error("Deze groep haalt de zes maanden niet.")

            st.markdown("### Pas nu 2 scores aan")
            st.write("Per aanpassing mag je maximaal 3 punten omhoog of omlaag gaan.")

            wijzigingen = []

            for i in range(2):

                st.markdown(f"**Aanpassing {i + 1}**")

                gekozen_naam = st.selectbox(
                    "Wie?",
                    list(st.session_state.huidige_profielen.keys()),
                    key=f"aanp_naam_{ronde}_{i}"
                )

                gekozen_trek = st.selectbox(
                    "Welke eigenschap?",
                    TREKKEN,
                    key=f"aanp_trek_{ronde}_{i}"
                )

                oude_score = st.session_state.huidige_profielen[gekozen_naam][gekozen_trek]

                minimum = max(1, oude_score - 3)
                maximum = min(10, oude_score + 3)

                nieuwe_score = st.slider(
                    "Nieuwe score",
                    min_value=minimum,
                    max_value=maximum,
                    value=oude_score,
                    key=f"aanp_nieuw_{ronde}_{i}"
                )

                wijzigingen.append({
                    "naam": gekozen_naam,
                    "trek": gekozen_trek,
                    "oud": oude_score,
                    "nieuw": nieuwe_score
                })

            reden = st.text_area(
                "Waarom denken jullie dat deze veranderingen zullen helpen?",
                placeholder="Bijvoorbeeld: meer zorgvuldigheid kan helpen om voedsel en water beter te plannen.",
                key=f"reden_{ronde}"
            )

            if st.button("Bewaar veranderingen en ga naar de volgende poging", key=f"volgende_poging_{ronde}"):

                paren = [(w["naam"], w["trek"]) for w in wijzigingen]

                if len(set(paren)) != len(paren):
                    st.warning("Kies 2 verschillende aanpassingen.")
                elif any(w["nieuw"] == w["oud"] for w in wijzigingen):
                    st.warning("Verander bij beide keuzes de score echt.")
                elif not reden.strip():
                    st.warning("Schrijf ook kort waarom jullie denken dat dit helpt.")
                else:
                    nieuwe_profielen = copy.deepcopy(st.session_state.huidige_profielen)

                    for wijziging in wijzigingen:
                        nieuwe_profielen[wijziging["naam"]][wijziging["trek"]] = wijziging["nieuw"]

                    st.session_state.aanpassingsgeschiedenis.append({
                        "na_ronde": ronde,
                        "wijzigingen": wijzigingen,
                        "reden": reden
                    })

                    st.session_state.huidige_profielen = nieuwe_profielen
                    st.session_state.simulatieronde += 1
                    st.rerun()

        # ------------------------------------------
        # GELUKT
        # ------------------------------------------

        else:

            st.success("Deze groep overleeft en wordt gered.")

            st.markdown("""
Jullie hebben uiteindelijk een combinatie gevonden die werkt.

Denk kort na:
- Welke aanpassing hielp het meest?
- Welke eigenschap bleek vooral nuttig?
- Bestaat er één ideale persoonlijkheid?
""")

            if st.button("Opnieuw spelen"):
                reset_spel()
                st.rerun()
