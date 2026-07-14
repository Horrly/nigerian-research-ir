import pytest
from rest_framework.test import APIClient

from papers.models import ResearchPaper
from papers.search import search


@pytest.fixture
def sample_papers(db):
    return [
        ResearchPaper.objects.create(
            title="Gamification Model for Personalized E-Learning",
            authors="Jane Doe",
            university="Test University",
            department="Computer Science",
            degree_type="MSc",
            year=2023,
            abstract=(
                "This thesis develops a gamification model to personalize "
                "e-learning experiences for students."
            ),
            keywords="gamification,e-learning,personalization",
        ),
        ResearchPaper.objects.create(
            title="Intrusion Detection Using Machine Learning",
            authors="John Smith",
            university="Test University",
            department="Computer Science",
            degree_type="PhD",
            year=2022,
            abstract=(
                "This study applies machine learning classifiers to detect "
                "network intrusions and reduce false positives."
            ),
            keywords="intrusion detection,machine learning,network security",
        ),
        ResearchPaper.objects.create(
            title="A Study of Nigerian Agricultural Supply Chains",
            authors="Amaka Obi",
            university="Test University",
            department="Agricultural Economics",
            degree_type="BSc",
            year=2021,
            abstract=(
                "This paper examines supply chain inefficiencies affecting "
                "Nigerian farmers and proposes logistics improvements."
            ),
            keywords="agriculture,supply chain,logistics",
        ),
    ]


@pytest.mark.django_db
def test_exact_title_query_returns_that_record_first(sample_papers):
    results = search("Gamification Model for Personalized E-Learning", limit=20)

    assert results
    top_paper, _ = results[0]
    assert top_paper.title == "Gamification Model for Personalized E-Learning"


@pytest.mark.django_db
def test_query_with_no_matches_returns_empty_list(sample_papers):
    results = search("xylophone zeppelin quokka", limit=20)

    assert results == []


@pytest.mark.django_db
def test_relevance_scores_are_descending(sample_papers):
    results = search("machine learning intrusion detection network", limit=20)

    assert len(results) >= 1
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.django_db
def test_basic_search_endpoint_matches_keyword_substring(sample_papers):
    client = APIClient()
    response = client.get("/api/search-basic/", {"q": "supply chain"})

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert "A Study of Nigerian Agricultural Supply Chains" in titles
