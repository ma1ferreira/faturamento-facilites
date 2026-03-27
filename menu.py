import streamlit as st

st.set_page_config(page_title="Faturamento Facilities", layout="wide", initial_sidebar_state="collapsed")

st.title("Faturamento Facilities - GrupoSC")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚗 Frota", use_container_width=True):
        st.switch_page("pages/frota.py")

with col2:
    if st.button("📦 Correios", use_container_width=True):
        st.switch_page("pages/correios.py")

with col3:
    if st.button("✈️ Viagens", use_container_width=True):
        st.switch_page("pages/viagens.py")