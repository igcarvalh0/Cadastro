<template>
  <q-layout view="lHh Lpr lFf">
    <MarcaDaguaFundo />

    <CabecalhoApp
      titulo="Cadastro de Vagas"
      :carregando="carregando"
      @atualizar="carregarEquipes"
    />

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="q-mb-md">
          <div class="text-h5"> Cadastro de Vagas </div>

          <div class="text-subtitle2 text-grey-7">
            Criação de equipes e das vagas disponíveis para alocação
          </div>
        </div>

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <q-banner
          v-if="sucesso"
          class="bg-green-1 text-positive q-mb-md"
          rounded
        >
          {{ sucesso }}
        </q-banner>

        <!-- ================================================== -->
        <!-- FORMULÁRIOS -->
        <!-- ================================================== -->

        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12 col-md-6">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Nova equipe </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-md">
                <q-select
                  v-model="novaEquipeBase"
                  outlined
                  dense
                  use-input
                  fill-input
                  hide-selected
                  input-debounce="0"
                  new-value-mode="add-unique"
                  label="Base"
                  hint="Selecione uma base existente ou digite uma nova"
                  :options="basesFiltradas"
                  @filter="filtrarBases"
                />

                <q-input
                  v-model="novaEquipePrefixo"
                  outlined
                  dense
                  label="Prefixo"
                  hint="Ex.: MA-BCB-O007M ou Folguista"
                />

                <q-btn
                  color="primary"
                  icon="group_add"
                  label="Criar equipe"
                  :disable="!podeCriarEquipe"
                  :loading="salvandoEquipe"
                  @click="criarEquipe"
                />
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-6">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Nova vaga </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-md">
                <q-select
                  v-model="vagaEquipe"
                  outlined
                  dense
                  use-input
                  fill-input
                  hide-selected
                  emit-value
                  map-options
                  input-debounce="0"
                  label="Equipe"
                  :options="equipesOpcoesFiltradas"
                  @filter="filtrarEquipesOpcoes"
                />

                <q-select
                  v-model="vagaFuncao"
                  outlined
                  dense
                  label="Função da vaga"
                  :options="FUNCOES_SISTEMA"
                />

                <q-select
                  v-model="vagaEstrutura"
                  outlined
                  dense
                  use-input
                  fill-input
                  hide-selected
                  input-debounce="0"
                  new-value-mode="add-unique"
                  label="Tipo de equipe (disciplina)"
                  hint="Ex.: CONSTRUÇÃO, PODA, LINHA VIVA..."
                  :options="estruturasFiltradas"
                  @filter="filtrarEstruturas"
                />

                <q-input v-model="vagaSetor" outlined dense label="Setor (opcional)" />

                <q-input
                  v-model="vagaSupervisor"
                  outlined
                  dense
                  label="Supervisor (opcional)"
                />

                <q-input
                  v-model="vagaCoordenador"
                  outlined
                  dense
                  label="Coordenador (opcional)"
                />

                <q-btn
                  color="primary"
                  icon="add"
                  label="Adicionar vaga"
                  :disable="!podeCriarVaga"
                  :loading="salvandoVaga"
                  @click="criarVaga"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- ================================================== -->
        <!-- PLANILHA EM MASSA -->
        <!-- ================================================== -->

        <q-card bordered class="q-mb-md">
          <q-card-section class="text-center">
            <div class="text-h6"> Cadastro em massa por planilha </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row q-col-gutter-md items-start">
              <div class="col-12 col-md-4">
                <q-btn
                  outline
                  color="primary"
                  icon="download"
                  label="Baixar planilha"
                  :loading="baixandoPlanilha"
                  class="full-width"
                  @click="baixarPlanilha"
                />
                <div class="text-caption text-grey-7 q-mt-sm">
                  Traz as equipes de hoje, uma por linha, com a quantidade de
                  cada função.
                </div>
              </div>

              <div class="col-12 col-md">
                <q-file
                  v-model="arquivoPlanilha"
                  outlined
                  dense
                  clearable
                  accept=".xlsx"
                  label="Planilha preenchida (.xlsx)"
                >
                  <template #prepend>
                    <q-icon name="attach_file" />
                  </template>
                </q-file>

                <div class="text-caption text-grey-7 q-mt-sm">
                  Preencha a coluna AÇÃO com <strong>criar</strong>,
                  <strong>editar</strong> ou <strong>excluir</strong>. Linha sem
                  ação é ignorada.
                </div>
              </div>

              <div class="col-12 col-md-auto">
                <q-btn
                  color="primary"
                  icon="fact_check"
                  label="Conferir mudanças"
                  :disable="!arquivoPlanilha"
                  :loading="analisandoPlanilha"
                  @click="analisarPlanilha"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- VAGAS CADASTRADAS -->
        <!-- ================================================== -->

        <q-card bordered>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">
                {{ modoVagas === 'lista' ? 'Vagas cadastradas' : 'Edição em massa' }}
              </div>

              <q-btn-toggle
                v-model="modoVagas"
                dense
                no-caps
                unelevated
                toggle-color="primary"
                color="grey-3"
                text-color="grey-8"
                :options="[
                  { label: 'Vagas cadastradas', value: 'lista' },
                  { label: 'Edição em massa', value: 'massa' }
                ]"
              />
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row q-col-gutter-md items-center filtros-campos">
              <div class="col-12 col-md-4">
                <q-select
                  :model-value="baseFiltro"
                  outlined
                  dense
                  clearable
                  multiple
                  use-chips
                  emit-value
                  map-options
                  label="Base"
                  :options="opcoesBaseFiltro"
                  @update:model-value="atualizarSelecaoBaseFiltro"
                >
                  <template #prepend>
                    <q-icon name="place" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="tipoFiltro"
                  outlined
                  dense
                  emit-value
                  map-options
                  label="Tipo"
                  :options="opcoesTipos"
                >
                  <template #prepend>
                    <q-icon name="category" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="setorFiltro"
                  outlined
                  dense
                  emit-value
                  map-options
                  label="Setor"
                  :options="opcoesSetores"
                >
                  <template #prepend>
                    <q-icon name="apartment" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md">
                <q-input
                  v-model="filtroEquipe"
                  outlined
                  dense
                  clearable
                  placeholder="Pesquisar por prefixo ou base..."
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>

              <div class="col-auto">
                <q-chip color="primary" text-color="white">
                  {{ equipesFiltradas.length }} equipe(s)
                </q-chip>
              </div>
            </div>
          </q-card-section>

          <div v-if="carregando" class="row justify-center q-pa-xl">
            <q-spinner color="primary" size="50px" />
          </div>

          <q-list v-else-if="modoVagas === 'lista'" separator>
            <div
              v-if="!equipesFiltradas.length"
              class="text-grey-7 q-pa-md text-center"
            >
              Nenhuma equipe encontrada.
            </div>

            <q-expansion-item
              v-for="equipe in equipesFiltradas"
              :key="equipe.id"
              expand-separator
              :label="equipe.prefixo || 'Equipe'"
              :caption="`${equipe.base || ''} — ${equipe.vagas.length} vaga(s)`"
            >
              <q-card flat>
                <q-card-section class="q-pb-none">
                  <div class="row q-gutter-sm justify-end">
                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="primary"
                      icon="edit"
                      label="Editar equipe"
                      @click="abrirEdicaoEquipe(equipe)"
                    />

                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="negative"
                      icon="person_remove"
                      label="Remover todos os colaboradores"
                      :disable="!equipe.vagas.some(vaga => vaga.ocupada)"
                      @click="liberarEquipe(equipe)"
                    >
                      <q-tooltip v-if="!equipe.vagas.some(vaga => vaga.ocupada)">
                        Nenhum colaborador alocado nesta equipe
                      </q-tooltip>
                    </q-btn>

                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="negative"
                      icon="delete_forever"
                      label="Excluir equipe"
                      :disable="equipe.vagas.some(vaga => vaga.ocupada)"
                      @click="removerEquipe(equipe)"
                    >
                      <q-tooltip v-if="equipe.vagas.some(vaga => vaga.ocupada)">
                        Remova os colaboradores alocados antes de excluir a
                        equipe
                      </q-tooltip>
                    </q-btn>
                  </div>
                </q-card-section>

                <q-card-section>
                  <div v-if="!equipe.vagas.length" class="text-grey-7">
                    Nenhuma vaga cadastrada nesta equipe.
                  </div>

                  <q-list v-else separator>
                    <q-item v-for="vaga in equipe.vagas" :key="vaga.id">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          {{ vaga.funcao_er || 'Função não informada' }}
                        </q-item-label>

                        <q-item-label caption>
                          {{
                            vaga.colaborador
                              ? `${vaga.colaborador.chapa} — ${vaga.colaborador.nome}`
                              : 'Sem colaborador alocado'
                          }}
                        </q-item-label>

                        <q-item-label
                          v-if="vaga.setor || vaga.supervisor || vaga.coordenador"
                          caption
                        >
                          {{
                            [
                              vaga.setor && `Setor: ${vaga.setor}`,
                              vaga.supervisor && `Supervisor: ${vaga.supervisor}`,
                              vaga.coordenador && `Coordenador: ${vaga.coordenador}`
                            ]
                              .filter(Boolean)
                              .join(' · ')
                          }}
                        </q-item-label>
                      </q-item-section>

                      <q-item-section side>
                        <div class="row items-center no-wrap">
                          <q-chip
                            v-if="vaga.ocupada"
                            color="positive"
                            text-color="white"
                            size="sm"
                          >
                            OCUPADA
                          </q-chip>

                          <q-chip
                            v-else
                            color="grey-6"
                            text-color="white"
                            size="sm"
                          >
                            LIVRE
                          </q-chip>

                          <q-btn
                            flat
                            round
                            dense
                            color="negative"
                            icon="delete"
                            class="q-ml-sm"
                            aria-label="Excluir vaga"
                            :disable="vaga.ocupada"
                            @click="removerVaga(vaga)"
                          >
                            <q-tooltip v-if="vaga.ocupada">
                              Remova o colaborador antes de excluir a vaga
                            </q-tooltip>
                          </q-btn>
                        </div>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </q-list>

          <!-- ============================================== -->
          <!-- EDIÇÃO EM MASSA -->
          <!-- ============================================== -->

          <q-card-section v-else>
            <div class="row q-col-gutter-sm items-end q-mb-md">
              <div class="col-12 col-md-3">
                <q-select
                  v-model="bulkSetor"
                  outlined
                  dense
                  clearable
                  label="Setor (aplicar aos filtrados)"
                  :options="setoresNegocio"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-input
                  v-model="bulkSupervisor"
                  outlined
                  dense
                  label="Supervisor (aplicar aos filtrados)"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-input
                  v-model="bulkCoordenador"
                  outlined
                  dense
                  label="Coordenador (aplicar aos filtrados)"
                />
              </div>
              <div class="col-12 col-md-auto">
                <q-btn
                  outline
                  color="primary"
                  label="Aplicar às equipes filtradas"
                  :disable="!equipesFiltradas.length"
                  @click="aplicarCamposEmMassa"
                />
              </div>
            </div>

            <div
              v-if="!equipesFiltradas.length"
              class="text-grey-7 q-pa-md text-center"
            >
              Nenhuma equipe encontrada para os filtros atuais.
            </div>

            <q-card
              v-for="equipe in equipesFiltradas"
              :key="equipe.id"
              flat
              bordered
              class="q-mb-sm"
            >
              <q-card-section>
                <div class="row q-col-gutter-sm items-center">
                  <div class="col-12 col-md-2">
                    <div class="text-weight-medium">
                      {{ equipe.prefixo || 'Equipe' }}
                    </div>
                    <div class="text-caption text-grey-7">
                      {{ equipe.vagas.length }} vaga(s)
                    </div>
                  </div>

                  <div class="col-6 col-md-2">
                    <q-input
                      v-model="obterLinhaMassa(equipe).base"
                      dense
                      outlined
                      label="Base"
                    />
                  </div>

                  <div class="col-6 col-md-2">
                    <q-select
                      v-model="obterLinhaMassa(equipe).setor"
                      dense
                      outlined
                      clearable
                      label="Setor"
                      :options="setoresNegocio"
                    />
                  </div>

                  <div class="col-6 col-md-2">
                    <q-input
                      v-model="obterLinhaMassa(equipe).supervisor"
                      dense
                      outlined
                      label="Supervisor"
                    />
                  </div>

                  <div class="col-6 col-md-2">
                    <q-input
                      v-model="obterLinhaMassa(equipe).coordenador"
                      dense
                      outlined
                      label="Coordenador"
                    />
                  </div>

                  <div class="col-12 col-md-auto">
                    <q-btn
                      flat
                      dense
                      no-caps
                      icon="tune"
                      color="primary"
                      :label="obterLinhaMassa(equipe).mostrarVagas ? 'Ocultar vagas' : 'Vagas por função'"
                      @click="obterLinhaMassa(equipe).mostrarVagas = !obterLinhaMassa(equipe).mostrarVagas"
                    />
                  </div>
                </div>

                <div
                  v-if="obterLinhaMassa(equipe).mostrarVagas"
                  class="q-mt-sm q-gutter-sm"
                >
                  <q-separator />

                  <div
                    v-for="(linha, indice) in obterLinhaMassa(equipe).vagas"
                    :key="indice"
                    class="row q-col-gutter-sm items-center"
                  >
                    <div class="col-4">
                      <q-select
                        v-model="linha.tipo"
                        dense
                        outlined
                        use-input
                        new-value-mode="add-unique"
                        label="Tipo"
                        :options="estruturasDisponiveis"
                      />
                    </div>
                    <div class="col-4">
                      <q-select
                        v-model="linha.funcao"
                        dense
                        outlined
                        label="Função"
                        :options="FUNCOES_SISTEMA"
                      />
                    </div>
                    <div class="col-3">
                      <q-input
                        v-model.number="linha.quantidade"
                        dense
                        outlined
                        type="number"
                        min="0"
                        label="Qtd."
                      />
                    </div>
                    <div class="col-1">
                      <q-btn
                        flat
                        round
                        dense
                        icon="delete"
                        color="negative"
                        @click="obterLinhaMassa(equipe).vagas.splice(indice, 1)"
                      />
                    </div>
                  </div>

                  <q-btn
                    flat
                    dense
                    icon="add"
                    label="Adicionar linha"
                    color="primary"
                    @click="
                      obterLinhaMassa(equipe).vagas.push({
                        tipo: 'CONSTRUÇÃO',
                        funcao: null,
                        quantidade: 0
                      })
                    "
                  />
                </div>
              </q-card-section>
            </q-card>

            <div v-if="equipesFiltradas.length" class="row justify-end q-mt-md">
              <q-btn
                color="primary"
                label="Salvar edição em massa"
                :loading="salvandoMassa"
                @click="salvarEdicaoMassa"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>

    <!-- ==================================================== -->
    <!-- EDIÇÃO DE EQUIPE -->
    <!-- ==================================================== -->

    <q-dialog v-model="dialogEdicao">
      <q-card style="min-width: 420px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6"> Editar equipe </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md" style="max-height: 70vh" >
          <q-select
            v-model="edicaoBase"
            outlined
            dense
            use-input
            fill-input
            hide-selected
            input-debounce="0"
            new-value-mode="add-unique"
            label="Base"
            :options="basesFiltradas"
            @filter="filtrarBases"
          />

          <q-input v-model="edicaoPrefixo" outlined dense label="Prefixo" />

          <q-select
            v-model="edicaoSetor"
            outlined
            dense
            clearable
            label="Setor"
            :options="setoresNegocio"
          />

          <q-input v-model="edicaoSupervisor" outlined dense label="Supervisor" />

          <q-input v-model="edicaoCoordenador" outlined dense label="Coordenador" />

          <q-separator />

          <div class="text-subtitle2">Vagas por função</div>

          <div
            v-for="(linha, indice) in edicaoVagas"
            :key="indice"
            class="row q-col-gutter-sm items-center"
          >
            <div class="col-4">
              <q-select
                v-model="linha.tipo"
                outlined
                dense
                use-input
                new-value-mode="add-unique"
                label="Tipo"
                :options="estruturasDisponiveis"
              />
            </div>
            <div class="col-4">
              <q-select
                v-model="linha.funcao"
                outlined
                dense
                label="Função"
                :options="FUNCOES_SISTEMA"
              />
            </div>
            <div class="col-3">
              <q-input
                v-model.number="linha.quantidade"
                outlined
                dense
                type="number"
                min="0"
                label="Qtd."
              />
            </div>
            <div class="col-1">
              <q-btn
                flat
                round
                dense
                icon="delete"
                color="negative"
                @click="edicaoVagas.splice(indice, 1)"
              />
            </div>
          </div>

          <q-btn
            flat
            dense
            icon="add"
            label="Adicionar linha"
            color="primary"
            @click="edicaoVagas.push({ tipo: 'CONSTRUÇÃO', funcao: null, quantidade: 0 })"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Cancelar" color="grey-7" />

          <q-btn
            color="primary"
            label="Salvar"
            :disable="!podeSalvarEdicao"
            :loading="salvandoEdicao"
            @click="salvarEdicaoEquipe()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ==================================================== -->
    <!-- PRÉVIA DA PLANILHA -->
    <!-- ==================================================== -->

    <q-dialog v-model="dialogPlanilha">
      <q-card style="min-width: 560px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6"> Conferir mudanças </div>
          <div class="text-caption text-grey-7">
            Nada foi gravado ainda. Confira e confirme.
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: 60vh" class="scroll">
          <div v-if="planoPlanilha" class="q-gutter-md">
            <div class="row q-gutter-sm">
              <q-chip
                :color="planoPlanilha.criar.length ? 'positive' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.criar.length }} a criar
              </q-chip>
              <q-chip
                :color="planoPlanilha.editar.length ? 'primary' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.editar.length }} a editar
              </q-chip>
              <q-chip
                :color="planoPlanilha.excluir.length ? 'negative' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.excluir.length }} a excluir
              </q-chip>
              <q-chip
                :color="planoPlanilha.erros.length ? 'negative' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.erros.length }} com erro
              </q-chip>
              <q-chip color="grey-6" text-color="white">
                {{ planoPlanilha.ignoradas }} sem alteração
              </q-chip>
            </div>

            <q-banner
              v-if="planoPlanilha.erros.length"
              class="bg-red-1 text-negative"
              rounded
            >
              Corrija as linhas com erro antes de aplicar. Nada será gravado
              enquanto houver erro.
            </q-banner>

            <div v-if="planoPlanilha.erros.length">
              <div class="text-subtitle2 text-negative q-mb-xs"> Erros </div>
              <q-list bordered separator dense>
                <q-item v-for="e in planoPlanilha.erros" :key="'e' + e.linha">
                  <q-item-section>
                    <q-item-label>
                      Linha {{ e.linha }} — {{ e.equipe }}
                    </q-item-label>
                    <q-item-label caption class="text-negative">
                      {{ e.erro }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.criar.length">
              <div class="text-subtitle2 q-mb-xs"> Criar </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.criar" :key="'c' + i.linha">
                  <q-item-section>
                    <q-item-label>
                      {{ i.equipe }}
                      <q-badge
                        v-if="i.era_edicao"
                        color="orange"
                        text-color="white"
                        class="q-ml-sm"
                      >
                        equipe nova
                      </q-badge>
                    </q-item-label>
                    <q-item-label caption>
                      {{ i.total }} vaga(s):
                      {{
                        Object.entries(i.vagas)
                          .map(([f, q]) => q + ' ' + f)
                          .join(', ')
                      }}
                    </q-item-label>
                    <q-item-label v-if="i.era_edicao" caption class="text-orange-9">
                      A linha {{ i.linha }} está como "editar", mas essa equipe
                      ainda não existe — será criada.
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.editar.length">
              <div class="text-subtitle2 q-mb-xs"> Editar </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.editar" :key="'ed' + i.linha">
                  <q-item-section>
                    <q-item-label>{{ i.equipe }}</q-item-label>
                    <q-item-label caption>{{ i.resumo }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.excluir.length">
              <div class="text-subtitle2 text-negative q-mb-xs"> Excluir </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.excluir" :key="'x' + i.linha">
                  <q-item-section>
                    <q-item-label>{{ i.equipe }}</q-item-label>
                    <q-item-label caption>
                      perde {{ i.vagas }} vaga(s) cadastrada(s)
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Cancelar" color="grey-7" />

          <q-btn
            color="primary"
            label="Aplicar"
            :disable="!podeAplicarPlanilha"
            :loading="aplicandoPlanilha"
            @click="aplicarPlanilha"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

import CabecalhoApp from '../components/CabecalhoApp.vue'
import MarcaDaguaFundo from '../components/MarcaDaguaFundo.vue'
import {
  equipeCombinaComSetor,
  equipeCombinaComTipo,
  equipeNaSelecaoDeBases,
  FUNCOES_SISTEMA,
  OPCAO_TODAS_BASES,
  opcoesSetorFiltro,
  opcoesTipoFiltro,
  proximaSelecaoBases,
  SETOR_TODOS,
  TIPO_TODOS
} from '../utils/equipes'

// ============================================================
// ESTADO
// ============================================================

const equipes = ref([])

const carregando = ref(false)

const erro = ref('')
const sucesso = ref('')

const novaEquipeBase = ref(null)
const novaEquipePrefixo = ref('')
const salvandoEquipe = ref(false)

const vagaEquipe = ref(null)
const vagaFuncao = ref(null)
const vagaEstrutura = ref(null)
const vagaSetor = ref('')
const vagaSupervisor = ref('')
const vagaCoordenador = ref('')
const salvandoVaga = ref(false)
const estruturasFiltradas = ref([])

const filtroEquipe = ref('')
const baseFiltro = ref([])
const tipoFiltro = ref(TIPO_TODOS)
const setorFiltro = ref(SETOR_TODOS)

const arquivoPlanilha = ref(null)
const planoPlanilha = ref(null)
const dialogPlanilha = ref(false)
const baixandoPlanilha = ref(false)
const analisandoPlanilha = ref(false)
const aplicandoPlanilha = ref(false)

const dialogEdicao = ref(false)
const equipeEmEdicao = ref(null)
const edicaoBase = ref(null)
const edicaoPrefixo = ref('')
const edicaoSetor = ref(null)
const edicaoSupervisor = ref('')
const edicaoCoordenador = ref('')
const edicaoVagas = ref([])
const salvandoEdicao = ref(false)
const setoresNegocio = ref([])

const basesFiltradas = ref([])
const equipesOpcoesFiltradas = ref([])

// alterna entre a lista de vagas cadastradas e a grade de edição em massa,
// para nao deixar as duas visiveis e a tela pesada ao mesmo tempo
const modoVagas = ref('massa')
const edicaoMassa = ref({})
const salvandoMassa = ref(false)
const bulkSetor = ref(null)
const bulkSupervisor = ref('')
const bulkCoordenador = ref('')

// ============================================================
// DERIVADOS
// ============================================================

const estruturasDisponiveis = computed(() => {
  const valores = new Set()

  equipes.value.forEach(equipe => {
    ;(equipe.tipos || []).forEach(tipo => tipo && valores.add(tipo))
  })

  return valores.size ? [...valores].sort() : ['CONSTRUÇÃO']
})

const bases = computed(() => {
  const valores = new Set()

  equipes.value.forEach(equipe => {
    if (equipe.base) {
      valores.add(equipe.base)
    }
  })

  return [...valores].sort()
})

const opcoesBaseFiltro = computed(() => [
  { label: 'Todas as bases', value: OPCAO_TODAS_BASES },
  ...bases.value.map(base => ({ label: base, value: base }))
])

function atualizarSelecaoBaseFiltro(selecao) {
  baseFiltro.value = proximaSelecaoBases(baseFiltro.value, selecao)
}

const opcoesTipos = computed(() => opcoesTipoFiltro(equipes.value))

const opcoesSetores = computed(() => opcoesSetorFiltro(equipes.value))

const equipesOpcoes = computed(() =>
  equipes.value.map(equipe => ({
    label: `${equipe.prefixo} — ${equipe.base}`,
    value: equipe.id
  }))
)

const equipesFiltradas = computed(() => {
  const termo = (filtroEquipe.value || '').trim().toLowerCase()
  const basesEscolhidas = baseFiltro.value || []

  return equipes.value.filter(equipe => {
    if (!equipeNaSelecaoDeBases(equipe, basesEscolhidas)) {
      return false
    }

    if (!equipeCombinaComTipo(equipe, tipoFiltro.value)) {
      return false
    }

    if (!equipeCombinaComSetor(equipe, setorFiltro.value)) {
      return false
    }

    return (
      !termo || `${equipe.prefixo} ${equipe.base}`.toLowerCase().includes(termo)
    )
  })
})

const podeAplicarPlanilha = computed(() => {
  const plano = planoPlanilha.value
  if (!plano || plano.erros.length) {
    return false
  }
  return Boolean(plano.criar.length || plano.editar.length || plano.excluir.length)
})

const podeSalvarEdicao = computed(() =>
  Boolean((edicaoBase.value || '').trim() && edicaoPrefixo.value.trim())
)

const podeCriarEquipe = computed(() =>
  Boolean(
    (novaEquipeBase.value || '').trim() && novaEquipePrefixo.value.trim()
  )
)

const podeCriarVaga = computed(() =>
  Boolean(vagaEquipe.value && vagaFuncao.value && vagaEstrutura.value)
)

// ============================================================
// FILTROS DOS SELECTS
// ============================================================

function filtrarBases(termo, update) {
  update(() => {
    const busca = termo.toLowerCase()

    basesFiltradas.value = busca
      ? bases.value.filter(base => base.toLowerCase().includes(busca))
      : bases.value
  })
}

function filtrarEstruturas(termo, update) {
  update(() => {
    const busca = termo.toUpperCase()

    estruturasFiltradas.value = busca
      ? estruturasDisponiveis.value.filter(tipo => tipo.toUpperCase().includes(busca))
      : estruturasDisponiveis.value
  })
}

function filtrarEquipesOpcoes(termo, update) {
  update(() => {
    const busca = termo.toLowerCase()

    equipesOpcoesFiltradas.value = busca
      ? equipesOpcoes.value.filter(opcao =>
          opcao.label.toLowerCase().includes(busca)
        )
      : equipesOpcoes.value
  })
}

// ============================================================
// AÇÕES
// ============================================================

async function carregarEquipes() {
  carregando.value = true

  try {
    const resposta = await fetch('/api/equipes')
    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao carregar as equipes.')
    }

    equipes.value = dados
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar as equipes.'
  } finally {
    carregando.value = false
  }
}

async function criarEquipe() {
  erro.value = ''
  sucesso.value = ''
  salvandoEquipe.value = true

  try {
    const resposta = await fetch('/api/equipes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base: novaEquipeBase.value,
        prefixo: novaEquipePrefixo.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao criar a equipe.')
    }

    sucesso.value = `Equipe ${dados.equipe.prefixo} criada com sucesso.`
    novaEquipePrefixo.value = ''

    await carregarEquipes()
    vagaEquipe.value = dados.equipe.id
  } catch (e) {
    erro.value = e.message || 'Erro ao criar a equipe.'
  } finally {
    salvandoEquipe.value = false
  }
}

async function criarVaga() {
  erro.value = ''
  sucesso.value = ''
  salvandoVaga.value = true

  try {
    const resposta = await fetch('/api/equipes/vagas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        equipe_id: vagaEquipe.value,
        funcao_er: vagaFuncao.value,
        estrutura: (vagaEstrutura.value || '').toUpperCase(),
        setor: vagaSetor.value,
        supervisor: vagaSupervisor.value,
        coordenador: vagaCoordenador.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao criar a vaga.')
    }

    sucesso.value = `Vaga de ${dados.vaga.funcao_er} adicionada com sucesso.`
    vagaFuncao.value = null

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao criar a vaga.'
  } finally {
    salvandoVaga.value = false
  }
}

async function removerVaga(vaga) {
  if (!window.confirm('Deseja realmente excluir esta vaga?')) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/vagas/${vaga.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao excluir a vaga.')
    }

    sucesso.value = 'Vaga excluída com sucesso.'

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao excluir a vaga.'
  }
}

async function baixarPlanilha() {
  erro.value = ''
  baixandoPlanilha.value = true

  try {
    const resposta = await fetch('/api/equipes/planilha')

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw new Error(dados.erro || 'Erro ao gerar a planilha.')
    }

    const blob = await resposta.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'equipes.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    erro.value = e.message || 'Erro ao gerar a planilha.'
  } finally {
    baixandoPlanilha.value = false
  }
}

async function enviarPlanilha(rota) {
  const corpo = new FormData()
  corpo.append('arquivo', arquivoPlanilha.value)

  const resposta = await fetch(rota, { method: 'POST', body: corpo })
  const dados = await resposta.json()

  return { ok: resposta.ok, dados }
}

async function analisarPlanilha() {
  if (!arquivoPlanilha.value) {
    return
  }

  erro.value = ''
  sucesso.value = ''
  analisandoPlanilha.value = true

  try {
    const { ok, dados } = await enviarPlanilha('/api/equipes/planilha/previa')

    if (!ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao analisar a planilha.')
    }

    planoPlanilha.value = dados
    dialogPlanilha.value = true
  } catch (e) {
    erro.value = e.message || 'Erro ao analisar a planilha.'
  } finally {
    analisandoPlanilha.value = false
  }
}

async function aplicarPlanilha() {
  erro.value = ''
  sucesso.value = ''
  aplicandoPlanilha.value = true

  try {
    const { ok, dados } = await enviarPlanilha('/api/equipes/planilha/aplicar')

    if (!ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao aplicar a planilha.')
    }

    sucesso.value =
      `Planilha aplicada: ${dados.criadas} equipe(s) criada(s), ` +
      `${dados.editadas} editada(s), ${dados.excluidas} excluída(s).`

    dialogPlanilha.value = false
    planoPlanilha.value = null
    arquivoPlanilha.value = null

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao aplicar a planilha.'
  } finally {
    aplicandoPlanilha.value = false
  }
}

function abrirEdicaoEquipe(equipe) {
  equipeEmEdicao.value = equipe
  edicaoBase.value = equipe.base
  edicaoPrefixo.value = equipe.prefixo

  const vagasPadrao = (equipe.vagas || []).filter(vaga => !vaga.eh_extra)
  edicaoSetor.value = vagasPadrao.find(vaga => vaga.setor)?.setor || null
  edicaoSupervisor.value = vagasPadrao.find(vaga => vaga.supervisor)?.supervisor || ''
  edicaoCoordenador.value = vagasPadrao.find(vaga => vaga.coordenador)?.coordenador || ''

  const agrupado = new Map()
  for (const vaga of vagasPadrao) {
    const chave = `${vaga.tipo}|${vaga.funcao_er}`
    agrupado.set(chave, (agrupado.get(chave) || 0) + 1)
  }

  edicaoVagas.value = [...agrupado.entries()].map(([chave, quantidade]) => {
    const [tipo, funcao] = chave.split('|')
    return { tipo, funcao, quantidade }
  })

  dialogEdicao.value = true
}

// calcula, por (tipo, funcao), quantas vagas OCUPADAS precisariam ser
// removidas para a nova quantidade pedida caber — o backend bloqueia essa
// redução sem confirmação explícita, então perguntamos aqui antes de enviar.
function calcularConflitosReducao() {
  const vagasPadrao = (equipeEmEdicao.value?.vagas || []).filter(
    vaga => !vaga.eh_extra
  )
  const porChave = new Map()

  for (const vaga of vagasPadrao) {
    const chave = `${vaga.tipo}|${vaga.funcao_er}`
    if (!porChave.has(chave)) {
      porChave.set(chave, [])
    }
    porChave.get(chave).push(vaga)
  }

  const conflitos = []

  for (const linha of edicaoVagas.value) {
    const chave = `${linha.tipo}|${linha.funcao}`
    const vagas = porChave.get(chave) || []
    const livres = vagas.filter(vaga => !vaga.colaborador)
    const ocupadas = vagas.filter(vaga => vaga.colaborador)
    const reducao = vagas.length - Number(linha.quantidade || 0)

    if (reducao > livres.length) {
      const precisaRemover = reducao - livres.length
      conflitos.push({
        tipo: linha.tipo,
        funcao: linha.funcao,
        vagas: ocupadas.slice(0, precisaRemover)
      })
    }
  }

  return conflitos
}

async function salvarEdicaoEquipe(confirmarRemocoesIds = null) {
  erro.value = ''
  sucesso.value = ''

  let confirmarRemocoes = confirmarRemocoesIds

  if (!confirmarRemocoes) {
    const conflitos = calcularConflitosReducao()

    if (conflitos.length) {
      const detalhe = conflitos
        .map(
          c =>
            `${c.funcao} (${c.tipo}): ${c.vagas
              .map(v => `${v.colaborador?.chapa} - ${v.colaborador?.nome}`)
              .join(', ')}`
        )
        .join('\n')

      if (
        !window.confirm(
          'Reduzir a quantidade vai remover colaborador(es) já alocado(s):\n\n' +
            `${detalhe}\n\n` +
            'Confirma a remoção desses colaboradores?'
        )
      ) {
        return
      }

      confirmarRemocoes = conflitos.flatMap(c => c.vagas.map(v => v.id))
    } else {
      confirmarRemocoes = []
    }
  }

  salvandoEdicao.value = true

  try {
    const resposta = await fetch(`/api/equipes/${equipeEmEdicao.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base: edicaoBase.value,
        prefixo: edicaoPrefixo.value,
        setor: edicaoSetor.value,
        supervisor: edicaoSupervisor.value,
        coordenador: edicaoCoordenador.value,
        vagas: edicaoVagas.value.filter(linha => linha.funcao),
        confirmar_remocoes: confirmarRemocoes
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao atualizar a equipe.')
    }

    sucesso.value = `Equipe ${dados.equipe.prefixo} atualizada com sucesso.`
    dialogEdicao.value = false

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao atualizar a equipe.'
  } finally {
    salvandoEdicao.value = false
  }
}

// ============================================================
// EDIÇÃO EM MASSA (várias equipes de uma vez, sem planilha)
// ============================================================

function linhaEdicaoMassa(equipe) {
  const vagasPadrao = (equipe.vagas || []).filter(vaga => !vaga.eh_extra)

  const agrupado = new Map()
  for (const vaga of vagasPadrao) {
    const chave = `${vaga.tipo}|${vaga.funcao_er}`
    agrupado.set(chave, (agrupado.get(chave) || 0) + 1)
  }

  return {
    base: equipe.base,
    prefixo: equipe.prefixo,
    setor: vagasPadrao.find(vaga => vaga.setor)?.setor || null,
    supervisor: vagasPadrao.find(vaga => vaga.supervisor)?.supervisor || '',
    coordenador: vagasPadrao.find(vaga => vaga.coordenador)?.coordenador || '',
    vagas: [...agrupado.entries()].map(([chave, quantidade]) => {
      const [tipo, funcao] = chave.split('|')
      return { tipo, funcao, quantidade }
    }),
    mostrarVagas: false
  }
}

// inicializa a linha de edicao da equipe na primeira vez que ela aparece na
// grade, e devolve sempre a MESMA referencia depois — assim os campos que o
// usuario ja editou nao sao perdidos quando o filtro muda a lista
function obterLinhaMassa(equipe) {
  if (!edicaoMassa.value[equipe.id]) {
    edicaoMassa.value[equipe.id] = linhaEdicaoMassa(equipe)
  }
  return edicaoMassa.value[equipe.id]
}

function aplicarCamposEmMassa() {
  for (const equipe of equipesFiltradas.value) {
    const linha = obterLinhaMassa(equipe)
    if (bulkSetor.value !== null) {
      linha.setor = bulkSetor.value
    }
    if (bulkSupervisor.value.trim()) {
      linha.supervisor = bulkSupervisor.value
    }
    if (bulkCoordenador.value.trim()) {
      linha.coordenador = bulkCoordenador.value
    }
  }
}

// mesma regra de calcularConflitosReducao, mas para uma equipe qualquer da
// grade em massa, nao so a que esta no dialog de edicao individual
function calcularConflitosReducaoEquipe(equipe, linha) {
  const vagasPadrao = (equipe.vagas || []).filter(vaga => !vaga.eh_extra)
  const porChave = new Map()

  for (const vaga of vagasPadrao) {
    const chave = `${vaga.tipo}|${vaga.funcao_er}`
    if (!porChave.has(chave)) {
      porChave.set(chave, [])
    }
    porChave.get(chave).push(vaga)
  }

  const conflitos = []

  for (const l of linha.vagas) {
    const chave = `${l.tipo}|${l.funcao}`
    const vagas = porChave.get(chave) || []
    const livres = vagas.filter(vaga => !vaga.colaborador)
    const ocupadas = vagas.filter(vaga => vaga.colaborador)
    const reducao = vagas.length - Number(l.quantidade || 0)

    if (reducao > livres.length) {
      const precisaRemover = reducao - livres.length
      conflitos.push(...ocupadas.slice(0, precisaRemover))
    }
  }

  return conflitos
}

async function salvarEdicaoMassa() {
  erro.value = ''
  sucesso.value = ''

  const conflitosPorEquipe = new Map()
  for (const equipe of equipesFiltradas.value) {
    const linha = obterLinhaMassa(equipe)
    const conflitos = calcularConflitosReducaoEquipe(equipe, linha)
    if (conflitos.length) {
      conflitosPorEquipe.set(equipe.id, conflitos)
    }
  }

  if (conflitosPorEquipe.size) {
    const detalhe = [...conflitosPorEquipe.entries()]
      .map(([id, vagas]) => {
        const equipe = equipesFiltradas.value.find(e => e.id === id)
        return (
          `${equipe?.prefixo}: ` +
          vagas.map(v => `${v.colaborador?.chapa} - ${v.colaborador?.nome}`).join(', ')
        )
      })
      .join('\n')

    if (
      !window.confirm(
        'Reduzir a quantidade de vagas vai remover colaborador(es) já alocado(s):\n\n' +
          `${detalhe}\n\n` +
          'Confirma a remoção desses colaboradores em todas as equipes listadas?'
      )
    ) {
      return
    }
  }

  salvandoMassa.value = true

  try {
    const equipesPayload = equipesFiltradas.value.map(equipe => {
      const linha = obterLinhaMassa(equipe)
      return {
        equipe_id: equipe.id,
        base: linha.base,
        prefixo: linha.prefixo,
        setor: linha.setor,
        supervisor: linha.supervisor,
        coordenador: linha.coordenador,
        vagas: linha.vagas.filter(v => v.funcao),
        confirmar_remocoes: (conflitosPorEquipe.get(equipe.id) || []).map(v => v.id)
      }
    })

    const resposta = await fetch('/api/equipes/edicao-massa', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ equipes: equipesPayload })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      if (dados.erros?.length) {
        erro.value =
          `${dados.erro} ` +
          dados.erros.map(e => `${e.equipe}: ${e.erro}`).join(' | ')
      } else {
        throw new Error(dados.erro || 'Erro ao salvar a edição em massa.')
      }
      return
    }

    sucesso.value = `${dados.equipes_editadas} equipe(s) atualizada(s) com sucesso.`
    edicaoMassa.value = {}

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao salvar a edição em massa.'
  } finally {
    salvandoMassa.value = false
  }
}

async function carregarSetoresNegocio() {
  try {
    const resposta = await fetch('/api/sessao')
    const dados = await resposta.json()
    setoresNegocio.value = dados.setores_negocio || []
  } catch (e) {
    console.error(e)
  }
}

async function liberarEquipe(equipe) {
  const ocupadas = (equipe.vagas || []).filter(vaga => vaga.ocupada)

  if (!ocupadas.length) {
    return
  }

  if (
    !window.confirm(
      `Remover os ${ocupadas.length} colaboradores da equipe ${equipe.prefixo}?`
    )
  ) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}/membros`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover os colaboradores da equipe.')
    }

    sucesso.value = dados.mensagem

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao remover os colaboradores da equipe.'
  }
}

async function removerEquipe(equipe) {
  if (
    !window.confirm(
      `Deseja realmente excluir a equipe ${equipe.prefixo} e todas as suas vagas?`
    )
  ) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao excluir a equipe.')
    }

    sucesso.value = `Equipe ${equipe.prefixo} excluída com sucesso.`

    if (vagaEquipe.value === equipe.id) {
      vagaEquipe.value = null
    }

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao excluir a equipe.'
  }
}

// ============================================================
// INICIALIZAÇÃO
// ============================================================

watch(vagaEquipe, id => {
  const equipe = equipes.value.find(item => item.id === id)

  if (!equipe) {
    return
  }

  vagaEstrutura.value =
    (equipe.prefixo || '').trim().toUpperCase() === 'FOLGUISTA'
      ? 'Folguista'
      : 'Construção'
})

onMounted(() => {
  carregarSetoresNegocio()
  carregarEquipes()
})
</script>
