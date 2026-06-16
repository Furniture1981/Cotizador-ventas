import streamlit as st
import pandas as pd
import io
from database import guardar_lead, obtener_leads, stats_leads

st.set_page_config(page_title="CRM Leads", page_icon="📇", layout="wide")
st.title("📇 CRM — Leads & Seguimiento")
st.caption("Fuente principal: Apollo.io | Pipeline MAGNEX INTERNATIONAL")

stats = stats_leads()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", stats["total"])
c2.metric("Nuevos",      stats["por_estado"].get("nuevo", 0))
c3.metric("Contactados", stats["por_estado"].get("contactado", 0))
c4.metric("Emails enviados", stats["emails"])

st.divider()
tab_pipeline, tab_import, tab_add = st.tabs(["📋 Pipeline", "📥 Importar Apollo CSV", "➕ Agregar Manual"])

ESTADOS  = ["nuevo","contactado","respondio","interesado","negociando","cerrado","descartado"]
PRODUCTOS = ["Pintura Industrial","Aceite de Palma","Fertilizantes","Acero Estructural","Furniture Cleans"]
PAISES    = ["Panamá","Costa Rica","Colombia","Guatemala","República Dominicana",
             "Honduras","El Salvador","México","Ecuador","Perú","Chile","Otro"]

# ── PIPELINE ─────────────────────────────────────────────────────────────────
with tab_pipeline:
    from database import actualizar_estado_lead
    col1, col2 = st.columns(2)
    filtro_estado = col1.selectbox("Estado", ["todos"] + ESTADOS)
    filtro_prod   = col2.selectbox("Producto", ["todos"] + PRODUCTOS)

    leads = obtener_leads(None if filtro_estado == "todos" else filtro_estado)
    if filtro_prod != "todos":
        leads = [l for l in leads if l["producto"] == filtro_prod]

    if not leads:
        st.info("Sin leads con ese filtro.")
    else:
        for lead in leads:
            with st.expander(
                f"**{lead['empresa']}** — {lead['nombre']} | {lead['producto']} | "
                f"🟢 {lead['estado'].upper()}"
            ):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.write(f"📧 {lead['email']} | 🌎 {lead['pais']} | 💼 {lead['cargo']}")
                    if lead["notas"]:
                        st.caption(f"Notas: {lead['notas']}")
                    st.caption(f"Fuente: {lead['fuente']} — {lead['fecha']}")
                with cb:
                    nuevo = st.selectbox("Estado", ESTADOS,
                                         index=ESTADOS.index(lead["estado"]),
                                         key=f"est_{lead['id']}")
                    if st.button("Guardar", key=f"upd_{lead['id']}"):
                        actualizar_estado_lead(lead["id"], nuevo)
                        st.rerun()

    leads_all = obtener_leads(limit=1000)
    if leads_all:
        df_exp = pd.DataFrame(leads_all)[["fecha","nombre","empresa","cargo",
                                           "email","pais","producto","estado","fuente"]]
        df_exp.columns = ["Fecha","Nombre","Empresa","Cargo","Email","País","Producto","Estado","Fuente"]
        st.download_button("⬇️ Exportar CSV", df_exp.to_csv(index=False).encode(),
                           "leads_magnex.csv", "text/csv")

# ── IMPORTAR CSV DE APOLLO ────────────────────────────────────────────────────
with tab_import:
    st.subheader("Importar leads desde Apollo.io")
    st.info(
        "En Apollo.io → Contacts → selecciona todos → Export CSV. "
        "Sube el archivo aquí y lo importamos al CRM automáticamente."
    )

    archivo = st.file_uploader("Sube el CSV de Apollo", type=["csv"])
    producto_default = st.selectbox("Producto asignado a estos leads", PRODUCTOS,
                                     key="prod_import")

    if archivo:
        try:
            df_raw = pd.read_csv(archivo)
            st.write(f"**{len(df_raw)} filas detectadas.** Columnas encontradas:")
            st.write(list(df_raw.columns))

            # Mapeo flexible de columnas de Apollo
            col_map = {
                "nombre":  next((c for c in df_raw.columns if any(
                    k in c.lower() for k in ["first name","nombre","name"])), None),
                "apellido": next((c for c in df_raw.columns if "last" in c.lower()), None),
                "empresa": next((c for c in df_raw.columns if any(
                    k in c.lower() for k in ["company","empresa","organization"])), None),
                "cargo":   next((c for c in df_raw.columns if any(
                    k in c.lower() for k in ["title","cargo","job","position"])), None),
                "email":   next((c for c in df_raw.columns if "email" in c.lower()), None),
                "pais":    next((c for c in df_raw.columns if any(
                    k in c.lower() for k in ["country","país","pais"])), None),
            }
            st.write("**Mapeo detectado:**", {k: v for k, v in col_map.items() if v})

            if not col_map["email"]:
                st.error("No se encontró columna de Email. Verifica el CSV.")
            else:
                preview = df_raw.head(5)
                st.dataframe(preview, use_container_width=True)

                if st.button("🚀 Importar al CRM", type="primary"):
                    importados = 0
                    errores = 0
                    for _, row in df_raw.iterrows():
                        try:
                            nombre_v = ""
                            if col_map["nombre"]:
                                nombre_v = str(row[col_map["nombre"]])
                                if col_map["apellido"]:
                                    nombre_v += f" {row[col_map['apellido']]}"
                            guardar_lead(
                                nombre  = nombre_v.strip(),
                                empresa = str(row[col_map["empresa"]]) if col_map["empresa"] else "",
                                cargo   = str(row[col_map["cargo"]])   if col_map["cargo"]   else "",
                                email   = str(row[col_map["email"]]),
                                pais    = str(row[col_map["pais"]])    if col_map["pais"]    else "Desconocido",
                                producto= producto_default,
                                fuente  = "Apollo",
                            )
                            importados += 1
                        except Exception:
                            errores += 1
                    st.success(f"✅ {importados} leads importados | {errores} errores")
                    st.rerun()
        except Exception as e:
            st.error(f"Error al leer el CSV: {e}")

# ── AGREGAR MANUAL ────────────────────────────────────────────────────────────
with tab_add:
    with st.form("form_lead"):
        c1, c2 = st.columns(2)
        nombre_l  = c1.text_input("Nombre")
        empresa_l = c2.text_input("Empresa")
        cargo_l   = c1.text_input("Cargo")
        email_l   = c2.text_input("Email")
        pais_l    = c1.selectbox("País", PAISES)
        prod_l    = c2.selectbox("Producto", PRODUCTOS)
        fuente_l  = c1.selectbox("Fuente", ["Apollo","LinkedIn","Referido","Web","Otro"])
        notas_l   = st.text_area("Notas", height=80)
        if st.form_submit_button("Guardar Lead", type="primary"):
            if not email_l:
                st.error("El email es obligatorio.")
            else:
                guardar_lead(nombre_l, empresa_l, cargo_l, email_l,
                             pais_l, prod_l, fuente_l, notas_l)
                st.success(f"✅ Lead guardado")
                st.rerun()
