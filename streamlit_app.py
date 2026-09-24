import streamlit as st
from google import genai
from pathlib import Path
import copy


# ==================================================
# INSTELLINGEN
# ==================================================

st.set_page_config(
    page_title="Expeditie Eiland",
    page_icon="🏝️",
    layout="centered"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ==================================================
# BIG FIVE
# ==================================================

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
        "en gemakkelijk contact legt. Lage score = eerder introvert en stiller "
        "in groepen. Hoge score = sociaal, actief en vlot in contact. "
        "1 = sterk introvert | 10 = sterk extravert",

    "Vriendelijkheid":
        "Vriendelijkheid gaat over de mate waarin iemand anderen helpt, vertrouwt "
        "en rekening houdt met anderen. Lage score = eerder afstandelijk, kritisch "
        "of competitief. Hoge score = behulpzaam, vriendelijk en gericht op samenwerking. "
        "1 = sterk afstandelijk | 10 = sterk vriendelijk",

    "Emotionele stabiliteit":
        "Emotionele stabiliteit gaat over hoe iemand omgaat met stress, problemen "
        "en tegenslagen. Lage score = sneller bezorgd, gespannen of emotioneel van slag. "
        "Hoge score = rustig en veerkrachtig onder druk. "
        "1 = sterk stressgevoelig | 10 = zeer emotioneel stabiel",

    "Zorgvuldigheid":
        "Zorgvuldigheid gaat over hoe georganiseerd, ordelijk en verantwoordelijk "
        "iemand is. Lage score = eerder slordig, chaotisch of impulsief. "
        "Hoge score = plant, werkt nauwkeurig en maakt dingen af. "
        "1 = sterk onzorgvuldig | 10 = zeer zorgvuldig",

    "Openheid voor ervaringen":
        "Openheid voor ervaringen gaat over de mate waarin iemand nieuwsgierig is "
        "en openstaat voor nieuwe ideeën en ervaringen. Lage score = liever bekende "
        "oplossingen en gewoontes. Hoge score = nieuwsgierig, creatief en bereid "
        "om iets nieuws te proberen. "
        "1 = sterk gesloten | 10 = zeer open voor nieuwe ervaringen"
}


# ==================================================
# PERSONAGES
# ==================================================

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


# ==================================================
# VERWACHTE PROFIELEN VOOR SNELLE FEEDBACK
# ==================================================

VERWACHT = {
    "Noor": {
        "Extraversie": {
            "min": 7,
            "max": 10,
            "uitleg": "ze gemakkelijk het woord neemt en anderen enthousiast krijgt"
        },
        "Vriendelijkheid": {
            "min": 5,
            "max": 8,
            "uitleg": "de tekst hierover geen heel duidelijke aanwijzingen geeft"
        },
        "Emotionele stabiliteit": {
            "min": 7,
            "max": 10,
            "uitleg": "ze zich na een mislukking meestal niet lang druk maakt"
        },
        "Zorgvuldigheid": {
            "min": 2,
            "max": 4,
            "uitleg": "ze vaak iets nieuws begint voordat het vorige af is"
        },
        "Openheid voor ervaringen": {
            "min": 8,
            "max": 10,
            "uitleg": "ze graag onbekende dingen probeert en originele oplossingen bedenkt"
        }
    },

    "Elias": {
        "Extraversie": {
            "min": 2,
            "max": 4,
            "uitleg": "hij niet veel praat in grote groepen"
        },
        "Vriendelijkheid": {
            "min": 3,
            "max": 6,
            "uitleg": "hij kritisch kan reageren wanneer anderen slordig werken"
        },
        "Emotionele stabiliteit": {
            "min": 5,
            "max": 7,
            "uitleg": "de tekst weinig duidelijke informatie geeft over zijn reactie op stress"
        },
        "Zorgvuldigheid": {
            "min": 8,
            "max": 10,
            "uitleg": "hij vooraf plant en taken nauwkeurig uitvoert"
        },
        "Openheid voor ervaringen": {
            "min": 2,
            "max": 5,
            "uitleg": "hij liever een aanpak kiest waarvan bewezen is dat die werkt"
        }
    },

    "Aya": {
        "Extraversie": {
            "min": 2,
            "max": 5,
            "uitleg": "ze niet snel de leiding neemt en anderen moeilijk tegenspreekt"
        },
        "Vriendelijkheid": {
            "min": 8,
            "max": 10,
            "uitleg": "ze anderen spontaan helpt en conflicten probeert te vermijden"
        },
        "Emotionele stabiliteit": {
            "min": 2,
            "max": 4,
            "uitleg": "ze in nieuwe situaties onzeker is en gemakkelijk piekert"
        },
        "Zorgvuldigheid": {
            "min": 4,
            "max": 7,
            "uitleg": "de tekst weinig informatie geeft over planning en ordelijkheid"
        },
        "Openheid voor ervaringen": {
            "min": 3,
            "max": 5,
            "uitleg": "nieuwe situaties haar aanvankelijk onzeker maken"
        }
    },

    "Mats": {
        "Extraversie": {
            "min": 6,
            "max": 8,
            "uitleg": "hij rechtstreeks zegt wat hij denkt en snel initiatief neemt"
        },
        "Vriendelijkheid": {
            "min": 2,
            "max": 4,
            "uitleg": "hij dingen zegt ook wanneer anderen dat onaangenaam vinden"
        },
        "Emotionele stabiliteit": {
            "min": 8,
            "max": 10,
            "uitleg": "hij kalm blijft wanneer anderen in paniek raken"
        },
        "Zorgvuldigheid": {
            "min": 2,
            "max": 4,
            "uitleg": "hij weinig geduld heeft voor uitgebreide plannen"
        },
        "Openheid voor ervaringen": {
            "min": 6,
            "max": 8,
            "uitleg": "hij risico's durft te nemen en snel voor actie kiest"
        }
    },

    "Lina": {
        "Extraversie": {
            "min": 2,
            "max": 4,
            "uitleg": "ze weinig behoefte heeft om voortdurend met anderen bezig te zijn"
        },
        "Vriendelijkheid": {
            "min": 4,
            "max": 7,
            "uitleg": "de tekst hierover weinig expliciete informatie geeft"
        },
        "Emotionele stabiliteit": {
            "min": 3,
            "max": 5,
            "uitleg": "ze zich behoorlijk zorgen kan maken wanneer iets belangrijk is"
        },
        "Zorgvuldigheid": {
            "min": 7,
            "max": 9,
            "uitleg": "ze eerst goed observeert en lang geconcentreerd kan werken"
        },
        "Openheid voor ervaringen": {
            "min": 8,
            "max": 10,
            "uitleg": "ze nieuwsgierig is en graag uitzoekt hoe dingen werken"
        }
    }
}


# ==================================================
# EXPEDITIEROLLEN
# ==================================================

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


# ==================================================
# SESSION STATE
# ==================================================

standaard_state = {
    "fase": "intro",
    "groepsleden": "",
    "analyse_intro_getoond": False,
    "personage_index": 0,
    "resultaten": {},
    "feedback": {},
    "analyse_log": {},
    "rollen": {},
    "rolredenen": {},
    "simulatieronde": 1,
    "huidige_profielen": {},
    "simulatieverhalen": {},
    "aanpassingsgeschiedenis": [],
    "redding_onthuld": False,
    "stappenstatus": {},

    # Alleen gebruikt door de verborgen presentatienavigatie
    "demo_stap": 0,
    "demo_navigatie_actief": False,
    "demo_profielen": {},
    "demo_rollen": {},
    "demo_rolredenen": {},
    "demo_simulatieverhalen": {}
}

for sleutel, waarde in standaard_state.items():
    if sleutel not in st.session_state:
        st.session_state[sleutel] = copy.deepcopy(waarde)


# ==================================================
# DEMO-PROFIELEN
# ==================================================

def standaard_profiel(naam):

    profiel = {}

    for trek, waarden in VERWACHT[naam].items():
        profiel[trek] = round(
            (waarden["min"] + waarden["max"]) / 2
        )

    return profiel


def maak_demo_profielen():

    return {
        persoon["naam"]: standaard_profiel(persoon["naam"])
        for persoon in personages
    }


if not st.session_state.demo_profielen:
    st.session_state.demo_profielen = maak_demo_profielen()


if not st.session_state.demo_rollen:
    st.session_state.demo_rollen = {
        "Verkenner": "Noor",
        "Planner / voorraadbeheerder": "Elias",
        "Kampbouwer": "Mats",
        "Onderzoeker": "Lina",
        "Groepscoördinator": "Aya"
    }


if not st.session_state.demo_rolredenen:
    st.session_state.demo_rolredenen = {
        "Verkenner":
            "Noor staat sterk open voor nieuwe ervaringen.",

        "Planner / voorraadbeheerder":
            "Elias werkt zeer zorgvuldig en planmatig.",

        "Kampbouwer":
            "Mats neemt snel beslissingen en blijft rustig onder druk.",

        "Onderzoeker":
            "Lina is nieuwsgierig en observeert zorgvuldig.",

        "Groepscoördinator":
            "Aya is vriendelijk en houdt sterk rekening met anderen."
    }


# ==================================================
# HULPFUNCTIES
# ==================================================

def profiel_voor_weergave(naam):

    status = st.session_state.stappenstatus.get(
        f"analyse_{naam}"
    )

    if (
        status == "voltooid"
        and naam in st.session_state.resultaten
    ):
        return copy.deepcopy(
            st.session_state.resultaten[naam]
        )

    return copy.deepcopy(
        st.session_state.demo_profielen[naam]
    )


def profielen_voor_simulatie():

    profielen = {}

    for persoon in personages:
        naam = persoon["naam"]
        profielen[naam] = profiel_voor_weergave(naam)

    return profielen


def actieve_rollen():

    if (
        st.session_state.stappenstatus.get("rollen") == "voltooid"
        and st.session_state.rollen
    ):
        return copy.deepcopy(
            st.session_state.rollen
        )

    return copy.deepcopy(
        st.session_state.demo_rollen
    )


def actieve_rolredenen():

    if (
        st.session_state.stappenstatus.get("rollen") == "voltooid"
        and st.session_state.rolredenen
    ):
        return copy.deepcopy(
            st.session_state.rolredenen
        )

    return copy.deepcopy(
        st.session_state.demo_rolredenen
    )


def profiel_regel(profiel):

    return (
        f"Extraversie {profiel['Extraversie']}/10 | "
        f"Vriendelijkheid {profiel['Vriendelijkheid']}/10 | "
        f"Emotionele stabiliteit {profiel['Emotionele stabiliteit']}/10 | "
        f"Zorgvuldigheid {profiel['Zorgvuldigheid']}/10 | "
        f"Openheid {profiel['Openheid voor ervaringen']}/10"
    )


def profielen_naar_tekst(profielen):

    tekst = ""

    for naam, profiel in profielen.items():

        tekst += (
            f"{naam}\n"
            f"- Extraversie: {profiel['Extraversie']}/10\n"
            f"- Vriendelijkheid: {profiel['Vriendelijkheid']}/10\n"
            f"- Emotionele stabiliteit: {profiel['Emotionele stabiliteit']}/10\n"
            f"- Zorgvuldigheid: {profiel['Zorgvuldigheid']}/10\n"
            f"- Openheid voor ervaringen: {profiel['Openheid voor ervaringen']}/10\n\n"
        )

    return tekst


def rollen_naar_tekst():

    rollen = actieve_rollen()
    redenen = actieve_rolredenen()

    tekst = ""

    for rol, persoon in rollen.items():

        tekst += (
            f"- {rol}: {persoon}. "
            f"Reden van de leerlingen: {redenen.get(rol, '')}\n"
        )

    return tekst


def score_feedback(
    score,
    minimum,
    maximum,
    uitleg
):

    if minimum <= score <= maximum:

        return (
            "goed",
            f"Deze score past goed: {uitleg}."
        )

    if minimum - 1 <= score <= maximum + 1:

        return (
            "twijfel",
            f"Deze score is nog verdedigbaar. "
            f"Kijk vooral naar het feit dat {uitleg}."
        )

    if score < minimum:

        return (
            "laag",
            f"Deze score lijkt wat laag. "
            f"Een score rond {minimum}–{maximum}/10 lijkt beter te passen, "
            f"omdat {uitleg}."
        )

    return (
        "hoog",
        f"Deze score lijkt wat hoog. "
        f"Een score rond {minimum}–{maximum}/10 lijkt beter te passen, "
        f"omdat {uitleg}."
    )


def maak_feedback_persoon(
    naam,
    scores,
    gekozen_trekken
):

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
            f"- {punt}"
            for punt in goed[:3]
        )
    else:
        tekst += "- Herbekijk de meeste scores nog eens."


    tekst += "\n\n### Herbekijk dit\n"

    if herbekijk:
        tekst += "\n".join(
            f"- {punt}"
            for punt in herbekijk
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
        "- Denk vooral in laag, gemiddeld of hoog; één exact cijfer bestaat niet.\n"
        "- Pas jullie scores aan als de feedback jullie overtuigt."
    )

    return tekst


def reset_spel():

    st.session_state.clear()
    st.rerun()


# ==================================================
# EINDVERSLAG
# ==================================================

def maak_verslag():

    lijnen = []

    lijnen.append("EXPEDITIE EILAND — OVERZICHT")
    lijnen.append("=" * 45)
    lijnen.append("")
    lijnen.append(
        f"Groepsleden: {st.session_state.groepsleden}"
    )
    lijnen.append("")


    # --------------------------------------------------
    # PERSOONLIJKHEIDSANALYSE
    # --------------------------------------------------

    lijnen.append("1. PERSOONLIJKHEIDSANALYSE")
    lijnen.append("")

    for persoon in personages:

        naam = persoon["naam"]

        lijnen.append(
            naam.upper()
        )

        status = st.session_state.stappenstatus.get(
            f"analyse_{naam}"
        )

        if status == "overgeslagen":

            lijnen.append(
                "STAP OVERGESLAGEN."
            )
            lijnen.append("")
            lijnen.append("-" * 30)
            lijnen.append("")
            continue

        if status != "voltooid":

            lijnen.append(
                "Geen volledige analyse geregistreerd."
            )
            lijnen.append("")
            lijnen.append("-" * 30)
            lijnen.append("")
            continue


        log = st.session_state.analyse_log.get(
            naam,
            {}
        )

        eerste = log.get(
            "voor_feedback",
            {}
        )

        definitief = st.session_state.resultaten.get(
            naam,
            {}
        )


        lijnen.append(
            "Eerste inschatting:"
        )

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
                "Twee beargumenteerde keuzes:"
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

        lijnen.append("")

        if wijzigingen:

            lijnen.append(
                "Aangepast na de feedback:"
            )

            lijnen.extend(
                wijzigingen
            )

        else:

            lijnen.append(
                "Na de feedback werden geen scores aangepast."
            )

        lijnen.append("")
        lijnen.append("-" * 30)
        lijnen.append("")


    # --------------------------------------------------
    # ROLLEN
    # --------------------------------------------------

    lijnen.append(
        "2. EXPEDITIEROLLEN"
    )
    lijnen.append("")

    rollenstatus = st.session_state.stappenstatus.get(
        "rollen"
    )

    if rollenstatus == "overgeslagen":

        lijnen.append(
            "STAP OVERGESLAGEN."
        )

    elif rollenstatus == "voltooid":

        for rol, persoon in st.session_state.rollen.items():

            lijnen.append(
                f"{rol}: {persoon}"
            )

            lijnen.append(
                f"Waarom: {st.session_state.rolredenen.get(rol, '')}"
            )

            lijnen.append("")

    else:

        lijnen.append(
            "Geen volledige rolverdeling geregistreerd."
        )


    # --------------------------------------------------
    # OVERLEVINGSPROEVEN
    # --------------------------------------------------

    lijnen.append("")
    lijnen.append(
        "3. OVERLEVINGSPROEVEN"
    )
    lijnen.append("")

    for nummer in range(1, 5):

        status = st.session_state.stappenstatus.get(
            f"overlevingsproef_{nummer}"
        )

        lijnen.append(
            f"Overlevingsproef {nummer}:"
        )

        if status == "voltooid":
            lijnen.append("Voltooid.")

        elif status == "overgeslagen":
            lijnen.append("STAP OVERGESLAGEN.")

        else:
            lijnen.append("Niet uitgevoerd.")

        lijnen.append("")


    # --------------------------------------------------
    # AANPASSINGEN
    # --------------------------------------------------

    lijnen.append(
        "4. PERSOONLIJKHEIDSAANPASSINGEN"
    )
    lijnen.append("")

    if st.session_state.aanpassingsgeschiedenis:

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

    else:

        lijnen.append(
            "Geen geregistreerde persoonlijkheidsaanpassingen."
        )


    # --------------------------------------------------
    # EINDPROFIELEN
    # --------------------------------------------------

    lijnen.append("")
    lijnen.append(
        "5. UITEINDELIJKE PERSOONLIJKHEIDSPROFIELEN"
    )
    lijnen.append("")

    for persoon in personages:

        naam = persoon["naam"]

        status = st.session_state.stappenstatus.get(
            f"analyse_{naam}"
        )

        if status != "voltooid":

            lijnen.append(
                f"{naam}: basisanalyse overgeslagen "
                "of niet volledig uitgevoerd."
            )
            continue

        profiel = st.session_state.huidige_profielen.get(
            naam
        )

        if profiel:

            lijnen.append(
                f"{naam}: {profiel_regel(profiel)}"
            )


    # --------------------------------------------------
    # EINDRESULTAAT
    # --------------------------------------------------

    lijnen.append("")
    lijnen.append(
        "6. EINDRESULTAAT"
    )
    lijnen.append("")

    laatste_status = st.session_state.stappenstatus.get(
        "overlevingsproef_4"
    )

    if laatste_status == "voltooid":

        lijnen.append(
            "De uiteindelijke expeditie overleefde zes maanden "
            "en werd gered."
        )

    elif laatste_status == "overgeslagen":

        lijnen.append(
            "Laatste overlevingsproef: STAP OVERGESLAGEN."
        )

    else:

        lijnen.append(
            "De laatste overlevingsproef werd niet volledig uitgevoerd."
        )

    return "\n".join(lijnen)


# ==================================================
# DEMOVERHALEN
# ==================================================

def demo_verhaal(ronde):

    verhalen = {
        1: """
### De eerste maanden
Elias probeert als planner meteen een systeem voor water en voedsel te maken. Noor wil als verkenner liever snel het eiland ontdekken en vertrekt soms zonder goede voorbereiding. Mats helpt het kamp bouwen, maar door zijn lage zorgvuldigheid laat hij taken onafgewerkt. Aya probeert ruzies te voorkomen en Lina vindt als onderzoeker een goede plek voor drinkwater.

### Het wordt moeilijk
Na een zware storm raakt een deel van het voedsel verloren. Elias wordt boos omdat afspraken niet zijn gevolgd en Mats reageert scherp. Aya probeert hen rustig te krijgen, maar raakt zelf steeds onzekerder. Noor vindt een nieuwe plek om voedsel te zoeken, maar de groep is ondertussen te moe en slecht georganiseerd om het probleem nog op te lossen.

### Uitkomst
De groep haalt de zes maanden niet.

### Waarom?
- **Noor — zorgvuldigheid / verkenner:** nieuwe ideeën helpen, maar haar voorbereiding is te zwak.
- **Elias — zorgvuldigheid / planner:** hij brengt structuur, maar botst vaak met anderen.
- **Mats — vriendelijkheid / kampbouwer:** zijn scherpe reacties maken conflicten groter.
""",

        2: """
### De eerste maanden
De groep werkt beter georganiseerd dan de vorige keer. Noor bereidt haar verkenningen zorgvuldiger voor en Elias hoeft minder vaak achter anderen aan te zitten. Lina houdt goed bij waar water en voedsel te vinden zijn. Aya probeert als groepscoördinator iedereen bij elkaar te houden.

### Het wordt moeilijk
Tijdens een lange tocht raakt de groep verdwaald. Mats blijft rustig en wil verdergaan, maar Aya raakt door de stress steeds onzekerder. Noor bedenkt een andere route en daardoor bereiken ze opnieuw het kamp. Toch zorgen stress en ruzies ervoor dat de groep het na enkele maanden niet meer volhoudt.

### Uitkomst
Ook deze groep haalt de zes maanden niet.

### Waarom?
- **Noor — hogere zorgvuldigheid:** de verkenningen verlopen beter voorbereid.
- **Aya — emotionele stabiliteit / groepscoördinator:** langdurige stress wordt een probleem.
- **Mats — vriendelijkheid:** zijn directe reacties veroorzaken opnieuw spanning.
""",

        3: """
### De eerste maanden
Het kamp functioneert deze keer goed. Elias beheert de voorraden, Noor verkent nieuwe gebieden en Lina onderzoekt planten en waterbronnen. Aya is rustiger dan voordien en grijpt sneller in wanneer een ruzie begint. Daardoor houdt de groep veel langer stand.

### Het wordt moeilijk
Lina ontdekt een route naar een hoog deel van het eiland. Mats wil snel vertrekken en Noor vindt dat spannend. Elias wil eerst extra materiaal meenemen. Ze bereiden de tocht beter voor dan vroeger, maar onderweg neemt Mats toch een groot risico. Noor volgt hem en daardoor komt de groep in een gevaarlijke situatie waaruit ze te laat terugkeert.

### Uitkomst
De groep haalt de zes maanden opnieuw niet.

### Waarom?
- **Aya — emotionele stabiliteit:** de samenwerking verloopt beter.
- **Elias — zorgvuldigheid / planner:** voedsel en materiaal zijn goed geregeld.
- **Mats — risico's / kampbouwer:** een te snelle beslissing zorgt voor het grootste probleem.
""",

        4: """
### De eerste maanden
De groep werkt vanaf het begin volgens duidelijke afspraken. Elias beheert de voorraden, Noor bereidt haar verkenningen beter voor en Lina onderzoekt water, planten en het weer. Mats blijft rustig als er iets misgaat. Aya houdt als groepscoördinator de sfeer in de groep goed.

### Het wordt moeilijk
Tijdens een tocht stort een deel van het pad in. Mats wil niet meer zomaar alleen beslissen en bespreekt de opties met de anderen. Noor en Lina vinden samen een veiligere route. Elias controleert of er genoeg voedsel en water is voor de omweg. De verschillende persoonlijkheden vullen elkaar nu beter aan en de groep bereikt het einde van de zesde maand.

### Uitkomst
De zes maanden zijn voorbij. De jongeren verzamelen zich op het strand en kijken naar de horizon.

### Waarom?
- **Noor — zorgvuldigheid / verkenner:** ze combineert nieuwsgierigheid nu met betere voorbereiding.
- **Mats — samenwerking:** zijn kalmte blijft nuttig zonder dat hij te snel risico's neemt.
- **De groep:** de verschillende persoonlijkheden vullen elkaar beter aan.
"""
    }

    return verhalen[ronde]


# ==================================================
# VERBORGEN PRESENTATIENAVIGATIE
# ==================================================

def markeer_huidige_stap_als_overgeslagen():

    stap = st.session_state.demo_stap

    if 2 <= stap <= 6:

        naam = personages[stap - 2]["naam"]

        sleutel = f"analyse_{naam}"

        if st.session_state.stappenstatus.get(sleutel) != "voltooid":
            st.session_state.stappenstatus[sleutel] = "overgeslagen"

    elif stap == 7:

        if st.session_state.stappenstatus.get("rollen") != "voltooid":
            st.session_state.stappenstatus["rollen"] = "overgeslagen"

    elif 8 <= stap <= 11:

        ronde = stap - 7

        sleutel = f"overlevingsproef_{ronde}"

        if st.session_state.stappenstatus.get(sleutel) != "voltooid":
            st.session_state.stappenstatus[sleutel] = "overgeslagen"


def ga_naar_demo_stap(stap):

    stap = max(
        0,
        min(12, stap)
    )

    st.session_state.demo_stap = stap
    st.session_state.demo_navigatie_actief = True

    if not st.session_state.groepsleden:
        st.session_state.groepsleden = "Demo"


    if stap == 0:

        st.session_state.fase = "intro"


    elif stap == 1:

        st.session_state.fase = "analyse"
        st.session_state.analyse_intro_getoond = False
        st.session_state.personage_index = 0


    elif 2 <= stap <= 6:

        st.session_state.fase = "analyse"
        st.session_state.analyse_intro_getoond = True
        st.session_state.personage_index = stap - 2


    elif stap == 7:

        st.session_state.fase = "rollen"
        st.session_state.personage_index = 5


    elif 8 <= stap <= 11:

        ronde = stap - 7

        st.session_state.fase = "simulatie"
        st.session_state.simulatieronde = ronde

        st.session_state.huidige_profielen = (
            profielen_voor_simulatie()
        )

        st.session_state.demo_simulatieverhalen[
            ronde
        ] = demo_verhaal(ronde)

        sleutel = f"overlevingsproef_{ronde}"

        if st.session_state.stappenstatus.get(sleutel) != "voltooid":
            st.session_state.stappenstatus[sleutel] = "overgeslagen"

        if ronde == 4:
            st.session_state.redding_onthuld = False


    elif stap == 12:

        st.session_state.fase = "simulatie"
        st.session_state.simulatieronde = 4

        st.session_state.huidige_profielen = (
            profielen_voor_simulatie()
        )

        st.session_state.demo_simulatieverhalen[
            4
        ] = demo_verhaal(4)

        st.session_state.redding_onthuld = True

        if (
            st.session_state.stappenstatus.get("overlevingsproef_4")
            != "voltooid"
        ):
            st.session_state.stappenstatus[
                "overlevingsproef_4"
            ] = "overgeslagen"


def huidig_verhaal(ronde):

    if ronde in st.session_state.simulatieverhalen:

        return st.session_state.simulatieverhalen[
            ronde
        ]

    if (
        st.session_state.demo_navigatie_actief
        and ronde in st.session_state.demo_simulatieverhalen
    ):

        return st.session_state.demo_simulatieverhalen[
            ronde
        ]

    return None


# ==================================================
# INTRO
# ==================================================

if st.session_state.fase == "intro":

    st.title(
        "Expeditie Eiland"
    )

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
            st.session_state.demo_stap = 1
            st.session_state.demo_navigatie_actief = False

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
            st.session_state.demo_stap = 2
            st.session_state.demo_navigatie_actief = False

            st.rerun()


    else:

        index = st.session_state.personage_index


        st.title(
            "Fase 1 — Leer de groep kennen"
        )


        st.progress(
            index / len(personages)
        )


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
                st.session_state.demo_stap = 7
                st.session_state.demo_navigatie_actief = False

                st.rerun()


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

                    if naam not in st.session_state.analyse_log:

                        st.session_state.analyse_log[
                            naam
                        ] = {
                            "voor_feedback": copy.deepcopy(scores),
                            "gekozen_trekken": list(gekozen_trekken),
                            "motivaties": copy.deepcopy(motivaties)
                        }


                    st.session_state.feedback[
                        naam
                    ] = maak_feedback_persoon(
                        naam,
                        scores,
                        gekozen_trekken
                    )


            if naam in st.session_state.feedback:

                st.markdown(
                    st.session_state.feedback[
                        naam
                    ]
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
                        trek: st.session_state[
                            f"{naam}_{trek}"
                        ]
                        for trek in TREKKEN
                    }


                    st.session_state.resultaten[
                        naam
                    ] = copy.deepcopy(
                        definitief
                    )


                    st.session_state.stappenstatus[
                        f"analyse_{naam}"
                    ] = "voltooid"


                    if naam not in st.session_state.analyse_log:

                        st.session_state.analyse_log[
                            naam
                        ] = {
                            "voor_feedback": copy.deepcopy(definitief),
                            "gekozen_trekken": list(gekozen_trekken),
                            "motivaties": copy.deepcopy(motivaties)
                        }


                    st.session_state.analyse_log[
                        naam
                    ][
                        "na_feedback"
                    ] = copy.deepcopy(
                        definitief
                    )


                    st.session_state.personage_index += 1


                    st.session_state.demo_stap = min(
                        7,
                        st.session_state.demo_stap + 1
                    )


                    st.session_state.demo_navigatie_actief = False


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


                profiel = profiel_voor_weergave(
                    naam
                )


                if (
                    st.session_state.stappenstatus.get(
                        f"analyse_{naam}"
                    )
                    == "voltooid"
                ):

                    st.markdown(
                        "**Jullie definitieve inschatting:**"
                    )

                else:

                    st.markdown(
                        "**Demo-profiel "
                        "(persoonlijkheidsanalyse overgeslagen):**"
                    )


                for trek in TREKKEN:

                    st.write(
                        f"{trek}: **{profiel[trek]}/10**"
                    )


    st.markdown(
        "### Verdeel de rollen"
    )


    gekozen_rollen = {}
    gekozen_redenen = {}

    namen = [
        persoon["naam"]
        for persoon in personages
    ]


    for rol, beschrijving in ROLLEN.items():

        st.markdown(
            f"#### {rol}"
        )


        st.caption(
            beschrijving
        )


        gekozen_rollen[
            rol
        ] = st.selectbox(
            f"Wie wordt {rol}?",
            namen,
            key=f"rol_{rol}"
        )


        gekozen_redenen[
            rol
        ] = st.text_area(
            "Waarom past deze persoon bij deze rol?",
            placeholder=(
                "Verbind jullie keuze met "
                "zijn of haar persoonlijkheid..."
            ),
            key=f"reden_rol_{rol}"
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

        if len(set(gekozen_rollen.values())) != len(gekozen_rollen):

            st.warning(
                "Geef elke rol aan een andere persoon."
            )

        elif any(
            not tekst.strip()
            for tekst in gekozen_redenen.values()
        ):

            st.warning(
                "Leg bij elke rol kort uit waarom "
                "die persoon volgens jullie geschikt is."
            )

        else:

            st.session_state.rollen = copy.deepcopy(
                gekozen_rollen
            )

            st.session_state.rolredenen = copy.deepcopy(
                gekozen_redenen
            )

            st.session_state.stappenstatus[
                "rollen"
            ] = "voltooid"


            # Als alles normaal werd uitgevoerd zijn dit exact
            # de leerlingenscores. Bij overgeslagen demo-stappen
            # worden alleen voor de simulatie demo-profielen gebruikt.
            st.session_state.huidige_profielen = (
                profielen_voor_simulatie()
            )


            st.session_state.fase = "simulatie"
            st.session_state.demo_stap = 8
            st.session_state.demo_navigatie_actief = False

            st.rerun()


# ==================================================
# OVERLEVINGSSIMULATIE
# ==================================================

elif st.session_state.fase == "simulatie":

    ronde = st.session_state.simulatieronde


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

        for naam, profiel in st.session_state.huidige_profielen.items():

            st.markdown(
                f"**{naam}**"
            )

            st.write(
                profiel_regel(profiel)
            )


        st.markdown(
            "**Rollen**"
        )


        for rol, persoon in actieve_rollen().items():

            st.write(
                f"{rol}: {persoon}"
            )


    verhaal = huidig_verhaal(
        ronde
    )


    # --------------------------------------------------
    # SIMULATIE NOG NIET GESTART
    # --------------------------------------------------

    if verhaal is None:

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

            st.session_state.demo_navigatie_actief = False


            profielen_tekst = profielen_naar_tekst(
                st.session_state.huidige_profielen
            )


            rollen_tekst = rollen_naar_tekst()


            if ronde <= 3:

                uitkomst = "MISLUKT"

            else:

                uitkomst = "SLAAGT"


            laatste_aanpassing = ""


            if st.session_state.aanpassingsgeschiedenis:

                laatste = st.session_state.aanpassingsgeschiedenis[-1]


                laatste_aanpassing += (
                    "Laatste persoonlijkheidsaanpassingen:\n"
                )


                for wijziging in laatste["wijzigingen"]:

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


            vorige_poging = ""

            if ronde > 1:

                vorig_verhaal = st.session_state.simulatieverhalen.get(
                    ronde - 1,
                    ""
                )

                if vorig_verhaal:

                    vorige_poging = (
                        "\nDIT GEBEURDE IN DE VORIGE POGING:\n"
                        f"{vorig_verhaal}\n"
                    )


            if ronde <= 3:

                eindinstructie = """
Bij de sectie 'Uitkomst' moet duidelijk worden
dat de groep de zes maanden niet heeft gehaald.
"""

            else:

                eindinstructie = """
Verklap nog NIET dat er redding komt.

Bij de sectie 'Uitkomst' schrijf je alleen dat
de zes maanden voorbij zijn en dat de jongeren
zich op het strand verzamelen en naar de horizon kijken.

Vermeld geen schip, helikopter, reddingsteam of redding.
"""


            prompt = f"""
Je bent de verteller van een kort en levendig expeditieverhaal
voor leerlingen van ongeveer 16 jaar.

ZEER BELANGRIJK:
- Schrijf ALLES uitsluitend in correct Nederlands.
- Gebruik korte en eenvoudige zinnen.
- Gebruik gewone woorden die een 16-jarige gemakkelijk begrijpt.
- Gebruik geen Engelse woorden, titels of zinnen.

Vijf jongeren zijn gestrand op een onbewoond eiland.
Ze moeten zes maanden overleven.

PERSOONLIJKHEDEN:

{profielen_tekst}

EXPEDITIEROLLEN:

{rollen_tekst}

{laatste_aanpassing}

{vorige_poging}

De verplichte uitkomst achter de schermen is:

{uitkomst}

{eindinstructie}

REGELS VOOR HET VERHAAL:

- Maak duidelijk dat de keuzes van de leerlingen gevolgen hebben.
- Noem de jongeren bij naam.
- Gebruik hun expeditierollen actief in het verhaal.
- Leg duidelijke verbanden tussen:
  persoonlijkheid → gedrag → gevolg.
- Baseer je op de scores die de leerlingen hebben gekozen.
- Laat minstens 4 van de 5 jongeren iets concreets doen.
- Een persoonlijkheidstrek kan helpen, maar ook problemen veroorzaken.
- Vermijd vage uitspraken zoals:
  'de groep werkte niet goed samen'.
- Vertel wie iets doet en wat daarvan het gevolg is.
- Gebruik concrete problemen:
  voedsel, water, kamp, verkennen, stress, risico's en ruzies.
- Bij poging 2, 3 en 4 moet duidelijk worden wat door de aanpassingen beter gaat.
- Benoem minstens één concrete verbetering tegenover de vorige poging.
- Herhaal niet telkens hetzelfde probleem.
- Bij MISLUKT haalt de groep de zes maanden niet.
- Beschrijf overlijden niet grafisch.
- Bij SLAAGT overleeft de groep zes maanden.
- Verklap de redding nog niet.
- Houd het verhaal kort: ongeveer 180 tot 220 woorden.
- Schrijf ALLES in het Nederlands.

Gebruik exact deze structuur:

### De eerste maanden
Schrijf één korte alinea van ongeveer 5 à 6 zinnen.
Vertel hoe het kamp, voedsel, water en de eerste verkenningen verlopen.
Noem verschillende jongeren.
Laat zien hoe hun persoonlijkheid en rol helpen of problemen veroorzaken.

### Het wordt moeilijk
Schrijf één korte alinea van ongeveer 5 à 6 zinnen.
Er ontstaat een belangrijk probleem.
Laat zien hoe de jongeren reageren.
Maak duidelijk welke persoonlijkheidstrekken hierbij helpen of problemen geven.
Maak duidelijk waarom de groep uiteindelijk wel of niet zes maanden volhoudt.

### Uitkomst
Geef maximaal 2 korte zinnen.
Volg strikt de verplichte uitkomst.

### Waarom?
Geef precies 3 korte punten in deze vorm:

- **Naam — persoonlijkheidstrek / rol:** concreet gevolg.
"""


            with st.spinner(
                "De expeditie wordt gesimuleerd..."
            ):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )


                    st.session_state.simulatieverhalen[
                        ronde
                    ] = response.text


                    st.session_state.stappenstatus[
                        f"overlevingsproef_{ronde}"
                    ] = "voltooid"


                    st.session_state.demo_stap = min(
                        11,
                        7 + ronde
                    )


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

        # --------------------------------------------------
        # MISLUKTE POGING
        # --------------------------------------------------

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
                verhaal
            )


            st.error(
                "Deze expeditie overleeft de zes maanden niet."
            )


            st.markdown(
                "## Jullie beurt"
            )


            st.info(
                "Lees eerst goed wat er is gebeurd. "
                "Pas daarna 2 persoonlijkheidsscores aan "
                "om de kans te verhogen dat de groep de volgende keer "
                "wél zes maanden kan overleven."
            )


            wijzigingen = []


            for i in range(2):

                st.markdown(
                    f"### Aanpassing {i + 1}"
                )


                gekozen_naam = st.selectbox(
                    "Wie willen jullie aanpassen?",
                    list(
                        st.session_state.huidige_profielen.keys()
                    ),
                    key=f"aanp_naam_{ronde}_{i}"
                )


                gekozen_trek = st.selectbox(
                    "Welke persoonlijkheidstrek?",
                    TREKKEN,
                    key=f"aanp_trek_{ronde}_{i}"
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
                    help=UITLEG[gekozen_trek]
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
                "Waarom verhogen deze veranderingen volgens jullie "
                "de kans op overleven?",
                placeholder=(
                    "Verbind jullie aanpassingen met wat "
                    "er tijdens deze expeditie misging."
                ),
                key=f"reden_{ronde}"
            )


            st.info(
                "Blijf persoonlijkheden aanpassen en opnieuw testen "
                "tot jullie een groep hebben gemaakt die "
                "het eiland kan overleven."
            )


            if st.button(
                "Test de aangepaste groep",
                key=f"volgende_poging_{ronde}"
            ):

                paren = [
                    (
                        wijziging["naam"],
                        wijziging["trek"]
                    )
                    for wijziging in wijzigingen
                ]


                if len(set(paren)) != len(paren):

                    st.warning(
                        "Kies twee verschillende aanpassingen."
                    )

                elif any(
                    wijziging["nieuw"] == wijziging["oud"]
                    for wijziging in wijzigingen
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
                        "wijzigingen": copy.deepcopy(wijzigingen),
                        "reden": reden
                    })


                    st.session_state.huidige_profielen = (
                        nieuwe_profielen
                    )


                    st.session_state.simulatieronde += 1
                    st.session_state.redding_onthuld = False
                    st.session_state.demo_navigatie_actief = False


                    st.rerun()


        # --------------------------------------------------
        # LAATSTE POGING
        # --------------------------------------------------

        else:

            st.markdown(
                verhaal
            )


            if not st.session_state.redding_onthuld:

                st.markdown(
                    "## De zes maanden zijn voorbij..."
                )


                st.write(
                    "De groep staat op het strand "
                    "en kijkt naar de horizon."
                )


                if st.button(
                    "Ontdek of jullie dit keer wel gered zijn"
                ):

                    st.session_state.redding_onthuld = True
                    st.session_state.demo_stap = 12

                    st.rerun()


            # --------------------------------------------------
            # REDDING
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
                    "Ze hebben het gehaald. De groep wordt gered."
                )


                st.markdown("""
Na zes maanden verschijnt eindelijk hulp.

Jullie zijn erin geslaagd een groep samen te stellen
die lang genoeg kon samenwerken, verkennen en overleven.
""")


                # --------------------------------------------------
                # VERSLAG
                # --------------------------------------------------

                st.header(
                    "Overzicht om in te dienen"
                )


                st.write(
                    "Dit overzicht toont jullie eerste "
                    "persoonlijkheidsinschattingen, argumentaties, "
                    "aanpassingen na feedback, expeditierollen "
                    "en veranderingen tijdens de overlevingsproeven."
                )


                st.info(
                    "Download hieronder het overzicht en dien het daarna in "
                    "via de uploadzone van het vak **Gedragswetenschappen**."
                )


                verslag = maak_verslag()


                st.text_area(
                    "Bekijk jullie overzicht",
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


# ==================================================
# BIJNA ONZICHTBARE NAVIGATIE RECHTSONDER
# ==================================================

css_geheime_nav = (
    "<style>"
    ".st-key-geheime_nav {"
    "position: fixed;"
    "right: 8px;"
    "bottom: 8px;"
    "width: 120px;"
    "padding: 12px;"
    "opacity: 0.04;"
    "z-index: 999999;"
    "transition: opacity 0.2s ease;"
    "}"
    ".st-key-geheime_nav:hover {"
    "opacity: 1;"
    "}"
    ".st-key-geheime_nav button {"
    "min-height: 29px !important;"
    "height: 29px !important;"
    "padding: 0px 6px !important;"
    "font-size: 13px !important;"
    "}"
    "</style>"
)


st.markdown(
    css_geheime_nav,
    unsafe_allow_html=True
)


with st.container(
    key="geheime_nav"
):

    links, rechts = st.columns(2)


    with links:

        if st.button(
            "‹",
            key="verborgen_terug",
            help="Vorige scherm"
        ):

            nieuwe_stap = max(
                0,
                st.session_state.demo_stap - 1
            )

            ga_naar_demo_stap(
                nieuwe_stap
            )

            st.rerun()


    with rechts:

        if st.button(
            "›",
            key="verborgen_verder",
            help="Volgende scherm"
        ):

            markeer_huidige_stap_als_overgeslagen()


            nieuwe_stap = min(
                12,
                st.session_state.demo_stap + 1
            )


            ga_naar_demo_stap(
                nieuwe_stap
            )


            st.rerun()
