-- Usuarios do sistema e o recorte de dados de cada um.
--
-- SENHA_HASH guarda o hash gerado pelo werkzeug (scrypt), nunca a senha.
-- NIVEL diz o que a pessoa pode fazer; os vinculos dizem sobre o que.
-- Os vinculos sao pares TIPO/VALOR (BASE, SETOR, SUPERVISOR, COORDENADOR)
-- porque um usuario pode ter varios do mesmo tipo, e os valores sao texto
-- livre cadastrado junto com as vagas.
--
-- Depois de rodar, crie o primeiro usuario administrador:
--   python -m database.criar_usuario_administrador
-- (nivel "MESTRE" renomeado para "ADMINISTRADOR" — ver migration 006)

CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    "USUARIO"       VARCHAR NOT NULL UNIQUE,
    "NOME"          VARCHAR NOT NULL,
    "SENHA_HASH"    VARCHAR NOT NULL,
    "NIVEL"         VARCHAR NOT NULL,
    "ATIVO"         BOOLEAN NOT NULL DEFAULT TRUE,
    "CRIADO_EM"     TIMESTAMPTZ DEFAULT NOW(),
    "ULTIMO_ACESSO" TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_usuarios_usuario ON usuarios ("USUARIO");

CREATE TABLE IF NOT EXISTS usuarios_vinculos (
    id         SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
    "TIPO"     VARCHAR NOT NULL,
    "VALOR"    VARCHAR NOT NULL,
    CONSTRAINT uq_vinculo_usuario_tipo_valor UNIQUE (usuario_id, "TIPO", "VALOR")
);

CREATE INDEX IF NOT EXISTS ix_usuarios_vinculos_usuario_id
    ON usuarios_vinculos (usuario_id);
