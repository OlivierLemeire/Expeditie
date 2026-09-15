import streamlit as st

from google import genai

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(
    page_title="Expeditie Eiland",
    page_icon="🏝️",
    layout="centered"
)

st.title("🏝️ Expeditie Eiland")
st.write(
    "Vijf jongeren vertrekken samen op expeditie. "
    "Voor je ontdekt hoe het hen vergaat, moet je eerst hun persoonlijkheid analyseren."
)

st.info(
    "Lees de beschrijving van elk personage aandachtig. "
    "Geef daarna voor elke Big Five-eigenschap een score van 1 tot 10. "
    "Er is niet altijd één exact juist antwoord: zorg vooral dat je je keuze kunt uitleggen."
)

# --------------------------------------------------
# UITLEG BIG FIVE
# --------------------------------------------------

with st.expander("🧠 Wat betekenen de Big Five?"):
    st.markdown("""
**Extraversie (tegenover introversie)**  
De mate waarin iemand nieuwe sociale contacten legt.  
**1 =** eerder introvert en minder behoefte aan sociale contacten  
**10 =** sterk extravert en legt gemakkelijk nieuwe sociale contacten

**Vriendelijkheid (tegenover afstandelijkheid)**  
De mate waarin iemand bereid is anderen te helpen en te vertrouwen.  
**1 =** eerder afstandelijk  
**10 =** sterk vriendelijk, behulpzaam en vertrouwend

**Emotionele stabiliteit (tegenover neuroticisme)**  
De mate waarin iemand goed omgaat met emotionele zaken zoals stress en problemen.  
**1 =** eerder neurotisch en gevoelig voor stress  
**10 =** emotioneel zeer stabiel

**Zorgvuldigheid (tegenover onzorgvuldigheid)**  
De mate waarin iemand georganiseerd en ordelijk is.  
**1 =** eerder chaotisch of onzorgvuldig  
**10 =** sterk georganiseerd, ordelijk en zorgvuldig

**Openheid voor ervaringen (tegenover geslotenheid voor ervaringen)**  
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

# Hier bewaren we de scores
scores = {}

# --------------------------------------------------
# SCORES LATEN INVULLEN
# --------------------------------------------------

for naam, beschrijving in personages.items():

    st.divider()
    st.header(naam)

    st.write(beschrijving)

    st.markdown("#### Jullie inschatting")

    openheid = st.slider(
        f"Openheid — {naam}",
        1, 10, 5,
        key=f"{naam}_openheid",
        help="1 = sterk gericht op het vertrouwde | 10 = zeer nieuwsgierig en open voor nieuwe ervaringen"
    )

    consci = st.slider(
        f"Consciëntieusheid — {naam}",
        1, 10, 5,
        key=f"{naam}_consci",
        help="1 = weinig georganiseerd | 10 = zeer georganiseerd, gedisciplineerd en plichtsbewust"
    )

    extra = st.slider(
        f"Extraversie — {naam}",
        1, 10, 5,
        key=f"{naam}_extra",
        help="1 = sterk introvert/teruggetrokken | 10 = zeer sociaal, actief en assertief"
    )

    altru = st.slider(
        f"Altruïsme — {naam}",
        1, 10, 5,
        key=f"{naam}_altru",
        help="1 = competitief/kritisch | 10 = zeer vriendelijk en coöperatief"
    )

    neuro = st.slider(
        f"Neuroticisme — {naam}",
        1, 10, 5,
        key=f"{naam}_neuro",
        help="1 = emotioneel zeer stabiel | 10 = zeer gevoelig voor stress en zorgen"
    )

    motivatie = st.text_area(
        f"Waarom kozen jullie deze scores voor {naam}?",
        placeholder="Verwijs naar informatie uit de beschrijving...",
        key=f"{naam}_motivatie"
    )

    scores[naam] = {
        "Openheid": openheid,
        "Consciëntieusheid": consci,
        "Extraversie": extra,
        "Altruïsme": altru,
        "Neuroticisme": neuro,
        "Motivatie": motivatie
    }
# --------------------------------------------------
# FEEDBACK OP DE ANALYSE
# --------------------------------------------------

st.divider()
st.header("🧠 Controleer jullie persoonlijkheidsanalyse")

st.write(
    "Laat jullie inschattingen controleren. "
    "Je krijgt geen exact 'juist antwoord', maar feedback over de vraag "
    "of jullie scores en argumenten goed passen bij de beschrijvingen."
)

if st.button("🔎 Controleer onze analyse"):

    ontbrekende_motivaties = [
        naam for naam, profiel in scores.items()
        if not profiel["Motivatie"].strip()
    ]

    if ontbrekende_motivaties:
        st.warning(
            "Geef eerst bij elk personage een korte motivatie. "
            "Nog niet ingevuld: " + ", ".join(ontbrekende_motivaties)
        )

    else:

        analyses = ""

        for naam, profiel in scores.items():
            analyses += f"""
PERSONAGE: {naam}

Beschrijving:
{personages[naam]}

Scores van de leerlingen:
- Openheid: {profiel['Openheid']}/10
- Consciëntieusheid: {profiel['Consciëntieusheid']}/10
- Extraversie: {profiel['Extraversie']}/10
- Altruïsme: {profiel['Altruïsme']}/10
- Neuroticisme: {profiel['Neuroticisme']}/10

Motivatie van de leerlingen:
{profiel['Motivatie']}

----------------------------
"""

        prompt = f"""
Je bent een docent gedragswetenschappen voor leerlingen van ongeveer 17 jaar.

De leerlingen leren de Big Five kennen. Ze hebben vijf fictieve personages
geanalyseerd en aan iedere Big Five-eigenschap een score van 1 tot 10 gegeven.

Geef didactische feedback op hun analyse.

BELANGRIJKE REGELS:

- Doe NIET alsof er voor een persoonlijkheidstrek één exact juist getal bestaat.
- Beoordeel vooral of de leerling de trek terecht als laag, gemiddeld of hoog inschat.
- Baseer je uitsluitend op de informatie in de karakterbeschrijving.
- Een eigenschap waarover de tekst weinig informatie geeft, moet je ook als onzeker benoemen.
- Leg steeds kort uit WELKE informatie uit de beschrijving relevant is.
- Geef ook feedback op de motivatie die de leerlingen zelf schreven.
- Als een score duidelijk moeilijk te verdedigen is, zeg welke richting
  waarschijnlijk beter past: lager, gemiddeld of hoger.
- Geef geen lange algemene uitleg over de Big Five.
- Schrijf helder en beknopt voor 17-jarige leerlingen.
- Wees kritisch: zeg niet automatisch dat elke keuze goed is.

Gebruik voor ELK personage deze structuur:

### Naam

**Wat jullie goed interpreteren**
[Korte feedback]

**Wat ik zou herbekijken**
[Korte feedback. Als er niets problematisch is, zeg dat.]

**Tip**
[Maximaal één concrete tip om de analyse te verbeteren.]

Hier zijn de analyses van de leerlingen:

{analyses}
"""

        with st.spinner("Jullie analyse wordt nagekeken..."):

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

        st.success("Feedback klaar!")
        st.markdown(response.text)
# --------------------------------------------------
# OVERZICHT
# --------------------------------------------------

st.divider()

if st.button("📋 Toon onze vijf persoonlijkheidsprofielen"):

    st.subheader("Jullie inschattingen")

    for naam, profiel in scores.items():
        st.markdown(f"### {naam}")
        st.write(
            f"Openheid: **{profiel['Openheid']}/10**  |  "
            f"Consciëntieusheid: **{profiel['Consciëntieusheid']}/10**  |  "
            f"Extraversie: **{profiel['Extraversie']}/10**  |  "
            f"Altruïsme: **{profiel['Altruïsme']}/10**  |  "
            f"Neuroticisme: **{profiel['Neuroticisme']}/10**"
        )
