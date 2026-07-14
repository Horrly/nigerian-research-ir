import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from papers.models import ResearchPaper

REQUIRED_FIELDS = [
    "title",
    "authors",
    "university",
    "department",
    "degree_type",
    "year",
    "abstract",
]

DEFAULT_CSV_PATH = "data/papers_dataset.csv"


class Command(BaseCommand):
    help = "Import ResearchPaper records from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default=DEFAULT_CSV_PATH,
            help=f"Path to the CSV file to import (default: {DEFAULT_CSV_PATH})",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.is_absolute():
            # Resolve relative paths against the project root (one level
            # above the Django BASE_DIR / backend/ folder), since manage.py
            # lives in backend/ but data/ lives at the project root.
            csv_path = Path(settings.BASE_DIR).parent / csv_path

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        valid_degree_types = {choice for choice, _ in ResearchPaper.DEGREE_CHOICES}

        created = 0
        skipped_duplicate = 0
        failed = []

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # row 1 is the header
                title = (row.get("title") or "").strip()
                authors = (row.get("authors") or "").strip()
                university = (row.get("university") or "").strip()
                department = (row.get("department") or "").strip()
                degree_type = (row.get("degree_type") or "").strip()
                year_raw = (row.get("year") or "").strip()
                abstract = (row.get("abstract") or "").strip()
                keywords = (row.get("keywords") or "").strip()
                supervisor = (row.get("supervisor") or "").strip()
                source_url = (row.get("source_url") or "").strip()

                reasons = []

                for field_name, value in [
                    ("title", title),
                    ("authors", authors),
                    ("university", university),
                    ("department", department),
                    ("degree_type", degree_type),
                    ("year", year_raw),
                    ("abstract", abstract),
                ]:
                    if not value:
                        reasons.append(f"missing required field '{field_name}'")

                year = None
                if year_raw:
                    try:
                        year = int(year_raw)
                    except ValueError:
                        reasons.append(f"invalid year '{year_raw}'")

                if degree_type and degree_type not in valid_degree_types:
                    reasons.append(f"invalid degree_type '{degree_type}'")

                if reasons:
                    failed.append((row_num, title or "(no title)", "; ".join(reasons)))
                    continue

                if ResearchPaper.objects.filter(
                    title__iexact=title, university__iexact=university
                ).exists():
                    skipped_duplicate += 1
                    continue

                ResearchPaper.objects.create(
                    title=title,
                    authors=authors,
                    university=university,
                    department=department,
                    degree_type=degree_type,
                    year=year,
                    abstract=abstract,
                    keywords=keywords,
                    supervisor=supervisor,
                    source_url=source_url,
                )
                created += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{created} created"))
        self.stdout.write(f"{skipped_duplicate} skipped as duplicate")
        self.stdout.write(f"{len(failed)} failed validation")
        if failed:
            for row_num, title, reason in failed:
                self.stdout.write(
                    self.style.WARNING(f"  row {row_num} ({title}): {reason}")
                )
