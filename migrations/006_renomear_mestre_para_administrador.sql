-- O nivel "MESTRE" foi renomeado para "ADMINISTRADOR" (mesmo acesso, so
-- muda o nome). Atualiza os usuarios ja cadastrados para o novo valor —
-- sem isso eles perderiam o nivel (NIVEIS so tem a chave "ADMINISTRADOR")
-- e ficariam sem nenhuma permissao ao reiniciar o servidor com o codigo novo.
UPDATE usuarios SET "NIVEL" = 'ADMINISTRADOR' WHERE "NIVEL" = 'MESTRE';
