from sqlalchemy import Column, Integer, String, create_engine, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///database.db")
SessionLocal = sessionmaker(bind=engine)

class Teacher(Base):
    __tablename__ = "teachers"
    id       = Column(Integer, primary_key=True)
    name     = Column(String, nullable=False)
    position = Column(String, nullable=False)
    experience = Column(String)
    photo    = Column(String)
    link     = Column(String, nullable=True)  # вот оно

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    article = Column(String)  # длинная статья
    link = Column(String, nullable=True)
    date = Column(Date)
    image = Column(String)    # главное изображение

class EventImage(Base):
    __tablename__ = "event_images"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    image_path = Column(String)

Base.metadata.create_all(bind=engine)