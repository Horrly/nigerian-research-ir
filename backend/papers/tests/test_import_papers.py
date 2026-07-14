from io import StringIO

import pytest
from django.core.management import call_command

from papers.models import ResearchPaper

CSV_HEADER = (
    "title,authors,university,department,degree_type,year,abstract,"
    "keywords,supervisor,source_url\n"
)


@pytest.mark.django_db
def test_import_skips_existing_duplicate_by_title_and_university(tmp_path):
    ResearchPaper.objects.create(
        title="Existing Paper",
        authors="Author A",
        university="Test University",
        department="Computer Science",
        degree_type="MSc",
        year=2020,
        abstract="Original abstract.",
        keywords="existing",
    )

    csv_path = tmp_path / "papers.csv"
    csv_path.write_text(
        CSV_HEADER
        + '"existing paper","Author B","test university","Computer Science",'
        '"MSc","2020","Duplicate row, different case.","dup","",""\n'
        '"New Paper","Author C","Test University","Computer Science",'
        '"PhD","2021","A brand new abstract.","new","",""\n',
        encoding="utf-8",
    )

    out = StringIO()
    call_command("import_papers", str(csv_path), stdout=out)
    output = out.getvalue()

    assert ResearchPaper.objects.count() == 2
    assert ResearchPaper.objects.filter(title="New Paper").exists()
    assert "1 created" in output
    assert "1 skipped as duplicate" in output
    assert "0 failed validation" in output


@pytest.mark.django_db
def test_import_reports_validation_failures_with_reasons(tmp_path):
    csv_path = tmp_path / "papers.csv"
    csv_path.write_text(
        CSV_HEADER
        + '"","Author","Uni","Dept","MSc","2020","Missing title.","k","",""\n'
        '"Bad Year Paper","Author","Uni","Dept","MSc","not-a-year",'
        '"Bad year.","k","",""\n'
        '"Bad Degree Paper","Author","Uni","Dept","XYZ","2020",'
        '"Bad degree type.","k","",""\n'
        '"Valid Paper","Author","Uni","Dept","MSc","2020",'
        '"A valid abstract.","k","",""\n',
        encoding="utf-8",
    )

    out = StringIO()
    call_command("import_papers", str(csv_path), stdout=out)
    output = out.getvalue()

    assert ResearchPaper.objects.count() == 1
    assert ResearchPaper.objects.filter(title="Valid Paper").exists()
    assert "1 created" in output
    assert "0 skipped as duplicate" in output
    assert "3 failed validation" in output
    assert "missing required field 'title'" in output
    assert "invalid year 'not-a-year'" in output
    assert "invalid degree_type 'XYZ'" in output
