from django.db import models


class ResearchPaper(models.Model):
    DEGREE_CHOICES = [
        ("BSc", "BSc"),
        ("MSc", "MSc"),
        ("PhD", "PhD"),
        ("N/A", "N/A"),
    ]

    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=3, choices=DEGREE_CHOICES)
    year = models.IntegerField()
    abstract = models.TextField()
    keywords = models.CharField(max_length=500)  # comma-separated
    supervisor = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
