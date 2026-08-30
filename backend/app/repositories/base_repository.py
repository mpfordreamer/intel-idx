from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract Generic Repository Interface adhering to LSP and OCP.
    Provides standard async CRUD contract for SQLAlchemy models.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: int) -> ModelType | None:
        """Fetch a single entity by primary key ID."""
        return await self.session.get(self.model, entity_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """Fetch all entities with limit and offset."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """Create and add a new entity to the session."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete_by_id(self, entity_id: int) -> bool:
        """Delete entity by ID. Returns True if deleted, False if not found."""
        instance = await self.get_by_id(entity_id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    @abstractmethod
    async def get_by_unique_key(self, **kwargs: Any) -> ModelType | None:
        """Abstract method to retrieve entity by its unique domain identifier."""
        pass
