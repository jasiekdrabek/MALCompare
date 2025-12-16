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
    "recommend": [
        {"label": "Poster", "key": "main_picture", "sortable": False},
        {"label": "Tytuł", "key": "title", "sortable": True},
        {"label": "Status", "key": "status", "sortable": True},
        {"label": "Score", "key": "score", "sortable": True},
        {"label": "Liczba odcinków", "key": "num_episodes", "sortable": False},
        {"label": "Gatunki", "key": "genres", "sortable": False},
    ],
    "anti_recommend": [
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