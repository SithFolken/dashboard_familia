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

def get_nivel_servicio(O,FAM) :
    conn = get_connection()
    cursor = conn.cursor()

    query = """CALL Analisis_Procesos.sp_consultas_revision_familias_app(%s, %s)"""
    cursor.execute(query, (O, FAM))

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    df = pd.DataFrame(rows, columns=columns)

    cursor.close()
    conn.close()

    return df

def get_nivel_inventario() :
    conn = get_connection()
    cursor = conn.cursor()

    query="""SELECT 
                pm.sku,
                pm.descripcion_producto,
                SUM(IFNULL(bp.W1,0)) as inv_proy_sem1,
                SUM(IFNULL(bp.W2,0))  as inv_proy_sem2,
                SUM(IFNULL(bp.W3,0))  as inv_proy_sem3,
                SUM(IFNULL(bp.W4,0))  as inv_proy_sem4,
                SUM(IFNULL(bp.W5,0))  as inv_proy_sem5,
                SUM(IFNULL(bp.W6,0))  as inv_proy_sem6,
                SUM(IFNULL(bp.W7,0))  as inv_proy_sem7,
                SUM(IFNULL(fc.W2,0)) as fcst_sem1,
                SUM(IFNULL(fc.W3,0)) as fcst_sem2,
                SUM(IFNULL(fc.W4,0)) as fcst_sem3,
                SUM(IFNULL(fc.W5,0)) as fcst_sem4,
                SUM(IFNULL(fc.W6,0)) as fcst_sem5,
                SUM(IFNULL(fc.W7,0)) as fcst_sem6,
                SUM(IFNULL(fc.W8,0)) as fcst_sem7,
                SUM(IFNULL(inv.saldo_disponible,0) + IF((invb.disp_bod + invb.pend_bod)=0;0;inv.saldo_pendiente) as stock_total,
                MAX(invb.disp_bod) as disp_bod,
                MAX(invb.pend_bod) as pend_bod


                FROM  sodimac_grt.productos_maestro as pm 
                INNER JOIN sodimac_grt.assorment_sku_tiendas as ass  on pm.sku = ass.sku
                LEFT JOIN relex.buying_projection as bp on ass.id_tienda = bp.destino and pm.sku = bp.sku
                LEFT JOIN relex.forecast_80_weeks_imported as fc on ass.id_tienda = fc.destino and pm.sku = fc.sku
                LEFT JOIN sodimac_grt.inventario_diario as inv on ass.id_tienda = inv.id_sucursal and pm.sku = inv.sku
                LEFT JOIN (SELECT 
                                                        inv.sku,
                                                        SUM(IFNULL(inv.saldo_disponible,0)) as disp_bod,
                                                        SUM(IFNULL(inv.saldo_pendiente,0)) as pend_bod
                                                        FROM sodimac_grt.inventario_diario as inv 
                                                        INNER JOIN sodimac_grt.bodegas as b on inv.id_sucursal = b.id_bodega and b.asigna = 1
                                                        GROUP BY inv.sku
                                                        ) as invb on pm.sku = invb.sku

                WHERE pm.id_familia = 417 and pm.id_comprador_producto not in (1,69,39,15,18)  and pm.origen = 'I'
                    
                GROUP BY pm.sku, pm.descripcion_producto"""
    
    cursor.execute(query)

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    df = pd.DataFrame(rows, columns=columns)

    cursor.close()
    conn.close()

    return df