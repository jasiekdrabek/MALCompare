from anime_compare.models import UserAnime, Anime, AnimeEntry
from django.db import transaction
from django.utils import timezone

def save_user_anime_list(username: str, animelist_data: dict) -> UserAnime:
    entries = animelist_data
    entry_count = len(entries)

    with transaction.atomic():
        snapshot, created = UserAnime.objects.get_or_create(username=username, defaults={"entry_count": entry_count})

        if not created:
            snapshot.entry_count = entry_count
            snapshot.fetched_at = timezone.now()
            snapshot.save()

        anime_ids = [item["node"]["id"] for item in entries]

        existing = {
            a.id: a for a in Anime.objects.filter(id__in=anime_ids)
        }

        new_anime_objs = []
        for item in entries:
            if item["node"]["id"]  in existing:
                continue 

            new_anime_objs.append(
                Anime(
                    id=item["node"]["id"],
                    title=item["node"]["title"],
                    genres=[g["name"] for g in item["node"]["genres"]] if item["node"]["genres"] else [],
                    num_episodes=item["node"]["num_episodes"],
                    main_picture=item["node"]["main_picture"]["medium"]
                )
            )
        if new_anime_objs:
            Anime.objects.bulk_create(new_anime_objs)
            existing.update({
                a.id: a for a in Anime.objects.filter(id__in=anime_ids)
            })

        new_entry_objs = []
        existing_entry = {
            e.anime_id
            for e in AnimeEntry.objects.filter(user_list=snapshot)
        }
        for item in entries:
            if item["node"]["id"]  in existing_entry:
                continue
            node = item["node"]
            status_obj = item.get("list_status", {})

            new_entry_objs.append(
                AnimeEntry(
                    user_list=snapshot,
                    anime=existing[node["id"]],
                    status=status_obj.get("status"),
                    score=status_obj.get("score"),
                )
            )
        if new_entry_objs:
            AnimeEntry.objects.bulk_create(new_entry_objs)
            existing_entry.update({
                a.id: a for a in AnimeEntry.objects.filter(id__in=anime_ids)
            })

    return snapshot
