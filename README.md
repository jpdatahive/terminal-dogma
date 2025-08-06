# Terminal Dogma

**Terminal Dogma: Um Sistema de Deliberação Temático de Evangelion**

Este projeto é uma aplicação de linha de comando (CLI) interativa inspirada no universo de *Neon Genesis Evangelion*. Ele funciona como um "sistema de deliberação" onde você pode submeter uma consulta (uma pergunta, um problema, uma ideia) e receber análises de diferentes "agentes" de IA, cada um com uma personalidade e perspectiva únicas.

## Funcionalidades

*   **Análise Multifacetada:** Receba feedback sobre suas ideias a partir de múltiplas perspectivas: lógica (Melchior), ética (Balthasar), pragmática (Casper), e mais.
*   **Experiência Imersiva:** A interface, os nomes dos agentes, e a mecânica do sistema são todos desenhados para criar uma experiência temática.
*   **Agentes Especializados:** Interaja com diferentes sistemas de análise, como o conselho MAGI, o comitê de risco SEELE, e o sistema de veto Longinus.
*   **Mecânica de Jogo:** O uso de certos sistemas, como o "Paradigm", é limitado por um cooldown, adicionando um elemento de estratégia.

## Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/seu-usuario/terminal-dogma.git
    cd terminal-dogma
    ```

2.  **Crie um Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua Chave de API:**
    *   Crie um arquivo chamado `.env` na raiz do projeto.
    *   Adicione sua chave de API do Google ao arquivo da seguinte forma:
        ```
        GOOGLE_API_KEY=sua_chave_de_api_aqui
        ```

## Como Usar

Execute o programa a partir da raiz do projeto:

```bash
python -m src.dogma_core.main
```

Uma vez dentro do sistema, use os seguintes comandos seguidos por sua consulta:

*   `magi <sua consulta>`: Recebe uma deliberação padrão do conselho MAGI.
*   `seele <sua consulta>`: Realiza uma análise de risco pessimista.
*   `paradigm <senha> <sua consulta>`: Compara o potencial de inovação com o impacto na estabilidade (uso restrito).
*   `veto <sua consulta>`: Verifica se a sua consulta viola regras fundamentais.
*   `help`: Mostra a lista de comandos.
*   `status`: Exibe o status do sistema.
*   `clear`: Limpa a tela.
*   `exit`: Encerra o programa.

---
*Aviso: Este é um projeto para fins de entretenimento e exploração de conceitos de IA. As análises são geradas por um modelo de linguagem e não devem ser consideradas como conselhos profissionais.*
