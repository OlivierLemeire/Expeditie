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
        "Extraversie": {
            "min": 7, "max": 10,
            "uitleg": "ze neemt gemakkelijk het woord en krijgt anderen enthousiast"
        },
        "Vriendelijkheid": {
            "min": 5, "max": 8,
            "uitleg": "de tekst geeft geen heel sterke aanwijzingen, maar ze functioneert vlot in een groep"
        },
        "Emotionele stabiliteit": {
            "min": 7, "max": 10,
            "uitleg": "als iets mislukt, maakt ze zich daar meestal niet lang druk over"
        },
        "Zorgvuldigheid": {
            "min": 2, "max": 4,
            "uitleg": "ze begint regelmatig aan iets nieuws voordat het vorige af is"
        },
        "Openheid voor ervaringen": {
            "min": 8, "max": 10,
            "uitleg": "ze probeert graag onbekende dingen uit en bedenkt originele oplossingen"
        }
    },

    "Elias": {
        "Extraversie": {
            "min": 2, "max": 4,
            "uitleg": "hij praat niet veel in grote groepen"
        },
        "Vriendelijkheid": {
            "min": 3, "max": 6,
            "uitleg": "hij kan nogal kritisch reageren wanneer anderen slordig werken"
        },
        "Emotionele stabiliteit": {
            "min": 5, "max": 7,
            "uitleg": "de tekst geeft weinig duidelijke informatie over zijn reactie op stress"
        },
        "Zorgvuldigheid": {
            "min": 8, "max": 10,
            "uitleg": "hij plant vooraf en voert taken nauwkeurig uit"
        },
        "Openheid voor ervaringen": {
            "min": 2, "max": 5,
            "uitleg": "hij kiest liever voor een aanpak waarvan bewezen is dat die werkt"
        }
    },

    "Aya": {
        "Extraversie": {
            "min": 2, "max": 5,
            "uitleg": "ze neemt niet snel de leiding en spreekt anderen moeilijk tegen"
        },
        "Vriendelijkheid": {
            "min": 8, "max": 10,
            "uitleg": "ze helpt anderen spontaan en probeert conflicten te vermijden"
        },
        "Emotionele stabiliteit": {
            "min": 2, "max": 4,
            "uitleg": "ze is onzeker in nieuwe situaties en piekert gemakkelijk"
        },
        "Zorgvuldigheid": {
            "min": 4, "max": 7,
            "uitleg": "de tekst geeft weinig informatie over planning en ordelijkheid"
        },
        "Openheid voor ervaringen": {
            "min": 3, "max": 5,
            "uitleg": "nieuwe situaties maken haar aanvankelijk onzeker"
        }
    },

    "Mats": {
        "Extraversie": {
            "min": 6, "max": 8,
            "uitleg": "hij zegt rechtstreeks wat hij denkt en neemt snel initiatief"
        },
        "Vriendelijkheid": {
            "min": 2, "max": 4,
            "uitleg": "hij zegt dingen ook wanneer anderen dat onaangenaam vinden"
        },
        "Emotionele stabiliteit": {
            "min": 8, "max": 10,
            "uitleg": "hij blijft kalm wanneer anderen in paniek raken"
        },
        "Zorgvuldigheid": {
            "min": 2, "max": 4,
            "uitleg": "hij heeft weinig geduld voor uitgebreide plannen"
        },
        "Openheid voor ervaringen": {
            "min": 6, "max": 8,
            "uitleg": "hij durft risico's te nemen en kiest snel voor actie"
        }
    },

    "Lina": {
        "Extraversie": {
            "min": 2, "max": 4,
            "uitleg": "ze heeft weinig behoefte om voortdurend met anderen bezig te zijn"
        },
        "Vriendelijkheid": {
            "min": 4, "max": 7,
            "uitleg": "de tekst zegt weinig expliciet over haar omgang met anderen"
        },
        "Emotionele stabiliteit": {
            "min": 3, "max": 5,
            "uitleg": "wanneer iets belangrijk is, maakt ze zich er behoorlijk zorgen over"
        },
        "Zorgvuldigheid": {
            "min": 7, "max": 9,
            "uitleg": "ze observeert eerst goed en kan lang geconcentreerd werken"
        },
        "Openheid voor ervaringen": {
            "min": 8, "max": 10,
            "uitleg": "ze is nieuwsgierig en wil uitzoeken hoe dingen werken"
        }
    }
}


# --------------------------------------------------
# EXPEDITIEROLLEN
# --------------------------------------------------

ROLLEN = {
    "Verkenner":
        "verkent onbekend terrein en zoekt nieuwe routes",

    "Planner / voorraadbeheerder":
        "houdt overzicht over voedsel, water en materiaal",

    "Kampbouwer":
        "organiseert praktisch werk en onderhoudt het kamp",

    "Onderzoeker":
        "observeert het terrein, planten, weer en mogelijke gevaren",

    "Groepscoördinator":
        "organiseert de samenwerking en probeert conflicten te beperken"
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

if "analyse_log" not in st.session_state:
    st.session_state.analyse_log = {}

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


def rollen_naar_tekst():

    tekst = ""

    for rol, persoon in st.session_state.rollen.items():

        reden = st.session_state.rolredenen.get(rol, "")

        tekst += (
            f"- {rol}: {persoon}. "
            f"Reden van de leerlingen: {reden}\n"
        )

    return tekst


def reset_spel():

    st.session_state.clear()


def score_feedback(score, minimum, maximum, uitleg):

    if minimum <= score <= maximum:

        return (
            "goed",
            f"Deze score past goed: {uitleg}."
        )

    elif minimum - 1 <= score <= maximum + 1:

        return (
            "twijfel",
            f"Deze score is nog verdedigbaar. Kijk vooral naar het feit dat {uitleg}."
        )

    elif score < minimum:

        return (
            "laag",
            f"Deze score lijkt wat laag. Een score rond {minimum}–{maximum}/10 lijkt beter te passen, omdat {uitleg}."
        )

    else:

        return (
            "hoog",
            f"Deze score lijkt wat hoog. Een score rond {minimum}–{maximum}/10 lijkt beter te passen, omdat {uitleg}."
        )


def maak_feedback_persoon(naam, scores, gekozen_trekken):

    profiel = VERWACHT[naam]

    goed = []
    herbekijk = []

    for trek in TREKKEN:

        verwacht = profiel[trek]

        status, tekst = score_feedback(
            scores[trek],
            verwacht["min"],
            verwacht["max"],
            verwacht["uitleg"]
        )

        if status in ["goed", "twijfel"]:
            goed.append(
                f"**{trek}:** {tekst}"
            )
        else:
            herbekijk.append(
                f"**{trek}:** {tekst}"
            )

    tekst = "### Goed gezien\n"

    if goed:
        tekst += "\n".join(
            [f"- {x}" for x in goed[:3]]
        )
    else:
        tekst += "- Herbekijk de meeste scores nog eens."

    tekst += "\n\n### Herbekijk dit\n"

    if herbekijk:
        tekst += "\n".join(
            [f"- {x}" for x in herbekijk]
        )
    else:
        tekst += "- De meeste scores zijn goed verdedigbaar."

    tekst += "\n\n### Jullie uitleg\n"

    for trek in gekozen_trekken:

        verwacht = profiel[trek]

        tekst += (
            f"- **{trek}:** Een goede argumentatie verwijst naar het feit dat "
            f"{verwacht['uitleg']}.\n"
        )

    tekst += (
        "\n### Advies\n"
        "- Kijk vooral naar laag, gemiddeld of hoog; één exact cijfer bestaat niet.\n"
        "- Pas jullie scores aan als de feedback jullie overtuigt."
    )

    return tekst


def profiel_regel(profiel):

    return (
        f"Extraversie {profiel['Extraversie']}/10 | "
        f"Vriendelijkheid {profiel['Vriendelijkheid']}/10 | "
        f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']}/10 | "
        f"Zorgvuldigheid {profiel['Zorgvuldigheid']}/10 | "
        f"Openheid {profiel['Openheid voor ervaringen']}/10"
    )


def maak_verslag():

    lijnen = []

    lijnen.append("EXPEDITIE EILAND — OVERZICHT")
    lijnen.append("=" * 40)
    lijnen.append("")
    lijnen.append(
        f"Groepsleden: {st.session_state.groepsleden}"
    )
    lijnen.append("")

    # -------------------------
    # PERSOONLIJKHEIDSANALYSE
    # -------------------------

    lijnen.append("1. PERSOONLIJKHEIDSANALYSE")
    lijnen.append("")

    for persoon in personages:

        naam = persoon["naam"]

        lijnen.append(naam.upper())

        log = st.session_state.analyse_log.get(
            naam,
            {}
        )

        eerste = log.get(
            "voor_feedback",
            st.session_state.resultaten.get(naam, {})
        )

        definitief = st.session_state.resultaten.get(
            naam,
            {}
        )

        lijnen.append("Eerste inschatting:")

        for trek in TREKKEN:

            if trek in eerste:

                lijnen.append(
                    f"- {trek}: {eerste[trek]}/10"
                )

        lijnen.append("")

        gekozen = log.get(
            "gekozen_trekken",
            []
        )

        motivaties = log.get(
            "motivaties",
            {}
        )

        if gekozen:

            lijnen.append(
                "Twee keuzes die we moesten uitleggen:"
            )

            for trek in gekozen:

                lijnen.append(
                    f"- {trek}: {motivaties.get(trek, '')}"
                )

            lijnen.append("")

        lijnen.append(
            "Definitieve inschatting na feedback:"
        )

        for trek in TREKKEN:

            if trek in definitief:

                lijnen.append(
                    f"- {trek}: {definitief[trek]}/10"
                )

        lijnen.append("")

        wijzigingen = []

        for trek in TREKKEN:

            if (
                trek in eerste
                and trek in definitief
                and eerste[trek] != definitief[trek]
            ):

                wijzigingen.append(
                    f"- {trek}: "
                    f"{eerste[trek]}/10 → "
                    f"{definitief[trek]}/10"
                )

        if wijzigingen:

            lijnen.append(
                "Aangepast na de feedback:"
            )

            lijnen.extend(
                wijzigingen
            )

        else:

            lijnen.append(
                "Na de feedback hebben we geen scores aangepast."
            )

        lijnen.append("")
        lijnen.append("-" * 30)
        lijnen.append("")


    # -------------------------
    # ROLLEN
    # -------------------------

    lijnen.append(
        "2. EXPEDITIEROLLEN"
    )
    lijnen.append("")

    for rol, persoon in st.session_state.rollen.items():

        lijnen.append(
            f"{rol}: {persoon}"
        )

        lijnen.append(
            f"Waarom: "
            f"{st.session_state.rolredenen.get(rol, '')}"
        )

        lijnen.append("")


    # -------------------------
    # OVERLEVINGSAANPASSINGEN
    # -------------------------

    lijnen.append(
        "3. AANPASSINGEN TIJDENS DE EXPEDITIES"
    )
    lijnen.append("")

    for nummer, ronde_data in enumerate(
        st.session_state.aanpassingsgeschiedenis,
        start=1
    ):

        lijnen.append(
            f"Na mislukte expeditie {nummer}:"
        )

        for wijziging in ronde_data["wijzigingen"]:

            lijnen.append(
                f"- {wijziging['naam']}: "
                f"{wijziging['trek']} "
                f"{wijziging['oud']}/10 → "
                f"{wijziging['nieuw']}/10"
            )

        lijnen.append(
            f"Onze reden: {ronde_data['reden']}"
        )

        lijnen.append("")


    # -------------------------
    # EINDPROFIEL
    # -------------------------

    lijnen.append(
        "4. UITEINDELIJKE PERSOONLIJKHEIDSPROFIELEN"
    )
    lijnen.append("")

    for naam, profiel in st.session_state.huidige_profielen.items():

        lijnen.append(
            f"{naam}: {profiel_regel(profiel)}"
        )

    lijnen.append("")
    lijnen.append(
        "5. EINDRESULTAAT"
    )
    lijnen.append("")

    lijnen.append(
        "We bleven de persoonlijkheden aanpassen tot we "
        "een groep hadden samengesteld die zes maanden kon "
        "overleven op het eiland."
    )

    lijnen.append(
        "De uiteindelijke expeditie overleefde en werd gered."
    )

    return "\n".join(lijnen)


# ==================================================
# INTRO
# ==================================================

if st.session_state.fase == "intro":

    st.title("Expeditie Eiland")

    eiland_pad = Path(
        "images/eiland.png"
    )

    if eiland_pad.exists():

        st.image(
            str(eiland_pad),
            use_container_width=True
        )

    st.markdown("""
Een groep jongeren is neergestort op een onbewoond eiland.

Redding kan pas over **zes maanden** komen.

Jullie missie:

**1.** schat hun persoonlijkheid in  
**2.** stel een expeditieteam samen  
**3.** ontdek of deze groep kan overleven  
**4.** pas persoonlijkheden aan als het misloopt  
**5.** blijf proberen tot jullie een groep hebben gemaakt die zes maanden kan overleven
""")

    st.info(
        "Op het einde maakt de app automatisch een uitgebreid overzicht "
        "van jullie antwoorden, keuzes en aanpassingen. "
        "Dat overzicht moeten jullie indienen."
    )

    groepsleden = st.text_input(
        "Namen van de groepsleden",
        placeholder="bv. Nora, Yassine, Marie"
    )

    if st.button(
        "Start de expeditie"
    ):

        if not groepsleden.strip():

            st.warning(
                "Vul eerst jullie namen in."
            )

        else:

            st.session_state.groepsleden = groepsleden

            st.session_state.fase = "analyse"

            st.rerun()


# ==================================================
# PERSOONLIJKHEIDSANALYSE
# ==================================================

elif st.session_state.fase == "analyse":

    if not st.session_state.analyse_intro_getoond:

        st.title(
            "Fase 1 — Leer de groep kennen"
        )

        st.markdown("""
Voor jullie de expeditie kunnen starten,
moeten jullie eerst de persoonlijkheid van de vijf jongeren inschatten.

Gebruik de **Big Five-persoonlijkheidstrekken**
uit het handboek, **pagina 157–158**.

Bij elke persoon:

- geef je alle vijf persoonlijkheidstrekken een score;
- leg je twee scores kort uit;
- krijg je feedback;
- mag je je scores daarna nog verbeteren.

Daarna gebruiken jullie deze profielen om de expeditie samen te stellen.
""")

        if st.button(
            "Ga naar persoon 1"
        ):

            st.session_state.analyse_intro_getoond = True

            st.rerun()

    else:

        index = st.session_state.personage_index

        st.title(
            "Fase 1 — Leer de groep kennen"
        )

        st.progress(
            index / len(personages)
        )


        # --------------------------------------------------
        # ALLE PERSONEN KLAAR
        # --------------------------------------------------

        if index >= len(personages):

            st.success(
                "De vijf persoonlijkheidsprofielen zijn klaar."
            )

            st.markdown("""
Nu kennen jullie de vijf jongeren.

De volgende stap is een **expeditieploeg samenstellen**.
Wie krijgt welke taak?
""")

            if st.button(
                "Stel de expeditie samen"
            ):

                st.session_state.fase = "rollen"

                st.rerun()


        # --------------------------------------------------
        # ÉÉN PERSOON
        # --------------------------------------------------

        else:

            persoon = personages[index]

            naam = persoon["naam"]

            st.caption(
                f"Persoon {index + 1} van {len(personages)}"
            )

            st.header(
                naam
            )

            afbeelding = Path(
                persoon["afbeelding"]
            )

            if afbeelding.exists():

                st.image(
                    str(afbeelding),
                    width=340
                )

            st.write(
                persoon["beschrijving"]
            )

            st.markdown(
                "### Schat de persoonlijkheid in"
            )

            st.info(
                "Zoek concrete aanwijzingen in de beschrijving. "
                "Gebruik wat deze persoon doet, denkt of zegt "
                "om de Big Five-scores in te schatten."
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

            st.markdown(
                "### Licht 2 keuzes toe"
            )

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
                    placeholder=(
                        "Verwijs naar concrete aanwijzingen "
                        "uit de beschrijving..."
                    ),
                    key=f"{naam}_motivatie_{trek}"
                )

            if st.button(
                "Geef feedback",
                key=f"feedback_{naam}"
            ):

                if len(
                    gekozen_trekken
                ) != 2:

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

                    # Eerste inschatting slechts één keer bewaren
                    if naam not in st.session_state.analyse_log:

                        st.session_state.analyse_log[naam] = {
                            "voor_feedback": copy.deepcopy(scores),
                            "gekozen_trekken": list(gekozen_trekken),
                            "motivaties": copy.deepcopy(motivaties)
                        }

                    st.session_state.feedback[naam] = (
                        maak_feedback_persoon(
                            naam,
                            scores,
                            gekozen_trekken
                        )
                    )


            # --------------------------------------------------
            # FEEDBACK
            # --------------------------------------------------

            if naam in st.session_state.feedback:

                st.markdown(
                    st.session_state.feedback[naam]
                )

                st.info(
                    "Bekijk jullie scores opnieuw. "
                    "Pas ze aan als de feedback jullie overtuigt."
                )

                if st.button(
                    "Bewaar en ga verder",
                    key=f"volgende_{naam}"
                ):

                    definitief = {
                        trek: st.session_state[f"{naam}_{trek}"]
                        for trek in TREKKEN
                    }

                    st.session_state.resultaten[naam] = (
                        definitief
                    )

                    if naam not in st.session_state.analyse_log:

                        st.session_state.analyse_log[naam] = {
                            "voor_feedback": copy.deepcopy(definitief),
                            "gekozen_trekken": list(gekozen_trekken),
                            "motivaties": copy.deepcopy(motivaties)
                        }

                    st.session_state.analyse_log[naam][
                        "na_feedback"
                    ] = copy.deepcopy(definitief)

                    st.session_state.personage_index += 1

                    st.rerun()


# ==================================================
# EXPEDITIEROLLEN
# ==================================================

elif st.session_state.fase == "rollen":

    st.title(
        "Fase 2 — Stel de expeditie samen"
    )

    kaart_pad = Path(
        "images/eilandkaart.png"
    )

    if kaart_pad.exists():

        st.image(
            str(kaart_pad),
            use_container_width=True
        )

    st.markdown("""
De groep zal onbekend terrein moeten verkennen,
voedsel en water beheren, een kamp onderhouden
en samen beslissingen nemen.

Geef elke jongere daarom een **expeditierol**.

Weet je niet meer goed wie iemand is?
Open hieronder zijn of haar profiel.
""")


    # --------------------------------------------------
    # PROFIELEN TERUG BEKIJKEN
    # --------------------------------------------------

    st.markdown(
        "### Bekijk de vijf jongeren opnieuw"
    )

    for persoon in personages:

        naam = persoon["naam"]

        with st.expander(
            f"Bekijk {naam}"
        ):

            afbeelding = Path(
                persoon["afbeelding"]
            )

            kolom1, kolom2 = st.columns(
                [1, 2]
            )

            with kolom1:

                if afbeelding.exists():

                    st.image(
                        str(afbeelding),
                        use_container_width=True
                    )

            with kolom2:

                st.write(
                    persoon["beschrijving"]
                )

                profiel = (
                    st.session_state
                    .resultaten[naam]
                )

                st.markdown(
                    "**Jullie definitieve inschatting:**"
                )

                for trek in TREKKEN:

                    st.write(
                        f"{trek}: **{profiel[trek]}/10**"
                    )


    # --------------------------------------------------
    # ROLLEN VERDELEN
    # --------------------------------------------------

    st.markdown(
        "### Verdeel de rollen"
    )

    gekozen_rollen = {}

    gekozen_redenen = {}

    namen = [
        p["naam"]
        for p in personages
    ]

    for rol, beschrijving in ROLLEN.items():

        st.markdown(
            f"#### {rol}"
        )

        st.caption(
            beschrijving
        )

        gekozen_rollen[rol] = (
            st.selectbox(
                f"Wie wordt {rol}?",
                namen,
                key=f"rol_{rol}"
            )
        )

        gekozen_redenen[rol] = (
            st.text_area(
                "Waarom past deze persoon bij deze rol?",
                placeholder=(
                    "Verbind jullie keuze met "
                    "zijn of haar persoonlijkheid..."
                ),
                key=f"reden_rol_{rol}"
            )
        )


    st.info(
        "Hierna begint de expeditie. "
        "Als de groep het niet haalt, passen jullie "
        "de persoonlijkheden aan en proberen jullie opnieuw. "
        "Jullie blijven dit doen tot jullie een groep hebben "
        "gemaakt die zes maanden kan overleven."
    )


    if st.button(
        "Start de expeditie"
    ):

        if len(
            set(
                gekozen_rollen.values()
            )
        ) != len(
            gekozen_rollen
        ):

            st.warning(
                "Geef elke rol aan een andere persoon."
            )

        elif any(
            not tekst.strip()
            for tekst
            in gekozen_redenen.values()
        ):

            st.warning(
                "Leg bij elke rol kort uit waarom "
                "die persoon volgens jullie geschikt is."
            )

        else:

            st.session_state.rollen = (
                copy.deepcopy(
                    gekozen_rollen
                )
            )

            st.session_state.rolredenen = (
                copy.deepcopy(
                    gekozen_redenen
                )
            )

            st.session_state.huidige_profielen = (
                copy.deepcopy(
                    st.session_state.resultaten
                )
            )

            st.session_state.fase = (
                "simulatie"
            )

            st.rerun()


# ==================================================
# OVERLEVINGSSIMULATIE
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = (
        st.session_state.simulatieronde
    )

    st.title(
        "Fase 3 — De expeditie"
    )

    kaart_pad = Path(
        "images/eilandkaart.png"
    )

    if kaart_pad.exists():

        st.image(
            str(kaart_pad),
            use_container_width=True
        )

    if ronde == 1:

        st.caption(
            "De eerste expeditie vertrekt."
        )

    else:

        st.caption(
            "De aangepaste groep probeert het opnieuw."
        )

    st.info(
        "Doel: blijf leren uit wat misgaat en "
        "de persoonlijkheden aanpassen tot jullie "
        "een groep hebben gemaakt die zes maanden overleeft."
    )


    with st.expander(
        "Bekijk de huidige expeditieploeg"
    ):

        for naam, profiel in (
            st.session_state
            .huidige_profielen
            .items()
        ):

            st.markdown(
                f"**{naam}**"
            )

            st.write(
                profiel_regel(
                    profiel
                )
            )

        st.markdown(
            "**Rollen**"
        )

        for rol, persoon in (
            st.session_state
            .rollen
            .items()
        ):

            st.write(
                f"{rol}: {persoon}"
            )


    # --------------------------------------------------
    # NOG NIET GESIMULEERD
    # --------------------------------------------------

    if ronde not in (
        st.session_state
        .simulatieverhalen
    ):

        if ronde == 1:

            st.markdown(
                "Kan deze expeditie zes maanden overleven?"
            )

        else:

            st.markdown(
                "Hebben jullie veranderingen genoeg geholpen?"
            )

        if st.button(
            "Start de overlevingsproef",
            key=f"start_test_{ronde}"
        ):

            profielen_tekst = (
                profielen_naar_tekst(
                    st.session_state
                    .huidige_profielen
                )
            )

            rollen_tekst = (
                rollen_naar_tekst()
            )

            if ronde <= 3:

                uitkomst = "MISLUKT"

            else:

                uitkomst = "SLAAGT"


            laatste_aanpassing = ""

            if (
                st.session_state
                .aanpassingsgeschiedenis
            ):

                laatste = (
                    st.session_state
                    .aanpassingsgeschiedenis[-1]
                )

                laatste_aanpassing += (
                    "Laatste persoonlijkheidsaanpassingen:\n"
                )

                for wijziging in laatste[
                    "wijzigingen"
                ]:

                    laatste_aanpassing += (
                        f"- {wijziging['naam']}: "
                        f"{wijziging['trek']} "
                        f"van {wijziging['oud']} "
                        f"naar {wijziging['nieuw']}\n"
                    )

                laatste_aanpassing += (
                    "\nWaarom de leerlingen dachten "
                    "dat dit zou helpen:\n"
                    f"{laatste['reden']}\n"
                )


            prompt = f"""
Je bent de verteller van een kort survivalverhaal
voor leerlingen van ongeveer 17 jaar.

ZEER BELANGRIJK:
Schrijf werkelijk ALLES uitsluitend in correct Nederlands.
Gebruik geen Engelse woorden, Engelse kopjes of Engelse zinnen.
Alle titels en tussenkopjes moeten Nederlands zijn.

Vijf jongeren zijn gestrand op een onbewoond eiland.
Ze moeten zes maanden overleven en ondernemen tegelijk
een ontdekkingsreis door onbekend terrein.

PERSOONLIJKHEDEN:

{profielen_tekst}

EXPEDITIEROLLEN:

{rollen_tekst}

{laatste_aanpassing}

De verplichte uitkomst is:

{uitkomst}

REGELS:

- Bij MISLUKT haalt de groep de zes maanden niet.
  Uiteindelijk sterven de groepsleden vóór de redding.
  Beschrijf dit niet grafisch.
- Bij SLAAGT overleeft de groep zes maanden en wordt iedereen gered.
- Baseer het verloop duidelijk op de persoonlijkheidsprofielen.
- Houd ook rekening met de expeditierollen.
- Persoonlijkheid bepaalt gedrag niet volledig.
- Elke persoonlijkheidstrek kan voordelen én nadelen hebben.
- Bij latere pogingen moet duidelijk worden wat door de aanpassingen beter gaat.
- Gebruik niet telkens hetzelfde probleem.
- Gebruik concrete situaties:
  water zoeken, voedsel beheren, kamp bouwen,
  onbekend terrein verkennen, risico's nemen,
  stress, conflicten en samenwerking.
- Houd het verhaal kort en levendig.
- Alles moet in het Nederlands zijn.

Gebruik exact deze structuur:

### De kust
Maximaal 2 korte zinnen.

### Het binnenland
Maximaal 2 korte zinnen.

### Het hoogste punt
Maximaal 2 korte zinnen.

### Uitkomst
Maximaal 2 korte zinnen.

### Waarom?
- één kort punt
- één kort punt
"""

            with st.spinner(
                "De expeditie wordt gesimuleerd..."
            ):

                try:

                    response = (
                        client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )
                    )

                    st.session_state.simulatieverhalen[
                        ronde
                    ] = response.text

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Er ging iets mis bij de simulatie."
                    )

                    st.code(
                        str(e)
                    )


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
            st.session_state
            .simulatieverhalen[ronde]
        )


        # --------------------------------------------------
        # MISLUKT
        # --------------------------------------------------

        if ronde <= 3:

            st.error(
                "Deze expeditie overleeft de zes maanden niet."
            )

            st.markdown(
                "## Jullie beurt"
            )

            st.info(
                "Lees eerst goed wat er misging. "
                "Pas daarna 2 persoonlijkheidsscores aan "
                "om de kans te verhogen dat de volgende "
                "expeditie wél zes maanden kan overleven."
            )

            wijzigingen = []

            for i in range(2):

                st.markdown(
                    f"### Aanpassing {i + 1}"
                )

                gekozen_naam = (
                    st.selectbox(
                        "Wie willen jullie aanpassen?",
                        list(
                            st.session_state
                            .huidige_profielen
                            .keys()
                        ),
                        key=f"aanp_naam_{ronde}_{i}"
                    )
                )

                gekozen_trek = (
                    st.selectbox(
                        "Welke persoonlijkheidstrek?",
                        TREKKEN,
                        key=f"aanp_trek_{ronde}_{i}"
                    )
                )

                oude_score = (
                    st.session_state
                    .huidige_profielen[
                        gekozen_naam
                    ][
                        gekozen_trek
                    ]
                )

                st.caption(
                    f"Huidige score: {oude_score}/10"
                )

                nieuwe_score = st.slider(
                    "Nieuwe score",
                    min_value=max(
                        1,
                        oude_score - 3
                    ),
                    max_value=min(
                        10,
                        oude_score + 3
                    ),
                    value=oude_score,
                    key=f"aanp_nieuw_{ronde}_{i}",
                    help=UITLEG[
                        gekozen_trek
                    ]
                )

                wijzigingen.append({
                    "naam": gekozen_naam,
                    "trek": gekozen_trek,
                    "oud": oude_score,
                    "nieuw": nieuwe_score
                })


            st.markdown(
                "### Leg jullie strategie uit"
            )

            reden = st.text_area(
                "Waarom verhogen deze veranderingen volgens jullie de kans op overleven?",
                placeholder=(
                    "Verbind jullie aanpassingen "
                    "met wat er tijdens deze expeditie misging."
                ),
                key=f"reden_{ronde}"
            )


            st.info(
                "Blijf persoonlijkheden aanpassen en opnieuw testen "
                "tot jullie een groep hebben gemaakt die het eiland kan overleven."
            )


            if st.button(
                "Test de aangepaste groep",
                key=f"volgende_poging_{ronde}"
            ):

                paren = [
                    (
                        w["naam"],
                        w["trek"]
                    )
                    for w in wijzigingen
                ]

                if len(
                    set(paren)
                ) != len(paren):

                    st.warning(
                        "Kies twee verschillende aanpassingen."
                    )

                elif any(
                    w["nieuw"] == w["oud"]
                    for w in wijzigingen
                ):

                    st.warning(
                        "Verander beide scores werkelijk."
                    )

                elif not reden.strip():

                    st.warning(
                        "Leg eerst uit waarom de veranderingen "
                        "de kans op overleven verhogen."
                    )

                else:

                    nieuwe_profielen = (
                        copy.deepcopy(
                            st.session_state
                            .huidige_profielen
                        )
                    )

                    for wijziging in wijzigingen:

                        nieuwe_profielen[
                            wijziging["naam"]
                        ][
                            wijziging["trek"]
                        ] = (
                            wijziging["nieuw"]
                        )

                    st.session_state.aanpassingsgeschiedenis.append({
                        "wijzigingen": copy.deepcopy(wijzigingen),
                        "reden": reden
                    })

                    st.session_state.huidige_profielen = (
                        nieuwe_profielen
                    )

                    st.session_state.simulatieronde += 1

                    st.rerun()


        # --------------------------------------------------
        # GERED
        # --------------------------------------------------

        else:

            gered_pad = Path(
                "images/gered.png"
            )

            if gered_pad.exists():

                st.image(
                    str(gered_pad),
                    use_container_width=True
                )

            st.success(
                "De groep heeft zes maanden overleefd en wordt gered."
            )

            st.markdown("""
Jullie zijn erin geslaagd een groep samen te stellen
die lang genoeg kon samenwerken, verkennen en overleven
om de redding te halen.
""")


            # --------------------------------------------------
            # EINDVERSLAG
            # --------------------------------------------------

            st.header(
                "Overzicht om in te dienen"
            )

            st.write(
                "Dit overzicht toont niet alleen het eindresultaat, "
                "maar ook jullie eerste persoonlijkheidsinschattingen, "
                "argumentaties en aanpassingen na feedback."
            )

            verslag = maak_verslag()

            st.text_area(
                "Kopieer dit overzicht en dien het in",
                value=verslag,
                height=650
            )

            st.download_button(
                label="Download het overzicht",
                data=verslag,
                file_name="expeditie_eiland_overzicht.txt",
                mime="text/plain"
            )

            if st.button(
                "Opnieuw beginnen"
            ):

                reset_spel()

                st.rerun()
