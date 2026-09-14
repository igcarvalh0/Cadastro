# Deploy no Render

O projeto tem duas partes que sobem juntas num único serviço: o Flask
(`app.py`) serve tanto a API quanto os arquivos já compilados do frontend
(`frontend/dist/spa`). Por isso o build no Render precisa instalar as
dependências Python **e** compilar o frontend antes de iniciar o servidor.

O banco continua sendo o mesmo do dia a dia — a Neon em produção. O Render
não hospeda banco nenhum aqui, só a aplicação.

## Passo a passo (dashboard do Render)

1. **New > Blueprint** e aponte para este repositório (`igcarvalh0/Cadastro`,
   branch `main`). O Render lê o [render.yaml](render.yaml) da raiz e já
   propõe o serviço configurado.
   - Se preferir configurar na mão em vez de Blueprint: **New > Web Service**,
     mesmo repositório, e copie os campos abaixo.

2. Confira/preencha os campos (já vêm do `render.yaml` no fluxo de Blueprint):
   - **Runtime**: Python 3
   - **Build Command**:
     `pip install -r requirements.txt && cd frontend && npm ci && npm run build`
   - **Start Command**:
     `waitress-serve --host=0.0.0.0 --port=$PORT app:app`
   - **Health Check Path**: `/api/status`

3. **Environment Variables** — únicas duas que a aplicação precisa (ver
   `database/database.py` e o topo do `app.py`):
   - `DATABASE_URL` — a mesma connection string da Neon que está no seu
     `.env` local (`postgresql+psycopg://usuario:senha@host/banco?sslmode=require`).
     **Não** reutilize a Neon de produção sem avisar o time — é a mesma base
     que a operação usa todo dia; um deploy de teste apontando pra ela grava
     dado de verdade.
   - `SECRET_KEY` — o `render.yaml` já marca `generateValue: true`, então o
     Render gera um valor aleatório sozinho na primeira vez. Sem isso, todo
     redeploy derruba quem estava logado (mesmo aviso que aparece no log
     local se o `.env` não tiver a chave).

4. Deploy. O primeiro build demora um pouco mais por causa do `npm ci`
   (instala os pacotes do frontend do zero).

## Depois do primeiro deploy

- A URL pública (`https://<nome-do-servico>.onrender.com`) já serve a tela de
  login direto — não tem passo manual de "rodar migração" aqui, porque o
  banco (Neon) já está com o schema atualizado pelas migrations de produção.
- Toda alteração de **backend** (`app.py`, `auth.py`, `database/`) ou
  **frontend** (`frontend/src/`) que for enviada (push) para `main` dispara
  um novo deploy automático — o Render já roda o `npm run build` de novo,
  então não precisa lembrar de compilar antes de subir.
- Planos gratuitos do Render "dormem" depois de um tempo sem acesso: a
  primeira requisição depois disso demora mais (o serviço acorda). Se isso
  incomodar no uso real, o plano pago tira essa espera.

## Se algo der errado

- **Build falha no `npm ci`**: geralmente é versão de Node. O
  `frontend/package.json` exige Node `>=22.12` — o `render.yaml` já fixa
  `NODE_VERSION=22.12.0`.
- **Tela abre em branco / 404 nos assets**: o Flask serve o frontend a partir
  de `frontend/dist/spa` (ver `FRONTEND_DIST_DIR` em `app.py`) — confirme que
  o build command rodou o `npm run build` antes do `waitress-serve` iniciar
  (é a ordem no comando combinado com `&&`, então build quebrado não deveria
  nem chegar a subir o servidor).
- **"A variável DATABASE_URL não foi encontrada"**: variável não configurada
  no serviço — conferir em Environment no dashboard do Render.
