# IA Assistente — Template 2 (dark dashboard)

Este template oferece uma interface escura com cabeçalho de boas-vindas, botões de exemplos, área de conversa e painel lateral com o fluxo do LangGraph.

A lógica do agente está em `agente.py`; a interface está em `app.py`.

## Executar

1. Crie e ative um ambiente virtual.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` e configure `OPENAI_KEY`.
4. Inicie:

```bash
streamlit run app.py
```

Não publique a chave da API no GitHub.
