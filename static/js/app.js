let colaboradores = [];
let equipes = [];
let colaboradorSelecionado = null;

let basesSelecionadas = [];

const CHAVE_FILTRO_BASE =
    "gerenciadorEquipes_basesSelecionadas";


// ============================================================
// FILTRO DE BASE COMPARTILHADO ENTRE AS ABAS
// ============================================================

function carregarFiltroBaseSalvo() {

    try {

        const salvo =
            localStorage.getItem(
                CHAVE_FILTRO_BASE
            );

        if (salvo) {

            const dados =
                JSON.parse(salvo);

            if (Array.isArray(dados)) {

                basesSelecionadas =
                    dados
                        .map(
                            base =>
                                String(base).trim()
                        )
                        .filter(
                            base =>
                                base !== ""
                        );

            } else {

                basesSelecionadas = [];

            }

        } else {

            basesSelecionadas = [];

        }

    } catch (erro) {

        console.error(
            "Erro ao carregar filtro salvo:",
            erro
        );

        basesSelecionadas = [];

    }

}


// ============================================================
// SALVAR FILTRO
// ============================================================

function salvarFiltroBase() {

    try {

        localStorage.setItem(
            CHAVE_FILTRO_BASE,
            JSON.stringify(
                basesSelecionadas
            )
        );

    } catch (erro) {

        console.error(
            "Erro ao salvar filtro:",
            erro
        );

    }

}


// ============================================================
// AVISAR A APLICAÇÃO QUE O FILTRO MUDOU
// ============================================================

function avisarAlteracaoFiltroBase() {

    try {

        window.dispatchEvent(
            new CustomEvent(
                "filtroBaseAlterado",
                {
                    detail: {
                        bases: [
                            ...basesSelecionadas
                        ]
                    }
                }
            )
        );

    } catch (erro) {

        console.error(
            "Erro ao avisar alteração do filtro:",
            erro
        );

    }

}


// ============================================================
// SINCRONIZAR FILTRO ENTRE AS ABAS
// ============================================================

function sincronizarFiltroBase() {

    const filtroAnterior =
        JSON.stringify(
            basesSelecionadas
        );


    carregarFiltroBaseSalvo();


    const filtroAtual =
        JSON.stringify(
            basesSelecionadas
        );


    // Se não houve alteração no filtro,
    // não precisa redesenhar nada.
    if (
        filtroAnterior === filtroAtual
    ) {

        return;

    }


    // ========================================================
    // AVISAR TODA A APLICAÇÃO
    // ========================================================

    avisarAlteracaoFiltroBase();


    // ========================================================
    // ATUALIZAR DROPDOWN DE BASE
    // ========================================================

    const opcoesFiltro =
        document.getElementById(
            "opcoesFiltroBase"
        );


    if (opcoesFiltro) {

        if (
            typeof montarFiltroBases === "function"
        ) {

            montarFiltroBases();

        }

        else if (
            typeof preencherFiltroBases === "function"
        ) {

            preencherFiltroBases();

        }

    }


    // ========================================================
    // ATUALIZAR TABELA DE EQUIPES
    // ========================================================

    const listaEquipes =
        document.getElementById(
            "listaEquipes"
        );


    if (listaEquipes) {

        renderizarEquipes();

    }


    // ========================================================
    // ATUALIZAR RESUMO
    // ========================================================

    const listaResumo =
        document.getElementById(
            "listaResumo"
        );


    if (listaResumo) {

        if (
            typeof renderizarResumo === "function"
        ) {

            renderizarResumo();

        }

        else if (
            typeof aplicarFiltroBase === "function"
        ) {

            aplicarFiltroBase();

        }

    }


    // ========================================================
    // ATUALIZAR BANCO DE DADOS
    // ========================================================

    if (
        typeof renderizarBancoDados === "function"
    ) {

        renderizarBancoDados();

    }

    else if (
        typeof aplicarFiltroBaseBanco === "function"
    ) {

        aplicarFiltroBaseBanco();

    }

}


// ============================================================
// EVENTO STORAGE
// ============================================================

window.addEventListener(
    "filtroBaseAlterado",
    function () {

        // ====================================================
        // ATUALIZAR TOTAL DE PESSOAS DISPONÍVEIS
        // ====================================================

        if (
            typeof atualizarTotalPessoasDisponiveis ===
            "function"
        ) {

            atualizarTotalPessoasDisponiveis();

        }


        // ====================================================
        // ATUALIZAR RESUMO
        // ====================================================

        if (
            typeof atualizarResumo ===
            "function"
        ) {

            atualizarResumo();

        }


        if (
            typeof atualizarIndicadoresResumo ===
            "function"
        ) {

            atualizarIndicadoresResumo();

        }


        if (
            typeof atualizarTotaisResumo ===
            "function"
        ) {

            atualizarTotaisResumo();

        }


        // ====================================================
        // RECARREGAR RESUMO QUANDO O FILTRO FOR ALTERADO
        // ====================================================

        if (
            typeof carregarResumo ===
            "function"
        ) {

            carregarResumo();

        }

    }
);

// ============================================================
// AO VOLTAR PARA A ABA
// ============================================================

document.addEventListener(
    "visibilitychange",
    function () {

        if (
            document.visibilityState ===
            "visible"
        ) {

            sincronizarFiltroBase();

        }

    }
);


// ============================================================
// AO RECEBER FOCO DA JANELA
// ============================================================

window.addEventListener(
    "focus",
    function () {

        sincronizarFiltroBase();

    }
);


// ============================================================
// PÁGINA VOLTAR A FICAR ATIVA
// ============================================================

window.addEventListener(
    "pageshow",
    function () {

        sincronizarFiltroBase();

    }
);


let posicaoRolagemEquipes = 0;


// ============================================================
// ALOCAÇÃO PELO COLABORADOR
// ============================================================

let opcoesAlocacao = {};
let equipeSelecionadaModal = null;
let vagaSelecionadaModal = null;


// ============================================================
// CARREGAR DADOS
// ============================================================

async function carregarDados(
    preservarRolagem = false
) {

    const listaEquipes =
        document.getElementById(
            "listaEquipes"
        );

    const listaColaboradores =
        document.getElementById(
            "listaColaboradores"
        );


    if (
        preservarRolagem &&
        listaEquipes
    ) {

        salvarPosicaoRolagem();

    }

    else if (
        !preservarRolagem
    ) {

        posicaoRolagemEquipes = 0;

    }


    try {

        if (listaEquipes) {

            listaEquipes.innerHTML = `
                <div class="estado-carregando">
                    Carregando equipes...
                </div>
            `;

        }


        if (listaColaboradores) {

            listaColaboradores.innerHTML = `
                <div class="estado-carregando">
                    Carregando colaboradores...
                </div>
            `;

        }


        const [
            respostaEquipes,
            respostaColaboradores
        ] = await Promise.all([

            fetch("/api/equipes"),

            fetch("/api/colaboradores")

        ]);


        if (
            !respostaEquipes.ok
        ) {

            throw new Error(
                "Erro ao carregar equipes."
            );

        }


        if (
            !respostaColaboradores.ok
        ) {

            throw new Error(
                "Erro ao carregar colaboradores."
            );

        }


        const dadosEquipes =
            await respostaEquipes.json();


        const dadosColaboradores =
            await respostaColaboradores.json();


        equipes =
            Array.isArray(
                dadosEquipes
            )
                ? dadosEquipes.sort(
                    (a, b) => {

                        const aFolguista =
                            String(
                                a.prefixo ?? ""
                            )
                                .trim()
                                .toUpperCase() ===
                            "FOLGUISTA";


                        const bFolguista =
                            String(
                                b.prefixo ?? ""
                            )
                                .trim()
                                .toUpperCase() ===
                            "FOLGUISTA";


                        if (
                            aFolguista &&
                            !bFolguista
                        ) {

                            return 1;

                        }


                        if (
                            !aFolguista &&
                            bFolguista
                        ) {

                            return -1;

                        }


                        return String(
                            a.prefixo ?? ""
                        )
                            .localeCompare(
                                String(
                                    b.prefixo ?? ""
                                ),
                                "pt-BR",
                                {
                                    numeric: true
                                }
                            );

                    }
                )
                : [];


        colaboradores =
            Array.isArray(
                dadosColaboradores
            )
                ? dadosColaboradores
                : [];


        carregarFiltroBaseSalvo();


        if (
            document.getElementById(
                "opcoesFiltroBase"
            )
        ) {

            if (
                typeof montarFiltroBases === "function"
            ) {

                montarFiltroBases();

            }

        }


        if (listaEquipes) {

            renderizarEquipes();

        }


        if (listaColaboradores) {

            renderizarColaboradores();

        }


        if (
            document.getElementById(
                "listaResumo"
            )
        ) {

            if (
                typeof aplicarFiltroBase === "function"
            ) {

                aplicarFiltroBase();

            }

        }


        // ====================================================
        // ATUALIZAR TOTAL APÓS CARREGAMENTO DOS DADOS
        // ====================================================

        if (
            typeof atualizarTotalPessoasDisponiveis ===
            "function"
        ) {

            atualizarTotalPessoasDisponiveis();

        }


        if (
            typeof atualizarResumo ===
            "function"
        ) {

            atualizarResumo();

        }


        if (
            typeof atualizarIndicadoresResumo ===
            "function"
        ) {

            atualizarIndicadoresResumo();

        }


        if (
            typeof atualizarTotaisResumo ===
            "function"
        ) {

            atualizarTotaisResumo();

        }


        if (
            preservarRolagem &&
            listaEquipes
        ) {

            restaurarPosicaoRolagem();

        }


    } catch (erro) {

        console.error(
            "Erro em carregarDados():",
            erro
        );


        if (listaEquipes) {

            listaEquipes.innerHTML = `
                <div class="estado-erro">
                    Erro ao carregar equipes.
                </div>
            `;

        }


        if (listaColaboradores) {

            listaColaboradores.innerHTML = `
                <div class="estado-erro">
                    Erro ao carregar colaboradores.
                </div>
            `;

        }

    }

}


// ============================================================
// MONTAR FILTRO DE BASE
// ============================================================

function montarFiltroBases() {

    const opcoes =
        document.getElementById(
            "opcoesFiltroBase"
        );

    const botao =
        document.getElementById(
            "btnFiltroBase"
        );


    if (
        !opcoes ||
        !botao
    ) {

        return;

    }


    const bases =
        [
            ...new Set(

                equipes
                    .map(
                        equipe =>
                            String(
                                equipe.base ?? ""
                            ).trim()
                    )
                    .filter(
                        base =>
                            base !== ""
                    )

            )
        ];


    bases.sort(
        (a, b) =>
            a.localeCompare(
                b,
                "pt-BR",
                {
                    numeric: true
                }
            )
    );


    // ========================================================
    // MANTER SOMENTE BASES QUE AINDA EXISTEM
    // ========================================================

    basesSelecionadas =
        basesSelecionadas.filter(
            base =>
                bases.includes(base)
        );


    // ========================================================
    // RECRIAR OPÇÕES SEM SALVAR NOVAMENTE O FILTRO
    // ========================================================

    opcoes.innerHTML = "";


    // ========================================================
    // SELECIONAR TODOS
    // ========================================================

    const labelTodas =
        document.createElement(
            "label"
        );


    labelTodas.className =
        "opcao-filtro-base";


    const checkboxTodas =
        document.createElement(
            "input"
        );


    checkboxTodas.type =
        "checkbox";


    checkboxTodas.value =
        "TODAS";


    checkboxTodas.checked =
        basesSelecionadas.length === 0;


    checkboxTodas.addEventListener(
        "change",
        function (event) {

            event.stopPropagation();

            alterarFiltroBase(
                checkboxTodas
            );

        }
    );


    labelTodas.appendChild(
        checkboxTodas
    );


    labelTodas.appendChild(
        document.createTextNode(
            " SELECIONAR TODOS"
        )
    );


    opcoes.appendChild(
        labelTodas
    );


    // ========================================================
    // BASES
    // ========================================================

    bases.forEach(
        base => {

            const label =
                document.createElement(
                    "label"
                );


            label.className =
                "opcao-filtro-base";


            const checkbox =
                document.createElement(
                    "input"
                );


            checkbox.type =
                "checkbox";


            checkbox.value =
                base;


            checkbox.checked =
                basesSelecionadas.includes(
                    base
                );


            checkbox.addEventListener(
                "change",
                function (event) {

                    event.stopPropagation();

                    alterarFiltroBase(
                        checkbox
                    );

                }
            );


            label.appendChild(
                checkbox
            );


            label.appendChild(
                document.createTextNode(
                    " " + base
                )
            );


            opcoes.appendChild(
                label
            );

        }
    );


    atualizarTextoFiltroBase();

}


// ============================================================
// ABRIR / FECHAR DROPDOWN
// ============================================================

function toggleFiltroBase(
    event
) {

    if (event) {

        event.preventDefault();

        event.stopPropagation();

    }


    const dropdown =
        document.querySelector(
            ".dropdown-base"
        );


    if (!dropdown) {

        return;

    }


    dropdown.classList.toggle(
        "aberto"
    );

}


// ============================================================
// ALTERAR FILTRO DE BASE
// ============================================================

function alterarFiltroBase(
    checkbox
) {

    if (!checkbox) {

        return;

    }


    const valor =
        String(
            checkbox.value ?? ""
        ).trim();


    if (
        valor === "TODAS"
    ) {

        if (
            checkbox.checked
        ) {

            basesSelecionadas = [];


            document
                .querySelectorAll(
                    '#opcoesFiltroBase input[type="checkbox"]:not([value="TODAS"])'
                )
                .forEach(
                    item => {

                        item.checked = false;

                    }
                );

        }

        else {

            const outrasMarcadas =
                document.querySelectorAll(
                    '#opcoesFiltroBase input[type="checkbox"]:checked:not([value="TODAS"])'
                );


            if (
                outrasMarcadas.length === 0
            ) {

                checkbox.checked =
                    true;

                basesSelecionadas =
                    [];

            }

        }

    }

    else {

        if (
            checkbox.checked
        ) {

            if (
                !basesSelecionadas.includes(
                    valor
                )
            ) {

                basesSelecionadas.push(
                    valor
                );

            }

        }

        else {

            basesSelecionadas =
                basesSelecionadas.filter(
                    base =>
                        base !== valor
                );

        }


        const checkboxTodas =
            document.querySelector(
                '#opcoesFiltroBase input[value="TODAS"]'
            );


        if (checkboxTodas) {

            checkboxTodas.checked =
                basesSelecionadas.length === 0;

        }

    }


    // ========================================================
    // SALVAR FILTRO
    // ========================================================

    salvarFiltroBase();


    // ========================================================
    // ATUALIZAR TEXTO
    // ========================================================

    atualizarTextoFiltroBase();


    // ========================================================
    // ATUALIZAR EQUIPES
    // ========================================================

    const listaEquipes =
        document.getElementById(
            "listaEquipes"
        );


    if (listaEquipes) {

        posicaoRolagemEquipes = 0;

        renderizarEquipes();

    }


    // ========================================================
    // ATUALIZAR RESUMO
    // ========================================================

    const listaResumo =
        document.getElementById(
            "listaResumo"
        );


    if (listaResumo) {

        if (
            typeof renderizarResumo === "function"
        ) {

            renderizarResumo();

        }

        else if (
            typeof aplicarFiltroBase === "function"
        ) {

            aplicarFiltroBase();

        }

    }


    // ========================================================
    // ATUALIZAR BANCO DE DADOS
    // ========================================================

    if (
        typeof renderizarBancoDados === "function"
    ) {

        renderizarBancoDados();

    }

    else if (
        typeof aplicarFiltroBaseBanco === "function"
    ) {

        aplicarFiltroBaseBanco();

    }


    // ========================================================
    // ATUALIZAR TOTAL DE PESSOAS DISPONÍVEIS
    //
    // ISSO ACONTECE IMEDIATAMENTE QUANDO O FILTRO MUDA.
    // NÃO DEPENDE DO BOTÃO ATUALIZAR.
    // ========================================================

    avisarAlteracaoFiltroBase();


    if (
        typeof atualizarTotalPessoasDisponiveis ===
        "function"
    ) {

        atualizarTotalPessoasDisponiveis();

    }


    if (
        typeof atualizarResumo ===
        "function"
    ) {

        atualizarResumo();

    }


    if (
        typeof atualizarIndicadoresResumo ===
        "function"
    ) {

        atualizarIndicadoresResumo();

    }


    if (
        typeof atualizarTotaisResumo ===
        "function"
    ) {

        atualizarTotaisResumo();

    }

}


// ============================================================
// ATUALIZAR TEXTO DO BOTÃO
// ============================================================

function atualizarTextoFiltroBase() {

    const textoFiltro =
        document.getElementById(
            "textoFiltroBase"
        );


    const botao =
        document.getElementById(
            "btnFiltroBase"
        );


    if (textoFiltro) {

        let texto =
            "SELECIONAR TODOS";


        if (
            basesSelecionadas.length === 1
        ) {

            texto =
                basesSelecionadas[0];

        }

        else if (
            basesSelecionadas.length > 1
        ) {

            texto =
                `${basesSelecionadas.length} BASES SELECIONADAS`;

        }


        textoFiltro.textContent =
            texto;

        return;

    }


    if (botao) {

        let texto =
            "SELECIONAR TODOS";


        if (
            basesSelecionadas.length === 1
        ) {

            texto =
                basesSelecionadas[0];

        }

        else if (
            basesSelecionadas.length > 1
        ) {

            texto =
                `${basesSelecionadas.length} BASES SELECIONADAS`;

        }


        botao.innerHTML = `
            ${texto}
            <span class="seta-dropdown">▼</span>
        `;

    }

}


// ============================================================
// FECHAR DROPDOWN AO CLICAR FORA
// ============================================================

document.addEventListener(
    "click",
    function (event) {

        const dropdown =
            document.querySelector(
                ".dropdown-base"
            );


        if (!dropdown) {

            return;

        }


        if (
            !dropdown.contains(
                event.target
            )
        ) {

            dropdown.classList.remove(
                "aberto"
            );

        }

    }
);


// ============================================================
// FILTRAR POR BASE
// ============================================================

function filtrarPorBase() {

    renderizarEquipes();


    avisarAlteracaoFiltroBase();


    if (
        typeof atualizarTotalPessoasDisponiveis ===
        "function"
    ) {

        atualizarTotalPessoasDisponiveis();

    }

}


// ============================================================
// RENDERIZAR EQUIPES
// ============================================================

function renderizarEquipes() {

    const container =
        document.getElementById(
            "listaEquipes"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    const equipesFiltradas =
        basesSelecionadas.length === 0
            ? equipes
            : equipes.filter(
                equipe =>
                    basesSelecionadas.includes(
                        String(
                            equipe.base ?? ""
                        ).trim()
                    )
            );


    if (
        equipesFiltradas.length === 0
    ) {

        container.innerHTML = `
            <div class="estado-vazio">
                Nenhuma equipe encontrada.
            </div>
        `;

        return;

    }


    equipesFiltradas.forEach(
        equipe => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "team-card";


            // =================================================
            // CABEÇALHO DA EQUIPE
            // =================================================

            const teamHeader =
                document.createElement(
                    "div"
                );


            teamHeader.className =
                "team-header";


            teamHeader.innerHTML = `

                <div class="team-title">
                    CONSTRUÇÃO - ${equipe.prefixo ?? ""}
                </div>

                <div class="team-base">
                    BASE: ${equipe.base ?? ""}
                </div>

            `;


            card.appendChild(
                teamHeader
            );


            // =================================================
            // CABEÇALHO DA TABELA
            // =================================================

            const gridHeader =
                document.createElement(
                    "div"
                );


            gridHeader.className =
                "grid-header";


            const cabecalhos = [

                "FUNÇÃO ER",

                "CHAPA",

                "NOME",

                "FUNÇÃO",

                "AÇÃO"

            ];


            cabecalhos.forEach(
                titulo => {

                    const celula =
                        document.createElement(
                            "div"
                        );


                    celula.className =
                        "grid-header-cell";


                    celula.textContent =
                        titulo;


                    gridHeader.appendChild(
                        celula
                    );

                }
            );


            card.appendChild(
                gridHeader
            );


            // =================================================
            // VAGAS
            // =================================================

            const vagas =
                Array.isArray(
                    equipe.vagas
                )
                    ? equipe.vagas
                    : [];


            vagas.forEach(
                vaga => {

                    card.appendChild(
                        criarLinhaVaga(
                            equipe,
                            vaga
                        )
                    );

                }
            );


            container.appendChild(
                card
            );

        }
    );

}


// ============================================================
// CRIAR LINHA DA VAGA
// ============================================================

function criarLinhaVaga(
    equipe,
    vaga
) {

    const linha =
        document.createElement(
            "div"
        );


    linha.className =
        "team-row";


    const colaborador =
        vaga.colaborador ||
        null;


    let chapa = "";
    let nome = "";
    let funcao = "";


    if (colaborador) {

        chapa =
            colaborador.chapa ?? "";

        nome =
            colaborador.nome ?? "";

        funcao =
            colaborador.funcao ?? "";

    }


    // ========================================================
    // FUNÇÃO ER
    // ========================================================

    const celulaFuncaoER =
        document.createElement(
            "div"
        );


    celulaFuncaoER.className =
        "cell-role";


    celulaFuncaoER.textContent =
        vaga.funcao_er ?? "";


    // ========================================================
    // CHAPA
    // ========================================================

    const celulaChapa =
        document.createElement(
            "div"
        );


    celulaChapa.className =
        "cell-chapa";


    const inputChapa =
        document.createElement(
            "input"
        );


    inputChapa.className =
        "input";


    inputChapa.type =
        "text";


    inputChapa.placeholder =
        "CHAPA";


    inputChapa.value =
        chapa;


    // ========================================================
    // NOME
    // ========================================================

    const celulaNome =
        document.createElement(
            "div"
        );


    celulaNome.className =
        "cell-name";


    const inputNome =
        document.createElement(
            "input"
        );


    inputNome.className =
        "input";


    inputNome.type =
        "text";


    inputNome.placeholder =
        "NOME";


    inputNome.value =
        nome;


    // ========================================================
    // FUNÇÃO
    // ========================================================

    const celulaFuncao =
        document.createElement(
            "div"
        );


    celulaFuncao.className =
        "cell-function";


    const inputFuncao =
        document.createElement(
            "input"
        );


    inputFuncao.className =
        "input";


    inputFuncao.type =
        "text";


    inputFuncao.value =
        funcao;


    inputFuncao.disabled =
        true;


    // ========================================================
    // AÇÃO
    // ========================================================

    const celulaAcao =
        document.createElement(
            "div"
        );


    celulaAcao.className =
        "cell-action";


    const botao =
        document.createElement(
            "button"
        );


    botao.type =
        "button";


    botao.className =
        "action-button";


    if (colaborador) {

        botao.textContent =
            "REMOVER";


        botao.classList.add(
            "remove"
        );


        botao.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                removerColaborador(
                    vaga.id
                );

            }
        );

    }

    else {

        botao.textContent =
            "ALOCAR";


        botao.classList.add(
            "allocate"
        );


        botao.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                vagaSelecionadaModal =
                    vaga;


                equipeSelecionadaModal =
                    equipe;


                abrirModalAlocacao();

            }
        );

    }


    // ========================================================
    // MONTAR CÉLULAS
    // ========================================================

    celulaChapa.appendChild(
        inputChapa
    );


    celulaNome.appendChild(
        inputNome
    );


    celulaFuncao.appendChild(
        inputFuncao
    );


    celulaAcao.appendChild(
        botao
    );


    // ========================================================
    // ORDEM DAS COLUNAS
    // ========================================================

    linha.appendChild(
        celulaFuncaoER
    );


    linha.appendChild(
        celulaChapa
    );


    linha.appendChild(
        celulaNome
    );


    linha.appendChild(
        celulaFuncao
    );


    linha.appendChild(
        celulaAcao
    );


    configurarAutocomplete(
        inputChapa,
        inputNome,
        inputFuncao
    );


    return linha;

}


// ============================================================
// RENDERIZAR COLABORADORES
// ============================================================

function renderizarColaboradores(
    lista = colaboradores
) {

    const container =
        document.getElementById(
            "listaColaboradores"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (
        lista.length === 0
    ) {

        container.innerHTML = `
            <div class="estado-vazio">
                Nenhum colaborador encontrado.
            </div>
        `;

        return;

    }


    lista.forEach(
        colaborador => {

            const linha =
                document.createElement(
                    "div"
                );


            linha.className =
                "employee-row";


            const chapa =
                document.createElement(
                    "div"
                );


            chapa.className =
                "employee-chapa";


            chapa.textContent =
                colaborador.chapa ?? "";


            const nome =
                document.createElement(
                    "div"
                );


            nome.className =
                "employee-name";


            nome.textContent =
                colaborador.nome ?? "";


            const funcao =
                document.createElement(
                    "div"
                );


            funcao.className =
                "employee-function";


            funcao.textContent =
                colaborador.funcao ?? "";


            const status =
                document.createElement(
                    "div"
                );


            status.className =
                "employee-status";


            if (
                colaborador.alocado === true
            ) {

                status.textContent =
                    "ALOCADO";


                status.classList.add(
                    "status-allocated"
                );

            }

            else {

                status.textContent =
                    "LIVRE";


                status.classList.add(
                    "status-free"
                );

            }


            linha.appendChild(
                chapa
            );


            linha.appendChild(
                nome
            );


            linha.appendChild(
                funcao
            );


            linha.appendChild(
                status
            );


            linha.addEventListener(
                "click",
                () => {

                    selecionarColaborador(
                        colaborador,
                        linha
                    );

                }
            );


            container.appendChild(
                linha
            );

        }
    );

}


// ============================================================
// SELECIONAR COLABORADOR
// ============================================================

function selecionarColaborador(
    colaborador,
    elemento
) {

    document
        .querySelectorAll(
            ".employee-row.colaborador-selecionado"
        )
        .forEach(
            linha => {

                linha.classList.remove(
                    "colaborador-selecionado"
                );

            }
        );


    elemento.classList.add(
        "colaborador-selecionado"
    );


    colaboradorSelecionado =
        colaborador;


    mostrarBotaoAlocacao();

}


// ============================================================
// MOSTRAR BOTÃO DE ALOCAÇÃO
// ============================================================

function mostrarBotaoAlocacao() {

    const panel =
        document.querySelector(
            ".employees-container"
        );


    if (!panel) {

        return;

    }


    const botaoAnterior =
        document.getElementById(
            "btnAlocarColaborador"
        );


    if (botaoAnterior) {

        botaoAnterior.remove();

    }


    if (!colaboradorSelecionado) {

        return;

    }


    const botao =
        document.createElement(
            "button"
        );


    botao.id =
        "btnAlocarColaborador";


    botao.type =
        "button";


    botao.className =
        "btn btn-primary btn-alocar-colaborador";


    botao.textContent =
        "ALOCAR COLABORADOR";


    botao.onclick =
        function (event) {

            event.preventDefault();

            event.stopPropagation();


            equipeSelecionadaModal =
                null;


            vagaSelecionadaModal =
                null;


            abrirModalAlocacao();

        };


    panel.parentElement.insertBefore(
        botao,
        panel
    );

}


// ============================================================
// ABRIR MODAL DE ALOCAÇÃO
// ============================================================

async function abrirModalAlocacao() {

    if (!colaboradorSelecionado) {

        alert(
            "Selecione um colaborador primeiro."
        );

        return;

    }


    const modal =
        document.getElementById(
            "modalAlocacao"
        );


    const colaborador =
        document.getElementById(
            "modalColaborador"
        );


    const selectBase =
        document.getElementById(
            "modalBase"
        );


    const selectEquipe =
        document.getElementById(
            "modalEquipe"
        );


    const selectVaga =
        document.getElementById(
            "modalVaga"
        );


    if (
        !modal ||
        !colaborador ||
        !selectBase ||
        !selectEquipe ||
        !selectVaga
    ) {

        console.error(
            "Elementos do modal de alocação não encontrados."
        );

        return;

    }


    colaborador.textContent =
        `${colaboradorSelecionado.chapa ?? ""} | ` +
        `${colaboradorSelecionado.nome ?? ""} | ` +
        `${colaboradorSelecionado.funcao ?? ""}`;


    selectBase.innerHTML = `
        <option value="">
            CARREGANDO BASES...
        </option>
    `;


    selectEquipe.innerHTML = `
        <option value="">
            SELECIONE A EQUIPE
        </option>
    `;


    selectVaga.innerHTML = `
        <option value="">
            SELECIONE A VAGA
        </option>
    `;


    selectEquipe.disabled =
        true;


    selectVaga.disabled =
        true;


    modal.style.display =
        "flex";


    try {

        const resposta =
            await fetch(
                "/api/opcoes-alocacao"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao carregar opções de alocação."
            );

        }


        opcoesAlocacao =
            dados || {};


        selectBase.innerHTML = `
            <option value="">
                SELECIONE A BASE
            </option>
        `;


        Object.keys(
            opcoesAlocacao
        )
            .sort(
                (a, b) =>
                    a.localeCompare(
                        b,
                        "pt-BR",
                        {
                            numeric: true
                        }
                    )
            )
            .forEach(
                base => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        base;


                    option.textContent =
                        base;


                    selectBase.appendChild(
                        option
                    );

                }
            );


        if (
            equipeSelecionadaModal
        ) {

            const baseEquipe =
                String(
                    equipeSelecionadaModal.base ?? ""
                ).trim();


            if (
                baseEquipe &&
                opcoesAlocacao[baseEquipe]
            ) {

                selectBase.value =
                    baseEquipe;


                carregarEquipesModal();


                selectEquipe.value =
                    equipeSelecionadaModal.id;


                carregarVagasModal();


                if (
                    vagaSelecionadaModal
                ) {

                    selectVaga.value =
                        vagaSelecionadaModal.id;

                }

            }

        }

    } catch (erro) {

        console.error(
            "Erro ao carregar opções de alocação:",
            erro
        );


        alert(
            erro.message ||
            "Erro ao carregar opções de alocação."
        );

    }

}


// ============================================================
// CARREGAR EQUIPES DO MODAL
// ============================================================

function carregarEquipesModal() {

    const selectBase =
        document.getElementById(
            "modalBase"
        );


    const selectEquipe =
        document.getElementById(
            "modalEquipe"
        );


    const selectVaga =
        document.getElementById(
            "modalVaga"
        );


    if (
        !selectBase ||
        !selectEquipe ||
        !selectVaga
    ) {

        return;

    }


    const base =
        selectBase.value;


    selectEquipe.innerHTML = `
        <option value="">
            SELECIONE A EQUIPE
        </option>
    `;


    selectVaga.innerHTML = `
        <option value="">
            SELECIONE A VAGA
        </option>
    `;


    selectVaga.disabled =
        true;


    if (!base) {

        selectEquipe.disabled =
            true;

        return;

    }


    const listaEquipes =
        Array.isArray(
            opcoesAlocacao[base]
        )
            ? [...opcoesAlocacao[base]]
            : [];


    listaEquipes.sort(
        (a, b) => {

            const aFolguista =
                String(
                    a.prefixo ?? ""
                )
                    .trim()
                    .toUpperCase() ===
                "FOLGUISTA";


            const bFolguista =
                String(
                    b.prefixo ?? ""
                )
                    .trim()
                    .toUpperCase() ===
                "FOLGUISTA";


            if (
                aFolguista &&
                !bFolguista
            ) {

                return 1;

            }


            if (
                !aFolguista &&
                bFolguista
            ) {

                return -1;

            }


            return String(
                a.prefixo ?? ""
            )
                .localeCompare(
                    String(
                        b.prefixo ?? ""
                    ),
                    "pt-BR",
                    {
                        numeric: true
                    }
                );

        }
    );


    listaEquipes.forEach(
        equipe => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                equipe.id;


            option.textContent =
                equipe.prefixo;


            selectEquipe.appendChild(
                option
            );

        }
    );


    selectEquipe.disabled =
        listaEquipes.length === 0;

}


// ============================================================
// CARREGAR VAGAS DO MODAL
// ============================================================

function carregarVagasModal() {

    const selectBase =
        document.getElementById(
            "modalBase"
        );


    const selectEquipe =
        document.getElementById(
            "modalEquipe"
        );


    const selectVaga =
        document.getElementById(
            "modalVaga"
        );


    if (
        !selectBase ||
        !selectEquipe ||
        !selectVaga
    ) {

        return;

    }


    const base =
        selectBase.value;


    const equipeId =
        selectEquipe.value;


    selectVaga.innerHTML = `
        <option value="">
            SELECIONE A VAGA
        </option>
    `;


    selectVaga.disabled =
        true;


    const listaEquipes =
        opcoesAlocacao[base] || [];


    const equipe =
        listaEquipes.find(
            item =>
                String(item.id) ===
                String(equipeId)
        );


    if (!equipe) {

        equipeSelecionadaModal =
            null;

        vagaSelecionadaModal =
            null;

        return;

    }


    equipeSelecionadaModal =
        equipe;


    const vagas =
        Array.isArray(
            equipe.vagas
        )
            ? equipe.vagas
            : [];


    vagas.forEach(
        vaga => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                vaga.id;


            option.textContent =
                `${vaga.funcao_er ?? ""} | ${vaga.estrutura ?? ""}`;


            selectVaga.appendChild(
                option
            );

        }
    );


    selectVaga.disabled =
        vagas.length === 0;

}


// ============================================================
// FECHAR MODAL
// ============================================================

function fecharModalAlocacao() {

    const modal =
        document.getElementById(
            "modalAlocacao"
        );


    if (!modal) {

        return;

    }


    modal.style.display =
        "none";


    vagaSelecionadaModal =
        null;


    equipeSelecionadaModal =
        null;

}


// ============================================================
// CONFIRMAR ALOCAÇÃO
// ============================================================

async function confirmarAlocacaoModal() {

    const selectBase =
        document.getElementById(
            "modalBase"
        );


    const selectEquipe =
        document.getElementById(
            "modalEquipe"
        );


    const selectVaga =
        document.getElementById(
            "modalVaga"
        );


    if (
        !selectBase ||
        !selectEquipe ||
        !selectVaga
    ) {

        return;

    }


    if (!colaboradorSelecionado) {

        alert(
            "Nenhum colaborador selecionado."
        );

        return;

    }


    if (!selectBase.value) {

        alert(
            "Selecione uma BASE."
        );

        return;

    }


    if (!selectEquipe.value) {

        alert(
            "Selecione uma EQUIPE."
        );

        return;

    }


    if (!selectVaga.value) {

        alert(
            "Selecione uma VAGA."
        );

        return;

    }


    const equipe =
        (
            opcoesAlocacao[
                selectBase.value
            ] || []
        )
            .find(
                item =>
                    String(item.id) ===
                    String(selectEquipe.value)
            );


    if (!equipe) {

        alert(
            "Não foi possível identificar a equipe selecionada."
        );

        return;

    }


    const vaga =
        (
            equipe.vagas || []
        )
            .find(
                item =>
                    String(item.id) ===
                    String(selectVaga.value)
            );


    if (!vaga) {

        alert(
            "Não foi possível identificar a vaga selecionada."
        );

        return;

    }


    const chapa =
        String(
            colaboradorSelecionado.chapa ?? ""
        ).trim();


    if (!chapa) {

        alert(
            "O colaborador selecionado não possui CHAPA."
        );

        return;

    }


    const botoes =
        document.querySelectorAll(
            "#modalAlocacao button"
        );


    botoes.forEach(
        botao => {

            botao.disabled =
                true;

        }
    );


    salvarPosicaoRolagem();


    try {

        const resposta =
            await fetch(
                "/api/equipes/alocar",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            composicao_id:
                                vaga.id,

                            chapa:
                                chapa,

                            nome:
                                colaboradorSelecionado.nome ?? ""

                        })

                }
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao alocar colaborador."
            );

        }


        alert(
            dados.mensagem ||
            "Colaborador alocado com sucesso."
        );


        colaboradorSelecionado =
            null;


        const botaoAlocar =
            document.getElementById(
                "btnAlocarColaborador"
            );


        if (botaoAlocar) {

            botaoAlocar.remove();

        }


        fecharModalAlocacao();


        await carregarDados(
            true
        );


    } catch (erro) {

        console.error(
            "ERRO AO ALOCAR COLABORADOR:",
            erro
        );


        alert(
            erro.message ||
            "Erro ao alocar colaborador."
        );


    } finally {

        botoes.forEach(
            botao => {

                botao.disabled =
                    false;

            }
        );

    }

}


// ============================================================
// FILTRAR COLABORADORES
// ============================================================

function filtrarColaboradores() {

    const campo =
        document.getElementById(
            "pesquisa"
        );


    if (!campo) {

        return;

    }


    const termo =
        campo.value
            .trim()
            .toLowerCase();


    if (!termo) {

        renderizarColaboradores(
            colaboradores
        );

        return;

    }


    const resultado =
        colaboradores.filter(
            colaborador => {

                const chapa =
                    String(
                        colaborador.chapa ?? ""
                    ).toLowerCase();


                const nome =
                    String(
                        colaborador.nome ?? ""
                    ).toLowerCase();


                return (
                    chapa.includes(termo) ||
                    nome.includes(termo)
                );

            }
        );


    renderizarColaboradores(
        resultado
    );

}


// ============================================================
// CONFIGURAR AUTOCOMPLETE
// ============================================================

function configurarAutocomplete(
    inputChapa,
    inputNome,
    inputFuncao
) {

    configurarCampoAutocomplete(
        inputChapa,
        inputChapa,
        inputNome,
        inputFuncao
    );


    configurarCampoAutocomplete(
        inputNome,
        inputChapa,
        inputNome,
        inputFuncao
    );

}


// ============================================================
// AUTOCOMPLETE
// ============================================================

function configurarCampoAutocomplete(
    campo,
    campoChapa,
    campoNome,
    campoFuncao
) {

    const wrapper =
        campo.parentElement;


    if (!wrapper) {

        return;

    }


    wrapper.style.position =
        "relative";


    const lista =
        document.createElement(
            "div"
        );


    lista.className =
        "autocomplete";


    lista.style.display =
        "none";


    wrapper.appendChild(
        lista
    );


    campo.addEventListener(
        "input",
        () => {

            const termo =
                campo.value
                    .trim()
                    .toLowerCase();


            lista.innerHTML = "";


            if (!termo) {

                lista.style.display =
                    "none";

                return;

            }


            const resultados =
                colaboradores
                    .filter(
                        colaborador => {

                            const chapa =
                                String(
                                    colaborador.chapa ?? ""
                                ).toLowerCase();


                            const nome =
                                String(
                                    colaborador.nome ?? ""
                                ).toLowerCase();


                            return (
                                chapa.includes(termo) ||
                                nome.includes(termo)
                            );

                        }
                    )
                    .slice(
                        0,
                        8
                    );


            if (
                resultados.length === 0
            ) {

                lista.style.display =
                    "none";

                return;

            }


            resultados.forEach(
                colaborador => {

                    const item =
                        document.createElement(
                            "button"
                        );


                    item.type =
                        "button";


                    item.className =
                        "autocomplete-item";


                    item.textContent =
                        `${colaborador.chapa ?? ""} | ${colaborador.nome ?? ""} | ${colaborador.funcao ?? ""}`;


                    item.addEventListener(
                        "mousedown",
                        event => {

                            event.preventDefault();

                        }
                    );


                    item.addEventListener(
                        "click",
                        event => {

                            event.preventDefault();

                            event.stopPropagation();


                            campoChapa.value =
                                colaborador.chapa ?? "";


                            campoNome.value =
                                colaborador.nome ?? "";


                            campoFuncao.value =
                                colaborador.funcao ?? "";


                            lista.style.display =
                                "none";

                        }
                    );


                    lista.appendChild(
                        item
                    );

                }
            );


            lista.style.display =
                "block";

        }
    );


    document.addEventListener(
        "click",
        event => {

            if (
                !wrapper.contains(
                    event.target
                )
            ) {

                lista.style.display =
                    "none";

            }

        }
    );

}


// ============================================================
// ALOCAR COLABORADOR SELECIONADO
// ============================================================

async function alocarColaboradorSelecionado(
    composicaoId
) {

    if (
        !colaboradorSelecionado
    ) {

        return;

    }


    const chapa =
        String(
            colaboradorSelecionado.chapa ?? ""
        ).trim();


    if (!chapa) {

        alert(
            "O colaborador selecionado não possui CHAPA."
        );

        return;

    }


    await alocarColaborador(
        composicaoId,
        chapa,
        colaboradorSelecionado.nome
    );

}


// ============================================================
// ALOCAR COLABORADOR
// ============================================================

async function alocarColaborador(
    composicaoId,
    chapa,
    nome
) {

    chapa =
        String(
            chapa ?? ""
        ).trim();


    nome =
        String(
            nome ?? ""
        ).trim();


    if (
        !chapa &&
        !nome
    ) {

        alert(
            "Informe a chapa ou o nome do colaborador."
        );

        return;

    }


    salvarPosicaoRolagem();


    try {

        const resposta =
            await fetch(
                "/api/equipes/alocar",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            composicao_id:
                                composicaoId,

                            chapa:
                                chapa,

                            nome:
                                nome

                        })

                }
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao alocar colaborador."
            );

        }


        colaboradorSelecionado =
            null;


        const botao =
            document.getElementById(
                "btnAlocarColaborador"
            );


        if (botao) {

            botao.remove();

        }


        await carregarDados(
            true
        );


    } catch (erro) {

        console.error(
            erro
        );


        alert(
            erro.message
        );

    }

}


// ============================================================
// REMOVER COLABORADOR
// ============================================================

async function removerColaborador(
    composicaoId
) {

    if (
        !confirm(
            "Deseja realmente remover este colaborador?"
        )
    ) {

        return;

    }


    salvarPosicaoRolagem();


    try {

        const resposta =
            await fetch(
                "/api/equipes/remover",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            composicao_id:
                                composicaoId

                        })

                }
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao remover colaborador."
            );

        }


        await carregarDados(
            true
        );


    } catch (erro) {

        console.error(
            erro
        );


        alert(
            erro.message
        );

    }

}


// ============================================================
// SALVAR POSIÇÃO DA ROLAGEM
// ============================================================

function salvarPosicaoRolagem() {

    const container =
        document.getElementById(
            "listaEquipes"
        );


    if (!container) {

        return;

    }


    posicaoRolagemEquipes =
        container.scrollTop;

}


// ============================================================
// RESTAURAR POSIÇÃO DA ROLAGEM
// ============================================================

function restaurarPosicaoRolagem() {

    const container =
        document.getElementById(
            "listaEquipes"
        );


    if (!container) {

        return;

    }


    container.scrollTop =
        posicaoRolagemEquipes;


    requestAnimationFrame(
        () => {

            container.scrollTop =
                posicaoRolagemEquipes;


            requestAnimationFrame(
                () => {

                    container.scrollTop =
                        posicaoRolagemEquipes;

                }
            );

        }
    );

}


// ============================================================
// INICIALIZAÇÃO
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "app.js carregado corretamente."
        );


        carregarFiltroBaseSalvo();


        carregarDados();

    }
);