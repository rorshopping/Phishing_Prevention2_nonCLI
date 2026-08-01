from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AuditLog


class BaseAgent:
    @staticmethod
    async def _log_action(
        db: AsyncSession,
        client_id: Any,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        log = AuditLog(client_id=client_id, action=action, details=details)
        db.add(log)
