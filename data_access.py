import mysql.connector
import pandas as pd

def get_connection():

    conexion = mysql.connector.connect(
        host ="ciclope.sodimac.cl",
        user ="ajperez",
        password = "W?K=r4mww",
        database = "sodimac_grt"
    )

    return conexion

# define("SERVER","ciclope.sodimac.cl");
# define("USUARIO","ajperez");
# define("PASSWORD","W?K=r4mww");
# define("BD","rct");

#consultas a la BD 

def get_disponibilidad() :

    conn = get_connection()

    query = """SELECT 
                vta.id_tienda,
                pm.sku,
                pm.descripcion_producto,
                pm.id_familia,
                pm.id_sub_familia,
                (GREATEST(inv.saldo_disponible,0) + inv.saldo_pendiente) as stock_total,
                comp.fcst1 as fcst,
                comp.lead_time,
                ROUND((GREATEST(inv.saldo_disponible,0) + inv.saldo_pendiente) / comp.fcst1,2) as disponibilidad_fcst,
                ROUND(((GREATEST(inv.saldo_disponible,0) + inv.saldo_pendiente) /(comp.fcst1 / 7 *comp.lead_time)) * 100,2) as disp_lt,
                ass.assorment

                FROM sodimac_grt.productos_maestro as pm 

                LEFT JOIN sodimac_grt.ventas_detalle_semanal_L6W as vta  on pm.sku = vta.sku
                LEFT JOIN relex.comparativo_RO as comp on  vta.id_tienda = comp.id_tienda and pm.sku = comp.sku
                LEFT JOIN sodimac_grt.assorment_sku_tiendas_no as ass on vta.id_tienda = ass.id_tienda and pm.sku = ass.sku
                LEFT JOIN sodimac_grt.MID_sku_tiendas as mid on vta.id_tienda = mid.id_tienda and pm.sku = mid.sku
                LEFT JOIN sodimac_grt.MAEMED as mae on  pm.sku = mae.SKU


                LEFT JOIN (SELECT 
                                                            inv.sku,
                                                            SUM(inv.saldo_disponible) as disp_bod,
                                                            SUM(inv.saldo_pendiente) as pend_bod
                                                        FROM sodimac_grt.inventario_diario as inv 
                                                        INNER JOIN sodimac_grt.bodegas as b on inv.id_sucursal = b.id_bodega and b.asigna = 1
                                                        GROUP BY 
                                                        inv.sku) as invb on pm.sku = invb.sku
                LEFT JOIN sodimac_grt.inventario_diario as inv on vta.id_tienda = inv.id_sucursal and pm.sku = inv.sku

                WHERE pm.id_familia = 417 and pm.id_comprador_producto not in (1,69,39,15,18) and ass.assorment = 'SI'
    """
    df = pd.read_sql(query,conn)
    conn.close()

    return df