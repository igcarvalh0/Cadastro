-- Adiciona SETOR, SUPERVISOR e COORDENADOR a cada vaga (ComposicaoEquipe).
-- Sao informados por TIPO EQUIPE (equipe + disciplina), nao por equipe inteira:
-- o Folguista de uma base pode ter um supervisor para a turma de construcao e
-- outro para a turma de poda. Serao usados para escopar os futuros usuarios
-- de alocacao. Colunas nulas nao afetam nenhuma vaga existente.
ALTER TABLE composicoes_equipes
    ADD COLUMN IF NOT EXISTS "SETOR" VARCHAR,
    ADD COLUMN IF NOT EXISTS "SUPERVISOR" VARCHAR,
    ADD COLUMN IF NOT EXISTS "COORDENADOR" VARCHAR;
