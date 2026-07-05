from django.shortcuts import  redirect
from django.http import HttpResponse, JsonResponse
from ..utils.pkce import generate_pkce_pair_plain
from ..utils.mal_api import mal_fetch_anime_list
from ..utils.db import save_user_anime_list
from urllib.parse import urlencode
import os
import requests

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
    request.session["mal_token"] = token_data["access_token"]

    pending_a = request.session.pop("pending_compare_a", None)
    pending_b = request.session.pop("pending_compare_b", None)

    if pending_a and pending_b:
        return redirect("compare_users_direct", user_a=pending_a, user_b=pending_b)

    return redirect("compare_form")

def mal_my_anime(request):
    access_token = request.session.get("mal_access_token")
    username = request.get("username")
    anime_list = mal_fetch_anime_list(username)
    return JsonResponse({"count": len(anime_list), "anime": anime_list})

def fetch_and_save(request, username):
    #token = request.session.get("mal_token")
    #if not token:
    #    return JsonResponse({"error": "Not authenticated with MAL"}, status=401)

    animelist_data = mal_fetch_anime_list(username)
    snapshot = save_user_anime_list(username, animelist_data)

    return JsonResponse({
        "message": "List saved",
        "username": username,
        "entries": snapshot.entry_count,
        "snapshot_id": snapshot.id,
        "fetched_at": snapshot.fetched_at
    })