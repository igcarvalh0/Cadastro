from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id = Column(Integer, primary_key=True, index=True)

    CHAPA = Column(String, unique=True, nullable=False, index=True)
    NOME = Column(String, nullable=False)
    RATEIO_FUNCIONARIO = Column(String)
    GRPCCUSTO = Column(String)
    FUNÇÃO = Column(String)
    ADMISSÃO = Column(Date)
    SEÇÃO = Column(String)
    SITUAÇÃO = Column(String)

    rateios = relationship(
        "Rateio",
        back_populates="colaborador",
        cascade="all, delete-orphan"
    )


class Rateio(Base):
    __tablename__ = "rateios"

    id = Column(Integer, primary_key=True, index=True)

    CHAPA = Column(
        String,
        ForeignKey("colaboradores.CHAPA"),
        nullable=False,
        index=True
    )

    RATEIO_FUNCIONARIO = Column(String)
    GRPCCUSTO = Column(String)

    colaborador = relationship(
        "Colaborador",
        back_populates="rateios"
    )


class Equipe(Base):
    __tablename__ = "equipes"
    __table_args__ = (
        UniqueConstraint("BASE", "PREFIXO", name="uq_equipes_base_prefixo"),
    )

    id = Column(Integer, primary_key=True, index=True)

    BASE = Column(String, nullable=False, index=True)

    PREFIXO = Column(
    String,
    nullable=False,
    index=True
)

    composicoes = relationship(
        "ComposicaoEquipe",
        back_populates="equipe",
        cascade="all, delete-orphan"
    )


class ComposicaoEquipe(Base):
    __tablename__ = "composicoes_equipes"

    id = Column(Integer, primary_key=True, index=True)

    equipe_id = Column(
        Integer,
        ForeignKey("equipes.id"),
        nullable=False
    )

    FUNÇÃO_ER = Column(String, nullable=False)

    ESTRUTURA = Column(String, nullable=False)

    equipe = relationship(
        "Equipe",
        back_populates="composicoes"
    )

    membro = relationship(
        "MembroEquipe",
        back_populates="composicao",
        uselist=False,
        cascade="all, delete-orphan"
    )


class MembroEquipe(Base):
    __tablename__ = "membros_equipes"
    __table_args__ = (
        UniqueConstraint("CHAPA", name="uq_membros_chapa"),
        UniqueConstraint("composicao_id", name="uq_membros_composicao_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    composicao_id = Column(
        Integer,
        ForeignKey("composicoes_equipes.id"),
        nullable=False
    )

    CHAPA = Column(
        String,
        ForeignKey("colaboradores.CHAPA"),
        nullable=False
    )

    composicao = relationship(
        "ComposicaoEquipe",
        back_populates="membro"
    )

    colaborador = relationship(
        "Colaborador"
    )
