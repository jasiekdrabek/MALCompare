def get_filters_open(request):
    return request.GET.get("filters_open", "1") == "1"


def build_filters_summary(
    included_genres,
    excluded_genres,
    included_statuses,
    excluded_statuses,
    score_min,
    score_max,
    ep_min,
    ep_max,
    status_labels=None,
):
    summary = []

    if included_genres:
        summary.append(
            "Included genres: " + ", ".join(sorted(included_genres))
        )

    if excluded_genres:
        summary.append(
            "Excluded genres: " + ", ".join(sorted(excluded_genres))
        )

    if included_statuses:
        labels = [
            status_labels.get(s, s) if status_labels else s
            for s in included_statuses
        ]
        summary.append("Status: " + ", ".join(labels))

    if excluded_statuses:
        labels = [
            status_labels.get(s, s) if status_labels else s
            for s in excluded_statuses
        ]
        summary.append("Status excluded: " + ", ".join(labels))

    if score_min is not None or score_max is not None:
        summary.append(
            f"Score: {score_min or '?'} – {score_max or '?'}"
        )

    if ep_min is not None or ep_max is not None:
        summary.append(
            f"Episodes: {ep_min or '?'} – {ep_max or '?'}"
        )

    return summary
