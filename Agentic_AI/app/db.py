from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DB_URL

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(String, index=True, default="demo")
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    price = Column(Float)
    unit = Column(String)              # e.g., "kg", "piece"
    color = Column(String)
    material = Column(String)
    weight = Column(String)
    dimensions = Column(String)
    stock_qty = Column(Integer)
    tags = Column(String)              # comma separated
    lang = Column(String, default="en")
    description_en = Column(Text)
    description_local = Column(Text)
    image_url = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
