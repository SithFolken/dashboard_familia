import streamlit as st
import pandas as pd
import plotly.express as px

from data_access import get_disponibilidad, get_nivel_servicio
from charts import grafico_disponibilidad


# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Disponibilidad",
    layout="wide"
)

# TÍTULO
st.title("Disponibilidad - Familia Muebles y Organización")

# CArgar Datos

@st.cache_data
def cargar_datos():
    df = get_disponibilidad()
    return df

df = cargar_datos()

# ---------------- CALCULO ERROR FORECAST ----------------

df["ratio_fcst"] = df["fcst"] / (df["PV6"] + 0.01)

df["estado_fcst"] = "FCST OK"

df.loc[df["ratio_fcst"] > 1.3, "estado_fcst"] = "FCST ALTO"
df.loc[df["ratio_fcst"] < 0.3, "estado_fcst"] = "FCST BAJO"

# ignorar ventas pequeñas (ruido)
df.loc[df["PV6"] < 5, "estado_fcst"] = "FCST OK"

# ---------------- KPI ----------------

@st.cache_data
def calcular_kpis(df):

    disponibilidad = df["disponibilidad_fcst"].mean()

    riesgo = (
        (df["alerta_abastecimiento"] == "RIESGO QUIEBRE")
        .mean() * 100
    )

    fcst_error = (
        (df["estado_fcst"] != "FCST OK")
        .mean() * 100
    )

    cobertura = df["sem_cobertura"].mean()

    return disponibilidad, riesgo, fcst_error, cobertura


disponibilidad, riesgo, fcst_error, cobertura = calcular_kpis(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Disponibilidad promedio",
    f"{disponibilidad:.2f}"
)

col2.metric(
    "% Riesgo quiebre",
    f"{riesgo:.2f}%"
)

col3.metric(
    "% Forecast incorrecto",
    f"{fcst_error:.2f}%"
)

col4.metric(
    "Cobertura semanas",
    f"{cobertura:.2f}"
)

st.divider()


# ---------------- DISPONIBILIDAD SEMANAL ----------------
dfN1 = get_nivel_servicio(1,417)
dfNI = get_nivel_servicio(2,417)
dfNN = get_nivel_servicio(3,417)

col1 , col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(
        grafico_disponibilidad(dfN1, "Disponibilidad Total por Semana"),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        grafico_disponibilidad(dfNI, "Disponibilidad Importado"),
        use_container_width=True
    )

with col3:
    st.plotly_chart(
        grafico_disponibilidad(dfNN, "Disponibilidad Nacional"),
        use_container_width=True
    )

st.divider()
# ---------------- ANALISIS GENERAL ----------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Estado Forecast")

    estado_fcst = df["estado_fcst"].value_counts()

    st.bar_chart(estado_fcst)

with col2:

    st.subheader("Disponibilidad promedio por tienda")

    disp_tienda = df.groupby("id_tienda")["disponibilidad_fcst"].mean()

    st.bar_chart(disp_tienda)


st.divider()

#-------------------- ANALISIS DEMANDA -----------------
col3, col4 = st.columns(2)

with col3:

    st.subheader("Forecast vs Ventas")

    sample_df = df.sample(min(len(df), 3000), random_state=1)

    fig = px.scatter(
        sample_df,
        x="fcst",
        y="PV6",
        color="alerta_abastecimiento",
        hover_data=["sku","id_tienda"]
    )

    st.plotly_chart(fig, use_container_width=True)


with col4:

    st.subheader("Cobertura en semanas")

    fig_hist = px.histogram(
        df,
        x="sem_cobertura",
        nbins=30
    )

    st.plotly_chart(fig_hist, use_container_width=True)


st.divider()

# --------------------------- ALERTAS ABASTECIMIENTO -----------------------

st.subheader("Alertas de abastecimiento")

alertas = df[df["alerta_abastecimiento"] != "OK"]

st.dataframe(
    alertas,
    use_container_width=True
)


st.divider()

st.subheader("SKUs con Alerta de Reposición")

problemas = df[
    (df["alerta_abastecimiento"] == "RIESGO QUIEBRE") &
    (df["obs_fcst"] != "FCST OK")
]

problemas = problemas.sort_values("PV6", ascending=False)

st.dataframe(
    problemas[
        [
            "id_tienda",
            "sku",
            "descripcion_producto",
            "stock_total",
            "fcst",
            "PV6",
            "sem_cobertura",
            "obs_fcst",
            "alerta_abastecimiento"
        ]
    ],
    use_container_width=True
)

st.subheader("Top 20 SKUs más críticos por venta")

st.dataframe(
    problemas.head(20),
    use_container_width=True
)


# ---------------- ANALISIS FCST POR SKU ----------------

fcst_error_sku = df[df["estado_fcst"] != "FCST OK"]

ranking_sku = (
    fcst_error_sku
    .groupby(["sku","descripcion_producto","estado_fcst"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

ranking_sku["total_problemas"] = (
    ranking_sku.get("FCST ALTO",0) +
    ranking_sku.get("FCST BAJO",0)
)

ranking_sku = ranking_sku.sort_values(
    "total_problemas",
    ascending=False
)

st.subheader("Top SKU con mayor problema de Forecast")

st.dataframe(
    ranking_sku.head(20),
    use_container_width=True
)

top_sku = ranking_sku.head(15)


st.divider()

col5, col6 = st.columns(2)




with col5:
    
    top_alto = ranking_sku.sort_values("FCST ALTO", ascending=False).head(10)
    top_alto["sku"] = top_alto["sku"].astype(str)

    fig = px.bar(
    top_alto,
    x="FCST ALTO",
    y="sku",
    orientation="h",
    title="Top SKU Forecast demasiado alto"
    )

    st.plotly_chart(fig, use_container_width=True)

with col6:
    top_bajo = ranking_sku.sort_values("FCST BAJO", ascending=False).head(10)
    top_bajo["sku"] = top_bajo["sku"].astype(str)

    fig = px.bar(
    top_bajo,
    x="FCST BAJO",
    y="sku",
    orientation="h",
    title="Top SKU Forecast demasiado bajo"
    )

    st.plotly_chart(fig, use_container_width=True)