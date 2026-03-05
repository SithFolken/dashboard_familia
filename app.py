import streamlit as st
import pandas as pd
from data_access import get_disponibilidad

st.title("Supply Dashboard")


st.title("Control Tower Supply")
st.header("Disponibilidad - Familia Muebles y Organización")

df = get_disponibilidad()

st.dataframe(df)