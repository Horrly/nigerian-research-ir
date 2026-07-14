from django.contrib import admin

from .models import ResearchPaper


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "university", "department", "degree_type", "year")
    search_fields = ("title", "authors", "abstract", "keywords")
