# Criando um Agente para Automatizar um Fluxo de Trabalho em Python

Este repositório fornece um servidor MCP (Model Context Protocol — Protocolo de Contexto de Modelo) que integra o Trello para permitir a criação de quadros de tarefas com informações contextuais. Ele amplia as capacidades do seu agente, permitindo gerenciar quadros do Trello automaticamente, criar tarefas de sprint com contexto e manter informações detalhadas do negócio diretamente no sistema de gerenciamento de projetos.

## Requisitos

Certifique-se de ter os seguintes programas instalados antes de começar:

- **Python e Poetry:** usados para gerenciar o ambiente Python e as dependências do servidor MCP.
- **Node.js e npx:** necessários para executar determinadas ferramentas ou utilitários MCP desenvolvidos em JavaScript, quando necessário.
- **Chave da API e token do Trello:** necessários para autenticar o servidor com o Trello. pode ajudar você a gerá-los.

## Instalação e configuração

1. **Clone este repositório** para o seu computador.
2. **Instale as dependências** executando `poetry install` dentro da pasta do projeto.
3. **Configure seu agente** adicionando o seguinte conteúdo ao arquivo de configuração MCP do seu agente. Substitua `/path/to/repository`, `<YOUR TRELLO API KEY>` e `<YOUR TRELLO API TOKEN>` pelos valores correspondentes.

```json
{
  "mcpServers": {
    "context_todo_board": {
      "command": "poetry",
      "args": [
        "-C",
        "/path/to/repository",
        "run",
        "python",
        "honu_context_powered_todo_mcp/server.py"
      ],
      "env": {
        "TRELLO_API_KEY": "<YOUR TRELLO API KEY>",
        "TRELLO_API_TOKEN": "<YOUR TRELLO API TOKEN>"
      }
    }
  }
}
```

## Como usar as Skills (habilidades)

Este projeto inclui **Skills**, que funcionam como fluxos de trabalho especializados e instruções para que o agente execute tarefas complexas e específicas de determinado domínio.

As Skills estão localizadas no diretório `.agent/skills/` ou podem ser distribuídas como arquivos `.skill`.

Para utilizá-las, basta pedir ao agente que execute a tarefa descrita pela Skill. Ele reconhecerá automaticamente sua intenção e seguirá as instruções correspondentes.
