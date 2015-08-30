__author__ = 'Emati Mitame'

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Binary, ForeignKey, Enum, create_engine, sql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bitorb.config import config

Base = declarative_base()

engine = create_engine("mysql+pymysql://%s:%s@%s/%s" % (
    config["mysql"]["username"],
    config["mysql"]["password"],
    config["mysql"]["host"],
    config["mysql"]["db"]
    )
)


class Establishment(Base):
    __tablename__ = "establishments"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    full_name = Column(String(256), nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    other_names = Column(String(256), default="")

    email = Column(String(256), unique=True)
    verified = Column(Boolean, default=False)
    username = Column(String(32), nullable=False)
    pass_hash = Column(Binary(64), nullable=False)

    establishment = Column(ForeignKey("establishments.id"), nullable=False)
    rank = Column(Enum("admin", "teacher", "student"), default="student")

    credits = Column(Integer, default=0)


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    created = Column(DateTime, default=sql.func.now())
    creator = Column(ForeignKey("users.id"), nullable=False)

    code = Column(String(10), nullable=False, unique=True)
    value = Column(Integer, default=0)

    redeemed = Column(Boolean, nullable=True)
    redeemer = Column(ForeignKey("users.id"), nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    timestamp = Column(DateTime, default=sql.func.now())

    user_from = Column(ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    user_to = Column(ForeignKey("users.id"), nullable=False)


Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

# __all__ = {
#     "User": User,
#     "Establishment": Establishment,
#     "Token": Token,
#     "Transaction": Transaction,
#     "Session": Session
# }
