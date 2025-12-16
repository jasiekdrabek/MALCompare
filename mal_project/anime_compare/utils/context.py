from .filters import *
from .table import paginate
from .constants import TABLE_COLUMNS, STATUS_LABELS
from .filters_state import get_filters_open, build_filters_summary

def build_table_context(request, table_type, comparison, user_a, user_b):
    if table_type not in comparison:
        raise ValueError("Nieznany typ tabeli")
    data = comparison[table_type]
    columns = TABLE_COLUMNS[table_type]
    
    included_genres = set(request.GET.getlist("genres_include[]"))
    excluded_genres = set(request.GET.getlist("genres_exclude[]"))
    all_genres = sorted({
        genre
        for row in data
        for genre in row.get("genres", [])
    })
    data = [row for row in data if genre_match(row,included_genres,excluded_genres)]
    
    included_statuses = set(request.GET.getlist("status_include[]"))
    excluded_statuses = set(request.GET.getlist("status_exclude[]"))
    if table_type == "common":
        all_statuses = sorted({
            s
            for row in data
            for s in (row.get("status_a"), row.get("status_b"))
            if s
        })
    else:
        all_statuses = sorted({
            row.get("status")
            for row in data
            if row.get("status")
        })
    data = [row for row in data if status_match(row, included_statuses, excluded_statuses, table_type)]
    
    score_min = _int(request.GET.get("score_min", 0))
    score_max = _int(request.GET.get("score_max", 10))
    if score_min is not None and score_max is not None:
        if score_min > score_max:
            score_min, score_max = score_max, score_min
    data = [row for row in data if score_match(row, score_min, score_max, table_type)]
    
    ep_min = _int(request.GET.get("ep_min", 0))
    ep_max = _int(request.GET.get("ep_max", 2000))
    if ep_min is not None and ep_max is not None:
        if ep_min > ep_max:
            ep_min, ep_max = ep_max, ep_min
    data = [row for row in data if episodes_match(row, ep_min, ep_max)]
    
    allowed_sort_keys = {
        col["key"] for col in columns if col["sortable"]
    }
    sort_key = request.GET.get("sort", "title")
    sort_dir = request.GET.get("dir", "asc")
    if sort_key not in allowed_sort_keys:
        sort_key = "title"
    reverse = sort_dir == "desc"
    data = sorted(data, key=lambda row: (row.get(sort_key) is None, row.get(sort_key)), reverse=reverse)
    
    page_obj = paginate(request, data, table_type)
    filters_open = get_filters_open(request)

    filters_summary = build_filters_summary(
        included_genres=included_genres,
        excluded_genres=excluded_genres,
        included_statuses=included_statuses,
        excluded_statuses=excluded_statuses,
        score_min=score_min,
        score_max=score_max,
        ep_min=ep_min,
        ep_max=ep_max,
        status_labels=STATUS_LABELS,
    )

    return {
        "table_type": table_type,
        "page_obj": page_obj,
        "user_a": user_a,
        "user_b": user_b,
        "current_sort": sort_key,
        "current_dir": sort_dir if sort_key else None,
        "columns": columns,
        "filters":"placeholder",
        "all_genres": all_genres,
        "included_genres": included_genres,
        "excluded_genres": excluded_genres,
        "all_statuses": all_statuses,
        "included_statuses": included_statuses,
        "excluded_statuses": excluded_statuses,
        "status_labels": STATUS_LABELS,
        "score_min":score_min,
        "score_max":score_max,
        "ep_min":ep_min,
        "ep_max":ep_max,
        "filters_open": filters_open,
        "filters_summary": filters_summary,   
    }
    
def _int(val):
    return int(val) if val not in ("", None) else None