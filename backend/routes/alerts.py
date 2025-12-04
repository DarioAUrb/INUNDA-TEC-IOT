import time
import logging
from config.db import engine
from models.devices import Phones
from app import send_sms_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alert thresholds
WATER_THRESHOLD_WARNING = 5  
WATER_THRESHOLD_DANGER = 9   

# Track last alert time to avoid spam
last_alert_time = {}

# Get active phone numbers from database
def get_active_phone_numbers():
    """Retrieve all active phone numbers from database"""
    conn = engine.connect()
    try:
        query = Phones.select().where(Phones.c.is_active == True)
        result = conn.execute(query)
        phones = [row.phone_number for row in result.fetchall()]
        return phones
    except Exception as e:
        logger.error(f"Error retrieving phone numbers: {str(e)}")
        return []
    finally:
        conn.close()


def check_and_send_alerts(water_level):
    """
    Check water level and send SMS alerts if thresholds are exceeded
    Uses phone numbers from database
    """
    current_time = time.time()
    phone_numbers = get_active_phone_numbers()
    
    if not phone_numbers:
        logger.warning("No active phone numbers configured for alerts")
        return
    
    if water_level >= WATER_THRESHOLD_DANGER:
        if "danger" not in last_alert_time or (current_time - last_alert_time["danger"]) > 600:
            send_sms_alert(water_level, "danger", phone_numbers)
            last_alert_time["danger"] = current_time
            logger.warning(f"DANGER alert sent: water level {water_level} cm")
    
    elif water_level >= WATER_THRESHOLD_WARNING:
        if "warning" not in last_alert_time or (current_time - last_alert_time["warning"]) > 300:
            send_sms_alert(water_level, "warning", phone_numbers)
            last_alert_time["warning"] = current_time
            logger.warning(f"WARNING alert sent: water level {water_level} cm")