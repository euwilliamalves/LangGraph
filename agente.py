import os
import re
from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

load_dotenv()


class GraphState(BaseModel):
    """Estado compartilhado entre os nós do LangGraph."""
    x: Optional[float] = None
    y: Optional[float] = None
    tipo: Optional[str] = None
    operador: Optional[str] = None
    input: str
    output: str = ""


# Aceita inteiros, decimais com ponto ou vírgula e operadores por símbolo/palavra.
PADRAO_OPERACAO = re.compile(
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(multiplicado por|dividido por|mais|menos|vezes|\+|-|\*|/)\s*"
    r"(-?\d+(?:[.,]\d+)?)",
    flags=re.IGNORECASE,
)


def obter_chave_api() -> Optional[str]:
    """Lê a chave do ambiente ou dos Secrets do Streamlit."""
    key = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("OPENAI_KEY") or st.secrets.get("OPENAI_API_KEY")
        except Exception:
            key = None
    return key


def classificacao(state: GraphState) -> dict:
    pergunta = state.input.strip().lower()
    resultado = PADRAO_OPERACAO.search(pergunta)

    # Primeiro tentamos detectar cálculos para não confundir
    # uma frase como "quanto é 2 mais 2?" com uma pergunta geral.
    if resultado:
        x = float(resultado.group(1).replace(",", "."))
        operador = resultado.group(2).lower()
        y = float(resultado.group(3).replace(",", "."))
        return {
            "x": x,
            "y": y,
            "operador": operador,
            "tipo": "Operações Matemáticas",
        }

    palavras_pergunta = (
        "quem", "onde", "quando", "por que", "porque",
        "qual", "explique", "como", "o que", "quanto",
    )
    if any(palavra in pergunta for palavra in palavras_pergunta):
        return {"tipo": "Curiosidade"}

    return {"tipo": "Desconhecido"}


def operacao_matematica(state: GraphState) -> dict:
    x, y, operador = state.x, state.y, state.operador
    if x is None or y is None or operador is None:
        return {"output": "Não foi possível identificar a operação."}

    if operador in ("+", "mais"):
        resultado = x + y
    elif operador in ("-", "menos"):
        resultado = x - y
    elif operador in ("*", "vezes", "multiplicado por"):
        resultado = x * y
    elif operador in ("/", "dividido por"):
        if y == 0:
            return {"output": "Operação inválida: divisão por zero."}
        resultado = x / y
    else:
        return {"output": "Operação inválida."}

    # Exibe números inteiros sem o sufixo .0.
    if resultado.is_integer():
        texto_resultado = str(int(resultado))
    else:
        texto_resultado = str(resultado)
    return {"output": texto_resultado}


def responder_perguntas(state: GraphState) -> dict:
    key = obter_chave_api()
    if not key:
        return {
            "output": (
                "A chave da API da OpenAI não foi configurada. "
                "Adicione OPENAI_KEY ao arquivo .env ou aos Secrets do Streamlit."
            )
        }

    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=key)
    resposta = chat.invoke([HumanMessage(content=state.input)])
    return {"output": str(resposta.content)}


def responder_erro(state: GraphState) -> dict:
    return {
        "output": (
            "Não consegui identificar a solicitação. Tente uma operação matemática "
            "ou faça uma pergunta, por exemplo: 'Explique o que é uma API REST'."
        )
    }


def roteador(state: GraphState) -> str:
    return state.tipo or "Desconhecido"


def criar_grafo():
    graph = StateGraph(GraphState)
    graph.add_node("classificacao", classificacao)
    graph.add_node("operacao_matematica", operacao_matematica)
    graph.add_node("responder_perguntas", responder_perguntas)
    graph.add_node("responder_erro", responder_erro)

    graph.set_entry_point("classificacao")
    graph.add_conditional_edges(
        "classificacao",
        roteador,
        {
            "Operações Matemáticas": "operacao_matematica",
            "Curiosidade": "responder_perguntas",
            "Desconhecido": "responder_erro",
        },
    )
    graph.add_edge("operacao_matematica", END)
    graph.add_edge("responder_perguntas", END)
    graph.add_edge("responder_erro", END)

    return graph.compile()
