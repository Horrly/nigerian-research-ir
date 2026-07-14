from rest_framework.decorators import api_view
from rest_framework.response import Response

from .search import basic_search, search as ranked_search

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


def _serialize(paper, score=None):
    data = {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "university": paper.university,
        "department": paper.department,
        "degree_type": paper.degree_type,
        "year": paper.year,
        "abstract": (paper.abstract or "")[:300],
        "keywords": paper.keywords,
        "source_url": paper.source_url,
    }
    if score is not None:
        data["relevance_score"] = round(score, 3)
    return data


def _parse_limit(request):
    try:
        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return max(1, min(limit, MAX_LIMIT))


@api_view(["GET"])
def search_ranked(request):
    query = (request.query_params.get("q") or "").strip()
    if not query:
        return Response({"results": [], "message": "Query parameter 'q' is required."})

    limit = _parse_limit(request)
    results = ranked_search(query, limit=limit)
    return Response([_serialize(paper, score) for paper, score in results])


@api_view(["GET"])
def search_basic(request):
    query = (request.query_params.get("q") or "").strip()
    if not query:
        return Response({"results": [], "message": "Query parameter 'q' is required."})

    papers = basic_search(query)
    return Response([_serialize(paper) for paper in papers])
