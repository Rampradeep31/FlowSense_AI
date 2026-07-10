from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse
from app.services.websocket import manager

router = APIRouter()

class AcknowledgeRequest(BaseModel):
    alert_id: int = Field(..., description="The database ID of the alert to mark as acknowledged.")

@router.get("/active", response_model=List[AlertResponse])
async def list_active_alerts(db: AsyncSession = Depends(get_db)):
    """
    List all active (unacknowledged) alerts for District Officers.
    """
    stmt = (
        select(Alert)
        .options(selectinload(Alert.shipment))
        .where(Alert.is_acknowledged == False)
        .order_by(Alert.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(payload: AcknowledgeRequest, db: AsyncSession = Depends(get_db)):
    """
    Mark an active warning/critical alert as acknowledged (acted upon).
    """
    stmt = (
        select(Alert)
        .options(selectinload(Alert.shipment))
        .where(Alert.id == payload.alert_id)
    )
    alert = (await db.execute(stmt)).scalars().first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {payload.alert_id} not found."
        )

    alert.is_acknowledged = True
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert

@router.websocket("/ws")
async def alerts_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket channel for pushing real-time cold chain violation alerts.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for client packets to keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
