from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    wallet = relationship("U_Wallet", back_populates="user", uselist=False)
    stock_ownerships = relationship("S_Ownership", back_populates="user")

class UserWallet(Base):
    __tablename__ = "u_wallet"
    
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    money = Column(DECIMAL(15, 2), default=0)
    
    user = relationship("User", back_populates="wallet")

class Stock(Base):
    __tablename__ = "stock"
    
    j_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    explanation = Column(Text)
    price = Column(DECIMAL(15, 2), nullable=False)
    
    ownerships = relationship("S_Ownership", back_populates="stock")

class StockOwnership(Base):
    __tablename__ = "s_ownership"
    
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    j_id = Column(Integer, ForeignKey("stock.j_id"), primary_key=True)
    price_at_time = Column(DECIMAL(15, 2), nullable=False)
    quantity = Column(Integer, default=0)
    
    user = relationship("User", back_populates="s_ownerships")
    stock = relationship("Stock", back_populates="ownerships")