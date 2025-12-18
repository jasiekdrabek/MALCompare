from ..utils.recommendations import build_recommendation_context
from django.shortcuts import render

def recommendation_block(request, table_type):
    user_a = request.session["user_a"]
    user_b = request.session["user_b"]
    anti = False
    if table_type == "anti_recommend":
        anti = True
    ctx = build_recommendation_context(request, table_type, user_a, user_b, anti)

    return render(
        request,
        "anime_compare/partials/recommendation_block.html",
        {"ctx": ctx}
    )