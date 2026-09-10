# Bem-vindo ao Gerenciador de Equipes

Este guia apresenta, de forma simples, todas as telas do sistema que você vai
usar no dia a dia. A ideia é te dar uma visão geral de para que cada tela
serve e o que você pode fazer nela — sem complicação.

Alguns itens deste guia podem não aparecer para você da mesma forma que
aparecem para outra pessoa: o sistema mostra só o que faz sentido para o seu
nível de acesso. Por exemplo, cadastrar equipes ou gerenciar usuários costuma
ficar disponível apenas para quem administra o sistema.

## Sumário

1. [Tela de Login](#1-tela-de-login)
2. [Barra Superior — presente em todas as telas](#2-barra-superior--presente-em-todas-as-telas)
3. [Resumo](#3-resumo)
4. [Banco de Dados](#4-banco-de-dados)
5. [Cadastro de Vagas](#5-cadastro-de-vagas)
6. [Usuários](#6-usuários)

---

## 1. Tela de Login

### Entrar no sistema

**Para que serve:** é a porta de entrada do sistema. É por aqui que você se
identifica para poder usar o Gerenciador de Equipes.

**O que você pode fazer aqui:**
- Digitar seu usuário e senha para entrar.
- Mostrar ou esconder a senha enquanto digita, para conferir se está certa.
- Ver um aviso caso sua sessão tenha expirado (quando você fica muito tempo
  sem usar o sistema e precisa entrar de novo).
- Pedir ajuda: se esqueceu a senha ou tem qualquer dúvida de acesso, a tela
  orienta a procurar o Administrador do sistema, já que não existe
  recuperação automática de senha por e-mail.
- Conferir, num selinho no topo da tela, se o sistema está funcionando
  normalmente ("Sistema online") ou fora do ar ("Sem conexão").

**Para onde você vai depois:** ao entrar com sucesso, você é levado
diretamente para a tela de **Resumo**, que é a tela inicial do sistema.

---

## 2. Barra Superior — presente em todas as telas

Depois que você entra no sistema, toda tela tem uma barra no topo com alguns
atalhos que ficam sempre à mão:

- **Atualizar:** recarrega as informações da tela que você está vendo, sem
  precisar sair e voltar.
- **Modo claro / modo noturno:** alterna a aparência do sistema entre um
  fundo claro e um fundo escuro, conforme sua preferência.
- **Menu:** abre a lista de telas que você tem permissão para acessar, para
  você navegar entre elas rapidamente.
- **Seu usuário (no canto direito):** mostra seu nome e seu nível de acesso,
  e dá acesso a duas ações:
  - **Trocar minha senha** — você mesmo pode alterar sua senha quando quiser.
  - **Sair** — encerra sua sessão no sistema.

---

## 3. Resumo

### Resumo

**Para que serve:** é a tela inicial do sistema. Mostra um panorama geral de
como as equipes estão organizadas: quantas vagas existem, quantas já estão
ocupadas e quantas ainda faltam preencher.

**O que você pode fazer aqui:**
- Filtrar as informações por base, por tipo de equipe (disciplina, como
  Construção, Poda, Linha Viva etc.) ou por setor.
- Ver, para cada base, a composição das equipes: quantas vagas cada função
  tem, quantas estão ocupadas e a diferença entre o que é necessário e o que
  já foi preenchido.
- Clicar nos números de "alocados" para ver a lista de pessoas ocupando
  aquelas vagas, com a opção de **exportar essa lista para uma planilha
  Excel**.
- Clicar nos números de vagas em aberto para ver quem ainda falta alocar,
  também com opção de exportar para Excel.
- Alternar entre uma visão em cartões (indicadores) e uma visão em tabela
  única (composição consolidada), como preferir.
- Ver de forma rápida, em destaque, se cada função está com déficit (faltando
  gente) ou superávit (mais gente que o necessário).

**Para onde você vai depois:** a partir daqui você normalmente segue para o
**Banco de Dados**, caso precise alocar ou trocar alguém de vaga, ou para o
**Cadastro de Vagas**, caso precise criar novas equipes ou vagas.

---

## 4. Banco de Dados

### Banco de Dados

**Para que serve:** é onde o dia a dia de alocação acontece — colocar e
tirar pessoas das vagas das equipes.

**O que você pode fazer aqui:**
- Filtrar equipes por base, tipo de equipe, setor, ou pesquisar diretamente
  pelo nome/prefixo da equipe.
- Ver a lista de equipes, cada uma podendo ser expandida para mostrar todas
  as suas vagas, quem está alocado em cada uma e o status (ocupada ou
  livre).
- **Alocar um colaborador** numa vaga livre.
- **Trocar** o colaborador que está numa vaga por outro.
- **Remover** um colaborador de uma vaga, liberando-a.
- **Remover todos os colaboradores de uma equipe** de uma vez, ou até de
  todas as equipes ao mesmo tempo, quando necessário.
- **Adicionar um "Folguista Extra"** em equipes desse tipo, quando for
  preciso colocar alguém a mais além do quadro normal.
- Ver a lista de colaboradores, filtrando entre todos, só os já alocados ou
  só os livres, e pesquisando por nome ou chapa.
- Fazer **alocação em massa por planilha**: baixar uma planilha com a
  situação atual, preenchê-la indicando quem deve ocupar cada vaga, e depois
  enviar de volta para o sistema. O sistema mostra uma prévia das mudanças
  antes de aplicar (o que vai ser alocado, removido ou ignorado), inclusive
  avisando se algum colaborador já está alocado em outro lugar, para você
  confirmar a transferência.

**Para onde você vai depois:** depois de organizar as alocações, você pode
voltar ao **Resumo** para conferir o resultado, ou seguir para o
**Cadastro de Vagas** se precisar ajustar a estrutura das equipes.

---

## 5. Cadastro de Vagas

### Cadastro de Vagas

**Para que serve:** é onde a estrutura das equipes é criada e organizada —
diferente do Banco de Dados, aqui você não aloca pessoas, você define quais
equipes e quais vagas existem.

**O que você pode fazer aqui:**
- **Criar uma nova equipe**, informando a base e um prefixo (o nome/código
  da equipe).
- **Adicionar uma nova vaga** a uma equipe já existente, escolhendo a
  função, o tipo de equipe (disciplina) e, se quiser, informando setor,
  supervisor e coordenador responsáveis por aquela vaga.
- Fazer o **cadastro em massa por planilha**: baixar um modelo com as
  equipes atuais, preencher indicando o que criar, editar ou excluir, e
  enviar de volta. O sistema mostra uma prévia de tudo o que vai mudar antes
  de aplicar, para você conferir e confirmar.
- Filtrar a lista de equipes por base, tipo ou setor, ou pesquisar
  diretamente.
- Para cada equipe já cadastrada: **editar** seus dados, **remover todos os
  colaboradores** alocados nela, ou **excluir a equipe** (só é possível
  excluir quando não há ninguém alocado nela).
- Excluir uma vaga específica (também só quando ela está livre).
- Fazer uma **edição em massa**: aplicar um mesmo setor, supervisor ou
  coordenador a várias equipes filtradas de uma vez, ou ajustar a
  quantidade de vagas por função de várias equipes ao mesmo tempo, sem
  precisar entrar equipe por equipe.

**Para onde você vai depois:** depois de criar ou ajustar a estrutura,
normalmente você vai para o **Banco de Dados** para começar a alocar
colaboradores nas vagas recém-criadas.

---

## 6. Usuários

### Usuários

**Para que serve:** é a tela de administração de quem tem acesso ao
sistema — normalmente disponível apenas para quem administra o
Gerenciador de Equipes.

**O que você pode fazer aqui:**
- Ver os **níveis de acesso** existentes (por exemplo, Administrador,
  Gerente, Coordenador, Supervisor) e o que cada um pode fazer, marcando ou
  desmarcando permissões como ver o resumo, ver equipes, alocar, editar ou
  remover colaboradores.
- **Atualizar o cadastro de colaboradores** enviando a planilha oficial de
  colaboradores, com uma prévia de quantos registros serão criados ou
  atualizados antes de confirmar.
- Ver a lista de **todos os usuários cadastrados** no sistema, com o nível
  de acesso de cada um e um resumo de sobre quais equipes cada pessoa pode
  atuar.
- **Cadastrar um novo usuário**, definindo login, nome, senha e nível de
  acesso.
- **Editar um usuário** já existente, incluindo trocar seu nível de acesso,
  a quem ele responde dentro da hierarquia (para Coordenadores e
  Supervisores) e sobre quais equipes ele pode atuar (por base, tipo de
  equipe, setor ou uma equipe específica).
- **Ativar ou desativar** um usuário, e **excluir** usuários (exceto o
  seu próprio usuário, por segurança).

**Para onde você vai depois:** depois de organizar o acesso das pessoas,
o ciclo de uso volta ao normal: **Resumo**, **Banco de Dados** e
**Cadastro de Vagas**, conforme a necessidade do dia a dia.
