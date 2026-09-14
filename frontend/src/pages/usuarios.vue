<template>
  <q-layout view="lHh Lpr lFf">
    <MarcaDaguaFundo />

    <CabecalhoApp
      titulo="Usuários"
      :carregando="carregando"
      @atualizar="carregarTudo"
    />

    <q-page-container>
      <q-page class="q-pa-md">
        <div class="q-mb-md">
          <div class="text-h5"> Usuários </div>

          <div class="text-subtitle2 text-grey-7">
            Quem entra no sistema, o que cada um pode fazer e sobre quais
            equipes
          </div>
        </div>

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <q-banner v-if="sucesso" class="bg-green-1 text-positive q-mb-md" rounded>
          {{ sucesso }}
        </q-banner>

        <!-- ================================================== -->
        <!-- NÍVEIS DE ACESSO -->
        <!-- ================================================== -->

        <q-card bordered class="q-mb-md">
          <q-card-section>
            <div class="text-h6"> Níveis de acesso </div>

            <div class="text-caption text-grey-7">
              O nível define <strong>o que</strong> a pessoa pode fazer. Os
              vínculos (ou, para Gerente e Coordenador, a hierarquia de
              responsáveis) definem <strong>sobre quais equipes</strong>.
              Marque ou desmarque as permissões e clique em Salvar na linha —
              o Administrador sempre tem acesso total.
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pt-sm">
            <q-markup-table flat square dense class="tabela-niveis">
              <thead>
                <tr>
                  <th class="text-left">Nível</th>
                  <th
                    v-for="permissao in PERMISSOES"
                    :key="permissao.valor"
                    class="text-center"
                  >
                    {{ permissao.rotulo }}
                  </th>
                  <th class="text-center">Ações</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="nivel in niveis" :key="nivel.valor">
                  <td>
                    <div class="text-weight-medium">{{ nivel.rotulo }}</div>
                    <div class="text-caption text-grey-7">
                      {{ nivel.descricao }}
                    </div>
                  </td>

                  <td
                    v-for="permissao in PERMISSOES"
                    :key="permissao.valor"
                    class="text-center"
                  >
                    <q-checkbox
                      v-if="nivel.personalizavel"
                      :model-value="(permissoesEditaveis[nivel.valor] || []).includes(permissao.valor)"
                      @update:model-value="alternarPermissaoNivel(nivel.valor, permissao.valor)"
                    />

                    <template v-else>
                      <q-icon
                        v-if="nivel.permissoes.includes(permissao.valor)"
                        name="check_circle"
                        color="positive"
                        size="20px"
                      />
                      <q-icon v-else name="remove" color="grey-5" size="18px" />
                    </template>
                  </td>

                  <td class="text-center">
                    <q-btn
                      v-if="nivel.personalizavel"
                      flat
                      dense
                      size="sm"
                      color="primary"
                      icon="save"
                      label="Salvar"
                      :loading="salvandoPermissoesNivel === nivel.valor"
                      @click="salvarPermissoesNivel(nivel.valor)"
                    />
                    <span v-else class="text-caption text-grey-6">fixo</span>
                  </td>
                </tr>
              </tbody>
            </q-markup-table>

            <q-banner dense class="bg-blue-1 q-mt-md" rounded>
              <template #avatar>
                <q-icon name="info" color="primary" />
              </template>
              O <strong>Analista</strong> (e o Supervisor) só ganham as
              operações de Alocar/Editar/Remover marcadas aqui de fato dentro
              do escopo definido nos vínculos de cada usuário (Setor, Equipe,
              Base), no formulário abaixo.
            </q-banner>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- ATUALIZAÇÃO DO CADASTRO DE COLABORADORES -->
        <!-- ================================================== -->

        <div class="row q-col-gutter-md q-mb-md items-stretch">
        <div
          v-if="temPermissao(PODE_GERENCIAR_COLABORADORES)"
          class="col-12 col-md-6 column"
        >
        <q-card bordered class="col column">
          <q-card-section>
            <div class="text-h6">Atualizar cadastro de colaboradores</div>
            <div class="text-caption text-grey-7">
              Exclusivo do Administrador. Envie a planilha Excel padrão do
              cadastro de colaboradores para criar ou atualizar os registros.
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="q-mb-md">
              <q-btn
                unelevated
                rounded
                no-caps
                dense
                color="positive"
                icon="download"
                label="Baixar planilha modelo"
                :loading="baixandoModeloColaboradores"
                class="btn-exportar"
                @click="baixarModeloColaboradores"
              />
              <div class="text-caption text-grey-7 q-mt-sm">
                Traz as colunas certas e uma linha de exemplo — preencha uma
                linha por colaborador (e uma linha extra por rateio, se houver
                mais de um) e envie abaixo.
              </div>
            </div>

            <div class="row q-col-gutter-md items-start">
              <div class="col-12 col-md">
                <q-file
                  v-model="arquivoColaboradores"
                  outlined
                  dense
                  clearable
                  accept=".xlsx"
                  label="Planilha de colaboradores (.xlsx)"
                  @update:model-value="resumoColaboradores = null"
                >
                  <template #prepend>
                    <q-icon name="attach_file" />
                  </template>
                </q-file>
              </div>

              <div class="col-12 col-md-auto">
                <q-btn
                  color="primary"
                  icon="fact_check"
                  label="Analisar planilha"
                  :disable="!arquivoColaboradores"
                  :loading="analisandoColaboradores"
                  @click="analisarPlanilhaColaboradores"
                />
              </div>
            </div>

            <!--
              Os 4 chips são o resumo clicável da análise: cada um abre o
              MESMO diálogo (detalheImportacao guarda qual), que troca só as
              colunas da tabela. Um diálogo por tipo seria 4 blocos quase
              idênticos de markup.
            -->
            <div v-if="resumoColaboradores" class="q-mt-md">
              <div class="row q-gutter-sm q-mb-sm">
                <q-chip
                  v-for="chip in chipsImportacao"
                  :key="chip.tipo"
                  :color="chip.cor"
                  text-color="white"
                  :clickable="chip.total > 0"
                  @click="abrirDetalheImportacao(chip.tipo)"
                >
                  {{ chip.total }} {{ chip.rotulo }}
                  <q-icon v-if="chip.total > 0" name="visibility" size="16px" class="q-ml-xs" />
                  <q-tooltip v-if="chip.total > 0">Clique para ver os detalhes</q-tooltip>
                </q-chip>
              </div>

              <q-banner
                v-if="resumoColaboradores.erros?.length"
                class="bg-red-1 text-negative q-mb-sm"
                rounded
                dense
              >
                {{ resumoColaboradores.erros.length }} linha(s) com erro impedem a
                aplicação. Clique no chip vermelho para ver quais.
              </q-banner>

              <q-btn
                color="positive"
                label="Confirmar e aplicar"
                :disable="!!resumoColaboradores.erros?.length"
                :loading="aplicandoColaboradores"
                @click="aplicarPlanilhaColaboradores"
              />
            </div>
          </q-card-section>
        </q-card>
        </div>

        <!-- ================================================== -->
        <!-- USUÁRIOS EM LOTE (EXPORTAR / SUBIR) -->
        <!-- ================================================== -->

        <div class="col-12 col-md-6 column">
        <q-card bordered class="col column">
          <q-card-section>
            <div class="text-h6">Usuários em lote</div>
            <div class="text-caption text-grey-7">
              Baixe a planilha com os usuários de hoje, edite as linhas (ou
              acrescente novas) e envie de volta. Serve para cadastrar e para
              editar — inclusive nível, vínculos e quem responde a quem.
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section class="col column">
            <div class="q-mb-md">
              <q-btn
                unelevated
                rounded
                no-caps
                dense
                color="positive"
                icon="download"
                label="Baixar planilha de usuários"
                :loading="baixandoPlanilhaUsuarios"
                class="btn-exportar"
                @click="baixarPlanilhaUsuarios"
              />
              <div class="text-caption text-grey-7 q-mt-sm">
                Vem com todos os usuários preenchidos e uma aba
                <strong>Opções</strong> listando o que pode ser escrito em cada
                coluna (níveis, bases, disciplinas, setores e equipes).
                <strong>Ninguém é excluído</strong> por sumir da planilha — para
                tirar o acesso, escreva NAO na coluna ATIVO.
              </div>
            </div>

            <div class="row q-col-gutter-md items-start">
              <div class="col-12 col-md">
                <q-file
                  v-model="arquivoUsuarios"
                  outlined
                  dense
                  clearable
                  accept=".xlsx"
                  label="Planilha de usuários (.xlsx)"
                  @update:model-value="planoUsuarios = null"
                >
                  <template #prepend>
                    <q-icon name="attach_file" />
                  </template>
                </q-file>
              </div>

              <div class="col-12 col-md-auto">
                <q-btn
                  color="primary"
                  icon="fact_check"
                  label="Conferir mudanças"
                  :disable="!arquivoUsuarios"
                  :loading="analisandoUsuarios"
                  @click="analisarPlanilhaUsuarios"
                />
              </div>
            </div>

            <div v-if="planoUsuarios" class="q-mt-md">
              <div class="row q-gutter-sm q-mb-sm">
                <q-chip color="positive" text-color="white">
                  {{ planoUsuarios.criar?.length || 0 }} novo(s)
                </q-chip>
                <q-chip color="primary" text-color="white">
                  {{ planoUsuarios.atualizar?.length || 0 }} alterado(s)
                </q-chip>
                <q-chip color="grey-7" text-color="white">
                  {{ planoUsuarios.ignoradas || 0 }} sem mudança
                </q-chip>
                <q-chip
                  v-if="planoUsuarios.erros?.length"
                  color="negative"
                  text-color="white"
                >
                  {{ planoUsuarios.erros.length }} com erro
                </q-chip>
              </div>

              <q-banner
                v-if="planoUsuarios.erros?.length"
                class="bg-red-1 text-negative q-mb-sm"
                rounded
                dense
              >
                <div
                  v-for="(item, indice) in planoUsuarios.erros"
                  :key="indice"
                  class="text-caption"
                >
                  <strong v-if="item.linha">Linha {{ item.linha }}</strong>
                  <strong v-else>Planilha</strong>
                  <span v-if="item.usuario"> ({{ item.usuario }})</span>:
                  {{ item.erro }}
                </div>
              </q-banner>

              <q-list
                v-if="linhasPlanoUsuarios.length"
                bordered
                dense
                separator
                class="rounded-borders q-mb-sm"
              >
                <q-item v-for="item in linhasPlanoUsuarios" :key="item.linha">
                  <q-item-section>
                    <q-item-label class="text-weight-medium">
                      {{ item.usuario }} — {{ item.nome }}
                      <q-badge
                        :color="item.novo ? 'positive' : 'primary'"
                        :label="item.novo ? 'novo' : 'alterado'"
                        class="q-ml-xs"
                      />
                    </q-item-label>

                    <q-item-label caption>
                      {{ item.nivel_rotulo }}
                      <span v-if="!item.ativo"> · será desativado</span>
                    </q-item-label>

                    <q-item-label
                      v-for="(mudanca, indice) in item.mudancas || []"
                      :key="indice"
                      caption
                    >
                      {{ mudanca.campo }}: {{ mudanca.de }} → {{ mudanca.para }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>

              <q-btn
                color="positive"
                label="Confirmar e aplicar"
                :disable="!!planoUsuarios.erros?.length || !linhasPlanoUsuarios.length"
                :loading="aplicandoUsuarios"
                @click="aplicarPlanilhaUsuarios"
              />
            </div>
          </q-card-section>
        </q-card>
        </div>
        </div>

        <!-- ================================================== -->
        <!-- LISTA DE USUÁRIOS -->
        <!-- ================================================== -->

        <q-card bordered>
          <q-card-section>
            <div class="row items-center q-col-gutter-sm">
              <div class="col-12 col-md">
                <div class="text-h6"> Cadastrados </div>
              </div>

              <div class="col-12 col-md-4">
                <q-input
                  v-model="filtroUsuario"
                  outlined
                  dense
                  clearable
                  placeholder="Nome, login, nível, base, setor..."
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>
                  <q-tooltip>
                    Busca pelo nome e login, e também pelo nível, por quem a
                    pessoa responde e pelos vínculos dela (ex.: GOMAN,
                    PRES DUTRA).
                  </q-tooltip>
                </q-input>
              </div>

              <div class="col-12 col-md-auto">
                <q-btn
                  color="primary"
                  icon="person_add"
                  label="Novo usuário"
                  @click="abrirNovo"
                />
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <div v-if="carregando && primeiraCarga" class="row justify-center q-pa-xl">
            <q-spinner color="primary" size="40px" />
          </div>

          <q-list v-else separator>
            <q-item v-if="!usuarios.length">
              <q-item-section class="text-grey-7">
                Nenhum usuário cadastrado.
              </q-item-section>
            </q-item>

            <q-item v-else-if="!usuariosFiltrados.length">
              <q-item-section class="text-grey-7">
                Nenhum usuário encontrado para "{{ filtroUsuario }}".
              </q-item-section>
            </q-item>

            <q-item v-for="pessoa in usuariosFiltrados" :key="pessoa.id">
              <q-item-section>
                <q-item-label class="text-weight-medium">
                  {{ pessoa.nome }}
                  <q-badge
                    v-if="pessoa.id === usuario?.id"
                    color="primary"
                    class="q-ml-sm"
                    label="você"
                  />
                  <q-badge
                    v-if="!pessoa.ativo"
                    color="grey-7"
                    class="q-ml-sm"
                    label="desativado"
                  />
                </q-item-label>

                <q-item-label caption>
                  {{ pessoa.usuario }} · {{ pessoa.nivel_rotulo }}
                  <template v-if="pessoa.responsavel_nome">
                    · responde a {{ pessoa.responsavel_nome }}
                  </template>
                </q-item-label>

                <q-item-label v-if="resumoVinculos(pessoa)" caption class="q-mt-xs">
                  <q-icon name="link" size="14px" />
                  {{ resumoVinculos(pessoa) }}
                </q-item-label>

                <q-item-label v-else-if="pessoa.ignora_vinculos" caption class="q-mt-xs">
                  <q-icon name="public" size="14px" /> Enxerga todas as equipes
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row q-gutter-xs">
                  <q-btn
                    flat
                    dense
                    round
                    icon="edit"
                    color="primary"
                    @click="abrirEdicao(pessoa)"
                  >
                    <q-tooltip>Editar</q-tooltip>
                  </q-btn>

                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    color="negative"
                    :disable="pessoa.id === usuario?.id"
                    @click="removerUsuario(pessoa)"
                  >
                    <q-tooltip>
                      {{
                        pessoa.id === usuario?.id
                          ? 'Você não pode excluir o seu próprio usuário'
                          : 'Excluir'
                      }}
                    </q-tooltip>
                  </q-btn>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>

        <!-- ================================================== -->
        <!-- FORMULÁRIO -->
        <!-- ================================================== -->

        <q-dialog v-model="dialogAberto">
          <q-card class="cartao-formulario">
            <q-card-section class="row items-center q-py-sm">
              <div class="text-subtitle1 text-weight-bold">
                {{ editando ? 'Editar usuário' : 'Novo usuário' }}
              </div>

              <q-space />

              <q-btn v-close-popup flat round dense icon="close" />
            </q-card-section>

            <q-separator />

            <q-card-section class="q-gutter-sm q-px-md q-py-sm corpo-formulario">
              <q-banner
                v-if="erroFormulario"
                dense
                class="bg-red-1 text-negative"
                rounded
              >
                {{ erroFormulario }}
              </q-banner>

              <q-input
                v-model="formulario.usuario"
                outlined
                dense
                label="Usuário (login)"
                hint="É o que a pessoa digita para entrar"
              />

              <q-input
                v-model="formulario.nome"
                outlined
                dense
                label="Nome completo"
              />

              <q-input
                v-model="formulario.senha"
                outlined
                dense
                type="password"
                autocomplete="new-password"
                :label="editando ? 'Nova senha (deixe em branco para manter)' : 'Senha'"
                :hint="`Mínimo de ${SENHA_MINIMA} caracteres`"
              />

              <q-select
                v-model="formulario.nivel"
                outlined
                dense
                emit-value
                map-options
                label="Nível de acesso"
                :options="opcoesNiveis"
              />

              <q-select
                v-if="nivelDoResponsavel"
                v-model="formulario.responsavel_id"
                outlined
                dense
                clearable
                emit-value
                map-options
                label="Responde a (responsável direto)"
                :hint="`Escolha um usuário do nível ${rotuloDoNivel(nivelDoResponsavel)}`"
                :options="opcoesResponsaveis"
              />

              <q-toggle
                v-model="formulario.ativo"
                label="Usuário ativo"
                :disable="editando && formulario.id === usuario?.id"
              />

              <!-- ------------------------------------------- -->
              <!-- VÍNCULOS -->
              <!-- ------------------------------------------- -->

              <q-separator />

              <div>
                <div class="text-subtitle2">Vínculos</div>

                <div class="text-caption text-grey-7 q-mb-sm">
                  <template v-if="nivelIgnoraVinculos">
                    O nível
                    <strong>{{ rotuloDoNivel(formulario.nivel) }}</strong>
                    enxerga todas as equipes — vínculos não se aplicam.
                  </template>

                  <template v-else>
                    Cada vínculo preenchido filtra uma dimensão; os que ficam
                    em branco não restringem. Só SETOR = todas as equipes
                    daquele setor, em qualquer base.
                    <strong>Sem nenhum vínculo a pessoa não enxerga equipe alguma</strong>

                    <template v-if="nivelSomaVinculoDeSubordinados">
                      — a não ser que algum Supervisor (ou Coordenador)
                      configurado para responder a ela tenha vínculo próprio:
                      o alcance final é a <strong>soma</strong> do vínculo
                      preenchido aqui com o de todos que respondem a ela.
                    </template>
                    <template v-else>.</template>
                  </template>
                </div>

                <div v-if="!nivelIgnoraVinculos" class="q-gutter-sm">
                  <template v-for="(rotulo, tipo) in tiposVinculo" :key="tipo">
                    <q-select
                      v-if="tipo === 'EQUIPE'"
                      v-model="formulario.vinculos[tipo]"
                      outlined
                      dense
                      multiple
                      use-chips
                      emit-value
                      map-options
                      :label="rotulo"
                      :options="opcoesEquipeVinculo"
                    />

                    <q-select
                      v-else
                      v-model="formulario.vinculos[tipo]"
                      outlined
                      dense
                      multiple
                      use-chips
                      use-input
                      new-value-mode="add-unique"
                      input-debounce="0"
                      :label="rotulo"
                      :options="opcoesVinculo[tipo] || []"
                    />
                  </template>
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right" class="q-py-sm">
              <q-btn v-close-popup flat dense label="Cancelar" />

              <q-btn
                dense
                color="primary"
                :label="editando ? 'Salvar' : 'Criar'"
                :loading="salvando"
                @click="salvar"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- ================================================== -->
        <!-- DETALHE DA IMPORTAÇÃO (novos / atualizados / rateios / erros) -->
        <!-- ================================================== -->

        <q-dialog v-model="dialogDetalheImportacao">
          <q-card style="width: 820px; max-width: 94vw">
            <q-card-section class="row items-center q-py-sm">
              <div class="text-h6">{{ tituloDetalheImportacao }}</div>
              <q-space />
              <q-btn v-close-popup flat round dense icon="close" />
            </q-card-section>

            <q-separator />

            <q-card-section class="q-pa-none" style="max-height: 62vh; overflow: auto">
              <q-markup-table flat dense separator="horizontal" class="tabela-detalhe">
                <thead>
                  <tr v-if="detalheImportacao === 'criados'">
                    <th class="text-left">Chapa</th>
                    <th class="text-left">Nome</th>
                    <th class="text-left">Função</th>
                    <th class="text-left">Seção</th>
                    <th class="text-left">Situação</th>
                    <th class="text-left">Admissão</th>
                  </tr>
                  <tr v-else-if="detalheImportacao === 'atualizados'">
                    <th class="text-left">Chapa</th>
                    <th class="text-left">Nome</th>
                    <th class="text-left">Campo</th>
                    <th class="text-left">De</th>
                    <th class="text-left">Para</th>
                  </tr>
                  <tr v-else-if="detalheImportacao === 'rateios'">
                    <th class="text-left">Chapa</th>
                    <th class="text-left">Nome</th>
                    <th class="text-left">Rateio</th>
                    <th class="text-left">Grupo de custo</th>
                  </tr>
                  <tr v-else>
                    <th class="text-left">Linha</th>
                    <th class="text-left">Chapa</th>
                    <th class="text-left">Nome</th>
                    <th class="text-left">Seção</th>
                    <th class="text-left">Erro</th>
                  </tr>
                </thead>

                <tbody v-if="detalheImportacao === 'criados'">
                  <tr v-for="item in resumoColaboradores?.detalhes_criados || []" :key="item.chapa">
                    <td>{{ item.chapa }}</td>
                    <td>{{ item.nome || '—' }}</td>
                    <td>{{ item.funcao || '—' }}</td>
                    <td>{{ item.secao || '—' }}</td>
                    <td>{{ item.situacao || '—' }}</td>
                    <td>{{ item.admissao }}</td>
                  </tr>
                </tbody>

                <!--
                  Atualizados vira uma linha POR MUDANÇA (de-para), não por
                  colaborador: chapa/nome só aparecem na primeira linha de
                  cada pessoa, pra leitura ficar em bloco.
                -->
                <tbody v-else-if="detalheImportacao === 'atualizados'">
                  <template
                    v-for="item in resumoColaboradores?.detalhes_atualizados || []"
                    :key="item.chapa"
                  >
                    <tr v-if="!item.mudancas?.length" class="linha-sem-mudanca">
                      <td>{{ item.chapa }}</td>
                      <td>{{ item.nome || '—' }}</td>
                      <td colspan="3" class="text-grey-7">
                        Sem alteração de campo — só reconfirmado pela planilha.
                      </td>
                    </tr>
                    <template v-else>
                      <tr
                        v-for="(mudanca, indice) in item.mudancas"
                        :key="`${item.chapa}-${indice}`"
                        :class="indice === 0 ? 'linha-inicio-grupo' : ''"
                      >
                        <td>{{ indice === 0 ? item.chapa : '' }}</td>
                        <td>{{ indice === 0 ? item.nome || '—' : '' }}</td>
                        <td class="text-weight-medium">{{ mudanca.campo }}</td>
                        <td class="text-grey-7">{{ mudanca.de }}</td>
                        <td class="text-positive text-weight-medium">{{ mudanca.para }}</td>
                      </tr>
                    </template>
                  </template>
                </tbody>

                <tbody v-else-if="detalheImportacao === 'rateios'">
                  <tr
                    v-for="(item, indice) in resumoColaboradores?.detalhes_rateios || []"
                    :key="indice"
                  >
                    <td>{{ item.chapa }}</td>
                    <td>{{ item.nome || '—' }}</td>
                    <td>{{ item.rateio }}</td>
                    <td>{{ item.grpccusto }}</td>
                  </tr>
                </tbody>

                <tbody v-else>
                  <tr
                    v-for="(item, indice) in resumoColaboradores?.erros || []"
                    :key="indice"
                  >
                    <td>{{ item.linha }}</td>
                    <td>{{ item.chapa || '—' }}</td>
                    <td>{{ item.nome || '—' }}</td>
                    <td>{{ item.secao || '—' }}</td>
                    <td class="text-negative">{{ item.erro }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </q-card-section>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import CabecalhoApp from '../components/CabecalhoApp.vue'
import MarcaDaguaFundo from '../components/MarcaDaguaFundo.vue'
import {
  PODE_GERENCIAR_COLABORADORES,
  PODE_GERENCIAR_USUARIOS,
  useSessao
} from '../composables/useSessao'

definePage({ meta: { permissao: PODE_GERENCIAR_USUARIOS } })

const {
  usuario,
  niveis,
  tiposVinculo,
  buscarSessao,
  temPermissao
} = useSessao()

const arquivoColaboradores = ref(null)
const baixandoModeloColaboradores = ref(false)
const dialogDetalheImportacao = ref(false)
const detalheImportacao = ref('criados')
const resumoColaboradores = ref(null)
const analisandoColaboradores = ref(false)
const aplicandoColaboradores = ref(false)

// planilha de usuários em lote (exportar -> editar -> conferir -> aplicar)
const arquivoUsuarios = ref(null)
const baixandoPlanilhaUsuarios = ref(false)
const planoUsuarios = ref(null)
const analisandoUsuarios = ref(false)
const aplicandoUsuarios = ref(false)

// novos e alterados numa lista só, na ordem da planilha — o "novo" de cada
// item é o que decide o selo e a cor na tela
const linhasPlanoUsuarios = computed(() => {
  if (!planoUsuarios.value) {
    return []
  }

  const novos = (planoUsuarios.value.criar || []).map(item => ({ ...item, novo: true }))
  const alterados = (planoUsuarios.value.atualizar || []).map(item => ({
    ...item,
    novo: false
  }))

  return [...novos, ...alterados].sort((a, b) => a.linha - b.linha)
})

// cópia local editável das permissões por nível, sincronizada sempre que
// 'niveis' (vindo da sessão) muda — assim dá pra marcar/desmarcar antes de
// salvar sem alterar o estado compartilhado da sessão
const permissoesEditaveis = reactive({})

watch(
  niveis,
  lista => {
    for (const nivel of lista) {
      permissoesEditaveis[nivel.valor] = [...nivel.permissoes]
    }
  },
  { immediate: true, deep: true }
)

const salvandoPermissoesNivel = ref('')

function alternarPermissaoNivel(nivelValor, permissaoValor) {
  const atuais = new Set(permissoesEditaveis[nivelValor] || [])
  if (atuais.has(permissaoValor)) {
    atuais.delete(permissaoValor)
  } else {
    atuais.add(permissaoValor)
  }
  permissoesEditaveis[nivelValor] = [...atuais]
}

async function salvarPermissoesNivel(nivelValor) {
  limparAvisos()
  salvandoPermissoesNivel.value = nivelValor

  try {
    const resposta = await fetch(`/api/niveis/${nivelValor}/permissoes`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ permissoes: permissoesEditaveis[nivelValor] || [] })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível salvar as permissões.')
    }

    niveis.value = dados.niveis
    sucesso.value = `Permissões do nível ${rotuloDoNivel(nivelValor)} atualizadas.`
  } catch (e) {
    erro.value = e.message || 'Não foi possível salvar as permissões.'
  } finally {
    salvandoPermissoesNivel.value = ''
  }
}

const SENHA_MINIMA = 6

// mesmos nomes do auth.py — cada uma é um "check" na tabela de níveis
const PERMISSOES = [
  { valor: 'ver_resumo', rotulo: 'Ver resumo' },
  { valor: 'ver_equipes', rotulo: 'Ver equipes' },
  { valor: 'alocar', rotulo: 'Alocar' },
  { valor: 'editar_alocacao', rotulo: 'Editar alocações' },
  { valor: 'remover_alocacao', rotulo: 'Remover' },
  { valor: 'gerenciar_vagas', rotulo: 'Cadastrar vagas' },
  { valor: 'gerenciar_usuarios', rotulo: 'Gerenciar usuários' },
  { valor: 'gerenciar_colaboradores', rotulo: 'Atualizar cadastro' }
]

const usuarios = ref([])
const equipes = ref([])
const carregando = ref(false)
// Spinner que OCUPA a tela inteira só na primeira abertura. Numa recarga
// (depois de alocar, salvar, aplicar planilha...) o conteúdo fica no lugar:
// trocar tudo pelo spinner desmontava a lista, a página encolhia para menos
// de uma tela e o navegador jogava a rolagem para o topo — além de fechar a
// equipe que estivesse aberta. O ícone de atualizar do cabeçalho continua
// girando, então o recarregamento não fica invisível.
const primeiraCarga = ref(true)
const erro = ref('')
const sucesso = ref('')

const dialogAberto = ref(false)
const editando = ref(false)
const salvando = ref(false)
const erroFormulario = ref('')

const formulario = reactive({
  id: null,
  usuario: '',
  nome: '',
  senha: '',
  nivel: '',
  ativo: true,
  vinculos: {},
  responsavel_id: null
})

const opcoesNiveis = computed(() =>
  niveis.value.map(nivel => ({ label: nivel.rotulo, value: nivel.valor }))
)

const nivelIgnoraVinculos = computed(
  () =>
    niveis.value.find(nivel => nivel.valor === formulario.nivel)
      ?.ignora_vinculos ?? false
)

// Este campo diz de QUE NIVEL e o responsavel de quem esta sendo editado.
const nivelDoResponsavel = computed(
  () =>
    niveis.value.find(nivel => nivel.valor === formulario.nivel)
      ?.nivel_do_responsavel || null
)

// Gerente/Coordenador: o alcance soma o vinculo da propria conta com o de
// todo Supervisor (ou Coordenador) que responde a ela — ver
// auth.escopo_efetivo. So pra ajustar o aviso da secao de Vinculos.
const nivelSomaVinculoDeSubordinados = computed(
  () =>
    niveis.value.find(nivel => nivel.valor === formulario.nivel)
      ?.soma_vinculo_de_subordinados ?? false
)

const opcoesResponsaveis = computed(() => {
  if (!nivelDoResponsavel.value) {
    return []
  }

  return usuarios.value
    .filter(
      pessoa =>
        pessoa.nivel === nivelDoResponsavel.value && pessoa.id !== formulario.id
    )
    .map(pessoa => ({ label: pessoa.nome, value: pessoa.id }))
    .sort((a, b) => a.label.localeCompare(b.label, 'pt-BR'))
})

// Sugestões vindas do que já está cadastrado nas vagas, para não digitar
// setor e supervisor de novo — mas o campo aceita texto novo também.
const opcoesVinculo = computed(() => {
  const mapa = {
    BASE: new Set(),
    TIPO_EQUIPE: new Set(),
    SETOR: new Set(),
    SUPERVISOR: new Set(),
    COORDENADOR: new Set()
  }

  for (const equipe of equipes.value) {
    if (equipe.base) {
      mapa.BASE.add(String(equipe.base).trim())
    }

    for (const vaga of equipe.vagas || []) {
      const tipo = String(vaga.tipo || '').trim()
      if (tipo) {
        mapa.TIPO_EQUIPE.add(tipo)
      }

      for (const campo of ['setor', 'supervisor', 'coordenador']) {
        const valor = String(vaga[campo] || '').trim()

        if (valor) {
          mapa[campo.toUpperCase()].add(valor)
        }
      }
    }
  }

  return Object.fromEntries(
    Object.entries(mapa).map(([tipo, valores]) => [
      tipo,
      [...valores].sort((a, b) => a.localeCompare(b, 'pt-BR'))
    ])
  )
})

const opcoesEquipeVinculo = computed(() =>
  [...equipes.value]
    .map(equipe => ({
      label: `${equipe.prefixo || 'Equipe'} — ${equipe.base || ''}`,
      value: String(equipe.id)
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'pt-BR'))
)

function rotuloDoNivel(valor) {
  return niveis.value.find(nivel => nivel.valor === valor)?.rotulo || valor
}

function resumoVinculos(pessoa) {
  const partes = Object.entries(pessoa.vinculos || {})
    .filter(([, valores]) => valores.length)
    .map(([tipo, valores]) => `${tiposVinculo.value[tipo] || tipo}: ${valores.join(', ')}`)

  return partes.join(' · ')
}

// A busca cobre tudo que a própria linha mostra — nome, login, nível, a
// quem responde e os vínculos. Procurar por "GOMAN" ou "PRES DUTRA" e achar
// quem tem aquele escopo é o caso mais útil no dia a dia, e sai de graça
// reaproveitando o mesmo resumoVinculos que a linha já exibe.
const filtroUsuario = ref('')

const usuariosFiltrados = computed(() => {
  const filtro = (filtroUsuario.value || '').trim().toLowerCase()

  if (!filtro) {
    return usuarios.value
  }

  return usuarios.value.filter(pessoa =>
    [
      pessoa.nome,
      pessoa.usuario,
      pessoa.nivel_rotulo,
      pessoa.responsavel_nome,
      resumoVinculos(pessoa)
    ]
      .filter(Boolean)
      .some(texto => String(texto).toLowerCase().includes(filtro))
  )
})

function limparAvisos() {
  erro.value = ''
  sucesso.value = ''
}

async function carregarTudo() {
  carregando.value = true
  limparAvisos()

  try {
    const [respostaUsuarios, respostaEquipes] = await Promise.all([
      fetch('/api/usuarios'),
      fetch('/api/equipes')
    ])

    const dadosUsuarios = await respostaUsuarios.json()

    if (!respostaUsuarios.ok || dadosUsuarios.erro) {
      throw new Error(dadosUsuarios.erro || 'Erro ao carregar os usuários.')
    }

    usuarios.value = dadosUsuarios

    // as sugestões de vínculo são um extra: se falharem, a tela segue
    const dadosEquipes = await respostaEquipes.json()
    equipes.value = Array.isArray(dadosEquipes) ? dadosEquipes : []
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar os usuários.'
  } finally {
    carregando.value = false
    primeiraCarga.value = false
  }
}

function preencher(pessoa) {
  formulario.id = pessoa?.id ?? null
  formulario.usuario = pessoa?.usuario || ''
  formulario.nome = pessoa?.nome || ''
  formulario.senha = ''
  formulario.nivel = pessoa?.nivel || niveis.value[0]?.valor || ''
  formulario.ativo = pessoa ? pessoa.ativo : true
  formulario.responsavel_id = pessoa?.responsavel_id ?? null
  formulario.vinculos = Object.fromEntries(
    Object.keys(tiposVinculo.value).map(tipo => [
      tipo,
      [...(pessoa?.vinculos?.[tipo] || [])]
    ])
  )
}

function abrirNovo() {
  erroFormulario.value = ''
  editando.value = false
  preencher(null)
  dialogAberto.value = true
}

function abrirEdicao(pessoa) {
  erroFormulario.value = ''
  editando.value = true
  preencher(pessoa)
  dialogAberto.value = true
}

async function salvar() {
  erroFormulario.value = ''
  salvando.value = true

  try {
    const corpo = {
      usuario: formulario.usuario.trim(),
      nome: formulario.nome.trim(),
      nivel: formulario.nivel,
      ativo: formulario.ativo,
      vinculos: nivelIgnoraVinculos.value ? {} : formulario.vinculos,
      responsavel_id: nivelDoResponsavel.value ? formulario.responsavel_id : null
    }

    if (formulario.senha) {
      corpo.senha = formulario.senha
    }

    const resposta = await fetch(
      editando.value ? `/api/usuarios/${formulario.id}` : '/api/usuarios',
      {
        method: editando.value ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo)
      }
    )

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível salvar o usuário.')
    }

    dialogAberto.value = false
    sucesso.value = editando.value ? 'Usuário atualizado.' : 'Usuário criado.'

    await carregarTudo()

    // se a pessoa mexeu no próprio cadastro, o menu precisa refletir isso
    if (formulario.id === usuario.value?.id) {
      await buscarSessao()
    }
  } catch (e) {
    erroFormulario.value = e.message || 'Não foi possível salvar o usuário.'
  } finally {
    salvando.value = false
  }
}

const chipsImportacao = computed(() => {
  const resumo = resumoColaboradores.value || {}

  return [
    {
      tipo: 'criados',
      cor: 'positive',
      rotulo: 'novo(s)',
      total: resumo.criados || 0
    },
    {
      tipo: 'atualizados',
      cor: 'primary',
      rotulo: 'atualizado(s)',
      total: resumo.atualizados || 0
    },
    {
      tipo: 'rateios',
      cor: 'grey-7',
      rotulo: 'rateio(s) novo(s)',
      total: resumo.rateios_novos || 0
    },
    {
      tipo: 'erros',
      cor: resumo.erros?.length ? 'negative' : 'grey-5',
      rotulo: 'com erro',
      total: resumo.erros?.length || 0
    }
  ]
})

const TITULOS_DETALHE_IMPORTACAO = {
  criados: 'Colaboradores novos',
  atualizados: 'Colaboradores atualizados (de → para)',
  rateios: 'Rateios novos',
  erros: 'Linhas com erro'
}

const tituloDetalheImportacao = computed(
  () => TITULOS_DETALHE_IMPORTACAO[detalheImportacao.value] || 'Detalhes'
)

function abrirDetalheImportacao(tipo) {
  const chip = chipsImportacao.value.find(item => item.tipo === tipo)

  if (!chip?.total) {
    return
  }

  detalheImportacao.value = tipo
  dialogDetalheImportacao.value = true
}

async function baixarModeloColaboradores() {
  limparAvisos()
  baixandoModeloColaboradores.value = true

  try {
    const resposta = await fetch('/api/colaboradores/planilha/modelo')

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw new Error(dados.erro || 'Erro ao gerar o modelo.')
    }

    const blob = await resposta.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'cadastro-colaboradores.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    erro.value = e.message || 'Erro ao gerar o modelo.'
  } finally {
    baixandoModeloColaboradores.value = false
  }
}

async function analisarPlanilhaColaboradores() {
  if (!arquivoColaboradores.value) {
    return
  }

  limparAvisos()
  analisandoColaboradores.value = true

  try {
    const corpo = new FormData()
    corpo.append('arquivo', arquivoColaboradores.value)

    const resposta = await fetch('/api/colaboradores/planilha/previa', {
      method: 'POST',
      body: corpo
    })

    const dados = await resposta.json()

    if (!resposta.ok && !dados.criados && !dados.atualizados) {
      throw new Error(dados.erro || 'Erro ao analisar a planilha.')
    }

    resumoColaboradores.value = dados
  } catch (e) {
    erro.value = e.message || 'Erro ao analisar a planilha.'
  } finally {
    analisandoColaboradores.value = false
  }
}

async function aplicarPlanilhaColaboradores() {
  if (!arquivoColaboradores.value) {
    return
  }

  limparAvisos()
  aplicandoColaboradores.value = true

  try {
    const corpo = new FormData()
    corpo.append('arquivo', arquivoColaboradores.value)

    const resposta = await fetch('/api/colaboradores/planilha/aplicar', {
      method: 'POST',
      body: corpo
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      resumoColaboradores.value = dados.resumo || resumoColaboradores.value
      throw new Error(dados.erro || 'Erro ao aplicar a planilha.')
    }

    sucesso.value =
      `Cadastro atualizado: ${dados.criados} novo(s), ` +
      `${dados.atualizados} atualizado(s), ${dados.rateios_novos} rateio(s) novo(s).`
    arquivoColaboradores.value = null
    resumoColaboradores.value = null
  } catch (e) {
    erro.value = e.message || 'Erro ao aplicar a planilha.'
  } finally {
    aplicandoColaboradores.value = false
  }
}

// ============================================================
// PLANILHA DE USUÁRIOS (EM LOTE)
// ============================================================

async function baixarPlanilhaUsuarios() {
  limparAvisos()
  baixandoPlanilhaUsuarios.value = true

  try {
    const resposta = await fetch('/api/usuarios/planilha')

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw new Error(dados.erro || 'Erro ao gerar a planilha de usuários.')
    }

    const blob = await resposta.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'usuarios.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    erro.value = e.message || 'Erro ao gerar a planilha de usuários.'
  } finally {
    baixandoPlanilhaUsuarios.value = false
  }
}

async function analisarPlanilhaUsuarios() {
  if (!arquivoUsuarios.value) {
    return
  }

  limparAvisos()
  analisandoUsuarios.value = true

  try {
    const corpo = new FormData()
    corpo.append('arquivo', arquivoUsuarios.value)

    const resposta = await fetch('/api/usuarios/planilha/previa', {
      method: 'POST',
      body: corpo
    })

    const dados = await resposta.json()

    // a prévia com linhas em erro volta 200 com a lista de erros dentro;
    // 400 aqui é problema no arquivo inteiro (coluna faltando, não é xlsx)
    if (!resposta.ok) {
      throw new Error(dados.erro || 'Erro ao analisar a planilha.')
    }

    planoUsuarios.value = dados
  } catch (e) {
    erro.value = e.message || 'Erro ao analisar a planilha.'
  } finally {
    analisandoUsuarios.value = false
  }
}

async function aplicarPlanilhaUsuarios() {
  if (!arquivoUsuarios.value) {
    return
  }

  limparAvisos()
  aplicandoUsuarios.value = true

  try {
    const corpo = new FormData()
    corpo.append('arquivo', arquivoUsuarios.value)

    const resposta = await fetch('/api/usuarios/planilha/aplicar', {
      method: 'POST',
      body: corpo
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      planoUsuarios.value = dados.plano || planoUsuarios.value
      throw new Error(dados.erro || 'Erro ao aplicar a planilha.')
    }

    sucesso.value =
      `Usuários atualizados: ${dados.criados} novo(s), ` +
      `${dados.atualizados} alterado(s), ${dados.ignoradas} sem mudança.`
    arquivoUsuarios.value = null
    planoUsuarios.value = null
    await carregarTudo()
  } catch (e) {
    erro.value = e.message || 'Erro ao aplicar a planilha.'
  } finally {
    aplicandoUsuarios.value = false
  }
}

async function removerUsuario(pessoa) {
  const confirmado = window.confirm(
    `Excluir o usuário "${pessoa.nome}" (${pessoa.usuario})?\n\n` +
      'Ele perde o acesso imediatamente. Isso não pode ser desfeito.'
  )

  if (!confirmado) {
    return
  }

  limparAvisos()

  try {
    const resposta = await fetch(`/api/usuarios/${pessoa.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível remover o usuário.')
    }

    sucesso.value = 'Usuário removido.'
    await carregarTudo()
  } catch (e) {
    erro.value = e.message || 'Não foi possível remover o usuário.'
  }
}

// trocar para um nível que ignora vínculos limpa o que estava escolhido
watch(nivelIgnoraVinculos, ignora => {
  if (ignora) {
    for (const tipo of Object.keys(formulario.vinculos)) {
      formulario.vinculos[tipo] = []
    }
  }
})

watch(nivelDoResponsavel, permitido => {
  if (!permitido) {
    formulario.responsavel_id = null
  }
})

onMounted(carregarTudo)
</script>

<style scoped>
.cartao-formulario {
  width: 100%;
  max-width: 440px;
}

/* o formulário é longo (dados + 4 vínculos); prende a altura na viewport pra
   o cartão não passar da tela em monitor baixo — rola só o miolo, deixando
   cabeçalho e botões sempre à vista */
.corpo-formulario {
  max-height: 68vh;
  overflow-y: auto;
}

.tabela-niveis :deep(th) {
  font-family: var(--fonte-ui);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.72rem;
}

/* tabela do diálogo de detalhe da importação */
.tabela-detalhe :deep(th) {
  font-family: var(--fonte-ui);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.7rem;
  position: sticky;
  top: 0;
  z-index: 1;
}

.tabela-detalhe :deep(td) {
  font-size: 0.8rem;
}

/* no "de-para", cada colaborador ocupa várias linhas (uma por campo
   alterado); a régua mais forte marca onde começa a próxima pessoa */
.tabela-detalhe :deep(tr.linha-inicio-grupo:not(:first-child) td),
.tabela-detalhe :deep(tr.linha-sem-mudanca:not(:first-child) td) {
  border-top: 2px solid var(--linha-forte);
}
</style>
