import os
import textwrap
import warnings
from dotenv import load_dotenv
from datetime import date

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import google.generativeai as genai

warnings.filterwarnings("ignore")

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class AgenteBuscadorDeVagas:
    def __init__(self, model_id="gemini-2.0-flash"):
        self.model_id = model_id

    def _call_agent(self, agent: Agent, message_text: str) -> str:
        session_service = InMemorySessionService()
        session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
        runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)

        content = types.Content(role="user", parts=[types.Part(text=message_text)])
        final_response = ""

        for event in runner.run(user_id="user1", session_id="session1", new_message=content):
            if event.is_final_response():
                for part in event.content.parts:
                    if part.text:
                        final_response += part.text + "\n"

        return final_response

    def buscar_vagas(self, dados_do_usuario: str, historico: str) -> str:
        buscador = Agent(
            name="agente_buscador",
            model=self.model_id,
            description="Agente que busca vagas de emprego no Google",
            tools=[google_search],
            instruction="""
                Você é o Agente 3, um buscador de vagas de emprego.
                Pesquise no Google por até 5 vagas de emprego relevantes ao usuário.
                Retorne cada vaga EXATAMENTE na seguinte linha, sem nenhuma informação adicional antes ou depois:
                
                1) Título da Vaga 1: Link da Vaga 1
                2) Título da Vaga 2: Link da Vaga 2
                3) Título da Vaga 3: Link da Vaga 3
                4) Título da Vaga 4: Link da Vaga 4
                5) Título da Vaga 5: Link da Vaga 5
                
                Retorne APENAS as 5 linhas no formato exato acima, mesmo que não encontre 5 vagas. Se não encontrar uma vaga específica, coloque "Título Indisponível: #" no lugar.
            """
        )

        entrada = f"Dados do Usuário: {dados_do_usuario}\nHistórico da conversa: {historico}"
        return self._call_agent(buscador, entrada)

    def formatar_markdown(self, texto: str) -> str:
        texto = texto.replace('•', '  *')
        return textwrap.indent(texto, '> ', predicate=lambda _: True)

    @staticmethod
    def data_hoje() -> str:
        return date.today().strftime("%d/%m/%Y")
