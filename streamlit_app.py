import streamlit as st

st.title("🏝️ Expeditie Eiland")

st.write(
    "Jullie zijn zes maanden gestrand op een onbewoond eiland. "
    "Kunnen jullie een groep samenstellen die goed blijft functioneren?"
)

st.subheader("Persoon 1")

naam = st.text_input("Naam")

openheid = st.slider("Openheid", 1, 10, 5)
consci = st.slider("Consciëntieusheid", 1, 10, 5)
extraversie = st.slider("Extraversie", 1, 10, 5)
altruisme = st.slider("Altruïsme", 1, 10, 5)
neuroticisme = st.slider("Neuroticisme", 1, 10, 5)

if st.button("Toon persoonlijkheid"):
    st.write(f"### {naam}")
    st.write(f"Openheid: {openheid}/10")
    st.write(f"Consciëntieusheid: {consci}/10")
    st.write(f"Extraversie: {extraversie}/10")
    st.write(f"Altruïsme: {altruisme}/10")
    st.write(f"Neuroticisme: {neuroticisme}/10")
