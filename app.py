import streamlit as st
from agente import criar_grafo

st.set_page_config(
    page_title="IA Assistente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #08111f 0%, #0b1526 55%, #101b30 100%);
        color: #edf3ff;
    }
    [data-testid="stSidebar"] {
        background: #0a1322;
        border-right: 1px solid #20314b;
    }
    [data-testid="stSidebar"] * { color: #e7efff; }
    .hero {
        background: linear-gradient(115deg, #142d5b, #193b78 70%, #162c58);
        border: 1px solid #294a80;
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 20px;
    }
    .hero h1 { color: #f3f7ff; margin: 0 0 8px 0; font-size: 2.15rem; }
    .hero p { color: #c5d7ff; font-size: 1.05rem; margin-bottom: 0; }
    .panel {
        background: rgba(17, 31, 52, 0.9);
        border: 1px solid #263b5a;
        border-radius: 17px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .panel h3 { margin-top: 0; color: #f0f5ff; font-size: 1.05rem; }
    .muted { color: #a8bad9; font-size: .92rem; }
    div[data-testid="stChatMessage"] {
        background: rgba(17, 31, 52, .72);
        border: 1px solid #223652;
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .step {
        border-left: 2px solid #3c75db;
        padding: 3px 0 12px 13px;
        margin-left: 8px;
        color: #c7d6f1;
    }
    .step b { color: #ffffff; }
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #2c4770;
        background: #12233c;
        color: #edf3ff;
        min-height: 42px;
    }
    .stButton > button:hover {
        border-color: #4b8cff;
        color: #ffffff;
        background: #19345a;
    }
    [data-testid="stChatInput"] textarea {
        background: #13243d;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "prompt_draft" not in st.session_state:
    st.session_state.prompt_draft = ""
if "graph" not in st.session_state:
    st.session_state.graph = criar_grafo()

with st.sidebar:
    st.markdown("## 🤖 IA Assistente")
    st.caption("Calculadora e respostas inteligentes")
    st.divider()
    st.markdown("### Navegação")
    st.markdown("💬 **Chat**")
    st.markdown("🧩 Exemplos")
    st.markdown("ℹ️ Sobre o projeto")
    st.divider()
    st.markdown("### O que posso fazer?")
    st.markdown("- Calcular operações matemáticas")
    st.markdown("- Responder perguntas gerais")
    st.markdown("- Classificar solicitações com LangGraph")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.prompt_draft = ""
        st.rerun()
    st.markdown("---")
    st.caption("Desenvolvido com Streamlit, LangChain e LangGraph.")

st.markdown("""
<div class="hero">
  <h1>Olá! 👋</h1>
  <p>Sou seu assistente inteligente. Posso fazer cálculos, responder perguntas gerais
  e direcionar cada solicitação para o fluxo correto.</p>
  <p style="margin-top:10px;font-size:.92rem;">Digite uma mensagem ou escolha um exemplo para começar.</p>
</div>
""", unsafe_allow_html=True)

main_col, side_col = st.columns([2.25, 1], gap="large")

with main_col:
    st.markdown("### 💡 Experimente uma pergunta")
    ex1, ex2, ex3 = st.columns(3)
    if ex1.button("🧮 Cálculo matemático", use_container_width=True):
        st.session_state.prompt_draft = "Quanto é 125,5 multiplicado por 4?"
    if ex2.button("💬 Pergunta geral", use_container_width=True):
        st.session_state.prompt_draft = "Explique como funciona uma API REST."
    if ex3.button("➗ Divisão", use_container_width=True):
        st.session_state.prompt_draft = "144 dividido por 12"

    st.markdown('<div class="panel"><h3>💬 Conversa</h3><p class="muted">As mensagens e respostas aparecem aqui.</p></div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if msg.get("tipo"):
                st.caption(f"Tipo identificado: {msg['tipo']}")

    # A caixa de chat nativa oferece o melhor comportamento para enviar mensagens.
    prompt = st.chat_input("Digite sua pergunta aqui...")
    if prompt is None and st.session_state.prompt_draft:
        prompt = st.session_state.prompt_draft
        st.session_state.prompt_draft = ""

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analisando sua solicitação..."):
                try:
                    resultado = st.session_state.graph.invoke({"input": prompt})
                    resposta = resultado.get("output", "Não foi gerada uma resposta.")
                    tipo = resultado.get("tipo", "Desconhecido")
                except Exception as erro:
                    print(f"Erro ao executar o grafo: {erro}")
                    resposta = "Ocorreu um erro ao processar a solicitação. Confira a chave da API e os logs."
                    tipo = "Erro"
            st.markdown(resposta)
            st.caption(f"Rota: {tipo}")
        st.session_state.messages.append(
            {"role": "assistant", "content": resposta, "tipo": tipo}
        )

with side_col:
    st.markdown("""
    <div class="panel">
      <h3>⚙️ Como funciona?</h3>
      <div class="step"><b>1. Entrada</b><br>Você envia uma pergunta.</div>
      <div class="step"><b>2. Classificação</b><br>O LangGraph identifica a intenção.</div>
      <div class="step"><b>3. Roteamento</b><br>A solicitação segue para o nó adequado.</div>
      <div class="step"><b>4. Resposta</b><br>O resultado aparece no chat.</div>
    </div>
    <div class="panel">
      <h3>🧰 Tecnologias</h3>
      <p>🔹 <b>Streamlit</b><br><span class="muted">Interface web</span></p>
      <p>🔹 <b>LangChain</b><br><span class="muted">Integração com o modelo</span></p>
      <p>🔹 <b>LangGraph</b><br><span class="muted">Orquestração do fluxo</span></p>
      <p>🔹 <b>OpenAI</b><br><span class="muted">Modelo GPT-4o-mini</span></p>
    </div>
    <div class="panel">
      <h3>✨ Dica</h3>
      <p class="muted">Você pode usar números decimais com vírgula ou ponto e operadores como “mais”, “menos”, “vezes” e “dividido por”.</p>
    </div>
    """, unsafe_allow_html=True)
