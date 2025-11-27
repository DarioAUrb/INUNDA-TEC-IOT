from fastapi import APIRouter, HTTPException, Query  
from config.db import conn  
from models.user import users  
from schemas.user import Lectura_Sensores 
from datetime import datetime, timedelta  
from sqlalchemy import desc  
import logging  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user = APIRouter()


# Función auxiliar para convertir una fecha en string a objeto datetime
def parse_fecha(fecha_str: str) -> datetime:
    try:
        # Intenta convertir la fecha en formato 'YYYY-MM-DD'
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except ValueError:
        # Si el formato es incorrecto, se lanza un error HTTP 400
        raise HTTPException(
            status_code=400, 
            detail="Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-01-15)"
        )


# Función para validar que el rango de fechas tenga sentido
def validar_rango_fechas(fecha_inicio: str, fecha_fin: str) -> tuple:
    inicio = parse_fecha(fecha_inicio)  # Convierte fecha_inicio
    fin = parse_fecha(fecha_fin)        # Convierte fecha_fin
    
    if inicio > fin:
        # Si la fecha inicial es mayor a la final, lanza un error HTTP 400
        raise HTTPException(
            status_code=400,
            detail="fecha_inicio no puede ser mayor que fecha_fin"
        )
    
    # Se agrega 1 día a la fecha final para incluir todo el día en la consulta
    fin = fin + timedelta(days=1)
    return inicio, fin


# Ruta POST para insertar datos de sensores en la base de datos
@user.post("/users")
def createSensorData(data: Lectura_Sensores):
    try:
        # Prepara los datos para insertarlos
        new_data = {
            "nivel_agua_cm": data.nivel_agua_cm,
            "temperatura_c": data.temperatura_c,
            "humedad_porcentaje": data.humedad_porcentaje
        }
        
        # Inserta los datos en la tabla users
        result = conn.execute(users.insert().values(new_data))
        conn.commit()  # Confirma la transacción
        
        logger.info(f"Datos insertados correctamente. ID: {result.inserted_primary_key}")
        
        return {
            "status": "success",
            "message": "Datos recibidos correctamente"
        }
    
    except Exception as e:
        # Si ocurre un error, se revierte la transacción
        conn.rollback()
        logger.error(f"Error al insertar datos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar los datos: {str(e)}"
        )


# Ruta GET para obtener los datos de sensores con paginación y filtro por fechas
@user.get("/users")
def get_users(
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    offset: int = Query(0, ge=0, description="Desplazamiento desde el inicio"),
    fecha_inicio: str = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha final (YYYY-MM-DD)")
):
    try:
        query = users.select()  # Selecciona todos los registros inicialmente
        
        # Si se proporcionan fechas, valida y filtra por rango
        if fecha_inicio or fecha_fin:
            if not (fecha_inicio and fecha_fin):
                raise HTTPException(
                    status_code=400,
                    detail="Debe proporcionar tanto fecha_inicio como fecha_fin"
                )
            inicio, fin = validar_rango_fechas(fecha_inicio, fecha_fin)
            query = query.where(users.c.fecha_registro.between(inicio, fin))
        
        # Ordena los resultados de forma descendente por fecha
        query = query.order_by(desc(users.c.fecha_registro))
        
        # Aplica límite y desplazamiento
        query = query.limit(limit).offset(offset)
        
        result = conn.execute(query)
        data = result.fetchall()
        
        logger.info(f"Consulta realizada: limit={limit}, offset={offset}, registros={len(data)}")
        
        # Devuelve los datos como lista de diccionarios
        return {
            "status": "success",
            "total": len(data),
            "limit": limit,
            "offset": offset,
            "data": [dict(row._mapping) for row in data]
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en GET /users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar datos: {str(e)}"
        )


# Ruta GET para calcular estadísticas de los sensores
@user.get("/users/estadisticas")
def get_estadisticas(
    fecha_inicio: str = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: str = Query(None, description="Fecha final (YYYY-MM-DD)")
):
    try:
        query = users.select()
        
        # Filtra por rango de fechas si se proporcionan
        if fecha_inicio or fecha_fin:
            if not (fecha_inicio and fecha_fin):
                raise HTTPException(
                    status_code=400,
                    detail="Debe proporcionar tanto fecha_inicio como fecha_fin"
                )
            inicio, fin = validar_rango_fechas(fecha_inicio, fecha_fin)
            query = query.where(users.c.fecha_registro.between(inicio, fin))
        
        result = conn.execute(query)
        datos = result.fetchall()
        
        # Si no hay datos, retorna mensaje informativo
        if not datos:
            logger.warning("No se encontraron datos para calcular estadísticas")
            return {
                "status": "info",
                "message": "No hay datos disponibles"
            }
        
        # Extrae listas de cada tipo de dato
        niveles = [row.nivel_agua_cm for row in datos if row.nivel_agua_cm is not None]
        temperaturas = [row.temperatura_c for row in datos if row.temperatura_c is not None]
        humedades = [row.humedad_porcentaje for row in datos if row.humedad_porcentaje is not None]
        
        # Función para calcular estadísticas básicas: min, max, promedio, cantidad
        def calcular_stats(datos_lista):
            if not datos_lista:
                return {"min": None, "max": None, "promedio": None, "cantidad": 0}
            return {
                "min": round(min(datos_lista), 2),
                "max": round(max(datos_lista), 2),
                "promedio": round(sum(datos_lista) / len(datos_lista), 2),
                "cantidad": len(datos_lista)
            }
        
        logger.info(f"Estadísticas calculadas: {len(datos)} registros procesados")
        
        # Retorna estadísticas por tipo de dato
        return {
            "status": "success",
            "total_registros": len(datos),
            "nivel_agua_cm": calcular_stats(niveles),
            "temperatura_c": calcular_stats(temperaturas),
            "humedad_porcentaje": calcular_stats(humedades)
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en GET /users/estadisticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular estadísticas: {str(e)}"
        )
