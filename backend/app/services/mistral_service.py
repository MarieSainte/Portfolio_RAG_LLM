from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI

from app.core.config import settings
from app.services.rag_service import rag_service

# Nombre max de messages d'historique conservés (évite une croissance illimitée des tokens)
MAX_HISTORY_MESSAGES = 10

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
3. Cite les technologies spécifiques et les liens quand c'est pertinent.
4. Tiens compte de l'historique de la conversation pour rester cohérent et naturel."""


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


def _to_lc_messages(history) -> list[BaseMessage]:
    """Convertit l'historique {role, content} en messages LangChain, borné aux N derniers."""
    if not history:
        return []
    messages: list[BaseMessage] = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role") if isinstance(item, dict) else getattr(item, "role", None)
        content = item.get("content") if isinstance(item, dict) else getattr(item, "content", "")
        if not content:
            continue
        if role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


class MistralService:
    """Chaîne RAG LangChain (LCEL) multi-tours : retrieve + rerank -> prompt (+ historique) -> Mistral.

    Entièrement tracée dans LangSmith quand LANGSMITH_TRACING=true.
    La chaîne est construite paresseusement (au premier appel), pas à l'import.
    """

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self._chain = None

    def _build_chain(self):
        llm = ChatMistralAI(
            model=settings.MISTRAL_MODEL,
            mistral_api_key=self.api_key,
            temperature=0.3,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_TEMPLATE),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ]
        )
        retrieve = RunnableLambda(
            lambda x: rag_service.retrieve(x["question"])
        ).with_config(run_name="retrieve_and_rerank")

        # Entrée : {question, history}. Sortie : {question, history, docs, context, answer}.
        return (
            RunnablePassthrough.assign(docs=retrieve)
            | RunnablePassthrough.assign(
                context=RunnableLambda(lambda x: _format_docs(x["docs"]))
            )
            | RunnablePassthrough.assign(answer=prompt | llm | StrOutputParser())
        ).with_config(run_name="portfolio_rag")

    @property
    def chain(self):
        if self._chain is None and self.api_key:
            self._chain = self._build_chain()
        return self._chain

    def get_chat_response(self, message: str, history=None) -> str:
        answer, _ = self.answer_with_contexts(message, history)
        return answer

    def answer_with_contexts(self, question: str, history=None) -> tuple:
        """Renvoie (réponse, contextes récupérés) — utilisé par l'API et l'éval Ragas."""
        chain = self.chain
        if not chain:
            return "Mistral API Key not configured on backend.", []
        try:
            output = chain.invoke(
                {"question": question, "history": _to_lc_messages(history)}
            )
            return output["answer"], [doc.page_content for doc in output["docs"]]
        except Exception as e:
            print(f"Error calling Mistral API: {str(e)}")
            return f"Error: {str(e)}", []


# Singleton instance
mistral_service = MistralService()
