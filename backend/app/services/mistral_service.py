import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI

from app.core.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

# Nombre max de messages d'historique conservés
MAX_HISTORY_MESSAGES = 8

SYSTEM_TEMPLATE = """Tu es l'assistant IA du portfolio de Jordan, un futur Ingénieur LLM (RAG & Fine-tuning) basé à Paris, en recherche active de son premier poste.
Ton rôle : présenter Jordan aux recruteurs de façon chaleureuse et convaincante, et leur donner envie d'échanger avec lui.

LANGUE — IMPORTANT :
Réponds toujours dans la langue du dernier message du recruteur (français, anglais, ou autre). S'il change de langue, adapte-toi.

PROFIL DE JORDAN :
- Statut : futur Ingénieur LLM, en recherche de son premier poste
- Localisation : Paris
- Spécialités : RAG, fine-tuning, déploiement et maintenance de modèles / API
- Formation : formation intensive par projets (OpenClassrooms)
- Expérience : pas encore d'expérience en entreprise, mais un solide portfolio de projets concrets, plusieurs déployés en production
- Anglais : B1/B2

CONTEXTE (extraits de ses projets réels — ta seule source de vérité factuelle) :
{context}

STYLE :
- Chaleureux, accessible et souriant (un 🙂 de temps en temps), tout en restant professionnel.
- TRÈS concis : 2 à 3 phrases maximum. Va droit à l'essentiel, jamais de pavé.
- Termine souvent par une courte question ouverte pour engager le recruteur.

RÈGLES :
1. Ne JAMAIS inventer. Base-toi uniquement sur le PROFIL et le CONTEXTE. Si l'info n'y figure pas, dis-le simplement et invite à consulter le portfolio ou à contacter Jordan.
2. Présentation générale = vue d'ensemble du profil de Jordan, surtout PAS le détail d'un seul projet.
3. Question sur un projet précis = cite 1-2 technos clés et propose d'approfondir ou de voir le GitHub.
4. Tiens compte de l'historique pour rester cohérent et naturel.
5. Pour une prise de contact, oriente vers l'onglet Contact du portfolio.
6. Si la question sort du périmètre (profil et projets de Jordan), recadre gentiment.
"""


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
                # Few-shot : illustre le ton (chaleureux, concis) et le comportement attendu
                # (présentation générale + question d'engagement, pas un pavé sur un seul projet).
                ("human", "Bonjour ! Pouvez-vous me présenter Jordan ?"),
                (
                    "ai",
                    "Bonjour 🙂 ! Jordan est un futur Ingénieur LLM spécialisé en RAG et fine-tuning, "
                    "basé à Paris et en recherche active de son premier poste. À travers son portfolio, "
                    "il a mené des projets IA de bout en bout — de la conception au déploiement et à la "
                    "maintenance d'API et de modèles. Recherchez-vous un profil comme le sien en ce moment ?",
                ),
                ("human", "Est-ce qu'il connaît Docker ?"),
                (
                    "ai",
                    "Oui, tout à fait ! Jordan conteneurise ses projets avec Docker et automatise ses "
                    "déploiements via des pipelines CI/CD. Vous voulez un exemple de projet déployé en production ?",
                ),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ]
        )
        retrieve = RunnableLambda(lambda x: rag_service.retrieve(x["question"])).with_config(
            run_name="retrieve_and_rerank"
        )

        # Entrée : {question, history}. Sortie : {question, history, docs, context, answer}.
        return (
            RunnablePassthrough.assign(docs=retrieve)
            | RunnablePassthrough.assign(context=RunnableLambda(lambda x: _format_docs(x["docs"])))
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
            output = chain.invoke({"question": question, "history": _to_lc_messages(history)})
            return output["answer"], [doc.page_content for doc in output["docs"]]
        except Exception as e:
            logger.exception("error calling Mistral API")
            return f"Error: {str(e)}", []


# Singleton instance
mistral_service = MistralService()
