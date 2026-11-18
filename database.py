import os
import tempfile
from datetime import date
from pathlib import Path
from sqlalchemy import String, URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

app_dir = Path(__file__).resolve().parent
if Path("/mount/src").is_dir():
    default_db_path = Path(tempfile.gettempdir()) / "food_saver.db"
else:
    default_db_path = app_dir / "food_saver.db"

db_path = Path(os.environ.get("FOOD_SAVER_DB_PATH", default_db_path)).expanduser()
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(URL.create("sqlite", database=str(db_path)))
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
