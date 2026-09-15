import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🏝️ Expeditie Eiland")

st.write(
    "Jullie zijn zes maanden gestrand op een onbewoond eiland. "
    "Pas de persoonlijkheid aan en ontdek hoe de groep functioneert."
)

st.subheader("Persoon 1")

naam = st.text_input("Naam", value="Alex")

openheid = st.slider("Openheid", 1, 10, 5)
consci = st.slider("Consciëntieusheid", 1, 10, 5)
extraversie = st.slider("Extraversie", 1, 10, 5)
altruisme = st.slider("Altruïsme", 1, 10, 5)
neuroticisme = st.slider("Neuroticisme", 1, 10, 5)

if st.button("🏝️ Simuleer 6 maanden"):

    prompt = f"""
Je bent een simulator voor een les gedragswetenschappen.

Een jongere strandt gedurende zes maanden op een onbewoond eiland.

Persoonlijkheidsprofiel volgens de Big Five:
- Naam: {naam}
- Openheid: {openheid}/10
- Consciëntieusheid: {consci}/10
- Extraversie: {extraversie}/10
- Altruïsme: {altruisme}/10
- Neuroticisme: {neuroticisme}/10

Beschrijf kort hoe deze persoon waarschijnlijk zou functioneren.

Bespreek:
1. Sterktes op het eiland
2. Mogelijke problemen
3. Gedrag onder stress
4. Hoe goed deze persoon zich waarschijnlijk aanpast

Behandel persoonlijkheid niet deterministisch:
een eigenschap maakt gedrag waarschijnlijker, maar bepaalt het niet volledig.

Schrijf begrijpelijk voor leerlingen van ongeveer 17 jaar.
"""

    with st.spinner("De expeditie wordt gesimuleerd..."):
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

    st.subheader("Resultaat")
    st.write(response.output_text)
