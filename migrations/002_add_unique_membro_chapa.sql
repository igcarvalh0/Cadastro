-- Garante que um colaborador nao possa ser alocado em duas vagas ao mesmo tempo.
-- O modelo declara uq_membros_chapa, mas o indice nao existe na base atual.
-- Execute depois de confirmar que nao ha CHAPA duplicada em membros_equipes:
--   SELECT "CHAPA", COUNT(*) FROM membros_equipes GROUP BY "CHAPA" HAVING COUNT(*) > 1;
CREATE UNIQUE INDEX IF NOT EXISTS uq_membros_chapa
    ON membros_equipes ("CHAPA");
