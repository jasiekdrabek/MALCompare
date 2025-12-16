from django.shortcuts import render, redirect
from ..utils.mal_api import mal_fetch_anime_list
from ..utils.db import save_user_anime_list
from ..utils.compare_lists import compare_users_lists
from ..utils.context import build_table_context
from datetime import timedelta
from django.utils import timezone
from ..models import UserAnime
from ..utils.recommendations import build_recommendation_context

def compare_users(request):
    pagination_params = {"page_common", "page_only_a", "page_only_b"}
    if request.method != "POST":
        if any(p in request.GET for p in pagination_params):
            user_a = request.session.get("user_a")
            user_b = request.session.get("user_b")
            if not user_a or not user_b:
                return redirect("compare_form")
            params = request.GET.urlencode()
            return redirect(f"/compare/run/{user_a}/{user_b}/?{params}")
        return redirect("compare_form")
    user_a = request.POST.get("user_a")
    user_b = request.POST.get("user_b")
    request.session["user_a"] = user_a
    request.session["user_b"] = user_b
    token = request.session.get("mal_token")

    if not token:
        request.session["pending_compare_a"] = user_a
        request.session["pending_compare_b"] = user_b
        return redirect("mal_login")

    return _run_comparison(request, user_a, user_b)

def compare_users_direct(request, user_a, user_b):
    token = request.session.get("mal_token")

    if not token:
        request.session["pending_compare_a"] = user_a
        request.session["pending_compare_b"] = user_b
        return redirect("mal_login")

    return _run_comparison(request, user_a, user_b)

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
    "recommendation_ctx": build_recommendation_context(request,"recommend", user_a, user_b),
    }

    return render(request, "anime_compare/compare_result.html", context)