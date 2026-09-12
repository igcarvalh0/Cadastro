-- ComposicaoEquipe.equipe_id e uma foreign key, mas nao tinha indice: toda
-- tela que carrega uma equipe com suas vagas (Resumo, Equipes, cadastro de
-- vagas) faz, na pratica, um WHERE composicoes_equipes.equipe_id IN (...),
-- e sem indice isso degrada conforme a tabela cresce.
CREATE INDEX IF NOT EXISTS ix_composicoes_equipes_equipe_id
    ON composicoes_equipes ("equipe_id");
