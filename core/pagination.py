from __future__ import annotations

from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate_queryset(request: HttpRequest, queryset, per_page: int):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()
    return page_obj, querystring
