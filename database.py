from datetime import date
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///food_saver.db")
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    purchase_date: Mapped[date]
    expiry_date: Mapped[date]

def init_db():
    Base.metadata.create_all(engine)


from sqlalchemy import Text


class MealPlan(Base):
    __tablename__ = "meal_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_date: Mapped[date]
    slot: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    used: Mapped[str] = mapped_column(Text, default="[]")
    missing: Mapped[str] = mapped_column(Text, default="[]")


class WasteLog(Base):
    __tablename__ = "waste_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(50))
    logged_date: Mapped[date]
