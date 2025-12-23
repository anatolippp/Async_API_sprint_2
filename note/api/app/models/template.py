from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Template(Base):
    __tablename__ = "templates"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    subject_template: Mapped[str] = mapped_column(String(255))
    body_template: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(16), default="email")

    notifications = relationship("Notification", back_populates="template")
