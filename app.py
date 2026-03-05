import streamlit as st
import pandas as pd

st.title("Supply Dashboard")

data = {
    "Familia": ["Bebidas", "Snacks", "Galletas"],
    "Disponibilidad": [95, 88, 92]
}

df = pd.DataFrame(data)

st.dataframe(df)
st.bar_chart(df.set_index("Familia"))