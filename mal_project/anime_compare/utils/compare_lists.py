from ..models import UserAnime, AnimeEntry, Anime

def compare_users_lists(userA: str, userB: str):

    snapA = UserAnime.objects.filter(username=userA).first()
    snapB = UserAnime.objects.filter(username=userB).first()

    if not snapA or not snapB:
        raise Exception("Brak snapshotów jednego z użytkowników.")

    entriesA = AnimeEntry.objects.filter(user_list=snapA).select_related("anime")
    entriesB = AnimeEntry.objects.filter(user_list=snapB).select_related("anime")

    dictA = {e.anime.id: e for e in entriesA}
    dictB = {e.anime.id: e for e in entriesB}

    common_ids = set(dictA.keys()) & set(dictB.keys())
    common = []
    for anime_id in common_ids:
        a = dictA[anime_id]
        b = dictB[anime_id]
        common.append({
            "anime_id": anime_id,
            "title": a.anime.title,
            "status_a": a.status,
            "status_b": b.status,
            "score_a": a.score,
            "score_b": b.score,
            "main_picture": a.anime.main_picture,
            "num_episodes": a.anime.num_episodes,
            "genres":a.anime.genres,
        })

    only_a = [{
        "anime_id": anime_id,
        "title": dictA[anime_id].anime.title,
        "status": dictA[anime_id].status,
        "score": dictA[anime_id].score,
        "main_picture": dictA[anime_id].anime.main_picture,
        "num_episodes": dictA[anime_id].anime.num_episodes,
        "genres":dictA[anime_id].anime.genres,
    } for anime_id in set(dictA.keys()) - set(dictB.keys())]

    only_b = [{
        "anime_id": anime_id,
        "title": dictB[anime_id].anime.title,
        "status": dictB[anime_id].status,
        "score": dictB[anime_id].score,
        "main_picture": dictB[anime_id].anime.main_picture,
        "num_episodes": dictB[anime_id].anime.num_episodes,
        "genres":dictB[anime_id].anime.genres,
    } for anime_id in set(dictB.keys()) - set(dictA.keys())]

    return {
        "user_a": userA,
        "user_b": userB,
        "common": common,
        "only_a": only_a,
        "only_b": only_b,
    }
