from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

from .config import DB_PATH

engine = create_engine(DB_PATH)


Base = declarative_base()


class Criterion(Base):
    # TODO: add constraint on parent_id that must already exist
    __tablename__ = "criteria"

    criterion_id = Column(Integer, primary_key=True)
    name_ar = Column(String, nullable=False, unique=True)
    name_fr = Column(String, nullable=False, unique=True)
    max_score = Column(Integer, nullable=False)
    level = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("criteria.criterion_id"), nullable=True)
    parent = relationship(
        "Criterion", backref=backref("children", lazy=True), remote_side=[criterion_id]
    )

    __table_args__ = (
        UniqueConstraint("name_ar", "name_fr", name="unique_criterion_name",),
    )


class Municipality(Base):
    __tablename__ = "municipalities"

    municipality_id = Column(Integer, primary_key=True)
    name_ar = Column(String, nullable=False)
    name_fr = Column(String, nullable=False)
    governorate_id = Column(
        Integer, ForeignKey("governorates.governorate_id"), nullable=False
    )
    governorate = relationship(
        "Governorate", backref=backref("municipalities", lazy=True)
    )
    __table_args__ = (
        UniqueConstraint(
            "name_ar", "governorate_id", name="only_one_mun_name_per_gov",
        ),
    )


class Governorate(Base):
    __tablename__ = "governorates"

    governorate_id = Column(Integer, primary_key=True)
    name_ar = Column(String, nullable=False, unique=True)
    name_fr = Column(String, nullable=False, unique=True)


class Evaluation(Base):
    __tablename__ = "evaluations"

    evaluation_id = Column(Integer, primary_key=True)

    year = Column(Integer, nullable=False)

    municipality_id = Column(
        Integer, ForeignKey("municipalities.municipality_id"), nullable=False
    )
    municipality = relationship(
        "Municipality", backref=backref("evaluations", lazy=True)
    )

    criterion_id = Column(Integer, ForeignKey("criteria.criterion_id"), nullable=False)
    criterion = relationship("Criterion", lazy=True)

    score = Column(Float, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "year",
            "municipality_id",
            "criterion_id",
            name="one_evaluation_for_each_mun_for_each_criterion_per_year",
        ),
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    init_db()


def get_session():
    Session = sessionmaker(bind=engine)
    return Session()
