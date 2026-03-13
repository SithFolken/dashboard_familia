import streamlit as st
import pandas as pd
import plotly.express as px

from data_access import get_disponibilidad, get_nivel_servicio, get_nivel_inventario
from charts import grafico_disponibilidad


# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Disponibilidad",
    layout="wide"
)

# TÍTULO
st.title("Disponibilidad - Familia Muebles y Organización")

# Cargar Datos

@st.cache_data
def cargar_datos():
    df = get_disponibilidad()
    return df

df = cargar_datos()

@st.cache_data
def cargar_inventario():
    return get_nivel_inventario()

df_inv = cargar_inventario()

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

familia = st.sidebar.number_input(
    "Ingrese ID Familia",
    min_value=1,
    step=1
)

# ---------------- DISPONIBILIDAD SEMANAL ----------------
def grafico_disponibilidad(df, titulo):

    import datetime

    semana_actual = datetime.date.today().isocalendar()[1]
    anio_actual = datetime.date.today().year

    # convertir formato largo
    df_long = df.melt(
        id_vars=["ano","semana"],
        value_vars=["porcIyII","porcTotal"],
        var_name="tipo",
        value_name="disponibilidad"
    )

    df_long["tipo"] = df_long["tipo"].replace({
        "porcIyII": "NS 1 y 2",
        "porcTotal": "NS Total"
    })

    df_long["serie"] = df_long["ano"].astype(str) + " - " + df_long["tipo"]

    fig = px.line(
        df_long,
        x="semana",
        y="disponibilidad",
        color="serie",
        markers=True,
        title=titulo
    )

    # línea meta
    fig.add_hline(
        y=0.95,
        line_dash="dash",
        line_color="red",
        annotation_text="Meta 95%"
    )

    # línea semana actual
    fig.add_vline(
        x=semana_actual,
        line_dash="dot",
        line_color="yellow"
    )

    # buscar datos semana actual año actual
    df_semana = df_long[
        (df_long["semana"] == semana_actual) &
        (df_long["ano"] == anio_actual)
    ]

    # agregar etiqueta
    if not df_semana.empty:
        for _, row in df_semana.iterrows():

            fig.add_annotation(
                x=row["semana"],
                y=row["disponibilidad"],
                text=f"{row['disponibilidad']:.1%}",
                showarrow=True,
                arrowhead=2,
                bgcolor="white"
            )

    # mover leyenda abajo horizontal
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.30,
            xanchor="center",
            x=0.5
        )
    )

    return fig


dfN1 = get_nivel_servicio(1,familia)
dfNI = get_nivel_servicio(2,familia)
dfNN = get_nivel_servicio(3,familia)

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

    estado_fcst = df["estado_fcst"].value_counts().reset_index()
    estado_fcst.columns = ["estado_fcst", "cantidad"]

    colores = {
    "FCST OK": "green",
    "FCST ALTO": "orange",
    "FCST BAJO": "red"
    }

    fig = px.bar(
    estado_fcst,
    x="estado_fcst",
    y="cantidad",
    color="estado_fcst",
    color_discrete_map=colores,
    title="Estado Forecast"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("Disponibilidad promedio SDS por tienda")

    # Agrupar SDS promedio por tienda
    disp_tienda = (
        df.groupby("id_tienda")["disponibilidad_fcst"]
        .mean()
        .reset_index()
    )

    # ordenar
    disp_tienda = disp_tienda.sort_values("disponibilidad_fcst")

    # convertir a texto para evitar espacios
    disp_tienda["id_tienda"] = disp_tienda["id_tienda"].astype(str)

    # gráfico
    fig = px.bar(
        disp_tienda,
        y="id_tienda",
        x="disponibilidad_fcst",
        orientation="h",
        text_auto=True,
        title="Disponibilidad promedio SDS por tienda"
    )

    # eje categórico (esto elimina los espacios)
    fig.update_yaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)

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


# ---------------- ANALISIS INVENTARIO----------------

df_inv["posicion_inventario"] = (
    df_inv["stock_total"]
    + df_inv["disp_bod"]
    + df_inv["pend_bod"]
)

df_inv["demanda_7w"] = (
    df_inv["fcst_sem1"] +
    df_inv["fcst_sem2"] +
    df_inv["fcst_sem3"] +
    df_inv["fcst_sem4"] +
    df_inv["fcst_sem5"] +
    df_inv["fcst_sem6"] +
    df_inv["fcst_sem7"]
)

df_inv["inventario_post_7w"] = (
    df_inv["posicion_inventario"]
    + df_inv["inv_proy_sem1"]
    + df_inv["inv_proy_sem2"]
    + df_inv["inv_proy_sem3"]
    + df_inv["inv_proy_sem4"]
    + df_inv["inv_proy_sem5"]
    + df_inv["inv_proy_sem6"]
    + df_inv["inv_proy_sem7"]
    - df_inv["demanda_7w"]
)

df_inv["compras_7w"] = (
    df_inv["inv_proy_sem1"] +
    df_inv["inv_proy_sem2"] +
    df_inv["inv_proy_sem3"] +
    df_inv["inv_proy_sem4"] +
    df_inv["inv_proy_sem5"] +
    df_inv["inv_proy_sem6"] +
    df_inv["inv_proy_sem7"]
)

st.subheader("Inventario proyectado después de 7 semanas")

fig = px.histogram(
    df_inv,
    x="inventario_post_7w",
    nbins=40,
    title="Distribución inventario proyectado"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

fig = px.scatter(
    df_inv.sample(min(len(df_inv),3000)),
    x="demanda_7w",
    y="compras_7w",
    size="stock_total",
    hover_data=[
        "sku",
        "descripcion_producto",
        "stock_total",
        "disp_bod",
        "pend_bod"
    ],
    title="Compras vs Demanda futura (tamaño = inventario)"
)

st.plotly_chart(fig, use_container_width=True)


quiebre = df_inv[df_inv["inventario_post_7w"] < 0]

st.subheader("SKU con quiebre proyectado")

st.dataframe(
    quiebre.sort_values("inventario_post_7w").head(20)[[
        "sku",
        "descripcion_producto",
        "stock_total",
        "disp_bod",
        "pend_bod",
        "inventario_post_7w"
    ]],
    use_container_width=True
)

riesgo = df_inv.sort_values("inventario_post_7w").head(15)

riesgo["sku"] = riesgo["sku"].astype(str)

fig = px.bar(
    riesgo,
    x="inventario_post_7w",
    y="sku",
    orientation="h",
    color="inventario_post_7w",
    hover_data=["descripcion_producto"],
    title="Top SKU con mayor riesgo de quiebre"
)

fig.update_layout(
    yaxis={'categoryorder':'total ascending'}
)

st.plotly_chart(fig, use_container_width=True)