from django.contrib import admin
from django.urls import path

from papers.views import health_check, search_basic, search_ranked

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/search/", search_ranked),
    path("api/search-basic/", search_basic),
]
