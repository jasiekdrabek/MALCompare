from .compare_lists import compare_users_lists
from .table import paginate
from .constants import TABLE_COLUMNS
import math

IGNORED_STATUSES = {"plan_to_watch"}
STATUS_MULTIPLIER = {
    "completed": 1.2,
    "watching": 1.1,
    "dropped": 0.4,
}

ANTI_STATUS_MULTIPLIER = {
    "completed": 0.5,
    "watching": 0.6,
    "dropped": 1.2,
}

def build_genre_preferences(user_rows):
    genre_scores = {}

    for row in user_rows:
        score = row.get("score")
        if row.get("status") in IGNORED_STATUSES:
            continue
        if not score:
            continue
        for g in row.get("genres", []):
            genre_scores.setdefault(g, []).append(score)

    genre_avg = {
        g: sum(scores) / len(scores)
        for g, scores in genre_scores.items()
        if len(scores) >= 3
    }

    if not genre_avg:
        return set(), set(),{}

    values = sorted(genre_avg.values())

    low_cut = values[int(len(values) * 0.1)]
    high_cut = values[int(len(values) * 0.9)]

    liked = {g for g, v in genre_avg.items() if v >= high_cut}
    disliked = {g for g, v in genre_avg.items() if v <= low_cut}
    return liked, disliked, genre_scores

def genre_confidence(genre_scores):
    confidence = {}
    for g, scores in genre_scores.items():
        if len(scores) < 3:
            continue

        avg = sum(scores) / len(scores)
        conf = min(1.0, math.log(len(scores) + 1, 10))

        confidence[g] = conf

    return confidence


def recommend_anime(
    only_a_rows,
    liked_genres,
    disliked_genres,
    genre_conf,
    limit=20,
    anti=False
):
    recommendations = []
    for row in only_a_rows:
        genres = set(row.get("genres", []))
        score_a = row.get("score")
        if (not score_a or score_a <= 6 or score_a == 0) and not anti:
            recommendations.append({
                **row,
                "recommendation_score": 0,
            })
            continue
        
        if (not score_a or score_a > 4 or score_a == 0) and anti:
            recommendations.append({
                **row,
                "recommendation_score": 0,
            })
            continue
        if anti:
            score_a = 10 - score_a
        score_component = (score_a / 10) * 3 

        genre_score = 0.0
        for g in genres:
            conf = genre_conf.get(g, 0)

            if g in liked_genres:
                genre_score += 0.7 * conf
            elif g in disliked_genres:
                genre_score -= 0.9 * conf

        status = row.get("status")
        status_mult = STATUS_MULTIPLIER.get(status, 1.0)
        if anti:
            status_mult = ANTI_STATUS_MULTIPLIER.get(status, 1.0)

        final_score = (score_component + genre_score) * status_mult

        recommendations.append({
            **row,
            "recommendation_score": round(final_score, 3),
        })

    recommendations.sort(
        key=lambda r: r["recommendation_score"],
        reverse=True
    )

    return recommendations[:limit]

def build_recommendation_context(request, table_type, user_a, user_b, anti = False):
    comparison = compare_users_lists(user_a, user_b)

    only_a = comparison.get("only_a", [])
    b_rows = comparison.get("only_b", [])

    auto_liked, auto_disliked, genre_scores = build_genre_preferences(b_rows)
    if anti:
        auto_liked, auto_disliked = auto_disliked, auto_liked
    manual_liked = set(request.GET.getlist("genres_include[]"))
    manual_disliked = set(request.GET.getlist("genres_exclude[]"))
    genre_conf = genre_confidence(genre_scores)
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
        genre_conf,
        limit=20,
        anti = anti
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