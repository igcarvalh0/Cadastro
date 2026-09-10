-- Marca a origem de uma vaga (ComposicaoEquipe): PADRAO (a maioria, inclusive
-- toda vaga existente) ou EXTRA (Folguista Extra, adicionada manualmente sem
-- alterar a quantidade padrao de vagas da equipe/disciplina).
-- Nula = PADRAO (nenhuma vaga existente muda de comportamento).
ALTER TABLE composicoes_equipes
    ADD COLUMN IF NOT EXISTS "ORIGEM" VARCHAR;
