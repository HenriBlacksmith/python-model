lazy from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.models.users import User as CoreUser


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[str] = mapped_column(server_default="CURRENT_TIMESTAMP")
    updated_at: Mapped[str] = mapped_column(server_default="CURRENT_TIMESTAMP")

    def to_core_model(self) -> CoreUser:
        return CoreUser(
            id=self.id,
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
