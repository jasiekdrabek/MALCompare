from .compare_lists import compare_users_lists
from .table import paginate
from .constants import TABLE_COLUMNS

def build_genre_preferences(user_rows):
    genre_scores = {}

    for row in user_rows:
        score = row.get("score")
        if not score:
            continue
        for g in row.get("genres", []):
            genre_scores.setdefault(g, []).append(score)

    # średnia per gatunek
    genre_avg = {
        g: sum(scores) / len(scores)
        for g, scores in genre_scores.items()
        if len(scores) >= 3
    }

    if not genre_avg:
        return set(), set()

    values = sorted(genre_avg.values())

    low_cut = values[int(len(values) * 0.1)]
    high_cut = values[int(len(values) * 0.9)]

    liked = {g for g, v in genre_avg.items() if v >= high_cut}
    disliked = {g for g, v in genre_avg.items() if v <= low_cut}

    return liked, disliked


def recommend_anime(
    only_a_rows,
    liked_genres,
    disliked_genres,
    limit=20
):
    recommendations = []

    for row in only_a_rows:
        genres = set(row.get("genres", []))
        score_a = row.get("score") or 0
        if score_a <= 6:
            recommendations.append({
            **row,
            "recommendation_score": 0,
        })
            continue
        score_component = (score_a / 10) * 3

        genre_match = len([g for g in liked_genres if g in genres])
        genre_unmatch = len([g for g in disliked_genres if g in genres])
        genre_component = (
            (genre_match - genre_unmatch) * 0.7
            if genres else 0
        )

        final_score = score_component + genre_component

        recommendations.append({
            **row,
            "recommendation_score": round(final_score, 3),
        })

    recommendations.sort(
        key=lambda r: r["recommendation_score"],
        reverse=True
    )

    return recommendations[:limit]

def build_recommendation_context(request, table_type, user_a, user_b):
    comparison = compare_users_lists(user_a, user_b)

    only_a = comparison.get("only_a", [])
    b_rows = comparison.get("only_b", [])

    auto_liked, auto_disliked = build_genre_preferences(b_rows)

    manual_liked = set(request.GET.getlist("genres_include[]"))
    manual_disliked = set(request.GET.getlist("genres_exclude[]"))

    has_manual_state = bool(manual_liked or manual_disliked)

    if not has_manual_state:
        liked = auto_liked.copy()
        disliked = auto_disliked.copy()
    else:
        liked = manual_liked
        disliked = manual_disliked

    recommendations = recommend_anime(
        only_a,
        liked,
        disliked,
    )
    all_genres = sorted({
        g
        for row in only_a
        for g in row.get("genres", [])
    })
    
    page_obj = paginate(request, recommendations, table_type)
    return {
        "table_type": table_type,
        "page_obj": page_obj, 
        "columns": TABLE_COLUMNS[table_type],
        "user_a": user_a,
        "user_b": user_b,
        "current_sort": None,
        "current_dir": None,
        "all_genres": all_genres,
        "included_genres": sorted(liked),
        "excluded_genres": sorted(disliked),
    }