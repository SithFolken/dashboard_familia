import plotly.express as px

def grafico_disponibilidad(df, titulo):

    anio_actual = df["ano"].max()
    df_actual = df[df["ano"] == anio_actual]

    ultima_fila = df_actual.loc[df_actual["semana"].idxmax()]

    fig = px.line(
        df,
        x="semana",
        y=["porcIyII", "porcTotal"],
        markers=True,
        title=titulo
    )

    fig.add_annotation(
        x=ultima_fila["semana"],
        y=ultima_fila["porcIyII"],
        text=f'{ultima_fila["porcIyII"]*100:.1f}%'
    )

    fig.add_annotation(
        x=ultima_fila["semana"],
        y=ultima_fila["porcTotal"],
        text=f'{ultima_fila["porcTotal"]*100:.1f}%'
    )

    fig.update_yaxes(range=[0.85,1])

    return fig