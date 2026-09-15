import streamlit as st

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
**Openheid**  
Hoe sterk iemand openstaat voor nieuwe ervaringen, ideeën en manieren van denken.  
**1 =** houdt sterk van het vertrouwde en bekende  
**10 =** zeer nieuwsgierig, creatief en experimenteel

**Consciëntieusheid**  
Hoe georganiseerd, verantwoordelijk en doelgericht iemand is.  
**1 =** spontaan, weinig georganiseerd  
**10 =** zeer planmatig, gedisciplineerd en plichtsbewust

**Extraversie**  
Hoe sterk iemand sociale interactie, activiteit en prikkels opzoekt.  
**1 =** eerder stil en teruggetrokken  
**10 =** zeer sociaal, energiek en assertief

**Altruïsme / vriendelijkheid**  
Hoe sterk iemand gericht is op samenwerking en rekening houdt met anderen.  
**1 =** eerder competitief, kritisch of wantrouwig  
**10 =** zeer vriendelijk, behulpzaam en coöperatief

**Neuroticisme**  
Hoe gevoelig iemand is voor stress, zorgen en negatieve emoties.  
**1 =** emotioneel stabiel en rustig  
**10 =** snel gespannen, bezorgd of emotioneel van slag
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
