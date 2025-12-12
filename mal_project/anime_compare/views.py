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
    return HttpResponse('anime_compare app — działa!')

def mal_login(request):
    # Generujemy PKCE
    code_verifier, code_challenge = generate_pkce_pair_plain()
    # Zapisujemy w session → będzie potrzebny przy token exchange
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
        "code_verifier": code_verifier,  # ważne
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
            user_a = request.session.get("last_user_a")
            user_b = request.session.get("last_user_b")
            if not user_a or not user_b:
                return redirect("compare_form")
            # Zachowujemy parametry GET
            params = request.GET.urlencode()
            return redirect(f"/compare/run/{user_a}/{user_b}/?{params}")
        return redirect("compare_form")
    user_a = request.POST.get("user_a")
    user_b = request.POST.get("user_b")
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

    context = compare_users_lists(user_a, user_b)
    
    def paginate(request,list_data, param):
        paginator = Paginator(list_data, 10)
        page = request.GET.get(param)
        return paginator.get_page(page)
    request.session["last_user_a"] = user_a
    request.session["last_user_b"] = user_b
    context["common_page"] = paginate(request,context["common"], "page_common")
    context["only_a_page"] = paginate(request,context["only_a"], "page_only_a")
    context["only_b_page"] = paginate(request,context["only_b"], "page_only_b")

    return render(request, "anime_compare/compare_result.html", context)
