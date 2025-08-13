from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Usr(Base):
    __tablename__ = "usr"
    
    uid = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(50), unique=True, nullable=False)
    pwd = Column(String(255), nullable=False)
    
    wallet = relationship("UsrWallet", back_populates="usr", uselist=False)
    stk_owns = relationship("StkOwn", back_populates="usr")

class UsrWallet(Base):
    __tablename__ = "usr_wallet"
    
    uid = Column(Integer, ForeignKey("usr.uid"), primary_key=True)
    money = Column(DECIMAL(15, 2), default=0)
    
    usr = relationship("Usr", back_populates="wallet")

class Stk(Base):
    __tablename__ = "stk"
    
    jid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    exp = Column(Text)
    price = Column(DECIMAL(15, 2), nullable=False)
    
    owns = relationship("StkOwn", back_populates="stk")

class StkOwn(Base):
    __tablename__ = "stk_own"
    
    uid = Column(Integer, ForeignKey("usr.uid"), primary_key=True)
    jid = Column(Integer, ForeignKey("stk.jid"), primary_key=True)
    price_at = Column(DECIMAL(15, 2), nullable=False)
    qty = Column(Integer, default=0)
    
    usr = relationship("Usr", back_populates="stk_owns")
    stk = relationship("Stk", back_populates="owns")