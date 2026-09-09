# Gerenciador de Equipes

Aplicacao Flask com frontend Quasar para administrar equipes, colaboradores e alocacoes.

## Configuracao

1. Crie um ambiente virtual e instale as dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copie `.env.example` para `.env` e configure `DATABASE_URL`.

3. Execute as migracoes de `migrations/` em ordem numerica antes de iniciar uma base existente:

   - `001_add_unique_team.sql` — impede duas equipes com a mesma BASE + PREFIXO.
   - `002_add_unique_membro_chapa.sql` — impede o mesmo colaborador em duas vagas.
   - `003_add_setor_supervisor_coordenador.sql` — SETOR, SUPERVISOR e COORDENADOR por vaga.

   Cada arquivo traz no cabecalho o que conferir antes de rodar.

4. Inicie o frontend e gere a build:

```powershell
cd frontend
npm install
npm run build
cd ..
```

5. Inicie a aplicacao:

```powershell
python app.py
```

A aplicacao sera servida em `http://127.0.0.1:5000`.

`AUTO_CREATE_SCHEMA=true` pode ser usado somente em ambientes descartaveis para criar tabelas automaticamente.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

Os testes nao tocam o banco: as regras de planilha sao exercitadas com objetos
de mentira, entao podem rodar com o `.env` apontando para producao.

## Atencao

A aplicacao **nao tem autenticacao**. Enquanto isso nao existir, mantenha o
servidor em `127.0.0.1` — expor a porta na rede da empresa deixa qualquer pessoa
ver e editar as equipes.
