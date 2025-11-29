from fastapi import APIRouter, HTTPException, Query  
from config.db import conn  
from models.devices import Sensors  
from schemas.devices import SensorReading
from sqlalchemy import desc  
import logging  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sensor = APIRouter()

# POST route to insert sensor data into the database
@sensor.post("/sensors")
def create_sensor_data(data: SensorReading):
    try:
        new_data = {
            "water_level_cm": data.water_level_cm,
            "temperature_c": data.temperature_c,
            "humidity_percentage": data.humidity_percentage
        }
        result = conn.execute(Sensors.insert().values(new_data))
        conn.commit()  
        
        logger.info(f"Data inserted successfully. ID: {result.inserted_primary_key}")
        
        return {
            "status": "success",
            "message": "Data received successfully"
        }
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving data: {str(e)}"
        )


# GET route to retrieve sensor data with pagination
@sensor.get("/sensors")
def get_sensors(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Offset from the beginning"),
):
    try:
        query = Sensors.select()   
        query = query.order_by(desc(Sensors.c.registration_date))
        query = query.limit(limit).offset(offset)
        result = conn.execute(query)
        data = result.fetchall()
        logger.info(f"Query executed: limit={limit}, offset={offset}, records={len(data)}")
        
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
        logger.error(f"Error in GET /sensors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying data: {str(e)}"
        )


# GET route to calculate sensor statistics
@sensor.get("/sensors/statistics")
def get_statistics():
    try:
        query = Sensors.select()

        result = conn.execute(query)
        data = result.fetchall()
        
        # If no data, return informative message
        if not data:
            logger.warning("No data found to calculate statistics")
            return {
                "status": "info",
                "message": "No data available"
            }
        
        # Extract lists of each data type
        water_levels = [row.water_level_cm for row in data if row.water_level_cm is not None]
        temperatures = [row.temperature_c for row in data if row.temperature_c is not None]
        humidity_values = [row.humidity_percentage for row in data if row.humidity_percentage is not None]
        
        # Function to calculate basic statistics: min, max, average, count
        def calculate_stats(data_list):
            if not data_list:
                return {"min": None, "max": None, "average": None, "count": 0}
            return {
                "min": round(min(data_list), 2),
                "max": round(max(data_list), 2),
                "average": round(sum(data_list) / len(data_list), 2),
                "count": len(data_list)
            }
        
        logger.info(f"Statistics calculated: {len(data)} records processed")
        
        # Return statistics by data type
        return {
            "status": "success",
            "total_records": len(data),
            "water_level_cm": calculate_stats(water_levels),
            "temperature_c": calculate_stats(temperatures),
            "humidity_percentage": calculate_stats(humidity_values)
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in GET /sensors/statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating statistics: {str(e)}"
        )