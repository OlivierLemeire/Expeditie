import streamlit as st
from google import genai


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
# TITEL EN INTRODUCTIE
# --------------------------------------------------

st.title("🏝️ Expeditie Eiland")

st.write(
    "Vijf jongeren vertrekken samen op expeditie. "
    "Voor je ontdekt hoe het hen vergaat, moet je eerst hun persoonlijkheid analyseren."
)

st.info(
    "Lees de beschrijving van elk personage aandachtig. "
    "Geef daarna voor elke persoonlijkheidsdimensie een score van 1 tot 10. "
    "Er is niet altijd één exact juist antwoord. "
    "Het belangrijkste is dat je je keuzes kunt verantwoorden."
)


# --------------------------------------------------
# UITLEG BIG FIVE
# --------------------------------------------------

with st.expander("🧠 Wat betekenen de vijf persoonlijkheidsdimensies?"):

    st.markdown("""
### Extraversie — tegenover introversie
De mate waarin iemand nieuwe sociale contacten legt.

**1 =** eerder introvert en weinig behoefte aan sociale contacten  
**10 =** sterk extravert en legt gemakkelijk nieuwe sociale contacten

---

### Vriendelijkheid — tegenover afstandelijkheid
De mate waarin iemand bereid is anderen te helpen en te vertrouwen.

**1 =** eerder afstandelijk  
**10 =** sterk vriendelijk, behulpzaam en vertrouwend

---

### Emotionele stabiliteit — tegenover neuroticisme
De mate waarin iemand goed omgaat met emotionele zaken zoals stress en problemen.

**1 =** eerder neurotisch en gevoelig voor stress  
**10 =** emotioneel zeer stabiel

---

### Zorgvuldigheid — tegenover onzorgvuldigheid
De mate waarin iemand georganiseerd en ordelijk is.

**1 =** eerder chaotisch of onzorgvuldig  
**10 =** sterk georganiseerd, ordelijk en zorgvuldig

---

### Openheid voor ervaringen — tegenover geslotenheid voor ervaringen
De mate waarin iemand openstaat voor nieuwe ervaringen.

**1 =** eerder gesloten voor nieuwe ervaringen  
**10 =** sterk open voor nieuwe ervaringen
""")


# --------------------------------------------------
# PERSONAGES
# --------------------------------------------------

personages = {

    "Noor": """
Noor probeert graag onbekende dingen uit en bedenkt vaak originele oplossingen.
In een groep neemt ze gemakkelijk het woord en krijgt ze anderen enthousiast.
Ze begint echter regelmatig aan iets nieuws voordat het vorige af is.
Als iets mislukt, maakt ze zich daar meestal niet lang druk over.
""",

    "Elias": """
Elias houdt van duidelijke afspraken en maakt graag vooraf een planning.
Hij voert taken nauwkeurig uit en merkt snel wanneer anderen zich niet aan afspraken houden.
Hij praat niet veel in grote groepen en kiest liever voor een aanpak waarvan bewezen is
dat die werkt. Als anderen slordig werken, kan hij nogal kritisch reageren.
""",

    "Aya": """
Aya merkt snel wanneer iemand zich niet goed voelt en probeert conflicten te vermijden.
Ze helpt anderen vaak zonder dat ze daarom vragen.
Zelf neemt ze niet snel de leiding en vindt ze het lastig om iemand tegen te spreken.
In nieuwe situaties is ze aanvankelijk onzeker en piekert ze gemakkelijk over wat er mis kan gaan.
""",

    "Mats": """
Mats blijft meestal kalm, ook wanneer anderen in paniek raken.
Hij neemt snel beslissingen en durft risico's te nemen.
Hij vindt discussies niet erg en zegt rechtstreeks wat hij denkt,
ook wanneer anderen dat onaangenaam vinden.
Hij heeft weinig geduld voor lange vergaderingen of uitgebreide plannen.
""",

    "Lina": """
Lina is nieuwsgierig en observeert eerst goed voordat ze iets doet.
Ze vindt het interessant om uit te zoeken hoe dingen werken
en kan lang geconcentreerd aan een probleem werken.
Ze heeft weinig behoefte om voortdurend met anderen bezig te zijn.
Wanneer iets belangrijk is, kan ze zich er wel behoorlijk zorgen over maken.
"""
}


# --------------------------------------------------
# SCORES BEWAREN
# --------------------------------------------------

scores = {}


# --------------------------------------------------
# LEERLINGEN LATEN ANALYSEREN
# --------------------------------------------------

for naam, beschrijving in personages.items():

    st.divider()

    st.header(naam)

    st.write(beschrijving)

    st.markdown("#### Jullie inschatting")

    extraversie = st.slider(
        f"Extraversie — {naam}",
        1,
        10,
        5,
        key=f"{naam}_extraversie",
        help="1 = eerder introvert | 10 = sterk extravert"
    )

    vriendelijkheid = st.slider(
        f"Vriendelijkheid — {naam}",
        1,
        10,
        5,
        key=f"{naam}_vriendelijkheid",
        help="1 = eerder afstandelijk | 10 = sterk vriendelijk, behulpzaam en vertrouwend"
    )

    emotionele_stabiliteit = st.slider(
        f"Emotionele stabiliteit — {naam}",
        1,
        10,
        5,
        key=f"{naam}_emotionele_stabiliteit",
        help="1 = eerder neurotisch en stressgevoelig | 10 = emotioneel zeer stabiel"
    )

    zorgvuldigheid = st.slider(
        f"Zorgvuldigheid — {naam}",
        1,
        10,
        5,
        key=f"{naam}_zorgvuldigheid",
        help="1 = eerder chaotisch of onzorgvuldig | 10 = sterk georganiseerd en zorgvuldig"
    )

    openheid = st.slider(
        f"Openheid voor ervaringen — {naam}",
        1,
        10,
        5,
        key=f"{naam}_openheid",
        help="1 = eerder gesloten voor nieuwe ervaringen | 10 = sterk open voor nieuwe ervaringen"
    )

    motivatie = st.text_area(
        f"Leg kort uit waarom jullie deze scores kozen voor {naam}.",
        placeholder=(
            "Verwijs naar concrete informatie uit de beschrijving. "
            "Bijvoorbeeld: 'We geven Elias een hoge score voor zorgvuldigheid "
            "omdat hij vooraf plant en taken nauwkeurig uitvoert.'"
        ),
        key=f"{naam}_motivatie"
    )

    scores[naam] = {
        "Extraversie": extraversie,
        "Vriendelijkheid": vriendelijkheid,
        "Emotionele stabiliteit": emotionele_stabiliteit,
        "Zorgvuldigheid": zorgvuldigheid,
        "Openheid voor ervaringen": openheid,
        "Motivatie": motivatie
    }


# --------------------------------------------------
# FEEDBACK
# --------------------------------------------------

st.divider()

st.header("🔎 Controleer jullie analyse")

st.write(
    "Als iedereen is geanalyseerd, kunnen jullie feedback vragen. "
    "De feedback kijkt niet naar één exact juist cijfer, maar naar de vraag "
    "of jullie inschatting goed past bij de beschrijving."
)

if st.button("🧠 Controleer onze persoonlijkheidsanalyse"):

    ontbrekende_motivaties = [
        naam
        for naam, profiel in scores.items()
        if not profiel["Motivatie"].strip()
    ]

    if ontbrekende_motivaties:

        st.warning(
            "Geef eerst bij elk personage een korte motivatie. "
            "Nog niet ingevuld: "
            + ", ".join(ontbrekende_motivaties)
        )

    else:

        analyses = ""

        for naam, profiel in scores.items():

            analyses += f"""

PERSONAGE: {naam}

Beschrijving:
{personages[naam]}

Scores van de leerlingen:
- Extraversie: {profiel['Extraversie']}/10
- Vriendelijkheid: {profiel['Vriendelijkheid']}/10
- Emotionele stabiliteit: {profiel['Emotionele stabiliteit']}/10
- Zorgvuldigheid: {profiel['Zorgvuldigheid']}/10
- Openheid voor ervaringen: {profiel['Openheid voor ervaringen']}/10

Motivatie van de leerlingen:
{profiel['Motivatie']}

----------------------------------------

"""

        prompt = f"""
Je bent docent gedragswetenschappen voor leerlingen van ongeveer 17 jaar.

De leerlingen leren vijf persoonlijkheidsdimensies kennen en hebben vijf
fictieve personages geanalyseerd.

Gebruik UITSLUITEND deze terminologie:

1. extraversie tegenover introversie
2. vriendelijkheid tegenover afstandelijkheid
3. emotionele stabiliteit tegenover neuroticisme
4. zorgvuldigheid tegenover onzorgvuldigheid
5. openheid voor ervaringen tegenover geslotenheid voor ervaringen

Een hoge score betekent telkens een hoge score op de eerstgenoemde eigenschap.

Dus bijvoorbeeld:

- 10 op extraversie = sterk extravert
- 1 op extraversie = sterk introvert

- 10 op emotionele stabiliteit = zeer emotioneel stabiel
- 1 op emotionele stabiliteit = eerder neurotisch en stressgevoelig

- 10 op openheid voor ervaringen = zeer open voor nieuwe ervaringen
- 1 op openheid voor ervaringen = eerder gesloten voor nieuwe ervaringen


DOEL VAN DE FEEDBACK

De leerlingen moeten vooral leren begrijpen wat de vijf dimensies betekenen.

Geef daarom didactische feedback op zowel:
- hun gekozen scores;
- hun geschreven motivatie.


BELANGRIJKE REGELS

- Doe NIET alsof voor iedere eigenschap één exact juist cijfer bestaat.
- Beoordeel vooral of laag, gemiddeld of hoog goed is ingeschat.
- Een verschil tussen bijvoorbeeld 7 en 8 is niet belangrijk.
- Baseer je uitsluitend op informatie uit de beschrijving.
- Bedenk geen eigenschappen die niet in de beschrijving staan.
- Als er te weinig informatie is om een eigenschap goed te beoordelen,
  zeg dan expliciet dat de score onzeker is.
- Leg steeds uit welke concrete informatie uit de beschrijving relevant is.
- Als de motivatie van de leerlingen goed is, zeg waarom.
- Als hun redenering niet klopt, leg kort uit waar de fout zit.
- Als een score moeilijk te verdedigen is, zeg dan of een lagere,
  gemiddelde of hogere score waarschijnlijk beter past.
- Gebruik GEEN termen zoals consciëntieusheid, altruïsme of agreeableness.
  Gebruik alleen de Nederlandstalige termen hierboven.
- Wees kritisch. Bevestig niet automatisch elke keuze.
- Houd de feedback overzichtelijk en beknopt.
- Schrijf begrijpelijk voor leerlingen van ongeveer 17 jaar.


GEEF VOOR ELK PERSONAGE DEZE STRUCTUUR:

### Naam van het personage

**Goed gezien**
Noem één of twee zaken die de leerlingen goed hebben geïnterpreteerd.

**Dit zouden we herbekijken**
Bespreek scores of redeneringen die minder goed bij de beschrijving passen.
Als alles redelijk verdedigbaar is, zeg dat.

**Tip**
Geef één concrete tip waarmee ze hun analyse kunnen verbeteren.


Hier zijn de analyses van de leerlingen:

{analyses}
"""

       with st.spinner("Jullie analyse wordt nagekeken..."):

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

st.success("Feedback klaar!")

st.markdown(response.output_text)


# --------------------------------------------------
# OVERZICHT VAN DE GEKOZEN PROFIELEN
# --------------------------------------------------

st.divider()

if st.button("📋 Toon onze vijf persoonlijkheidsprofielen"):

    st.subheader("Jullie huidige inschattingen")

    for naam, profiel in scores.items():

        st.markdown(f"### {naam}")

        st.write(
            f"Extraversie: **{profiel['Extraversie']}/10**  |  "
            f"Vriendelijkheid: **{profiel['Vriendelijkheid']}/10**  |  "
            f"Emotionele stabiliteit: **{profiel['Emotionele stabiliteit']}/10**  |  "
            f"Zorgvuldigheid: **{profiel['Zorgvuldigheid']}/10**  |  "
            f"Openheid: **{profiel['Openheid voor ervaringen']}/10**"
        )
