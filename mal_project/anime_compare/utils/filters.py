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
        return True

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