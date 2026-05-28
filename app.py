import streamlit as st
from database import stats_totales, stats_magnex

st.set_page_config(page_title="MAGNEX INTERNATIONAL", page_icon="⚡", layout="wide")

st.title("⚡ MAGNEX INTERNATIONAL")
st.caption("Connecting Markets. Delivering Trust.")
st.divider()

col1, col2, col3, col4 = st.columns(4)

stats_m = stats_magnex()
stats_f = stats_totales()

col1.metric("Cotizaciones MAGNEX", stats_m["total_cot"])
col2.metric("Comisiones Estimadas", f"${stats_m['total_comisiones'] or 0:,.2f}")
col3.metric("Cotizaciones Furniture", stats_f["total_cot"])
col4.metric("Facturado Furniture", f"${stats_f['total_ventas'] or 0:,.2f}")

st.divider()
st.subheader("Módulos disponibles")

c1, c2, c3, c4 = st.columns(4)
c1.page_link("pages/1_MAGNEX_B2B.py",       label="🏭 MAGNEX B2B",          icon="⚡")
c2.page_link("pages/2_Furniture_Cleans.py",  label="🧼 Furniture Cleans",    icon="🧼")
c3.page_link("pages/3_CRM_Leads.py",         label="📇 CRM / Leads Apollo",  icon="📇")
c4.page_link("pages/4_Automatizacion.py",    label="📧 Automatización Email", icon="📧")
