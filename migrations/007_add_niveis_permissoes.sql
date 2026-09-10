-- Permite ao Administrador personalizar, por tela, quais permissoes cada
-- nivel tem (hoje fixas em auth.NIVEIS). Ausencia de linhas para um nivel
-- mantem o comportamento padrao do codigo; nada muda para quem nunca usar
-- essa tela.
CREATE TABLE IF NOT EXISTS niveis_permissoes (
    id SERIAL PRIMARY KEY,
    "NIVEL" VARCHAR NOT NULL,
    "PERMISSAO" VARCHAR NOT NULL,
    CONSTRAINT uq_nivel_permissao UNIQUE ("NIVEL", "PERMISSAO")
);

CREATE INDEX IF NOT EXISTS ix_niveis_permissoes_nivel ON niveis_permissoes ("NIVEL");
