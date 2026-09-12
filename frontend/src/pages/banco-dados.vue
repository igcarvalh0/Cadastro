<template>
  <q-layout view="lHh Lpr lFf">
    <MarcaDaguaFundo />

    <CabecalhoApp
      titulo="Banco de Dados"
      :carregando="carregando"
      @atualizar="carregarDados"
    />

    <q-page-container>
      <q-page class="q-pa-md banco-page">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="q-mb-md">
          <div class="text-h5"> Banco de Dados </div>

          <div class="text-subtitle2 text-grey-7">
            Gerenciamento de equipes e colaboradores
          </div>
        </div>

        <!-- ================================================== -->
        <!-- STATUS -->
        <!-- ================================================== -->

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <!-- ================================================== -->
        <!-- FILTROS -->
        <!-- ================================================== -->

        <q-card flat bordered class="q-mb-md barra-filtros">
          <q-card-section>
            <div class="row items-center q-col-gutter-md">
              <div class="col-12 col-md-4">
                <q-select
                  :model-value="baseSelecionada"
                  :options="opcoesBases"
                  label="Base"
                  outlined
                  dense
                  clearable
                  multiple
                  use-chips
                  emit-value
                  map-options
                  @update:model-value="atualizarSelecaoBases"
                >
                  <template #prepend>
                    <q-icon name="place" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="tipoSelecionado"
                  :options="opcoesTipos"
                  label="Tipo"
                  outlined
                  dense
                  emit-value
                  map-options
                >
                  <template #prepend>
                    <q-icon name="category" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="setorSelecionado"
                  :options="opcoesSetores"
                  label="Setor"
                  outlined
                  dense
                  emit-value
                  map-options
                >
                  <template #prepend>
                    <q-icon name="apartment" size="20px" />
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-3">
                <q-input
                  v-model="filtroEquipe"
                  outlined
                  dense
                  clearable
                  placeholder="Prefixo, base, nome ou chapa..."
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>
                  <q-tooltip>
                    Busca pelo prefixo e base da equipe e também pelo nome ou
                    chapa de quem está alocado. Ao achar uma pessoa, a equipe
                    dela já abre com a linha destacada.
                  </q-tooltip>
                </q-input>
              </div>

              <div class="col-auto">
                <q-btn-toggle
                  v-model="situacaoAlocacao"
                  dense
                  no-caps
                  unelevated
                  toggle-color="primary"
                  color="grey-3"
                  text-color="grey-8"
                  :options="[
                    { label: 'Todas', value: 'TODAS' },
                    { label: 'Completas', value: 'COMPLETAS' },
                    { label: 'Incompletas', value: 'INCOMPLETAS' }
                  ]"
                />
              </div>

              <div class="col-auto">
                <q-btn
                  outline
                  dense
                  color="primary"
                  icon="upload_file"
                  label="Alocação em massa"
                  @click="abrirPlanilhaAlocacoes"
                />
              </div>

              <div class="col-auto">
                <q-chip color="primary" text-color="white">
                  {{ equipesFiltradas.length }} equipes
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="positive" text-color="white">
                  {{ colaboradoresAlocados }} alocados
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="grey-7" text-color="white">
                  {{ colaboradoresLivres }} livres
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- CONTEÚDO -->
        <!-- ================================================== -->

        <div v-if="carregando" class="row justify-center q-pa-xl">
          <q-spinner color="primary" size="50px" />
        </div>

        <div v-else class="row q-col-gutter-md">
          <!-- ================================================= -->
          <!-- EQUIPES -->
          <!-- ================================================= -->

          <div class="col-12 col-lg-8">
            <q-card bordered>
              <q-card-section>
                <div class="row items-center q-col-gutter-sm">
                  <div class="col">
                    <div class="text-h6"> Equipes </div>
                  </div>

                  <div class="col-auto">
                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="negative"
                      icon="person_remove"
                      label="Remover todas as alocações"
                      :disable="!colaboradoresAlocados"
                      :loading="limpandoAlocacoes"
                      @click="removerTodasAlocacoes"
                    >
                      <q-tooltip>
                        {{
                          colaboradoresAlocados
                            ? `Libera as ${colaboradoresAlocados} vagas ocupadas de todas as bases`
                            : 'Nenhum colaborador alocado'
                        }}
                      </q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </q-card-section>

              <q-separator />

              <q-list separator>
                <!--
                  A chave leva o texto da busca junto de propósito: quando a
                  busca muda, o item é recriado e o :default-opened volta a
                  ser avaliado — é o que faz a equipe da pessoa encontrada
                  abrir sozinha, sem tirar do usuário o direito de recolher
                  depois na mão (o que um :model-value fixo impediria).
                -->
                <q-expansion-item
                  v-for="equipe in equipesFiltradas"
                  :key="`${equipe.id}-${textoBuscaEquipe}`"
                  :default-opened="buscaCasaComPessoa(equipe)"
                  expand-separator
                  :label="equipe.prefixo || 'Equipe'"
                  :caption="equipe.base || ''"
                  header-class="equipe-header"
                  expand-icon="fiber_manual_record"
                  expanded-icon="fiber_manual_record"
                  :expand-icon-class="
                    equipePreenchida(equipe) ? 'text-positive' : 'text-negative'
                  "
                >
                  <q-card flat>
                    <q-card-section class="q-pb-none text-right">
                      <q-btn
                        v-if="ehEquipeFolguista(equipe)"
                        outline
                        dense
                        size="sm"
                        color="primary"
                        icon="person_add"
                        label="Adicionar Folguista Extra"
                        class="q-mr-sm"
                        @click="abrirFolguistaExtra(equipe)"
                      />

                      <q-btn
                        outline
                        dense
                        size="sm"
                        color="negative"
                        icon="person_remove"
                        label="Remover todos os colaboradores"
                        :disable="!equipe.vagas.some(vaga => vaga.colaborador)"
                        @click="liberarEquipe(equipe)"
                      >
                        <q-tooltip
                          v-if="!equipe.vagas.some(vaga => vaga.colaborador)"
                        >
                          Nenhum colaborador alocado nesta equipe
                        </q-tooltip>
                      </q-btn>
                    </q-card-section>

                    <q-card-section>
                      <div
                        class="row items-center text-center text-caption text-grey-7 text-weight-medium q-pb-sm"
                      >
                        <div class="col-12 col-sm-2">CHAPA</div>
                        <div class="col-12 col-sm-3">Colaborador</div>
                        <div class="col-12 col-sm-2">Função cadastrada</div>
                        <div class="col-12 col-sm-2">Vaga</div>
                        <div class="col-12 col-sm-3">Status</div>
                      </div>

                      <div v-if="!equipe.vagas.length" class="text-grey-7">
                        Nenhuma vaga cadastrada.
                      </div>

                      <div
                        v-for="vaga in equipe.vagas"
                        :key="vaga.id"
                        class="row items-center text-center q-py-sm"
                        :class="{ 'linha-encontrada': vagaCasaComBusca(vaga) }"
                      >
                        <div class="col-12 col-sm-2 text-caption">
                          {{ vaga.colaborador?.chapa || '-' }}
                        </div>

                        <div class="col-12 col-sm-3">
                          {{ vaga.colaborador?.nome || 'Vaga livre' }}
                        </div>

                        <div class="col-12 col-sm-2 text-caption">
                          {{ vaga.colaborador?.funcao || '-' }}
                        </div>

                        <div class="col-12 col-sm-2 text-weight-medium">
                          {{ vaga.funcao_er || 'Não informada' }}
                        </div>

                        <div
                          class="col-12 col-sm-3 flex justify-center items-center"
                        >
                          <q-chip
                            v-if="vaga.eh_extra"
                            color="amber-8"
                            text-color="white"
                            size="sm"
                            icon="star"
                          >
                            EXTRA
                          </q-chip>

                          <q-chip
                            v-if="vaga.colaborador"
                            color="positive"
                            text-color="white"
                            size="sm"
                          >
                            ALOCADO
                          </q-chip>

                          <q-chip
                            v-else
                            color="grey-5"
                            text-color="white"
                            size="sm"
                          >
                            LIVRE
                          </q-chip>

                          <template v-if="vaga.colaborador">
                            <q-btn
                              flat
                              round
                              dense
                              color="primary"
                              icon="swap_horiz"
                              class="q-ml-sm"
                              aria-label="Trocar colaborador"
                              @click="abrirEdicaoAlocacao(vaga)"
                            />

                            <q-btn
                              flat
                              round
                              dense
                              color="negative"
                              icon="person_remove"
                              class="q-ml-sm"
                              aria-label="Remover colaborador"
                              @click="removerColaborador(vaga.id)"
                            />
                          </template>

                          <q-btn
                            v-else
                            flat
                            round
                            dense
                            color="primary"
                            icon="person_add"
                            class="q-ml-sm"
                            aria-label="Alocar colaborador"
                            @click="abrirAlocacaoParaVaga(equipe, vaga)"
                          />
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </q-expansion-item>
              </q-list>
            </q-card>
          </div>

          <!-- ================================================= -->
          <!-- COLABORADORES -->
          <!-- ================================================= -->

          <div class="col-12 col-lg-4">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Colaboradores </div>
              </q-card-section>

              <q-separator />

              <q-card-section>
                <div class="row q-col-gutter-sm q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="filtroColaborador"
                      outlined
                      dense
                      clearable
                      placeholder="Pesquisar por nome ou chapa..."
                    >
                      <template #prepend>
                        <q-icon name="search" />
                      </template>
                    </q-input>
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'TODOS' ? 'primary' : 'grey-7'
                      "
                      outline
                      label="Todos"
                      @click="statusColaborador = 'TODOS'"
                    />
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'ALOCADOS' ? 'positive' : 'grey-7'
                      "
                      outline
                      :label="`Alocados (${colaboradoresAlocados})`"
                      @click="statusColaborador = 'ALOCADOS'"
                    />
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'LIVRES' ? 'primary' : 'grey-7'
                      "
                      outline
                      :label="`Livres (${colaboradoresLivres})`"
                      @click="statusColaborador = 'LIVRES'"
                    />
                  </div>
                </div>

                <q-list bordered separator class="rounded-borders">
                  <q-item
                    v-for="colaborador in colaboradoresFiltrados"
                    :key="colaborador.chapa"
                    clickable
                    :disable="colaborador.alocado"
                    @click="selecionarColaborador(colaborador)"
                  >
                    <q-item-section class="text-center">
                      <q-item-label>
                        {{ colaborador.nome }}
                      </q-item-label>

                      <q-item-label caption>
                        {{ colaborador.funcao }}
                      </q-item-label>

                      <q-item-label caption>
                        SEÇÃO: {{ colaborador.secao || 'Não informada' }}
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side class="text-center">
                      <q-chip
                        v-if="colaborador.alocado"
                        color="positive"
                        text-color="white"
                        size="sm"
                      >
                        ALOCADO
                      </q-chip>

                      <q-chip
                        v-else
                        color="grey-6"
                        text-color="white"
                        size="sm"
                      >
                        LIVRE
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <q-dialog v-model="dialogAlocacao">
      <q-card style="min-width: 500px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6"> Alocar colaborador </div>

          <div
            v-if="colaboradorSelecionado"
            class="text-subtitle2 text-grey-7 q-mt-sm"
          >
            {{ colaboradorSelecionado.chapa }}
            -
            {{ colaboradorSelecionado.nome }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-select
            v-model="colaboradorSelecionado"
            :options="opcoesColaboradoresAlocacao"
            label="Colaborador"
            outlined
            dense
            use-input
            clearable
            option-label="nome"
            input-debounce="0"
            class="q-mb-md"
            hint="Pesquise pelo nome ou pela CHAPA"
            @filter="filtrarColaboradoresAlocacao"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.nome }}</q-item-label>
                  <q-item-label caption>
                    CHAPA: {{ scope.opt.chapa }} |
                    {{ scope.opt.funcao || 'Função não informada' }}
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip
                    v-if="scope.opt.alocado"
                    color="amber-8"
                    text-color="white"
                    size="sm"
                    dense
                  >
                    {{ descricaoAlocacaoAtual(scope.opt.chapa) }}
                  </q-chip>

                  <q-chip v-else color="positive" text-color="white" size="sm" dense>
                    Livre
                  </q-chip>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-select
            v-model="baseAlocacao"
            :options="basesAlocacao"
            label="Base"
            outlined
            dense
            emit-value
            map-options
            clearable
            @update:model-value="limparEquipeAlocacao"
          />

          <q-select
            v-if="baseAlocacao"
            v-model="equipeAlocacao"
            :options="equipesAlocacao"
            label="Equipe"
            outlined
            dense
            emit-value
            map-options
            clearable
            class="q-mt-md"
            @update:model-value="limparVagaAlocacao"
          />

          <q-select
            v-if="equipeAlocacao"
            v-model="vagaAlocacao"
            :options="vagasAlocacao"
            label="Vaga"
            outlined
            dense
            emit-value
            map-options
            clearable
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />

          <q-btn
            color="primary"
            label="Alocar"
            :loading="carregandoAlocacao"
            :disable="!vagaAlocacao"
            @click="alocarColaborador"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ================================================== -->
    <!-- EDITAR ALOCAÇÃO (TROCAR COLABORADOR) -->
    <!-- ================================================== -->

    <q-dialog v-model="dialogEdicaoAlocacao">
      <q-card style="min-width: 500px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Trocar colaborador da vaga</div>

          <div v-if="vagaEmEdicao" class="text-subtitle2 text-grey-7 q-mt-sm">
            Vaga de {{ vagaEmEdicao.funcao_er }} — ocupada por
            {{ vagaEmEdicao.colaborador?.chapa }} -
            {{ vagaEmEdicao.colaborador?.nome }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-select
            v-model="colaboradorNovoEdicao"
            :options="opcoesColaboradoresAlocacao"
            label="Novo colaborador"
            outlined
            dense
            use-input
            clearable
            option-label="nome"
            input-debounce="0"
            hint="Pesquise pelo nome ou pela CHAPA"
            @filter="filtrarColaboradoresAlocacao"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.nome }}</q-item-label>
                  <q-item-label caption>
                    CHAPA: {{ scope.opt.chapa }} |
                    {{ scope.opt.funcao || 'Função não informada' }}
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip
                    v-if="scope.opt.alocado"
                    color="amber-8"
                    text-color="white"
                    size="sm"
                    dense
                  >
                    {{ descricaoAlocacaoAtual(scope.opt.chapa) }}
                  </q-chip>

                  <q-chip v-else color="positive" text-color="white" size="sm" dense>
                    Livre
                  </q-chip>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />

          <q-btn
            color="primary"
            label="Trocar"
            :loading="salvandoEdicaoAlocacao"
            :disable="!colaboradorNovoEdicao"
            @click="salvarEdicaoAlocacao()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ================================================== -->
    <!-- FOLGUISTA EXTRA -->
    <!-- ================================================== -->

    <q-dialog v-model="dialogFolguistaExtra">
      <q-card style="min-width: 500px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Adicionar Folguista Extra</div>

          <div class="text-caption text-grey-7 q-mt-sm">
            Equipe {{ equipeFolguistaExtra?.prefixo }} — não altera a quantidade
            padrão de folguistas, só adiciona uma alocação extra sinalizada.
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-select
            v-model="colaboradorExtra"
            :options="opcoesColaboradoresAlocacao"
            label="Colaborador"
            outlined
            dense
            use-input
            clearable
            option-label="nome"
            input-debounce="0"
            class="q-mb-md"
            hint="Pesquise pelo nome ou pela CHAPA"
            @filter="filtrarColaboradoresAlocacao"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.nome }}</q-item-label>
                  <q-item-label caption>
                    CHAPA: {{ scope.opt.chapa }} |
                    {{ scope.opt.funcao || 'Função não informada' }}
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip
                    v-if="scope.opt.alocado"
                    color="amber-8"
                    text-color="white"
                    size="sm"
                    dense
                  >
                    {{ descricaoAlocacaoAtual(scope.opt.chapa) }}
                  </q-chip>

                  <q-chip v-else color="positive" text-color="white" size="sm" dense>
                    Livre
                  </q-chip>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-input
            v-model="funcaoExtra"
            label="Função"
            outlined
            dense
            class="q-mb-md"
            hint="Ex.: ELETRICISTA, PODADOR..."
          />

          <q-select
            v-model="setorExtra"
            :options="setoresNegocio"
            label="Setor"
            outlined
            dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />

          <q-btn
            color="primary"
            label="Adicionar"
            :loading="salvandoFolguistaExtra"
            :disable="!colaboradorExtra || !funcaoExtra || !setorExtra"
            @click="salvarFolguistaExtra()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ================================================== -->
    <!-- CONFIRMAR TRANSFERÊNCIA (colaborador já alocado) -->
    <!-- ================================================== -->

    <q-dialog v-model="confirmacaoTransferencia.aberto" persistent>
      <q-card style="min-width: 420px; max-width: 90vw">
        <q-card-section class="row items-center">
          <q-icon name="warning" color="warning" size="28px" class="q-mr-sm" />
          <div class="text-h6">Colaborador já alocado</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <p class="q-mb-md">{{ confirmacaoTransferencia.mensagem }}</p>

          <q-list bordered dense class="rounded-borders">
            <q-item>
              <q-item-section>
                <q-item-label caption>Equipe atual</q-item-label>
                <q-item-label>
                  {{ confirmacaoTransferencia.equipe || '?' }}
                  <span v-if="confirmacaoTransferencia.base">
                    ({{ confirmacaoTransferencia.base }})
                  </span>
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="confirmacaoTransferencia.tipoEquipe">
              <q-item-section>
                <q-item-label caption>Tipo de equipe</q-item-label>
                <q-item-label>{{ confirmacaoTransferencia.tipoEquipe }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="confirmacaoTransferencia.funcaoEr">
              <q-item-section>
                <q-item-label caption>Vaga</q-item-label>
                <q-item-label>{{ confirmacaoTransferencia.funcaoEr }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <p class="q-mt-md q-mb-none">
            Deseja transferir o colaborador mesmo assim?
          </p>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" @click="cancelarTransferenciaPendente" />

          <q-btn
            color="primary"
            label="Confirmar transferência"
            @click="confirmarTransferenciaPendente"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ================================================== -->
    <!-- ALOCAÇÃO EM MASSA POR PLANILHA -->
    <!-- ================================================== -->

    <q-dialog v-model="dialogPlanilhaAlocacoes">
      <q-card style="width: 480px; max-width: 92vw">
        <q-card-section class="row items-center">
          <div class="text-h6">Alocação em massa por planilha</div>
          <q-space />
          <q-btn v-close-popup flat round dense icon="close" />
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
              label="Baixar planilha atual"
              class="btn-exportar"
              @click="baixarPlanilhaAlocacoes"
            />
          </div>

          <q-file
            v-model="arquivoPlanilhaAlocacoes"
            label="Selecionar planilha preenchida (.xlsx)"
            outlined
            dense
            accept=".xlsx"
            @update:model-value="planoAlocacoes = null"
          >
            <template #prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>

          <div class="text-caption text-grey-7 q-mt-sm">
            A planilha tem duas abas: <strong>Alocações</strong> (para editar) e
            <strong>Ativos</strong> (consulta de colaboradores ativos). Na aba
            Alocações, preencha a coluna <strong>CHAPA</strong> com quem deve
            ocupar a vaga — deixe em branco para liberar. O sistema compara com
            o que já está no banco e identifica sozinho novas alocações,
            remoções e trocas. Linha sem mudança é ignorada.
          </div>

          <div class="row q-gutter-sm q-mt-md">
            <q-btn
              color="primary"
              label="Analisar planilha"
              :disable="!arquivoPlanilhaAlocacoes"
              :loading="analisandoPlanilha"
              @click="enviarPreviaAlocacoes"
            />
          </div>

          <div v-if="planoAlocacoes" class="q-mt-md">
            <div class="row q-gutter-sm q-mb-sm">
              <q-chip color="primary" text-color="white">
                {{ planoAlocacoes.alocar?.length || 0 }} para alocar
              </q-chip>
              <q-chip color="negative" text-color="white">
                {{ planoAlocacoes.remover?.length || 0 }} para remover
              </q-chip>
              <q-chip color="grey-7" text-color="white">
                {{ planoAlocacoes.ignoradas || 0 }} ignoradas
              </q-chip>
            </div>

            <q-banner
              v-if="planoAlocacoes.erros?.length"
              class="bg-red-1 text-negative q-mb-sm"
              rounded
            >
              <div class="text-weight-medium q-mb-xs">
                {{ planoAlocacoes.erros.length }} linha(s) com problema:
              </div>
              <div v-for="(item, indice) in planoAlocacoes.erros" :key="indice">
                Linha {{ item.linha }} ({{ item.equipe }}): {{ item.erro }}
              </div>
            </q-banner>

            <q-banner
              v-if="conflitosPendentes.length"
              class="bg-orange-1 text-orange-9 q-mb-sm"
              rounded
            >
              <div class="text-weight-medium q-mb-xs">
                Colaborador já alocado em outra equipe — confirme a transferência:
              </div>
              <div
                v-for="item in conflitosPendentes"
                :key="item.chapa"
                class="row items-center q-py-xs"
              >
                <q-checkbox
                  :model-value="conflitosConfirmados.has(item.chapa)"
                  :label="
                    `${item.chapa} - ${item.nome} (estava em ${item.alocacao_atual?.equipe || '?'}` +
                    (item.alocacao_atual?.tipo_equipe ? `, ${item.alocacao_atual.tipo_equipe}` : '') +
                    ')'
                  "
                  @update:model-value="alternarConflito(item.chapa)"
                />
              </div>
            </q-banner>

            <q-btn
              color="positive"
              label="Aplicar mudanças"
              :disable="
                !!planoAlocacoes.erros?.length ||
                conflitosPendentes.some(item => !conflitosConfirmados.has(item.chapa))
              "
              :loading="aplicandoPlanilha"
              @click="aplicarPlanilhaAlocacoes"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

import CabecalhoApp from '../components/CabecalhoApp.vue'
import MarcaDaguaFundo from '../components/MarcaDaguaFundo.vue'
import { PODE_VER_EQUIPES } from '../composables/useSessao'
import {
  CHAVE_BASES_SELECIONADAS,
  ehEquipeFolguista,
  equipeCombinaComSetor,
  equipeCombinaComTipo,
  normalizarSelecaoBases,
  OPCAO_TODAS_BASES,
  opcoesSetorFiltro,
  opcoesTipoFiltro,
  proximaSelecaoBases,
  SETOR_TODOS,
  TIPO_TODOS
} from '../utils/equipes'

definePage({ meta: { permissao: PODE_VER_EQUIPES } })

// ============================================================
// ESTADO
// ============================================================

const equipes = ref([])

const colaboradores = ref([])

const carregando = ref(false)

const erro = ref('')

const baseSelecionada = ref([])
const tipoSelecionado = ref(TIPO_TODOS)
const setorSelecionado = ref(SETOR_TODOS)
const filtroEquipe = ref('')
const situacaoAlocacao = ref('TODAS')
const limpandoAlocacoes = ref(false)

const filtroColaborador = ref('')
const statusColaborador = ref('TODOS')

// Opções do combo de busca nos diálogos de Alocar/Trocar/Folguista Extra.
// Inclui colaboradores JÁ ALOCADOS de propósito (com o "Alocado em ..."
// aparecendo no item) — o backend já sabe mover alguém de uma vaga para
// outra com confirmação (ver o fluxo de "conflito" em cada função de
// salvar), então esconder quem já está alocado só forçava o usuário a
// remover a pessoa da equipe atual antes, num passo a mais. Livres
// aparecem primeiro na lista.
const opcoesColaboradoresAlocacao = ref([])
// CHAPA a excluir das opções (o próprio ocupante da vaga, no diálogo de
// trocar) — sem isso a pessoa apareceria como opção pra "substituir a si
// mesma".
const chapaExcluidaAlocacao = ref('')

// Diálogo (dentro do próprio site, sem window.confirm — nativo do
// navegador pode ser bloqueado/ignorado silenciosamente, e não segue o
// visual do projeto) usado pelos 3 fluxos que podem mover alguém de uma
// equipe pra outra: Alocar, Trocar colaborador e Folguista Extra.
const confirmacaoTransferencia = ref({
  aberto: false,
  mensagem: '',
  equipe: '',
  base: '',
  tipoEquipe: '',
  funcaoEr: '',
  aoConfirmar: null
})

function abrirConfirmacaoTransferencia({ mensagem, alocacaoAtual, aoConfirmar }) {
  const atual = alocacaoAtual || {}
  confirmacaoTransferencia.value = {
    aberto: true,
    mensagem: mensagem || 'Este colaborador já está alocado em outra equipe.',
    equipe: atual.equipe || '',
    base: atual.base || '',
    tipoEquipe: atual.tipo_equipe || '',
    funcaoEr: atual.funcao_er || '',
    aoConfirmar
  }
}

function confirmarTransferenciaPendente() {
  const acao = confirmacaoTransferencia.value.aoConfirmar
  confirmacaoTransferencia.value.aberto = false
  if (acao) {
    acao()
  }
}

function cancelarTransferenciaPendente() {
  confirmacaoTransferencia.value.aberto = false
  confirmacaoTransferencia.value.aoConfirmar = null
}

const opcoesAlocacao = ref({})
const colaboradorSelecionado = ref(null)
const dialogAlocacao = ref(false)
const carregandoAlocacao = ref(false)

const baseAlocacao = ref(null)
const equipeAlocacao = ref(null)
const vagaAlocacao = ref(null)

// Editar alocação (trocar colaborador de uma vaga ocupada)
const dialogEdicaoAlocacao = ref(false)
const vagaEmEdicao = ref(null)
const colaboradorNovoEdicao = ref(null)
const salvandoEdicaoAlocacao = ref(false)

// Folguista Extra
const dialogFolguistaExtra = ref(false)
const equipeFolguistaExtra = ref(null)
const colaboradorExtra = ref(null)
const funcaoExtra = ref('')
const setorExtra = ref(null)
const salvandoFolguistaExtra = ref(false)
const setoresNegocio = ref([])

// Alocação em massa por planilha
const dialogPlanilhaAlocacoes = ref(false)
const arquivoPlanilhaAlocacoes = ref(null)
const analisandoPlanilha = ref(false)
const aplicandoPlanilha = ref(false)
const planoAlocacoes = ref(null)
const conflitosConfirmados = ref(new Set())

const conflitosPendentes = computed(() =>
  (planoAlocacoes.value?.alocar || []).filter(item => item.conflito)
)

const basesAlocacao = computed(() => {
  return Object.keys(opcoesAlocacao.value)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'))
    .map(base => ({
      label: base,
      value: base
    }))
})

const equipesAlocacao = computed(() => {
  if (!baseAlocacao.value) {
    return []
  }

  return (opcoesAlocacao.value[baseAlocacao.value] || [])
    .map(equipe => ({
      label: equipe.prefixo || 'Equipe sem prefixo',
      value: equipe.id
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'pt-BR'))
})

const vagasAlocacao = computed(() => {
  if (!baseAlocacao.value || !equipeAlocacao.value) {
    return []
  }

  const equipe = (opcoesAlocacao.value[baseAlocacao.value] || []).find(
    item => String(item.id) === String(equipeAlocacao.value)
  )

  if (!equipe) {
    return []
  }

  return (equipe.vagas || []).map(vaga => ({
    label:
      [vaga.funcao_er, vaga.estrutura].filter(Boolean).join(' | ') ||
      'Função não informada',
    value: vaga.id
  }))
})

// ============================================================
// BASES
// ============================================================

// Folguista Extra nao entra no calculo de completude: a equipe e considerada
// completa/incompleta so pelas vagas padrao dela.
function vagasPadrao(equipe) {
  return (equipe.vagas || []).filter(vaga => !vaga.eh_extra)
}

function equipePreenchida(equipe) {
  const vagas = vagasPadrao(equipe)

  return vagas.length > 0 && vagas.every(vaga => Boolean(vaga.colaborador))
}

function atualizarSelecaoBases(bases) {
  baseSelecionada.value = proximaSelecaoBases(baseSelecionada.value, bases)
}

// nome da base -> sigla, montado a partir do que o servidor manda em cada
// equipe. Antes era uma tabela fixa aqui, que saía do ar sempre que uma base
// nova aparecia no backend.
const codigosPorBase = computed(() => {
  const mapa = {}

  for (const equipe of equipes.value) {
    const base = String(equipe.base || '').trim()

    if (base && equipe.codigo_base) {
      mapa[base] = equipe.codigo_base
    }
  }

  return mapa
})

const opcoesBases = computed(() => {
  const bases = [
    {
      label: 'Todas as bases',
      value: OPCAO_TODAS_BASES
    }
  ]

  for (const equipe of equipes.value) {
    const base = String(equipe.base || '').trim()

    if (!base) {
      continue
    }

    if (!bases.some(item => item.value === base)) {
      const codigo = codigosPorBase.value[base]
      bases.push({
        label: codigo && codigo !== base ? `${base} (${codigo})` : base,
        value: base
      })
    }
  }

  return bases.sort((a, b) => {
    if (a.value === OPCAO_TODAS_BASES) return -1
    if (b.value === OPCAO_TODAS_BASES) return 1
    return a.label.localeCompare(b.label, 'pt-BR')
  })
})

const opcoesTipos = computed(() => opcoesTipoFiltro(equipes.value))

const opcoesSetores = computed(() => opcoesSetorFiltro(equipes.value))

// ============================================================
// EQUIPES FILTRADAS
// ============================================================

const textoBuscaEquipe = computed(() =>
  (filtroEquipe.value || '').trim().toLowerCase()
)

// A busca cobre a equipe (prefixo/base) E as pessoas dentro dela (nome/chapa),
// para achar "onde fulano está alocado" sem abrir equipe por equipe.
function vagaCasaComBusca(vaga) {
  const texto = textoBuscaEquipe.value
  if (!texto || !vaga?.colaborador) {
    return false
  }

  const colaborador = vaga.colaborador
  return `${colaborador.nome || ''} ${colaborador.chapa || ''}`
    .toLowerCase()
    .includes(texto)
}

function buscaCasaComPessoa(equipe) {
  return (equipe.vagas || []).some(vagaCasaComBusca)
}

const equipesFiltradas = computed(() => {
  const visiveisPorBase =
    !baseSelecionada.value.length ||
    baseSelecionada.value.includes(OPCAO_TODAS_BASES)
      ? equipes.value
      : equipes.value.filter(equipe => {
          const base = String(equipe.base || '').trim()
          return baseSelecionada.value.includes(base)
        })

  const textoBusca = textoBuscaEquipe.value

  const equipesVisiveis = visiveisPorBase.filter(equipe => {
    if (
      !equipeCombinaComTipo(equipe, tipoSelecionado.value) ||
      !equipeCombinaComSetor(equipe, setorSelecionado.value)
    ) {
      return false
    }

    if (textoBusca) {
      const alvoEquipe = `${equipe.prefixo || ''} ${equipe.base || ''}`.toLowerCase()
      if (!alvoEquipe.includes(textoBusca) && !buscaCasaComPessoa(equipe)) {
        return false
      }
    }

    if (situacaoAlocacao.value !== 'TODAS') {
      const completa = equipePreenchida(equipe)
      if (situacaoAlocacao.value === 'COMPLETAS' && !completa) {
        return false
      }
      if (situacaoAlocacao.value === 'INCOMPLETAS' && completa) {
        return false
      }
    }

    return true
  })

  return [...equipesVisiveis].sort((a, b) => {
    const baseA = String(a.base || '').trim()
    const baseB = String(b.base || '').trim()
    const comparacaoBase = baseA.localeCompare(baseB, 'pt-BR')

    if (comparacaoBase !== 0) {
      return comparacaoBase
    }

    // Folguista fica no fim da base, igual ao resto do sistema
    const folguistaA = ehEquipeFolguista(a) ? 1 : 0
    const folguistaB = ehEquipeFolguista(b) ? 1 : 0

    if (folguistaA !== folguistaB) {
      return folguistaA - folguistaB
    }

    return String(a.prefixo || '')
      .trim()
      .localeCompare(String(b.prefixo || '').trim(), 'pt-BR')
  })
})

// ============================================================
// COLABORADORES FILTRADOS
// ============================================================

const colaboradoresBase = computed(() => {
  if (
    !baseSelecionada.value.length ||
    baseSelecionada.value.includes(OPCAO_TODAS_BASES)
  ) {
    return colaboradores.value
  }

  return colaboradores.value.filter(colaborador =>
    baseSelecionada.value.some(
      base =>
        base === colaborador.base ||
        codigosPorBase.value[base] === colaborador.codigo_base
    )
  )
})

const colaboradoresFiltrados = computed(() => {
  const filtro = filtroColaborador.value.trim().toLowerCase()

  return colaboradoresBase.value.filter(colaborador => {
    const correspondeStatus =
      statusColaborador.value === 'TODOS' ||
      (statusColaborador.value === 'ALOCADOS' && colaborador.alocado) ||
      (statusColaborador.value === 'LIVRES' && !colaborador.alocado)

    const correspondeTexto =
      !filtro ||
      String(colaborador.nome || '')
        .toLowerCase()
        .includes(filtro) ||
      String(colaborador.chapa || '')
        .toLowerCase()
        .includes(filtro) ||
      String(colaborador.funcao || '')
        .toLowerCase()
        .includes(filtro)

    return correspondeStatus && correspondeTexto
  })
})

// ============================================================
// CONTADORES
// ============================================================

const colaboradoresAlocados = computed(() => {
  return colaboradoresBase.value.filter(colaborador => colaborador.alocado)
    .length
})

const colaboradoresLivres = computed(() => {
  return colaboradoresBase.value.filter(colaborador => !colaborador.alocado)
    .length
})

// CHAPA -> onde a pessoa esta alocada hoje (prefixo + base da equipe) — usa
// pra rotular "Alocado em ..." nas opções de colaborador dos diálogos de
// Alocar/Trocar/Folguista Extra.
const mapaEquipeAtualPorChapa = computed(() => {
  const mapa = new Map()

  for (const equipe of equipes.value) {
    for (const vaga of equipe.vagas || []) {
      if (vaga.colaborador?.chapa) {
        mapa.set(String(vaga.colaborador.chapa), {
          prefixo: equipe.prefixo,
          base: equipe.base
        })
      }
    }
  }

  return mapa
})

function descricaoAlocacaoAtual(chapa) {
  const atual = mapaEquipeAtualPorChapa.value.get(String(chapa))
  if (!atual) {
    return 'Alocado em outra equipe'
  }
  return `Alocado em ${atual.prefixo} (${atual.base})`
}

// ============================================================
// CARREGAR DADOS
// ============================================================

async function carregarDados() {
  carregando.value = true

  erro.value = ''

  try {
    const [respostaEquipes, respostaColaboradores] = await Promise.all([
      fetch('/api/equipes'),

      fetch('/api/colaboradores')
    ])

    if (!respostaEquipes.ok) {
      throw new Error('Erro ao carregar equipes.')
    }

    if (!respostaColaboradores.ok) {
      throw new Error('Erro ao carregar colaboradores.')
    }

    const dadosEquipes = await respostaEquipes.json()

    const dadosColaboradores = await respostaColaboradores.json()

    if (dadosEquipes.erro) {
      throw new Error(dadosEquipes.erro)
    }

    if (dadosColaboradores.erro) {
      throw new Error(dadosColaboradores.erro)
    }

    equipes.value = dadosEquipes

    colaboradores.value = dadosColaboradores

    const respostaOpcoes = await fetch('/api/opcoes-alocacao')

    if (!respostaOpcoes.ok) {
      throw new Error('Erro ao carregar opções de alocação.')
    }

    const dadosOpcoes = await respostaOpcoes.json()

    if (dadosOpcoes.erro) {
      throw new Error(dadosOpcoes.erro)
    }

    opcoesAlocacao.value = dadosOpcoes
  } catch (e) {
    console.error(e)

    erro.value = e.message || 'Erro ao carregar dados.'
  } finally {
    carregando.value = false
  }
}

// Lista as opções do combo de colaborador dos 3 diálogos (Alocar, Trocar,
// Folguista Extra): livres primeiro, depois os já alocados (identificados
// no item pelo "Alocado em ..." — ver mapaEquipeAtualPorChapa), e sem a
// CHAPA marcada em chapaExcluidaAlocacao (o proprio ocupante da vaga, so
// no diálogo de trocar).
function opcoesColaboradoresParaFiltro(filtro = '') {
  const termo = String(filtro || '').trim().toLowerCase()
  const excluir = String(chapaExcluidaAlocacao.value || '')

  return colaboradores.value
    .filter(colaborador => {
      if (excluir && String(colaborador.chapa) === excluir) {
        return false
      }
      return (
        !termo ||
        String(colaborador.nome || '').toLowerCase().includes(termo) ||
        String(colaborador.chapa || '').toLowerCase().includes(termo)
      )
    })
    .slice()
    .sort((a, b) => Number(a.alocado) - Number(b.alocado))
}

function selecionarColaborador(colaborador) {
  if (colaborador.alocado) {
    return
  }

  colaboradorSelecionado.value = colaborador
  chapaExcluidaAlocacao.value = ''
  opcoesColaboradoresAlocacao.value = opcoesColaboradoresParaFiltro()

  dialogAlocacao.value = true
}

function abrirAlocacaoParaVaga(equipe, vaga) {
  colaboradorSelecionado.value = null
  baseAlocacao.value = equipe.base
  equipeAlocacao.value = equipe.id
  vagaAlocacao.value = vaga.id
  chapaExcluidaAlocacao.value = ''
  opcoesColaboradoresAlocacao.value = opcoesColaboradoresParaFiltro()
  dialogAlocacao.value = true
}

function filtrarColaboradoresAlocacao(valor, atualizar) {
  atualizar(() => {
    opcoesColaboradoresAlocacao.value = opcoesColaboradoresParaFiltro(valor)
  })
}

function limparEquipeAlocacao() {
  equipeAlocacao.value = null
  vagaAlocacao.value = null
}

function limparVagaAlocacao() {
  vagaAlocacao.value = null
}

// ============================================================
// EDITAR ALOCAÇÃO (TROCAR COLABORADOR)
// ============================================================

function abrirEdicaoAlocacao(vaga) {
  vagaEmEdicao.value = vaga
  colaboradorNovoEdicao.value = null
  chapaExcluidaAlocacao.value = vaga.colaborador?.chapa || ''
  opcoesColaboradoresAlocacao.value = opcoesColaboradoresParaFiltro()
  dialogEdicaoAlocacao.value = true
}

async function salvarEdicaoAlocacao(confirmarTransferencia = false) {
  if (!vagaEmEdicao.value || !colaboradorNovoEdicao.value) {
    return
  }

  salvandoEdicaoAlocacao.value = true

  try {
    const resposta = await fetch('/api/equipes/editar-alocacao', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        composicao_id: vagaEmEdicao.value.id,
        chapa: colaboradorNovoEdicao.value.chapa,
        confirmar_transferencia: confirmarTransferencia
      })
    })

    const dados = await resposta.json()

    if (resposta.status === 409 && dados.conflito) {
      abrirConfirmacaoTransferencia({
        mensagem: dados.mensagem,
        alocacaoAtual: dados.alocacao_atual,
        aoConfirmar: () => salvarEdicaoAlocacao(true)
      })
      return
    }

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao trocar o colaborador.')
    }

    dialogEdicaoAlocacao.value = false
    vagaEmEdicao.value = null
    colaboradorNovoEdicao.value = null

    await carregarDados()
  } catch (e) {
    erro.value = e.message || 'Erro ao trocar o colaborador.'
  } finally {
    salvandoEdicaoAlocacao.value = false
  }
}

// ============================================================
// FOLGUISTA EXTRA
// ============================================================

function abrirFolguistaExtra(equipe) {
  equipeFolguistaExtra.value = equipe
  colaboradorExtra.value = null
  funcaoExtra.value = ''
  setorExtra.value = null
  chapaExcluidaAlocacao.value = ''
  opcoesColaboradoresAlocacao.value = opcoesColaboradoresParaFiltro()
  dialogFolguistaExtra.value = true
}

async function salvarFolguistaExtra(confirmarTransferencia = false) {
  if (!equipeFolguistaExtra.value || !colaboradorExtra.value || !funcaoExtra.value || !setorExtra.value) {
    return
  }

  salvandoFolguistaExtra.value = true

  try {
    const resposta = await fetch(
      `/api/equipes/${equipeFolguistaExtra.value.id}/folguista-extra`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          funcao_er: funcaoExtra.value,
          chapa: colaboradorExtra.value.chapa,
          setor: setorExtra.value,
          confirmar_transferencia: confirmarTransferencia
        })
      }
    )

    const dados = await resposta.json()

    if (resposta.status === 409 && dados.conflito) {
      abrirConfirmacaoTransferencia({
        mensagem: dados.mensagem,
        alocacaoAtual: dados.alocacao_atual,
        aoConfirmar: () => salvarFolguistaExtra(true)
      })
      return
    }

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao adicionar Folguista Extra.')
    }

    dialogFolguistaExtra.value = false
    await carregarDados()
  } catch (e) {
    erro.value = e.message || 'Erro ao adicionar Folguista Extra.'
  } finally {
    salvandoFolguistaExtra.value = false
  }
}

// ============================================================
// ALOCAÇÃO EM MASSA POR PLANILHA
// ============================================================

function abrirPlanilhaAlocacoes() {
  arquivoPlanilhaAlocacoes.value = null
  planoAlocacoes.value = null
  conflitosConfirmados.value = new Set()
  dialogPlanilhaAlocacoes.value = true
}

function baixarPlanilhaAlocacoes() {
  window.location.href = '/api/alocacoes/planilha'
}

function alternarConflito(chapa) {
  const novo = new Set(conflitosConfirmados.value)
  if (novo.has(chapa)) {
    novo.delete(chapa)
  } else {
    novo.add(chapa)
  }
  conflitosConfirmados.value = novo
}

async function enviarPreviaAlocacoes() {
  if (!arquivoPlanilhaAlocacoes.value) {
    return
  }

  analisandoPlanilha.value = true
  erro.value = ''

  try {
    const formData = new FormData()
    formData.append('arquivo', arquivoPlanilhaAlocacoes.value)

    const resposta = await fetch('/api/alocacoes/planilha/previa', {
      method: 'POST',
      body: formData
    })

    const dados = await resposta.json()

    if (!resposta.ok || (dados.erro && !dados.alocar)) {
      throw new Error(dados.erro || 'Erro ao analisar a planilha.')
    }

    planoAlocacoes.value = dados
    conflitosConfirmados.value = new Set()
  } catch (e) {
    erro.value = e.message || 'Erro ao analisar a planilha.'
  } finally {
    analisandoPlanilha.value = false
  }
}

async function aplicarPlanilhaAlocacoes() {
  if (!arquivoPlanilhaAlocacoes.value || !planoAlocacoes.value) {
    return
  }

  aplicandoPlanilha.value = true
  erro.value = ''

  try {
    const formData = new FormData()
    formData.append('arquivo', arquivoPlanilhaAlocacoes.value)
    for (const chapa of conflitosConfirmados.value) {
      formData.append('confirmar_conflitos', chapa)
    }

    const resposta = await fetch('/api/alocacoes/planilha/aplicar', {
      method: 'POST',
      body: formData
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      planoAlocacoes.value = dados.plano || planoAlocacoes.value
      throw new Error(dados.erro || 'Erro ao aplicar a planilha.')
    }

    dialogPlanilhaAlocacoes.value = false
    await carregarDados()
  } catch (e) {
    erro.value = e.message || 'Erro ao aplicar a planilha.'
  } finally {
    aplicandoPlanilha.value = false
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

function localizarVaga(composicaoId) {
  for (const equipe of equipes.value) {
    const vaga = (equipe.vagas || []).find(
      item => String(item.id) === String(composicaoId)
    )

    if (vaga) {
      return vaga
    }
  }

  return null
}

function atualizarEstadoAposAlocacao(composicaoId, colaborador) {
  const vaga = localizarVaga(composicaoId)

  if (vaga) {
    vaga.colaborador = {
      ...colaborador,
      alocado: true
    }
    vaga.ocupada = true
  }

  const colaboradorLista = colaboradores.value.find(
    item => item.chapa === colaborador.chapa
  )

  if (colaboradorLista) {
    colaboradorLista.alocado = true
  }

  for (const equipe of Object.values(opcoesAlocacao.value)) {
    const equipeAlocacaoAtual = equipe.find(item =>
      (item.vagas || []).some(
        vagaItem => String(vagaItem.id) === String(composicaoId)
      )
    )

    if (equipeAlocacaoAtual) {
      equipeAlocacaoAtual.vagas = equipeAlocacaoAtual.vagas.filter(
        vagaItem => String(vagaItem.id) !== String(composicaoId)
      )
      break
    }
  }
}

function atualizarEstadoAposRemocao(chapa, composicaoId) {
  const vaga = localizarVaga(composicaoId)

  if (vaga) {
    vaga.colaborador = null
    vaga.ocupada = false
  }

  const colaborador = colaboradores.value.find(item => item.chapa === chapa)

  if (colaborador) {
    colaborador.alocado = false
  }
}

async function alocarColaborador(confirmarTransferencia = false) {
  if (!colaboradorSelecionado.value || !vagaAlocacao.value) {
    return
  }

  carregandoAlocacao.value = true
  const composicaoId = vagaAlocacao.value

  try {
    const resposta = await fetch('/api/equipes/alocar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        composicao_id: vagaAlocacao.value,
        chapa: colaboradorSelecionado.value.chapa,
        confirmar_transferencia: confirmarTransferencia
      })
    })

    const dados = await resposta.json()

    if (resposta.status === 409 && dados.conflito) {
      abrirConfirmacaoTransferencia({
        mensagem: dados.mensagem || 'Este colaborador já está alocado em outra equipe.',
        alocacaoAtual: dados.alocacao_atual,
        aoConfirmar: () => alocarColaborador(true)
      })
      return
    }

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao alocar colaborador.')
    }

    dialogAlocacao.value = false
    colaboradorSelecionado.value = null
    baseAlocacao.value = null
    equipeAlocacao.value = null
    vagaAlocacao.value = null

    await carregarDados()
  } catch (e) {
    erro.value = e.message || 'Erro ao alocar colaborador.'
  } finally {
    carregandoAlocacao.value = false
  }
}

async function removerColaborador(composicaoId) {
  if (!window.confirm('Deseja realmente remover este colaborador da equipe?')) {
    return
  }

  erro.value = ''
  const vaga = equipes.value
    .flatMap(equipe => equipe.vagas || [])
    .find(item => String(item.id) === String(composicaoId))
  const chapa = vaga?.colaborador?.chapa

  try {
    const resposta = await fetch('/api/equipes/remover', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        composicao_id: composicaoId
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover colaborador.')
    }

    atualizarEstadoAposRemocao(chapa, composicaoId)
  } catch (e) {
    erro.value = e.message || 'Erro ao remover colaborador.'
  }
}

async function removerTodasAlocacoes() {
  if (
    !window.confirm(
      `Remover as ${colaboradoresAlocados.value} alocações de TODAS as bases?

` +
        'As vagas continuam cadastradas — só os colaboradores saem delas. ' +
        'Isso não pode ser desfeito.'
    )
  ) {
    return
  }

  erro.value = ''
  limpandoAlocacoes.value = true

  try {
    const resposta = await fetch('/api/membros', { method: 'DELETE' })
    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover as alocações.')
    }

    await carregarDados()
  } catch (e) {
    erro.value = e.message || 'Erro ao remover as alocações.'
  } finally {
    limpandoAlocacoes.value = false
  }
}

async function liberarEquipe(equipe) {
  const ocupadas = (equipe.vagas || []).filter(vaga => vaga.colaborador)

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

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}/membros`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover os colaboradores da equipe.')
    }

    ocupadas.forEach(vaga => {
      atualizarEstadoAposRemocao(vaga.colaborador?.chapa, vaga.id)
    })
  } catch (e) {
    erro.value = e.message || 'Erro ao remover os colaboradores da equipe.'
  }
}

// ============================================================
// INICIALIZAÇÃO
// ============================================================

onMounted(() => {
  carregarSetoresNegocio()
  carregarDados().then(() => {
    try {
      const filtroSalvo = JSON.parse(
        localStorage.getItem(CHAVE_BASES_SELECIONADAS) || '[]'
      )

      if (Array.isArray(filtroSalvo)) {
        if (filtroSalvo.length === 0) {
          baseSelecionada.value = [OPCAO_TODAS_BASES]
        } else {
          const basesExistentes = opcoesBases.value.map(opcao => opcao.value)
          const validas = filtroSalvo.filter(
            base => basesExistentes.includes(base) || base === OPCAO_TODAS_BASES
          )
          baseSelecionada.value = validas.length
            ? normalizarSelecaoBases(validas)
            : [OPCAO_TODAS_BASES]
        }
      } else {
        baseSelecionada.value = [OPCAO_TODAS_BASES]
      }
    } catch {
      baseSelecionada.value = [OPCAO_TODAS_BASES]
    }
  })
})

watch(
  baseSelecionada,
  bases => {
    const basesNormalizadas = normalizarSelecaoBases(bases)

    if (JSON.stringify(basesNormalizadas) !== JSON.stringify(bases)) {
      baseSelecionada.value = basesNormalizadas
      return
    }

    localStorage.setItem(
      CHAVE_BASES_SELECIONADAS,
      JSON.stringify(basesNormalizadas)
    )
  },
  { deep: true }
)
</script>

<style scoped>
.banco-page :deep(.q-list .q-item__section--main) {
  text-align: center;
}

.banco-page :deep(.equipe-header .q-item__section--main) {
  align-items: flex-start !important;
  justify-content: flex-start !important;
  text-align: left !important;
  width: 100%;
}

.banco-page :deep(.equipe-header .q-item__label) {
  display: block;
  width: 100%;
  text-align: left !important;
}

/* linha da pessoa que a busca encontrou: a equipe pode ter 8+ vagas, então o
   destaque é o que faz o olho cair direto em quem foi procurado */
.linha-encontrada {
  background: var(--realce);
  border-left: 3px solid var(--marca);
  border-radius: 4px;
  font-weight: 600;
}
</style>
