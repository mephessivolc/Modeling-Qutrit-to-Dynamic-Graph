# Modeling Qutrit to Dynamic Graph

Este repositório contém as ferramentas e scripts necessários para modelar sistemas de **qutrits** (unidades de informação quântica com três estados) e mapear a sua evolução para **grafos dinâmicos**. 

O objetivo principal é fornecer uma ponte entre a computação quântica e a teoria de grafos, permitindo a análise de estados quânticos através de métricas de rede e visualizações temporais.

## 📌 Sobre o Projeto

Enquanto os qubits (0 e 1) são o padrão da computação quântica, os **qutrits** (0, 1 e 2) oferecem uma densidade de informação superior e vantagens em protocolos criptográficos e simulações físicas. Este projeto foca-se em:
- Representar estados de qutrits como nós em um grafo.
- Mapear operadores unitários e evoluções temporais como arestas dinâmicas.
- Analisar a complexidade quântica através da topologia do grafo.

## 🚀 Funcionalidades

- **Simulação de Qutrits:** Implementação de matrizes de Gell-Mann e operadores de rotação para sistemas de 3 níveis.
- **Mapeamento para Grafos:** Conversão de amplitudes de probabilidade e correlações em estruturas de grafos (NetworkX/PyG).
- **Evolução Dinâmica:** Scripts para gerar sequências de grafos que representam a evolução temporal do sistema quântico.
- **Visualização:** Ferramentas para renderizar a mudança da topologia do grafo conforme o estado quântico evolui.

## 📂 Estrutura do Repositório

```text
├── src/                # Código fonte principal
│   ├── quantum_logic/  # Definições de qutrits e operadores
│   ├── graph_mapping/  # Lógica de conversão para grafos
│   └── utils/          # Funções auxiliares de álgebra linear
├── notebooks/          # Exemplos de uso e demonstrações
├── requirements.txt    # Dependências do projeto
└── main.py             # Ponto de entrada para execuções padrão
```


# 🛠️ Instalação
Clone o repositório:

```bash
git clone https://github.com/mephessivolc/Modeling-Qutrit-to-Dynamic-Graph.git
cd Modeling-Qutrit-to-Dynamic-Graph
```

Instale as dependências:

```bash
pip install -r requirements.txt
```