from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from database import Base

class Guardian(Base):
    __tablename__ = "guardians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    fcm_token = Column(String(255), unique=True, index=True)

    # 이 Guardian이 관리하는 ProtectedPerson 목록을 관계(relationship)로 정의
    protected_persons = relationship("ProtectedPerson", back_populates="guardian")

class ProtectedPerson(Base):
    __tablename__ = "protected_persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    device_id = Column(String(255), unique=True)
    
    # 외래키(ForeignKey)를 사용하여 guardians 테이블과 연결
    guardian_id = Column(Integer, ForeignKey("guardians.id"))

    # 이 ProtectedPerson을 관리하는 Guardian 객체를 관계(relationship)로 정의
    guardian = relationship("Guardian", back_populates="protected_persons")