import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import async_session_maker
from app.services.sensor import sensor_simulator
import random

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Active cold boxes to continuously poll in the background
ACTIVE_COLD_BOXES = ["BOX-001", "BOX-002", "BOX-003"]

async def poll_sensors_job():
    """
    Simulates real-time IoT gateway polling.
    Inserts a single sensor reading for each active cold box.
    """
    logger.info("Background scheduler: Polling IoT cold box sensors...")
    async with async_session_maker() as db:
        try:
            for box_id in ACTIVE_COLD_BOXES:
                # 15% chance of simulating a temp excursion warning on BOX-003
                failing = False
                if box_id == "BOX-003" and random.random() < 0.15:
                    failing = True
                    logger.warning(f"Simulating temperature excursion failure for {box_id} in background polling.")
                
                # Duration=5, Interval=5 generates exactly 1 reading step at the current timestamp
                await sensor_simulator.generate_readings(
                    db=db,
                    cold_box_id=box_id,
                    failing=failing,
                    duration_minutes=5,
                    interval_minutes=5
                )
            logger.info("Successfully polled and stored readings for active cold boxes.")
        except Exception as e:
            logger.error(f"Error in background poll_sensors_job: {e}")

def start_scheduler():
    if not scheduler.running:
        # Run every 30 seconds for simulated real-time activity
        scheduler.add_job(poll_sensors_job, "interval", seconds=30, id="sensor_polling")
        scheduler.start()
        logger.info("APScheduler started: sensor polling job scheduled every 30 seconds.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down.")
