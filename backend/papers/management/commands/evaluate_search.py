import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from papers.search import basic_search, basic_search_or, search as ranked_search

DEFAULT_QUERIES_PATH = "data/test_queries.json"
TOP_K = 10


def _resolve_path(raw_path):
    path = Path(raw_path)
    if not path.is_absolute():
        # Resolve relative paths against the project root (one level above
        # backend/), since manage.py lives in backend/ but data/ lives at
        # the project root.
        path = Path(settings.BASE_DIR).parent / path
    return path


def _precision_recall_f1(retrieved_ids, relevant_ids, k=TOP_K):
    """Precision@k, Recall, F1 for one query.

    Precision@k divides by k (not by however many results were actually
    retrieved), following the standard IR convention that a short result
    list is penalized as if the missing slots were non-relevant.
    """
    relevant_set = set(relevant_ids)
    top_k_ids = retrieved_ids[:k]
    true_positives = sum(1 for pid in top_k_ids if pid in relevant_set)

    precision = true_positives / k if k else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return precision, recall, f1


class Command(BaseCommand):
    help = (
        "Evaluate ranked (TF-IDF) vs. basic phrase-match vs. basic OR-terms "
        "search against data/test_queries.json ground truth using "
        "Precision@10, Recall, F1."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "queries_path",
            nargs="?",
            default=DEFAULT_QUERIES_PATH,
            help=f"Path to the test queries JSON file (default: {DEFAULT_QUERIES_PATH})",
        )

    def handle(self, *args, **options):
        queries_path = _resolve_path(options["queries_path"])
        if not queries_path.exists():
            self.stderr.write(self.style.ERROR(f"Test queries file not found: {queries_path}"))
            return

        with queries_path.open(encoding="utf-8") as f:
            test_queries = json.load(f)

        if not test_queries:
            self.stdout.write(self.style.WARNING("No test queries found."))
            return

        self._evaluate(
            "RANKED SEARCH (TF-IDF cosine similarity)",
            test_queries,
            lambda q: [paper.id for paper, _ in ranked_search(q, limit=TOP_K)],
        )
        self.stdout.write("")
        self._evaluate(
            "BASIC SEARCH - PHRASE MATCH (existing icontains behavior)",
            test_queries,
            lambda q: [paper.id for paper in basic_search(q, limit=TOP_K)],
        )
        self.stdout.write("")
        self._evaluate(
            "BASIC SEARCH - OR TERMS (matches if any query word appears)",
            test_queries,
            lambda q: [paper.id for paper in basic_search_or(q, limit=TOP_K)],
        )

    def _evaluate(self, title, test_queries, run_query):
        self.stdout.write(self.style.SUCCESS(title))
        header = f"{'Query':<40} {'P@10':>8} {'Recall':>8} {'F1':>8}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))

        precisions, recalls, f1s = [], [], []
        for entry in test_queries:
            query = entry.get("query", "")
            relevant_ids = entry.get("relevant_ids", [])
            retrieved_ids = run_query(query)
            precision, recall, f1 = _precision_recall_f1(retrieved_ids, relevant_ids)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

            label = query if len(query) <= 40 else query[:37] + "..."
            self.stdout.write(f"{label:<40} {precision:>8.3f} {recall:>8.3f} {f1:>8.3f}")

        n = len(test_queries)
        self.stdout.write("-" * len(header))
        self.stdout.write(
            f"{'AVERAGE':<40} "
            f"{sum(precisions) / n:>8.3f} "
            f"{sum(recalls) / n:>8.3f} "
            f"{sum(f1s) / n:>8.3f}"
        )
