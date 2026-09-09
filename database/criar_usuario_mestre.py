"""Cria ou repoe um usuario MESTRE pelo terminal.

Serve para o primeiro acesso e como saida de emergencia: se ninguem mais
conseguir entrar (senha esquecida, ultimo mestre desativado sem querer), este
script devolve o acesso sem precisar mexer no banco na mao.

    python -m database.criar_usuario_mestre

A senha e pedida sem aparecer na tela e nunca e gravada em texto puro — vai
para o banco so como hash.
"""

import getpass
import sys

import auth
from database.database import SessionLocal
from database.models import Usuario


def perguntar_senha():
    while True:
        senha = getpass.getpass("Senha: ")
        problema = auth.validar_senha(senha)

        if problema:
            print(f"  {problema}")
            continue

        if senha != getpass.getpass("Repita a senha: "):
            print("  As senhas não conferem.")
            continue

        return senha


def main():
    print()
    print("=" * 56)
    print("USUÁRIO MESTRE — acesso total ao sistema")
    print("=" * 56)

    login = input("Usuário: ").strip()
    if not login:
        print("Usuário não informado. Nada foi feito.")
        return 1

    sessao = SessionLocal()
    try:
        existente = (
            sessao.query(Usuario)
            .filter(Usuario.USUARIO.ilike(login))
            .first()
        )

        if existente:
            print(f"\n'{existente.USUARIO}' já existe ({existente.NOME}).")
            resposta = input(
                "Redefinir a senha e devolver o acesso de mestre? [s/N] "
            ).strip().lower()

            if resposta != "s":
                print("Nada foi feito.")
                return 1

            existente.SENHA_HASH = auth.gerar_hash_senha(perguntar_senha())
            existente.NIVEL = auth.NIVEL_MESTRE
            existente.ATIVO = True
            sessao.commit()

            print(f"\nPronto: '{existente.USUARIO}' voltou a ser mestre ativo.")
            return 0

        nome = input("Nome completo: ").strip() or login
        senha = perguntar_senha()

        sessao.add(Usuario(
            USUARIO=login,
            NOME=nome,
            NIVEL=auth.NIVEL_MESTRE,
            ATIVO=True,
            SENHA_HASH=auth.gerar_hash_senha(senha),
        ))
        sessao.commit()

        print(f"\nPronto: '{login}' criado como mestre.")
        return 0
    except Exception as erro:
        sessao.rollback()
        print(f"\nNão deu certo: {erro}")
        return 1
    finally:
        sessao.close()


if __name__ == "__main__":
    sys.exit(main())
