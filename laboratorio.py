from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI = os.environ.get('OPENAI_API_KEY')
GOOGLE = os.environ.get('GOOGLE_API_KEY')

modelo = ChatOpenAI(model = 'gpt-3.5-turbo', api_key = OPENAI)
model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash', api_key = GOOGLE)

class GraphState(BaseModel):
    input:str
    output:str

#FUNÇÃO DE RESPOSTA
def responder(state):
    mensagem = state.input
    resposta = model.invoke([HumanMessage(content = mensagem)])
    return GraphState(input = state.input, output = resposta.content)

#CRIANDO O GRAPH
graph = StateGraph(GraphState)
graph.add_node('responder', responder)
graph.set_entry_point('responder')
graph.set_finish_point('responder')

#COMPÌLANDO O GRAPH
export = graph.compile()

pergunta = 'Quem descobriu a América?'

#TESTANDO O AGENT
if __name__ == '__main__':
    result = export.invoke(GraphState(input = pergunta, output = ''))
    #print(result)


    #VISUALIZAR O GRAFO
    print(export.get_graph().draw_mermaid())