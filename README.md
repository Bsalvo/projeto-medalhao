# Pipeline de Dados com Arquitetura Medalhão (Parte 1)

Este projeto implementa a primeira etapa de um pipeline de engenharia de dados fundamentado na **Arquitetura Medalhão** (*Bronze, Prata e Ouro*). O sistema gerencia um catálogo de fontes de dados públicas, realiza a ingestão e preservação dos dados brutos e gera um diagnóstico técnico aprofundado sobre a qualidade e a estrutura dos dados.

---

## 👥 Integrantes do Projeto

Trabalho desenvolvido em dupla pelos alunos:

- **Enzo Rossi** — Matrícula: `2025112797`
- **Bruno Salvo** — Matrícula: `2025112838`

---

## 🏛️ Arquitetura Medalhão no Projeto

A arquitetura organiza os dados em três níveis de maturidade e refinamento:

1. **Camada Bronze (Dados Brutos / Raw):**
   - Preserva os dados exatamente como foram extraídos da fonte, sem qualquer transformação ou limpeza.
   - Salvo em: `bronze/dados_brutos.csv`.

2. **Camada Prata (Validação e Diagnóstico):**
   - Nesta primeira etapa, realiza uma varredura técnica completa da base de dados, identificando inconsistências, padrões e anomalias para orientar as etapas posteriores de tratamento.
   - Gera o relatório em: `prata/diagnostico.txt`.

3. **Camada Ouro (Agregação e Negócio):**
   - Pasta estruturada para receber as tabelas analíticas, métricas agregadas e modelos prontos para relatórios/BI em etapas futuras.
   - Diretório: `ouro/`.

---

## 📊 Diagnóstico Técnico Realizado (Camada Prata)

O relatório `prata/diagnostico.txt` contempla as seguintes análises automatizadas:

- **Identificação da Fonte**: Código, tema e URL de origem dos dados.
- **Visão Geral**: Volume de linhas e colunas (segmentadas em numéricas e categóricas).
- **Estrutura das Variáveis**: Mapeamento dos tipos de dados e contagem/percentual de valores ausentes (*NaN/null*).
- **Registros Duplicados**: Verificação de linhas 100% idênticas.
- **Cardinalidade**: Contagem de valores únicos por variável.
- **Estatísticas Descritivas (Numéricas)**: Mínimo, máximo, média, mediana e desvio-padrão.
- **Amostras Categóricas**: Exibição dos primeiros valores únicos encontrados em variáveis de texto.
- **Informações Adicionais & Heurísticas de Qualidade**:
  - Detecção de valores atípicos (*outliers*) pela regra do IQR (Intervalo Interquartil).
  - Identificação de colunas com alta taxa de ausência (>= 20%).
  - Alerta de variáveis numéricas com pouca variedade (possíveis códigos/categorias).
  - Detecção de marcadores textuais que simulam dados nulos (ex.: `?`, `-`, `nd`, `s/i`).
  - Verificação de colunas numéricas salvas como texto.

---

## 📁 Estrutura de Arquivos

```text
projeto-medalhao/
│
├── bronze/
│   └── dados_brutos.csv       # Dados originais sem alteração
├── prata/
│   └── diagnostico.txt        # Relatório de diagnóstico técnico
├── ouro/                      # Camada reservada para análises futuras
│
├── fontes.txt                 # Catálogo com código, tema e URL das bases
├── main.py                    # Script principal do pipeline
├── requirements.txt           # Dependências do projeto (Pandas)
└── README.md                  # Documentação do projeto
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+** (testado no Python 3.14)
- **Pandas**: Para leitura de dados, manipulação e cálculo de métricas estatísticas

---

## 🚀 Como Configurar e Executar

### 1. Clonar ou abrir o diretório do projeto
Certifique-se de estar na pasta raiz do projeto:

### 2. Criar e ativar o ambiente virtual (opcional, recomendado)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências
```powershell
pip install -r requirements.txt
```

### 4. Executar o pipeline
```powershell
python main.py
```

### 5. Escolher a base de dados
Ao executar, o programa exibirá o catálogo disponível e solicitará sua escolha:
- `A` - Pinguins (*Palmer Penguins*)
- `B` - Desempenho escolar (*Student Performance*)
- `C` - Produtos (*Olist Products*)
- `D` - População brasileira (*IBGE*)

Digite a letra correspondente e pressione **Enter**. O pipeline fará o download, salvará a camada **Bronze** e emitirá o relatório na camada **Prata**.

