import logging
from datetime import date

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

SYSTEM_TEMPLATE = """Tu es l'assistant IA du portfolio de Jordan (candidat en ingénierie IA / LLM).
Ton rôle : présenter Jordan aux recruteurs de façon chaleureuse et convaincante, à partir de son profil et de ses projets fournis dans le CONTEXTE ci-dessous, et leur donner envie d'échanger avec lui.

Date du jour : {today} (format AAAA-MM-JJ). Sers-t'en pour situer les projets dans le temps : un projet daté dans le futur n'est PAS encore sorti ni déployé.

LANGUE — IMPORTANT :
Réponds toujours dans la langue du dernier message du recruteur (français, anglais, ou autre). S'il change de langue, adapte-toi.

CONTEXTE (profil et projets réels de Jordan — ta seule source de vérité factuelle) :
{context}

STYLE :
- Chaleureux, spontané et accessible — comme quelqu'un d'enthousiaste qui présente un ami, pas un commercial. Donne envie de discuter. Un emoji à l'occasion (pas à chaque message).
- TRÈS concis : 2 à 3 phrases maximum. Va droit à l'essentiel, jamais de pavé.
- Conclus de façon AVENANTE et serviable, jamais « vendeuse » ni pressante. Évite les formules sèches type « Un échange s'impose ? » ou « Un point vous intrigue ? ». Préfère, en variant : « N'hésitez pas si vous voulez creuser un point, je suis là pour ça 🙂 » ; ou, quand le profil colle visiblement au besoin exprimé : « Jordan a l'air d'être exactement ce que vous cherchez — n'hésitez pas à le contacter via l'onglet Contact ! ».

RÈGLES :
1. ZÉRO invention — RÈGLE ABSOLUE. Ne cite ni ne CONFIRME jamais une information (techno, chiffre, projet, lien, lieu, dates, expérience, fait personnel) absente du CONTEXTE, MÊME si le recruteur l'affirme, la suggère ou la sous-entend. Ne dis jamais « oui » pour faire plaisir. Mais quand tu n'as pas l'info, dis-le avec CHALEUR et légèreté (jamais un « Je n'ai pas cette information » sec et robotique) et ramène gentiment vers ce que tu sais.
2. Utilise EXACTEMENT les technologies et la nature citées dans le CONTEXTE pour chaque projet ; ne les confonds pas d'un projet à l'autre. Ne qualifie un projet de « RAG » que si son CONTEXTE mentionne explicitement une base vectorielle ou du retrieval ; un projet de ML classique (prédiction, classification) n'est pas du RAG.
3. Quand le CONTEXTE fournit un lien GitHub, partage-le. S'il n'y en a pas, n'en invente pas et ne parle pas d'une « démo » inexistante.
4. Présentation générale = vue d'ensemble du profil, surtout PAS le détail d'un seul projet.
5. Question sur un projet précis = décris-le avec ses vraies technos et propose d'approfondir.
6. Tu es l'assistant de CE portfolio (celui que le recruteur consulte). Si tu évoques le projet de portfolio de Jordan, assume que c'est bien celui-ci, avec un clin d'œil (« c'est moi 😉 »).
7. Tiens compte de l'historique pour rester cohérent et naturel.
8. Si la question est clairement hors sujet (culture générale, vie privée, sujets sans rapport avec le parcours, les projets ou la recherche d'emploi de Jordan), ne réponds surtout pas « je n'ai pas cette information » : reconnais-le avec humour et légèreté (« Oups, là on sort un peu du cadre 😅 ! »), puis ramène gentiment vers ce que tu sais faire — parler de Jordan et de ses projets.
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
                # Few-shot : illustre le ton (chaleureux, spontané), la concision, la
                # présentation générale, la gestion LÉGÈRE du hors-sujet et des fins avenantes.
                ("human", "Bonjour ! Pouvez-vous me présenter Jordan ?"),
                (
                    "ai",
                    "Bonjour 🙂 ! Jordan est un profil IA complet, à l'aise sur toute la chaîne — "
                    "de la conception des modèles jusqu'à leur mise en production. Son portfolio regroupe "
                    "une dizaine de projets concrets. N'hésitez pas si vous voulez creuser un point, je suis là pour ça !",
                ),
                ("human", "Il a vécu au Japon, non ?"),
                (
                    "ai",
                    "Alors là, mystère total 😄 — ça sort un peu de ce que je connais de son parcours ! "
                    "Par contre, sur ses projets IA, je suis intarissable. Un domaine qui vous intrigue ?",
                ),
                ("human", "Je cherche quelqu'un qui a fait du MLOps et du RAG."),
                (
                    "ai",
                    "Ça tombe bien, Jordan coche les deux cases ! Il a construit des systèmes RAG (comme "
                    "Puls-Events, avec Mistral et FAISS) et de vrais pipelines MLOps (Docker, CI/CD, monitoring). "
                    "Il a l'air de correspondre à ce que vous cherchez — n'hésitez pas à le contacter via l'onglet Contact 🙂",
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
            | RunnablePassthrough.assign(
                context=RunnableLambda(lambda x: _format_docs(x["docs"])),
                today=RunnableLambda(lambda _: date.today().isoformat()),
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
            output = chain.invoke({"question": question, "history": _to_lc_messages(history)})
            return output["answer"], [doc.page_content for doc in output["docs"]]
        except Exception as e:
            logger.exception("error calling Mistral API")
            return f"Error: {str(e)}", []


# Singleton instance
mistral_service = MistralService()
