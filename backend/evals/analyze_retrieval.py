"""Analyse comparative des deux sources de retrieval : dense (sémantique) vs lexical (BM25).

Pour un jeu de questions représentatives, on regarde d'où viennent les contextes
qui survivent au reranking cross-encoder (dense seul, lexical seul, ou les deux),
et quelle source produit les contextes les mieux notés.

Usage (dans le conteneur backend) :
    python -m evals.analyze_retrieval
"""

from collections import Counter
from pathlib import Path

from app.services.rag_service import rag_service

# Questions catégorisées pour couvrir les cas typiques.
QUERIES = [
    ("mots-clés/techno", "Jordan connaît-il le langage Rust ?"),
    ("mots-clés/techno", "Quelles bases de données vectorielles a-t-il utilisées ?"),
    ("mots-clés/techno", "A-t-il utilisé XGBoost dans un projet ?"),
    ("mots-clés/techno", "Il connaît vLLM et le serving de modèles ?"),
    ("conceptuel/reformulé", "Sait-il mettre des modèles en production ?"),
    (
        "conceptuel/reformulé",
        "A-t-il de l'expérience avec l'intégration et le déploiement continus ?",
    ),
    ("conceptuel/reformulé", "Peux-tu me présenter Jordan en quelques mots ?"),
    ("anglais/cross-lingue", "Has Jordan fine-tuned his own language models?"),
    ("anglais/cross-lingue", "Tell me about his computer vision experience."),
    ("anglais/cross-lingue", "Which vector databases has he used?"),
    ("réel/problématique", "parle moi du projet portfolio"),
    ("réel/problématique", "je recherche un ingénieur qui a fait du mlops et du rag"),
]


def _source(content, dense_set, lexical_set):
    in_d, in_l = content in dense_set, content in lexical_set
    if in_d and in_l:
        return "les deux"
    return "dense" if in_d else "lexical"


def main() -> int:
    csv_path = Path(__file__).resolve().parents[1] / "app" / "data" / "experience.csv"
    rag_service.index_csv(
        str(csv_path)
    )  # peuple l'index lexical de ce process (dense déjà en base)
    ce = rag_service.cross_encoder

    win_by_source = Counter()  # sources des contextes finaux (après rerank)
    top1_by_source = Counter()  # source du meilleur contexte par question
    cat_win = {}  # {catégorie: Counter(source)}
    scores_by_source = {"dense": [], "lexical": [], "les deux": []}
    unique_saves = Counter()  # top-1 exclusif à une source (perdu si on la retirait)

    print("=" * 78)
    print("ANALYSE RETRIEVAL — dense (sémantique) vs lexical (BM25)")
    print("=" * 78)

    for cat, q in QUERIES:
        k, top_n = rag_service._adaptive_sizes(q)
        dense = rag_service._dense_candidates(q, k)
        lexical = rag_service.lexical_index.search(q, k)
        dense_set = {d.page_content for d in dense}
        lexical_set = {d.page_content for d in lexical}

        merged = {}
        for d in [*dense, *lexical]:
            merged.setdefault(d.page_content, d)
        candidates = list(merged.values())
        if not candidates:
            print(f"\n[{cat}] {q}\n  (aucun candidat)")
            continue

        scores = ce.score([(q, c.page_content) for c in candidates])
        ranked = sorted(zip(candidates, scores, strict=True), key=lambda x: x[1], reverse=True)
        winners = ranked[:top_n]

        cat_win.setdefault(cat, Counter())
        print(f"\n[{cat}] {q}")
        print(
            f"  dense={len(dense)}  lexical={len(lexical)}  fusion={len(candidates)}  gardés(top_n)={top_n}"
        )
        for rank, (doc, sc) in enumerate(winners, 1):
            src = _source(doc.page_content, dense_set, lexical_set)
            pid = doc.metadata.get("project_id", "?")
            win_by_source[src] += 1
            cat_win[cat][src] += 1
            scores_by_source[src].append(sc)
            flag = ""
            if rank == 1:
                top1_by_source[src] += 1
                if src != "les deux":
                    unique_saves[src] += 1
                    flag = "  <- top1 EXCLUSIF à cette source"
            print(f"    #{rank} [{src:8s}] score={sc:+.2f} projet={pid}{flag}")

    total = sum(win_by_source.values())
    print("\n" + "=" * 78)
    print("SYNTHÈSE")
    print("=" * 78)
    print(f"\nContextes finaux par source (sur {total} au total) :")
    for src, n in win_by_source.most_common():
        print(f"  {src:8s} : {n:2d}  ({100 * n / total:.0f}%)")

    print("\nSource du MEILLEUR contexte (top-1) par question :")
    for src, n in top1_by_source.most_common():
        print(f"  {src:8s} : {n}/{len(QUERIES)} questions")

    print("\nScore moyen de reranking par source (plus haut = plus pertinent) :")
    for src, arr in scores_by_source.items():
        if arr:
            print(f"  {src:8s} : {sum(arr) / len(arr):+.2f}  (n={len(arr)})")

    print("\nTop-1 EXCLUSIF à une source (info perdue si on la retirait) :")
    for src, n in unique_saves.most_common():
        print(f"  {src:8s} : {n} question(s)")

    print("\nPar catégorie (répartition des contextes gardés) :")
    for cat, c in cat_win.items():
        detail = ", ".join(f"{s}={n}" for s, n in c.most_common())
        print(f"  {cat:22s} : {detail}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
