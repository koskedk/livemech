from uuid import UUID
from sqlalchemy import String,Text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    pass

class ShopEntity(Base):
   __tablename__="shops"
   
   id:Mapped[UUID]=mapped_column(primary_key=True)
   name:Mapped[str]=mapped_column(String(250),nullable=False)
   description:Mapped[str|None]=mapped_column(Text,nullable=True)