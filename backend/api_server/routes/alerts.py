from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.get("/")
async def get_alerts(unread_only: bool = False, limit: int = 50):
    from backend.database.connection import get_session
    from backend.database.repositories import AlertRepository
    async for session in get_session():
        repo = AlertRepository(session)
        if unread_only:
            alerts = await repo.get_unread()
        else:
            alerts = await repo.get_recent(limit=limit)
        return {"success": True, "alerts": [a.__dict__ for a in alerts]}


@router.post("/{alert_id}/read")
async def mark_read(alert_id: str):
    from backend.database.connection import get_session
    from backend.database.models.alert import Alert
    from sqlalchemy import select
    async for session in get_session():
        result = await session.execute(select(Alert).where(Alert.alert_id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.is_read = 1
            await session.commit()
        return {"success": True}
