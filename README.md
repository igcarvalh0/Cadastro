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

3. Execute a migracao SQL em `migrations/001_add_unique_team.sql` antes de iniciar uma base existente.

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
