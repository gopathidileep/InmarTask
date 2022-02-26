from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

class Location(Base):
    __tablename__ = 'location'
    location_id = Column(Integer, primary_key=True)
    location_desc = Column(String(250))

class Department(Base):
    __tablename__ = 'department'
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String(250))

class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    category_desc = Column(String(250))

class Subcategory(Base):
    __tablename__ = 'sub_category'
    sub_category_id = Column(Integer, primary_key=True)
    sub_category_desc = Column(String(250))

class Sku(Base):
    __tablename__ = 'sku'
    sku_id = Column(Integer, primary_key=True)
    name = Column(String(250))
    location_id = Column(Integer, ForeignKey('location.location_id'))
    department_id = Column(Integer, ForeignKey('department.department_id'))
    category_id = Column(Integer, ForeignKey('category.category_id'))
    sub_category_id = Column(Integer, ForeignKey('sub_category.sub_category_id'))


engine = create_engine('sqlite:///location_details.db')
Base.metadata.create_all(engine)