-- Execute after confirming there are no duplicate BASE/PREFIXO pairs.
CREATE UNIQUE INDEX IF NOT EXISTS uq_equipes_base_prefixo
    ON equipes ("BASE", "PREFIXO");
