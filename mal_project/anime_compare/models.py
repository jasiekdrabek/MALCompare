from django.db import models

class UserAnime(models.Model):
    """
    Snapshot listy anime danego użytkownika z MAL w konkretnym momencie.
    """
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, db_index=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    entry_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-fetched_at']

    def __str__(self):
        return f"{self.username} – {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"


class Anime(models.Model):
    """
    Unikalne anime z MAL – przechowywane tylko raz.
    """
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=500)
    genres = models.JSONField(default=list)
    num_episodes = models.PositiveIntegerField(null=True, blank=True)
    main_picture = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title


class AnimeEntry(models.Model):
    """
    Relacja UserAnime ↔ Anime — dane specyficzne dla użytkownika.
    """
    id = models.AutoField(primary_key=True)
    user_list = models.ForeignKey(UserAnime, on_delete=models.CASCADE, related_name="entries")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="user_entries")

    status = models.CharField(max_length=100, null=True, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("user_list", "anime")

    def __str__(self):
        return f"{self.user_list.username} – {self.anime.title} ({self.status}, {self.score})"