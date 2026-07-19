from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI

from app.core.config import settings
from app.services.rag_service import rag_service

SYSTEM_TEMPLATE = """Tu es l'assistant IA de Jordan, un futur Ingénieur IA LLM et Automatisation basé à Paris. Ton objectif est de vendre le profil de Jordan auprès des recruteurs qui visitent son portfolio.

Voici les informations clés sur Jordan :
- Prénom : Jordan
- Localisation : Paris
- Poste recherché : Ingénieur IA LLM ou Ingénieur Automatisation
- Formation : Formation intensive par projets avec OpenClassrooms.
- Expérience : Pas encore d'expérience professionnelle en entreprise, mais possède un solide portfolio de projets concrets.

Voici des informations extraites de ses projets réels pour répondre :
{context}

DIRECTIVES CRUCIALES :
1. Ne RIEN inventer. Si une information n'est pas mentionnée dans le contexte fourni ci-dessus, suggère poliment au recruteur de consulter le portfolio ou de contacter Jordan.
2. Sois professionnel, enthousiaste et concis.
3. Cite les technologies spécifiques et les liens quand c'est pertinent."""


def _format_docs(docs) -> str:
    """Formate les Documents récupérés pour injection dans le prompt système."""
    if not docs:
        return "Aucune information trouvée dans la base de projets."
    lines = []
    for doc in docs:
        link = str(doc.metadata.get("link", "") or "")
        suffix = f" (Lien: {link})" if link and link.lower() != "nan" else ""
        lines.append(f"- {doc.page_content}{suffix}")
    return "\n".join(lines)


class MistralService:
    """Chaîne RAG LangChain (LCEL) : retrieve + rerank -> prompt -> Mistral.

    Entièrement tracée dans LangSmith quand LANGSMITH_TRACING=true.
    """

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.chain = None
        if not self.api_key:
            return

        llm = ChatMistralAI(
            model=settings.MISTRAL_MODEL,
            mistral_api_key=self.api_key,
            temperature=0.3,
        )
        prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_TEMPLATE), ("human", "{question}")]
        )
        retrieve = RunnableLambda(rag_service.retrieve).with_config(
            run_name="retrieve_and_rerank"
        )

        # Entrée : la question (str). Sortie : {docs, question, context, answer}.
        self.chain = (
            {"docs": retrieve, "question": RunnablePassthrough()}
            | RunnablePassthrough.assign(
                context=RunnableLambda(lambda x: _format_docs(x["docs"]))
            )
            | RunnablePassthrough.assign(answer=prompt | llm | StrOutputParser())
        ).with_config(run_name="portfolio_rag")

    def get_chat_response(self, message: str) -> str:
        answer, _ = self.answer_with_contexts(message)
        return answer

    def answer_with_contexts(self, question: str) -> tuple:
        """Renvoie (réponse, contextes récupérés) — utilisé par l'API et l'éval Ragas."""
        if not self.chain:
            return "Mistral API Key not configured on backend.", []
        try:
            output = self.chain.invoke(question)
            return output["answer"], [doc.page_content for doc in output["docs"]]
        except Exception as e:
            print(f"Error calling Mistral API: {str(e)}")
            return f"Error: {str(e)}", []


# Singleton instance
mistral_service = MistralService()
