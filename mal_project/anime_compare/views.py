from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .utils.pkce import generate_pkce_pair_plain
from .utils.mal_api import mal_fetch_anime_list
from .utils.db import save_user_anime_list
from .utils.compare_lists import compare_users_lists
from urllib.parse import urlencode
from django.core.paginator import Paginator
import os
import requests
from datetime import timedelta
from django.utils import timezone
from .models import UserAnime

def home(request):
    return redirect("compare_users")

def mal_login(request):
    code_verifier, code_challenge = generate_pkce_pair_plain()
    request.session["code_verifier"] = code_verifier

    params = {
        "response_type": "code",
        "client_id": os.getenv("MAL_CLIENT_ID"),
        "redirect_uri": os.getenv("MAL_REDIRECT_URI"),
        "code_challenge": code_challenge,
        "code_challenge_method": "plain",
    }

    url = "https://myanimelist.net/v1/oauth2/authorize?" + urlencode(params)
    return redirect(url)

def mal_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Brak code", status=400)

    code_verifier = request.session.get("code_verifier")
    if not code_verifier:
        return HttpResponse("Brak code_verifier w session", status=400)

    token_url = "https://myanimelist.net/v1/oauth2/token"

    data = {
        "client_id": os.getenv("MAL_CLIENT_ID"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("MAL_REDIRECT_URI"),
        "code_verifier": code_verifier,
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_data = response.json()

    # Zapisujemy token w session
    request.session["mal_token"] = token_data["access_token"]

    # Sprawdzamy, czy użytkownik próbował wykonać porównanie
    pending_a = request.session.pop("pending_compare_a", None)
    pending_b = request.session.pop("pending_compare_b", None)

    if pending_a and pending_b:
        # automatyczne odpalenie porównania
        return redirect("compare_users_direct", user_a=pending_a, user_b=pending_b)

    return redirect("compare_form")

def mal_my_anime(request):
    access_token = request.session.get("mal_access_token")
    username = request.get("username")

    anime_list = mal_fetch_anime_list(access_token, username)

    return JsonResponse({"count": len(anime_list), "anime": anime_list})

def fetch_and_save(request, username):
    token = request.session.get("mal_token")
    if not token:
        return JsonResponse({"error": "Not authenticated with MAL"}, status=401)

    animelist_data = mal_fetch_anime_list(username, token)

    snapshot = save_user_anime_list(username, animelist_data)

    return JsonResponse({
        "message": "List saved",
        "username": username,
        "entries": snapshot.entry_count,
        "snapshot_id": snapshot.id,
        "fetched_at": snapshot.fetched_at
    })
    
def compare_form(request):
    return render(request, "anime_compare/compare_form.html")

def compare_users(request):
    pagination_params = {"page_common", "page_only_a", "page_only_b"}
    if request.method != "POST":
        if any(p in request.GET for p in pagination_params):
        # Przekieruj do direct z tymi samymi parametrami
            user_a = request.session.get("user_a")
            user_b = request.session.get("user_b")
            if not user_a or not user_b:
                return redirect("compare_form")
            # Zachowujemy parametry GET
            params = request.GET.urlencode()
            return redirect(f"/compare/run/{user_a}/{user_b}/?{params}")
        return redirect("compare_form")
    user_a = request.POST.get("user_a")
    user_b = request.POST.get("user_b")
    request.session["user_a"] = user_a
    request.session["user_b"] = user_b
    token = request.session.get("mal_token")

    if not token:
        # ZAPAMIĘTUJEMY użytkowników i przekierowujemy do MAL
        request.session["pending_compare_a"] = user_a
        request.session["pending_compare_b"] = user_b
        return redirect("mal_login")  # <-- automatyczne logowanie

    return _run_comparison(request, user_a, user_b)

def compare_users_direct(request, user_a, user_b):
    token = request.session.get("mal_token")

    if not token:
        # bardzo mało prawdopodobne, ale obsługujemy
        request.session["pending_compare_a"] = user_a
        request.session["pending_compare_b"] = user_b
        return redirect("mal_login")

    return _run_comparison(request, user_a, user_b)

def paginate(request,list_data, param):
    paginator = Paginator(list_data, 10)
    page = request.GET.get(param)
    return paginator.get_page(page)

def _run_comparison(request, user_a, user_b):

    token = request.session["mal_token"]
    snapA = UserAnime.objects.filter(username=user_a).first()
    snapB = UserAnime.objects.filter(username=user_b).first()

    now = timezone.now()
    max_age = timedelta(days=7)

    if not snapA or not snapA.fetched_at or now - snapA.fetched_at > max_age:
        data_a = mal_fetch_anime_list(user_a, token)
        save_user_anime_list(user_a, data_a)

    if not snapB or not snapB.fetched_at or now - snapB.fetched_at > max_age:
        data_b = mal_fetch_anime_list(user_b, token)
        save_user_anime_list(user_b, data_b)
    comparison = compare_users_lists(user_a, user_b)
    context = {
    "common_ctx": build_table_context(request, "common", comparison, user_a, user_b),
    "only_a_ctx": build_table_context(request, "only_a", comparison, user_a, user_b),
    "only_b_ctx": build_table_context(request, "only_b", comparison, user_a, user_b),
    }

    return render(request, "anime_compare/compare_result.html", context)

def compare_table_partial(request, table_type):
    user_a = request.session.get("user_a")
    user_b = request.session.get("user_b")
    comparison = compare_users_lists(user_a, user_b)
    if not user_a or not user_b:
        return render(request, "anime_compare/partials/error.html")

    ctx = build_table_context(request, table_type, comparison, user_a, user_b)
    return render(
        request,
        "anime_compare/partials/table_block.html",
        {"ctx": ctx}
    )

TABLE_COLUMNS = {
    "common": [
        {"label": "Poster", "key": "main_picture", "sortable": False},
        {"label": "Tytuł", "key": "title", "sortable": True},
        {"label": "Status ", "key": "status_a", "sortable": True},
        {"label": "Score ", "key": "score_a", "sortable": True},
        {"label": "Status ", "key": "status_b", "sortable": True},
        {"label": "Score ", "key": "score_b", "sortable": True},
        {"label": "Liczba odcinków", "key": "num_episodes", "sortable": False},
        {"label": "Gatunki", "key": "genres", "sortable": False},
    ],
    "only_a": [
        {"label": "Poster", "key": "main_picture", "sortable": False},
        {"label": "Tytuł", "key": "title", "sortable": True},
        {"label": "Status", "key": "status", "sortable": True},
        {"label": "Score", "key": "score", "sortable": True},
        {"label": "Liczba odcinków", "key": "num_episodes", "sortable": False},
        {"label": "Gatunki", "key": "genres", "sortable": False},
    ],
    "only_b": [
        {"label": "Poster", "key": "main_picture", "sortable": False},
        {"label": "Tytuł", "key": "title", "sortable": True},
        {"label": "Status", "key": "status", "sortable": True},
        {"label": "Score", "key": "score", "sortable": True},
        {"label": "Liczba odcinków", "key": "num_episodes", "sortable": False},
        {"label": "Gatunki", "key": "genres", "sortable": False},
    ],
}

STATUS_LABELS = {
    "watching": "Watching",
    "completed": "Completed",
    "on_hold": "On hold",
    "dropped": "Dropped",
    "plan_to_watch": "Plan to watch",
}

def genre_match(row, included, excluded):
    genres = set(row.get("genres", []))
    if included and not included.issubset(genres):
        return False
    if excluded and excluded & genres:
        return False
    return True

def status_match(row, included, excluded, table_type):
    if table_type == "common":
        statuses = {row.get("status_a"), row.get("status_b")}
        statuses.discard(None)
    else:
        status = row.get("status")
        statuses = {status} if status else set()

    if not statuses:
        return False

    if included and not (statuses & included):
        return False

    if statuses & excluded:
        return False

    return True

def score_match(row, score_min, score_max, table_type):
    if table_type == "common":
        scores = {row.get("score_a"), row.get("score_b")}
        scores.discard(None)
    else:
        score = row.get("score")
        scores = {score} if score is not None else set()

    if not scores:
        return False

    for s in scores:
        if score_min is not None and s < score_min:
            continue
        if score_max is not None and s > score_max:
            continue
        return True   # przynajmniej jeden pasuje

    return False

def episodes_match(row, ep_min, ep_max):
    ep = row.get("num_episodes")
    if ep is None:
        return False
    if ep_min is not None and ep < ep_min:
        return False
    if ep_max is not None and ep > ep_max:
        return False
    return True


def build_table_context(request, table_type, comparison, user_a, user_b):
    if table_type not in comparison:
        raise ValueError("Nieznany typ tabeli")
    data = comparison[table_type]
    columns = TABLE_COLUMNS[table_type]
    allowed_sort_keys = {
        col["key"] for col in columns if col["sortable"]
    }
    filters_open = request.GET.get("filters_open", "1") == "1"
    sort_key = request.GET.get("sort", "title")
    sort_dir = request.GET.get("dir", "asc")
    included = set(request.GET.getlist("genres_include[]"))
    excluded = set(request.GET.getlist("genres_exclude[]"))
    all_genres = sorted({
        genre
        for row in data
        for genre in row.get("genres", [])
    })
    data = [row for row in data if genre_match(row,included,excluded)]
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
    score_min = request.GET.get("score_min",1)
    score_max = request.GET.get("score_max",10)
    score_min = int(score_min) if score_min else None
    score_max = int(score_max) if score_max else None
    if score_min is not None and score_max is not None:
        if score_min > score_max:
            score_min, score_max = score_max, score_min
    data = [row for row in data if score_match(row, score_min, score_max, table_type)]
    ep_min = request.GET.get("ep_min",1)
    ep_max = request.GET.get("ep_max",2000)
    ep_min = int(ep_min) if ep_min else None
    ep_max = int(ep_max) if ep_max else None
    if ep_min is not None and ep_max is not None:
        if ep_min > ep_max:
            ep_min, ep_max = ep_max, ep_min
    data = [row for row in data if episodes_match(row, ep_min, ep_max)]
    if sort_key not in allowed_sort_keys:
        sort_key = "title"
    reverse = sort_dir == "desc"
    data = sorted(data, key=lambda row: (row.get(sort_key) is None, row.get(sort_key)), reverse=reverse)
    page_param = f"page_{table_type}"
    paginator = Paginator(data, 10)
    page = request.GET.get(page_param)
    summary = []

    # GENRES
    if included:
        summary.append(
            "Wybrane gatunki: " + ", ".join(sorted(included))
        )
    if excluded:
        summary.append(
            "Wykluczone gatunki: " + ", ".join(sorted(excluded))
        )

    # STATUS
    if included_statuses:
        summary.append(
            "Status: " + ", ".join([s] for s in included_statuses)
        )
    if excluded_statuses:
        summary.append(
            "Status -: " + ", ".join([s] for s in excluded_statuses)
        )

    # SCORE
    if score_min is not None or score_max is not None:
        summary.append(
            f"Ocena: {score_min or '?'} – {score_max or '?'}"
        )

    # EPISODES
    if ep_min is not None or ep_max is not None:
        summary.append(
            f"Odcinki: {ep_min or '?'} – {ep_max or '?'}"
        )
    return {
        "table_type": table_type,
        "page_obj": paginator.get_page(page),
        "user_a": user_a,
        "user_b": user_b,
        "current_sort": sort_key,
        "current_dir": sort_dir if sort_key else None,
        "columns": columns,
        "filters":"placeholder",
        "all_genres": all_genres,
        "included_genres": included,
        "excluded_genres": excluded,
        "all_statuses": all_statuses,
        "included_statuses": included_statuses,
        "excluded_statuses": excluded_statuses,
        "status_labels": STATUS_LABELS,
        "score_min":score_min,
        "score_max":score_max,
        "ep_min":ep_min,
        "ep_max":ep_max,
        "filters_open": filters_open,
        "filters_summary": summary,
        
    }
