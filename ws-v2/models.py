from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, INT

from config import settings


engine = create_engine(settings.db_url)
Base = declarative_base()
DBSession = sessionmaker(bind=engine)


class History(Base):
    __tablename__ = 'history'

    id = Column(INT, primary_key=True, autoincrement=True)
    client_id = Column(String(255), index=True)
    message = Column(String(255))


Base.metadata.create_all(engine)
