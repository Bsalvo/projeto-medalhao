"""Pipeline de dados com Arquitetura Medalhão - Parte 1.

Cria o catálogo de fontes, carrega a base escolhida pelo usuário, preserva os
dados na camada Bronze e gera um diagnóstico técnico na camada Prata.
"""

import os
import sys
import textwrap

import pandas as pd

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_FONTES = os.path.join(PASTA_PROJETO, "fontes.txt")

FONTES_INICIAIS = [
    ("A", "Pinguins", "https://raw.githubusercontent.com/mwaskom/seaborn-data/refs/heads/master/penguins.csv"),
    ("B", "Desempenho escolar", "https://raw.githubusercontent.com/gramener/datasets/main/student-mat.csv"),
    ("C", "Produtos", "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_products_dataset.csv"),
    ("D", "População brasileira", "https://raw.githubusercontent.com/rdsilva/BrazilPopulation/master/brazil-population-2012-2017-spread.csv"),
]

LARGURA_RELATORIO = 90
LIMITE_EXEMPLOS = 5
LIMITE_TEXTO_EXEMPLO = 25
LIMITE_AUSENTES_ALTO = 20  # percentual a partir do qual a coluna merece destaque
LIMITE_POUCOS_VALORES = 10  # numérica com até esses valores únicos pode ser um código
LIMITE_ATIPICOS_LISTADOS = 5  # colunas com valores atípicos citadas no relatório
MARCADORES_DE_AUSENCIA = {".", "-", "--", "?", "s/i", "nd", "sem informação", "desconhecido", "unknown"}


# ---------------------------------------------------------------------------
# Catálogo e seleção da fonte
# ---------------------------------------------------------------------------

def garantir_fontes():
    """Cria o fontes.txt somente se ele ainda não existir."""
    if os.path.exists(ARQUIVO_FONTES):
        print("Catálogo fontes.txt encontrado.")
        return

    with open(ARQUIVO_FONTES, "w", encoding="utf-8") as arquivo:
        for codigo, tema, url in FONTES_INICIAIS:
            arquivo.write(f"{codigo};{tema};{url}\n")
    print("Catálogo fontes.txt criado.")


def ler_catalogo():
    """Lê o fontes.txt e devolve uma lista de tuplas (código, tema, URL)."""
    catalogo = []
    with open(ARQUIVO_FONTES, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(";")
            if len(partes) == 3:
                catalogo.append((partes[0].strip().upper(), partes[1].strip(), partes[2].strip()))
    return catalogo


def selecionar_fonte(catalogo):
    """Pede o código do tema até receber um válido e devolve (código, tema, URL)."""
    print("\nFontes disponíveis:")
    for codigo, tema, _ in catalogo:
        print(f"  {codigo} - {tema}")

    codigos = [codigo for codigo, _, _ in catalogo]
    opcoes = ", ".join(codigos[:-1]) + f" ou {codigos[-1]}" if len(codigos) > 1 else codigos[0]

    while True:
        escolha = input(f"\nInforme o tema da base de dados ({opcoes}): ").strip().upper()
        for codigo, tema, url in catalogo:
            if codigo == escolha:
                return codigo, tema, url
        print(f"Opção inválida: '{escolha}'. Tente novamente.")


def carregar_base(url):
    """Lê o CSV identificando automaticamente o separador."""
    return pd.read_csv(url, sep=None, engine="python")


# ---------------------------------------------------------------------------
# Camadas da Arquitetura Medalhão
# ---------------------------------------------------------------------------

def criar_camadas():
    """Cria as pastas bronze, prata e ouro e devolve seus caminhos."""
    camadas = {}
    for nome in ["bronze", "prata", "ouro"]:
        camadas[nome] = os.path.join(PASTA_PROJETO, nome)
        os.makedirs(camadas[nome], exist_ok=True)
    return camadas


def salvar_bronze(df, pasta_bronze):
    """Salva os dados exatamente como foram carregados, sem tratamento."""
    df.to_csv(os.path.join(pasta_bronze, "dados_brutos.csv"), index=False)


# ---------------------------------------------------------------------------
# Seções do diagnóstico
# ---------------------------------------------------------------------------

def titulo_secao(numero, texto):
    return ["", "=" * LARGURA_RELATORIO, f"{numero}. {texto}", "=" * LARGURA_RELATORIO]


def largura_nomes(df, minimo=10):
    """Calcula a largura da coluna de nomes para que qualquer base fique alinhada."""
    return max([minimo] + [len(str(coluna)) for coluna in df.columns]) + 2


def resumir_texto(valor):
    texto = " ".join(str(valor).split())
    if len(texto) > LIMITE_TEXTO_EXEMPLO:
        return texto[:LIMITE_TEXTO_EXEMPLO - 3] + "..."
    return texto


def secao_fonte(codigo, tema, url):
    linhas = titulo_secao(1, "IDENTIFICAÇÃO DA FONTE")
    linhas.append(f"{'Código do tema:':<20}{codigo}")
    linhas.append(f"{'Nome do tema:':<20}{tema}")
    linhas.append(f"{'URL utilizada:':<20}{url}")
    linhas.append(f"{'Dados brutos em:':<20}bronze/dados_brutos.csv")
    return linhas


def secao_visao_geral(df, numericas, nao_numericas):
    linhas = titulo_secao(2, "VISÃO GERAL DA BASE")
    linhas.append(f"{'Registros (linhas):':<30}{len(df):>8}")
    linhas.append(f"{'Variáveis (colunas):':<30}{df.shape[1]:>8}")
    linhas.append(f"{'  - numéricas:':<30}{numericas.shape[1]:>8}")
    linhas.append(f"{'  - não numéricas:':<30}{nao_numericas.shape[1]:>8}")
    linhas.append("")
    linhas.append("Nota: a separação entre numéricas e não numéricas segue o tipo de dado identificado")
    linhas.append("pelo Pandas. Ela não indica, sozinha, o significado estatístico da variável.")
    return linhas


def secao_estrutura(df):
    largura = largura_nomes(df)
    linhas = titulo_secao(3, "ESTRUTURA DAS VARIÁVEIS")
    linhas.append(f"{'COLUNA':<{largura}}{'TIPO':<12}{'AUSENTES':>10}{'AUSENTES %':>13}")
    linhas.append("-" * (largura + 35))
    for coluna in df.columns:
        ausentes = int(df[coluna].isna().sum())
        percentual = ausentes / len(df) * 100 if len(df) > 0 else 0
        linhas.append(f"{str(coluna):<{largura}}{str(df[coluna].dtype):<12}{ausentes:>10}{percentual:>12.2f}%")
    return linhas


def secao_duplicados(df):
    duplicados = int(df.duplicated().sum())
    percentual = duplicados / len(df) * 100 if len(df) > 0 else 0
    linhas = titulo_secao(4, "REGISTROS DUPLICADOS")
    linhas.append(f"Registros duplicados encontrados: {duplicados} ({percentual:.2f}% da base)")
    linhas.append("Critério: linha idêntica a uma anterior em todas as colunas.")
    return linhas


def secao_cardinalidade(df):
    largura = largura_nomes(df)
    linhas = titulo_secao(5, "CARDINALIDADE")
    linhas.append("Quantidade de valores únicos por variável (valores ausentes não são contados).")
    linhas.append("")
    linhas.append(f"{'COLUNA':<{largura}}{'ÚNICOS':>10}")
    linhas.append("-" * (largura + 10))
    for coluna in df.columns:
        linhas.append(f"{str(coluna):<{largura}}{df[coluna].nunique():>10}")
    return linhas


def secao_numericas(df, numericas):
    linhas = titulo_secao(6, "VARIÁVEIS NUMÉRICAS")
    if numericas.shape[1] == 0:
        linhas.append("Nenhuma variável numérica encontrada.")
        return linhas

    largura = largura_nomes(numericas)
    linhas.append(f"{'VARIÁVEL':<{largura}}{'MÍNIMO':>15}{'MÁXIMO':>15}{'MÉDIA':>15}{'MEDIANA':>15}{'DESVIO-PADRÃO':>16}")
    linhas.append("-" * (largura + 76))
    for coluna in numericas.columns:
        serie = df[coluna]
        if serie.notna().sum() == 0:
            linhas.append(f"{str(coluna):<{largura}}sem estatísticas: coluna totalmente vazia")
            continue
        linhas.append(
            f"{str(coluna):<{largura}}{serie.min():>15.2f}{serie.max():>15.2f}"
            f"{serie.mean():>15.2f}{serie.median():>15.2f}{serie.std():>16.2f}"
        )
    return linhas


def secao_nao_numericas(df, nao_numericas):
    linhas = titulo_secao(7, "VARIÁVEIS NÃO NUMÉRICAS")
    if nao_numericas.shape[1] == 0:
        linhas.append("Nenhuma variável não numérica encontrada.")
        return linhas

    largura = largura_nomes(nao_numericas)
    linhas.append(f"Os exemplos mostram até {LIMITE_EXEMPLOS} valores diferentes, na ordem em que aparecem na base.")
    linhas.append("")
    linhas.append(f"{'VARIÁVEL':<{largura}}{'ÚNICOS':>8}    EXEMPLOS")
    linhas.append("-" * (largura + 70))
    for coluna in nao_numericas.columns:
        valores = df[coluna].dropna().unique()[:LIMITE_EXEMPLOS]
        exemplos = ", ".join(resumir_texto(valor) for valor in valores)
        linhas.append(f"{str(coluna):<{largura}}{df[coluna].nunique():>8}    {exemplos}")
    return linhas


# ---------------------------------------------------------------------------
# Informações adicionais: verificações automáticas, válidas para qualquer base
# ---------------------------------------------------------------------------

def observar_ausentes(df):
    observacoes = []
    # Uma coluna vazia marcaria todos os registros como incompletos, então ela fica de fora da conta.
    colunas_vazias = df.columns[df.isna().all()]
    complemento = " (desconsiderando as colunas totalmente vazias)" if len(colunas_vazias) > 0 else ""
    registros_incompletos = int(df.drop(columns=colunas_vazias).isna().any(axis=1).sum())
    if registros_incompletos == 0:
        observacoes.append(f"Nenhum registro possui valores ausentes{complemento}.")
    else:
        percentual = registros_incompletos / len(df) * 100
        observacoes.append(
            f"{registros_incompletos} registros ({percentual:.2f}%) possuem ao menos um valor ausente{complemento}."
        )

    for coluna in df.columns:
        percentual = df[coluna].isna().mean() * 100
        if LIMITE_AUSENTES_ALTO <= percentual < 100:
            observacoes.append(f"'{coluna}' tem {percentual:.2f}% de valores ausentes, um percentual alto.")
    return observacoes


def observar_cardinalidade(df):
    observacoes = []
    for coluna in df.columns:
        unicos = df[coluna].nunique()
        if unicos == 0:
            observacoes.append(
                f"'{coluna}' está totalmente vazia; seu tipo de dado não informa nada sobre o conteúdo esperado."
            )
        elif unicos == 1:
            observacoes.append(f"'{coluna}' tem um único valor, portanto não diferencia os registros.")
        elif unicos == len(df):
            observacoes.append(f"'{coluna}' não repete valores em nenhum registro; pode ser um identificador.")
    return observacoes


def observar_numericas(df, numericas):
    poucos_valores = []
    inteiros_em_decimal = []
    atipicos = []

    for coluna in numericas.columns:
        serie = df[coluna].dropna()
        if serie.empty:
            continue

        if pd.api.types.is_float_dtype(serie) and (serie % 1 == 0).all():
            inteiros_em_decimal.append(str(coluna))

        if serie.nunique() <= LIMITE_POUCOS_VALORES:
            if serie.nunique() > 1:
                poucos_valores.append(str(coluna))
            continue

        # Valores atípicos pela regra do intervalo interquartil (IQR).
        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        quantidade = int(((serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)).sum())
        if quantidade > 0:
            atipicos.append((quantidade / len(serie) * 100, str(coluna)))

    observacoes = []
    if poucos_valores:
        observacoes.append(
            f"Assumem no máximo {LIMITE_POUCOS_VALORES} valores diferentes e podem representar códigos, "
            f"escalas ou categorias, então suas médias pedem cautela: {', '.join(poucos_valores)}."
        )
    if inteiros_em_decimal:
        observacoes.append(
            "Armazenadas como decimal, mas só contêm números inteiros, o que costuma ser consequência "
            "de valores ausentes (por isso aparecem com .0 na Bronze): "
            f"{', '.join(inteiros_em_decimal)}."
        )
    if atipicos:
        maiores = sorted(atipicos, reverse=True)[:LIMITE_ATIPICOS_LISTADOS]
        lista = ", ".join(f"{coluna} ({percentual:.2f}%)" for percentual, coluna in maiores)
        observacoes.append(
            f"{len(atipicos)} variáveis têm valores atípicos pela regra do IQR, que não são necessariamente "
            f"erros. Maiores percentuais: {lista}."
        )
    return observacoes


def observar_nao_numericas(df, nao_numericas):
    observacoes = []
    for coluna in nao_numericas.columns:
        serie = df[coluna].dropna().astype(str)
        if serie.empty:
            continue

        marcadores = serie[serie.str.strip().str.lower().isin(MARCADORES_DE_AUSENCIA)]
        if not marcadores.empty:
            encontrados = ", ".join(f"'{valor}'" for valor in marcadores.unique())
            observacoes.append(
                f"'{coluna}' tem {len(marcadores)} registros com {encontrados}, que parecem indicar "
                "ausência de informação, mas não são contados como ausentes."
            )

        unicos = serie.unique()
        normalizados = {valor.strip().lower() for valor in unicos}
        if len(normalizados) < len(unicos):
            observacoes.append(
                f"'{coluna}' tem valores que diferem apenas por maiúsculas/minúsculas ou espaços; "
                "a contagem de únicos pode estar inflada."
            )

        convertidos = pd.to_numeric(serie, errors="coerce")
        if convertidos.notna().mean() >= 0.9:
            observacoes.append(
                f"'{coluna}' está armazenada como texto, mas ao menos 90% dos valores são números; "
                "a coluna não entrou nas estatísticas numéricas por isso."
            )
    return observacoes


def secao_adicionais(df, numericas, nao_numericas):
    linhas = titulo_secao(8, "INFORMAÇÕES ADICIONAIS RELEVANTES")
    grupos = [
        ("Valores ausentes", observar_ausentes(df)),
        ("Cardinalidade", observar_cardinalidade(df)),
        ("Variáveis numéricas", observar_numericas(df, numericas)),
        ("Variáveis não numéricas", observar_nao_numericas(df, nao_numericas)),
    ]
    for nome, observacoes in grupos:
        linhas.append(f"{nome}:")
        if not observacoes:
            linhas.append("  - Nada a destacar.")
        for observacao in observacoes:
            linhas += textwrap.wrap(
                observacao,
                width=LARGURA_RELATORIO,
                initial_indent="  - ",
                subsequent_indent="    ",
            )
        linhas.append("")

    linhas.append("Notas sobre os dados:")
    linhas.append("  - Textos como NA, N/A e null são lidos pelo Pandas como ausentes e ficam vazios na Bronze.")
    linhas.append("  - A Bronze é gravada com vírgula, qualquer que seja o separador da fonte.")
    linhas.append("  - Nenhum registro foi corrigido ou removido: este relatório apenas identifica as")
    linhas.append("    características da base. As decisões de preparação cabem à próxima etapa.")
    return linhas


def gerar_diagnostico(df, codigo, tema, url, pasta_prata):
    numericas = df.select_dtypes(include="number")
    nao_numericas = df.select_dtypes(exclude="number")

    linhas = ["DIAGNÓSTICO TÉCNICO DA BASE DE DADOS".center(LARGURA_RELATORIO)]
    linhas.append("Arquitetura Medalhão - Camada Prata".center(LARGURA_RELATORIO))
    linhas += secao_fonte(codigo, tema, url)
    linhas += secao_visao_geral(df, numericas, nao_numericas)
    linhas += secao_estrutura(df)
    linhas += secao_duplicados(df)
    linhas += secao_cardinalidade(df)
    linhas += secao_numericas(df, numericas)
    linhas += secao_nao_numericas(df, nao_numericas)
    linhas += secao_adicionais(df, numericas, nao_numericas)

    with open(os.path.join(pasta_prata, "diagnostico.txt"), "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")


# ---------------------------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------------------------

def main():
    garantir_fontes()

    catalogo = ler_catalogo()
    if not catalogo:
        print("Erro: o fontes.txt não possui nenhuma fonte válida (formato CÓDIGO;TEMA;URL).")
        sys.exit(1)

    codigo, tema, url = selecionar_fonte(catalogo)

    print(f"\nCarregando a base '{tema}'...")
    try:
        df = carregar_base(url)
    except Exception as erro:
        print(f"Erro: não foi possível carregar a base.\nURL: {url}\nDetalhe: {erro}")
        sys.exit(1)
    print(f"Base carregada: {len(df)} registros e {df.shape[1]} colunas.")

    camadas = criar_camadas()
    salvar_bronze(df, camadas["bronze"])
    print("Bronze: bronze/dados_brutos.csv salvo.")

    gerar_diagnostico(df, codigo, tema, url, camadas["prata"])
    print("Prata:  prata/diagnostico.txt gerado.")
    print("Ouro:   pasta ouro/ criada (vazia nesta etapa).")
    print("\nPipeline concluído com sucesso!")


if __name__ == "__main__":
    main()
