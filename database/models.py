from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import backref, relationship

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
        nullable=False,
        index=True
    )

    FUNÇÃO_ER = Column(String, nullable=False)

    ESTRUTURA = Column(String, nullable=False)

    # informados por disciplina (equipe + TIPO EQUIPE), nao por equipe inteira.
    # servem para escopar os futuros usuarios de alocacao.
    SETOR = Column(String, nullable=True)
    SUPERVISOR = Column(String, nullable=True)
    COORDENADOR = Column(String, nullable=True)

    # None/"PADRAO" = vaga padrao (conta nas vagas da equipe/disciplina).
    # "EXTRA" = Folguista Extra: colaborador alocado sem aumentar a
    # quantidade padrao de vagas (ver ORIGEM_EXTRA em app.py).
    ORIGEM = Column(String, nullable=True)

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


class Usuario(Base):
    """Quem entra no sistema.

    A senha nunca e guardada: fica so o hash gerado pelo werkzeug. NIVEL define
    o que a pessoa pode fazer (ver app.py, NIVEIS); os vinculos definem sobre
    quais equipes ela pode fazer.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    USUARIO = Column(String, unique=True, nullable=False, index=True)
    NOME = Column(String, nullable=False)
    SENHA_HASH = Column(String, nullable=False)
    NIVEL = Column(String, nullable=False)
    ATIVO = Column(Boolean, nullable=False, default=True)

    # Superior direto na hierarquia Gerente -> Coordenador -> Supervisor (o
    # Coordenador de um Supervisor, o Gerente de um Coordenador). O escopo de
    # dados de Gerente/Coordenador e calculado em auth.py somando os vinculos
    # dos Supervisores abaixo dele nesta arvore — nao ha nada gravado aqui
    # alem do proprio elo.
    RESPONSAVEL_ID = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    CRIADO_EM = Column(DateTime(timezone=True), server_default=func.now())
    ULTIMO_ACESSO = Column(DateTime(timezone=True), nullable=True)

    vinculos = relationship(
        "VinculoUsuario",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    subordinados = relationship(
        "Usuario",
        foreign_keys=[RESPONSAVEL_ID],
        backref=backref("responsavel", remote_side=[id]),
    )


class NivelPermissao(Base):
    """Personalizacao das permissoes de um nivel, feita pelo Administrador na
    tela de Usuarios. Ausencia de linhas para um NIVEL = usa o padrao do
    codigo (auth.NIVEIS); a primeira vez que o Administrador salva mudancas
    para aquele nivel, o conjunto completo desejado e gravado aqui.
    """

    __tablename__ = "niveis_permissoes"
    __table_args__ = (
        UniqueConstraint("NIVEL", "PERMISSAO", name="uq_nivel_permissao"),
    )

    id = Column(Integer, primary_key=True, index=True)

    NIVEL = Column(String, nullable=False, index=True)
    PERMISSAO = Column(String, nullable=False)


class VinculoUsuario(Base):
    """Recorte de dados que um usuario enxerga.

    Guardado como pares TIPO/VALOR (BASE=BACABAL, SETOR=Setor Leste,
    SUPERVISOR=Joao...) em vez de colunas fixas, porque um usuario pode ter
    varios vinculos do mesmo tipo e porque os valores sao texto livre,
    cadastrados junto com as vagas.
    """

    __tablename__ = "usuarios_vinculos"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "TIPO", "VALOR", name="uq_vinculo_usuario_tipo_valor"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    TIPO = Column(String, nullable=False)
    VALOR = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="vinculos")
