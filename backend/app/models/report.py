from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_type = Column(
        Enum("lost", "found", name="report_type_enum"),
        nullable=False,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    location = Column(String(200), nullable=False)
    reported_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now())

    def __repr__(self):
        return f"<Report(id={self.id}, type='{self.report_type}', title='{self.title}')>"
