import threading

from django.db.models import Count, Max, Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import ResearchPaper

_lock = threading.Lock()
_vectorizer = None
_doc_vectors = None
_paper_ids = None
_index_key = None


def _combined_text(paper):
    return f"{paper.title} {paper.abstract} {paper.keywords}"


def _current_index_key():
    agg = ResearchPaper.objects.aggregate(count=Count("id"), max_id=Max("id"))
    return (agg["count"], agg["max_id"])


def _build_index():
    global _vectorizer, _doc_vectors, _paper_ids, _index_key
    papers = list(ResearchPaper.objects.order_by("id"))
    _paper_ids = [p.id for p in papers]
    _vectorizer = TfidfVectorizer(stop_words="english")
    if papers:
        _doc_vectors = _vectorizer.fit_transform(_combined_text(p) for p in papers)
    else:
        _doc_vectors = None
    _index_key = _current_index_key()


def _ensure_index():
    with _lock:
        if _vectorizer is None or _index_key != _current_index_key():
            _build_index()


def search(query, limit=20):
    """Rank ResearchPaper records by TF-IDF cosine similarity to query.

    Returns a list of (ResearchPaper, score) tuples sorted by score
    descending, excluding zero-score matches.
    """
    query = (query or "").strip()
    if not query:
        return []

    _ensure_index()
    if not _paper_ids:
        return []

    query_vector = _vectorizer.transform([query])
    scores = cosine_similarity(query_vector, _doc_vectors).flatten()

    ranked = [(pid, score) for pid, score in zip(_paper_ids, scores) if score > 0]
    ranked.sort(key=lambda pair: pair[1], reverse=True)
    ranked = ranked[:limit]

    papers_by_id = ResearchPaper.objects.in_bulk([pid for pid, _ in ranked])
    return [
        (papers_by_id[pid], float(score))
        for pid, score in ranked
        if pid in papers_by_id
    ]


def basic_search(query, limit=None):
    """Unranked case-insensitive substring search across title/abstract/keywords."""
    query = (query or "").strip()
    if not query:
        return []

    papers = ResearchPaper.objects.filter(
        Q(title__icontains=query)
        | Q(abstract__icontains=query)
        | Q(keywords__icontains=query)
    ).order_by("id")

    if limit is not None:
        papers = papers[:limit]

    return list(papers)


def basic_search_or(query, limit=None):
    """Unranked case-insensitive search matching ANY query word.

    Unlike basic_search(), which requires the whole query to appear as one
    substring, this splits the query into words and matches records where
    at least one word appears in title/abstract/keywords. For evaluation
    comparison only — not wired into any API endpoint.
    """
    query = (query or "").strip()
    if not query:
        return []

    words = query.split()
    if not words:
        return []

    word_filter = Q()
    for word in words:
        word_filter |= (
            Q(title__icontains=word)
            | Q(abstract__icontains=word)
            | Q(keywords__icontains=word)
        )

    papers = ResearchPaper.objects.filter(word_filter).distinct().order_by("id")

    if limit is not None:
        papers = papers[:limit]

    return list(papers)
