import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

from data_access import get_disponibilidad,get_nivel_servicio


#falta agregar
    #distribucion de inventario por subfamilia.
    #primeros 20 sku tip 1 y 2 de la categoria.

# Layout ancho
st.set_page_config(layout="wide")

st.title("Disponibilidad - Familia Muebles y Organización")

df = get_disponibilidad()

# ---------------- KPI ----------------

disponibilidad = df["disponibilidad_fcst"].mean()
riesgo = (df["alerta_abastecimiento"] == "RIESGO QUIEBRE").mean()*100
fcst_error = (df["obs_fcst"] != "FCST OK").mean()*100
cobertura = df["sem_cobertura"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Disponibilidad promedio", round(disponibilidad,2))
col2.metric("% Riesgo quiebre", round(riesgo,2))
col3.metric("% Forecast incorrecto", round(fcst_error,2))
col4.metric("Cobertura semanas", round(cobertura,2))

st.divider()


# ---------------- DISPONIBILIDAD SEMANAL ----------------
dfN1 = get_nivel_servicio(1,417)
dfNI = get_nivel_servicio(2,417)
dfNN = get_nivel_servicio(3,417)

col1 , col2, col3 = st.columns(3)

with col1:

    st.subheader("Disponibilidad Total por Semana")

    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(6,3))

    sns.lineplot(data=dfN1, x="semana", y="porcIyII", label="NS 1 y 2", ax=ax)
    sns.lineplot(data=dfN1, x="semana", y="porcTotal", label="NS Total", ax=ax)

    # obtener año actual
    anio_actual = dfN1["ano"].max()

    df_actual = dfN1[dfN1["ano"] == anio_actual]

    # obtener última semana
    ultima_fila = df_actual.loc[df_actual["semana"].idxmax()]

    # mostrar solo ese valor
    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcIyII"],
        f'{ultima_fila["porcIyII"]*100:.1f}%',
        fontsize=9
    )

    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcTotal"],
        f'{ultima_fila["porcTotal"]*100:.1f}%',
        fontsize=9
    )

    ax.set_ylim(0.85,1)
    ax.grid(True)

    st.pyplot(fig)

with col2:
    st.subheader("Disponibilidad Importado")

    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(6,3))

    sns.lineplot(data=dfNI, x="semana", y="porcIyII", label="NS 1 y 2", ax=ax)
    sns.lineplot(data=dfNI, x="semana", y="porcTotal", label="NS Total", ax=ax)

    # obtener año actual
    anio_actual = dfNI["ano"].max()

    df_actual = dfNI[dfNI["ano"] == anio_actual]

    # obtener última semana
    ultima_fila = df_actual.loc[df_actual["semana"].idxmax()]

    # mostrar solo ese valor
    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcIyII"],
        f'{ultima_fila["porcIyII"]*100:.1f}%',
        fontsize=9
    )

    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcTotal"],
        f'{ultima_fila["porcTotal"]*100:.1f}%',
        fontsize=9
    )

    ax.set_ylim(0.85,1)
    ax.grid(True)

    st.pyplot(fig)

with col3:
    st.subheader("Disponibilidad Nacional")

    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(6,3))

    sns.lineplot(data=dfNN, x="semana", y="porcIyII", label="NS 1 y 2", ax=ax)
    sns.lineplot(data=dfNN, x="semana", y="porcTotal", label="NS Total", ax=ax)

    # obtener año actual
    anio_actual = dfNN["ano"].max()

    df_actual = dfNN[dfNN["ano"] == anio_actual]

    # obtener última semana
    ultima_fila = df_actual.loc[df_actual["semana"].idxmax()]

    # mostrar solo ese valor
    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcIyII"],
        f'{ultima_fila["porcIyII"]*100:.1f}%',
        fontsize=9
    )

    ax.text(
        ultima_fila["semana"],
        ultima_fila["porcTotal"],
        f'{ultima_fila["porcTotal"]*100:.1f}%',
        fontsize=9
    )

    ax.set_ylim(0.85,1)
    ax.grid(True)

    st.pyplot(fig)

st.divider()

# ---------------- ANALISIS GENERAL ----------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Forecast")
    st.bar_chart(df["obs_fcst"].value_counts())

with col2:
    st.subheader("Disponibilidad promedio por tienda")
    disp_tienda = df.groupby("id_tienda")["disponibilidad_fcst"].mean()
    st.bar_chart(disp_tienda)

st.divider()

# ---------------- ANALISIS DEMANDA ----------------

col3, col4 = st.columns(2)

with col3:

    st.subheader("Forecast vs Ventas")

    fig = px.scatter(
        df,
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

# ---------------- ALERTAS ----------------

st.subheader("Alertas de abastecimiento")

alertas = df[df["alerta_abastecimiento"] != "OK"]

st.dataframe(
    alertas,
    use_container_width=True
)

st.divider()

# ---------------- SKU CRITICOS ----------------

st.subheader("SKUs con Alerta de Reposicion")

problemas = df[
    (df["alerta_abastecimiento"] == "RIESGO QUIEBRE") |
    (df["obs_fcst"] != "FCST OK")
]

problemas = problemas.sort_values("PV6", ascending=False)

st.dataframe(
    problemas[[
        "id_tienda",
        "sku",
        "descripcion_producto",
        "stock_total",
        "fcst",
        "PV6",
        "sem_cobertura",
        "obs_fcst",
        "alerta_abastecimiento"
    ]],
    use_container_width=True
)

st.subheader("Top 20 SKUs más críticos por venta")

st.dataframe(
    problemas.nlargest(20, "PV6"),
    use_container_width=True
)