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
   - `004_add_usuarios.sql` — usuarios do sistema e os vinculos de cada um.
   - `005_add_origem_vaga.sql` — marca a vaga como PADRAO ou EXTRA (Folguista Extra).
   - `006_renomear_mestre_para_administrador.sql` — renomeia o nivel MESTRE para ADMINISTRADOR.
   - `007_add_niveis_permissoes.sql` — permissoes por nivel personalizaveis pelo Administrador.
   - `008_add_hierarquia_usuarios.sql` — hierarquia Gerente -> Coordenador -> Supervisor.
   - `009_add_indice_equipe_id.sql` — índice em composicoes_equipes.equipe_id (melhora a carga de equipes/resumo).
   - `010_add_secao_tratada_tipo_ccusto.sql` — SEÇÃO_TRATADA e TIPO_CCUSTO em colaboradores (ver database/depara.py); depois de aplicar, rode `python -m database.importacao.recalcular_secao_tipo_ccusto` para preencher quem já estava cadastrado.

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

## Acesso

Toda a API exige login. Para criar o primeiro usuario (ou recuperar o acesso,
se ninguem mais conseguir entrar):

```powershell
.\.venv\Scripts\python.exe -m database.criar_usuario_administrador
```

A senha e pedida sem aparecer na tela e vai para o banco apenas como hash
(scrypt) — nunca em texto puro.

### Niveis e vinculos

- O **nivel** diz o que a pessoa pode fazer. Definido em `auth.py`, em `NIVEIS`:
  e o unico lugar a mexer para criar ou alterar um nivel. A tela de usuarios le
  essa tabela, entao um nivel novo aparece no formulario sozinho.
- Os **vinculos** dizem sobre quais equipes ela age (base, tipo de equipe,
  setor, supervisor, coordenador, equipe especifica, operacao liberada). Sem
  nenhum vinculo, a pessoa alcanca todas as equipes.
- `ADMINISTRADOR` tem todas as permissoes e ignora vinculos (nivel antigo
  "MESTRE", renomeado — ver migration 006).
- `SUPERVISOR` ve o resumo e as equipes inteiros, mas so aloca ou remove
  colaborador nas vagas cuja base **e** cujo tipo de equipe estejam nos
  vinculos dele (as duas coisas ao mesmo tempo). A checagem fica em
  `auth.pode_atuar_na_base_e_tipo`.
- `ANALISTA` so aloca, edita ou remove dentro do escopo (equipe especifica,
  base+tipo, ou setor) e das operacoes liberadas pelo Administrador (vinculo
  `OPERACAO`). A checagem fica em `auth.pode_realizar_operacao`.

`SECRET_KEY` no `.env` assina o cookie de sessao. Trocar esse valor desloga
todo mundo; nao ter o valor faz as sessoes cairem a cada reinicio do servidor.

## Atencao

Mesmo com login, mantenha o servidor em `127.0.0.1` enquanto o controle de
acesso nao estiver validado em uso. O trafego e HTTP puro: numa rede aberta,
usuario e senha viajam sem criptografia.
