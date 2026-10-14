from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(String(255), default="")
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    land_size_acres: Mapped[float] = mapped_column(Float, default=0)
    soil_type: Mapped[str] = mapped_column(String(80), default="Other")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="farms")
    soil_records = relationship("SoilData", back_populates="farm", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="farm", cascade="all, delete-orphan")


class SoilData(Base):
    __tablename__ = "soil_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), index=True)
    nitrogen: Mapped[float] = mapped_column(Float)
    phosphorus: Mapped[float] = mapped_column(Float)
    potassium: Mapped[float] = mapped_column(Float)
    ph: Mapped[float] = mapped_column(Float)
    moisture: Mapped[float] = mapped_column(Float, default=0)
    temperature: Mapped[float] = mapped_column(Float, default=0)
    humidity: Mapped[float] = mapped_column(Float, default=70)
    rainfall: Mapped[float] = mapped_column(Float, default=100)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="soil_records")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), index=True)
    prediction_type: Mapped[str] = mapped_column(String(80), index=True)
    input_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation_json: Mapped[str] = mapped_column(Text, default="{}")
    model_name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="predictions")
