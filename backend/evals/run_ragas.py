"""Évaluation Ragas du pipeline RAG — gate qualité pour la CI.

Usage (depuis backend/) :
    python -m evals.run_ragas

Prérequis :
- ChromaDB accessible (CHROMA_HOST / CHROMA_PORT)
- MISTRAL_API_KEY défini (génération + juge LLM)

Le script indexe le corpus, fait répondre la chaîne RAG sur le dataset
d'évaluation, puis note les réponses avec Ragas (LLM-as-a-judge).
Code de sortie 1 si un score moyen passe sous son seuil -> CI bloquée.
"""

import json
import math
import os
import sys
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset.json"
RESULTS_PATH = Path(__file__).parent / "ragas_results.csv"
JUDGE_MODEL = os.getenv("RAGAS_JUDGE_MODEL", "mistral-small-latest")


def main() -> int:
    if not os.getenv("MISTRAL_API_KEY"):
        print("ERREUR : MISTRAL_API_KEY manquant.")
        return 2

    from langchain_mistralai import ChatMistralAI
    from ragas import EvaluationDataset, evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
        ResponseRelevancy,
    )
    from ragas.run_config import RunConfig

    from app.services.mistral_service import mistral_service
    from app.services.rag_service import rag_service

    # Seuils PLANCHER (temporaires) : volontairement bas pour ne détecter qu'un
    # pipeline cassé, sans bloquer sur la variance du juge LLM.
    # Baseline observée : faithfulness ~0.56, relevancy ~0.70, precision ~0.82, recall ~0.51.
    # TODO : relever ces seuils une fois la qualité du RAG affinée.
    thresholds = [
        (Faithfulness(), 0.30),
        (ResponseRelevancy(), 0.40),
        (LLMContextPrecisionWithReference(), 0.40),
        (LLMContextRecall(), 0.30),
    ]

    # 1. Indexation du corpus dans ChromaDB
    csv_path = Path(__file__).resolve().parents[1] / "app" / "data" / "experience.csv"
    rag_service.index_csv(str(csv_path))
    if rag_service.retriever is None:
        print("ERREUR : ChromaDB inaccessible — impossible d'évaluer le pipeline.")
        return 2

    # 2. Génération des réponses de la chaîne RAG sur le dataset d'éval
    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    rows = []
    for i, case in enumerate(cases, 1):
        question = case["question"]
        print(f"[{i}/{len(cases)}] {question}")
        answer, contexts = mistral_service.answer_with_contexts(question)
        if answer.startswith("Error:") or not contexts:
            print(f"  -> réponse ou contextes invalides : {answer[:120]}")
        rows.append(
            {
                "user_input": question,
                "response": answer,
                "retrieved_contexts": contexts,
                "reference": case["reference"],
            }
        )

    # 3. Évaluation LLM-as-a-judge (max_workers=1 : respect du rate limit Mistral)
    judge = LangchainLLMWrapper(ChatMistralAI(model=JUDGE_MODEL, temperature=0))
    embeddings = LangchainEmbeddingsWrapper(rag_service.embeddings)
    result = evaluate(
        dataset=EvaluationDataset.from_list(rows),
        metrics=[metric for metric, _ in thresholds],
        llm=judge,
        embeddings=embeddings,
        run_config=RunConfig(max_workers=1, timeout=180),
    )

    # 4. Rapport + gate
    df = result.to_pandas()
    df.to_csv(RESULTS_PATH, index=False)
    print(f"\nDétail par question sauvegardé dans {RESULTS_PATH}")

    lines = ["| Métrique | Score moyen | Seuil | Statut |", "|---|---|---|---|"]
    failed = []
    for metric, minimum in thresholds:
        name = metric.name
        mean = df[name].mean() if name in df.columns else float("nan")
        ok = not math.isnan(mean) and mean >= minimum
        if not ok:
            failed.append(name)
        shown = "n/a" if math.isnan(mean) else f"{mean:.3f}"
        lines.append(f"| {name} | {shown} | {minimum:.2f} | {'✅' if ok else '❌'} |")

    report = "\n".join(
        [
            "## 📊 Évaluation Ragas",
            "",
            *lines,
            "",
            f"Juge : `{JUDGE_MODEL}` — {len(rows)} questions.",
        ]
    )
    print("\n" + report)

    # Résumé visible dans l'onglet Actions de GitHub
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report + "\n")

    if failed:
        print(f"\n❌ Gate qualité NON franchie : {', '.join(failed)}")
        return 1
    print("\n✅ Gate qualité franchie.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
