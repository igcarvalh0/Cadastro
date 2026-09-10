-- Hierarquia entre usuarios: Gerente -> Coordenador -> Supervisor.
--
-- RESPONSAVEL_ID aponta para o superior DIRETO do usuario (o Coordenador de
-- um Supervisor, o Gerente de um Coordenador). E so isso: uma arvore simples
-- por auto-relacionamento, sem tabela nova. O escopo de dados de um Gerente
-- ou Coordenador continua vindo dos vinculos (BASE/TIPO_EQUIPE) dos
-- Supervisores abaixo dele na arvore — calculado em auth.py, nao gravado
-- aqui, entao nao ha nada para duplicar.
--
-- Nivel ANALISTA foi descontinuado (nenhum usuario real o usava); os niveis
-- validos passam a ser ADMINISTRADOR, GERENTE, COORDENADOR e SUPERVISOR.

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS "RESPONSAVEL_ID" INTEGER REFERENCES usuarios (id);

CREATE INDEX IF NOT EXISTS ix_usuarios_responsavel_id
    ON usuarios ("RESPONSAVEL_ID");
