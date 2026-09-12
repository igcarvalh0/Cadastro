-- Adiciona SEÇÃO_TRATADA e TIPO_CCUSTO em colaboradores.
--
-- Calculados a partir do de-para importado uma unica vez de uma planilha do
-- RH (cadastro.xlsx com as abas SEÇÃO e RATEIO_FUNCIONARIO, ver
-- database/depara.py e database/importacao/depara_cadastro.json) e
-- persistidos aqui pra tela (Banco de Dados > Colaboradores) e exportacao
-- (planilha de alocacoes/ativos) sempre baterem.
--
-- So preenche a coluna; nao apaga nem altera nenhum dado existente. Depois
-- de rodar esta migration, rode
-- database/importacao/recalcular_secao_tipo_ccusto.py pra preencher os
-- colaboradores ja cadastrados (colaboradores importados dali em diante ja
-- vem com os campos calculados automaticamente).

ALTER TABLE colaboradores
    ADD COLUMN IF NOT EXISTS "SEÇÃO_TRATADA" VARCHAR;

ALTER TABLE colaboradores
    ADD COLUMN IF NOT EXISTS "TIPO_CCUSTO" VARCHAR;
