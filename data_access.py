import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return conexion
# define("SERVER","ciclope.sodimac.cl");
# define("USUARIO","ajperez");
# define("PASSWORD","W?K=r4mww");
# define("BD","rct");

#consultas a la BD 

def get_disponibilidad() :

    conn = get_connection()
    cursor = conn.cursor()

    query = """ CALL Analisis_Procesos.sp_dashboard_python() """
    cursor.execute(query)

    columns = [col[0] for col in cursor.description]
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=columns)
    
    cursor.close()
    conn.close()

    return df