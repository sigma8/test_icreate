from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Generator



engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


#-----Agregado jtortolero-----

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
#-----------------------------
