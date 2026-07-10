import datetime
import random
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sensor import SensorReading

class SensorSimulator:
    async def generate_readings(
        self,
        db: AsyncSession,
        cold_box_id: str,
        shipment_id: Optional[str] = None,
        failing: bool = False,
        duration_minutes: int = 180,
        interval_minutes: int = 5
    ) -> List[SensorReading]:
        """
        Generates simulated time-series sensor readings and writes them to the database.
        Working cold box: fluctuates between 2.0°C and 8.0°C.
        Failing cold box: climbs gradually from normal cold box range to around 15.0°C.
        """
        now = datetime.datetime.utcnow()
        steps = duration_minutes // interval_minutes
        
        # Initial starting temperature (normal vaccine range: 2-8°C)
        temp = random.uniform(3.5, 5.5)
        # Humidity is typically high inside a sealed cold container
        humidity = random.uniform(85.0, 92.0)
        
        readings = []
        for i in range(steps):
            # Generate timestamps spaced backwards from 'now'
            timestamp = now - datetime.timedelta(minutes=(steps - 1 - i) * interval_minutes)
            
            if failing:
                # Climb starts after 20% of duration is complete
                climb_start = steps // 5
                if i > climb_start:
                    remaining_climb_steps = (steps - 1) - i
                    target_temp = 15.0 + random.uniform(-0.5, 0.5)
                    # Linearly step towards target temp based on remaining steps
                    temp = temp + (target_temp - temp) / (remaining_climb_steps + 1)
                else:
                    # Normal fluctuation before failure
                    temp = max(2.0, min(8.0, temp + random.uniform(-0.2, 0.2)))
            else:
                # Normal cold box behavior: random walk bounded strictly between 2.0°C and 8.0°C
                temp = max(2.0, min(8.0, temp + random.uniform(-0.2, 0.2)))
            
            humidity = max(50.0, min(98.0, humidity + random.uniform(-1.0, 1.0)))
            
            reading = SensorReading(
                cold_box_id=cold_box_id,
                shipment_id=shipment_id,
                temperature_c=round(temp, 2),
                humidity_pct=round(humidity, 2),
                timestamp=timestamp
            )
            readings.append(reading)
        
        # Add all to database session and commit
        db.add_all(readings)
        await db.commit()
        
        # Refresh to load auto-generated IDs
        for r in readings:
            await db.refresh(r)

        # Run rules engine check if shipment_id is linked to trigger alerts in real-time
        if shipment_id:
            try:
                from app.services.rules_engine import rules_engine
                await rules_engine.check_shipment_alerts(db, int(shipment_id))
            except Exception as e:
                logger.error(f"Rules engine trigger failed in sensor simulator: {e}")
            
        return readings

sensor_simulator = SensorSimulator()
