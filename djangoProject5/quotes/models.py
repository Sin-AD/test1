from django.db import models
from django.db.models import F
from django.contrib.auth.models import User

class Source(models.Model):
    TYPE_CHOICES = [
        ("film", "Фильм"),
        ("book", "Книга"),
        ("other", "Другое"),
    ]
    name = models.CharField("Название источника", max_length=255, unique=True)
    type = models.CharField("Тип", max_length=20, choices=TYPE_CHOICES, default="other")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"


class Quote(models.Model):
    text = models.TextField(
        "Текст цитаты",
        unique=True,
        error_messages={
            "unique": "Цитата с таким текстом уже есть."  
        }
    )

    source = models.ForeignKey(Source, verbose_name="Источник", on_delete=models.CASCADE, related_name="quotes")
    weight = models.PositiveIntegerField("Вес (чем выше — тем чаще выдаётся)", default=1)
    views = models.PositiveIntegerField("Просмотры", default=0)
    likes = models.IntegerField("Лайки", default=0)
    dislikes = models.IntegerField("Дизлайки", default=0)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        ordering = ["-likes", "-views", "-created_at"]
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"

    def __str__(self):
        short = (self.text[:75] + "...") if len(self.text) > 75 else self.text
        return f"{short} — {self.source.name}"


    def increment_views(self):
        Quote.objects.filter(pk=self.pk).update(views=F("views") + 1)

    def vote(self, user, kind: str):
        if kind not in ("like", "dislike"):
            raise ValueError("Unknown vote kind")

        try:
            existing = QuoteVote.objects.get(user=user, quote=self)
            if existing.vote == kind:
                return
            if existing.vote == "like":
                Quote.objects.filter(pk=self.pk).update(likes=F("likes") - 1)
            elif existing.vote == "dislike":
                Quote.objects.filter(pk=self.pk).update(dislikes=F("dislikes") - 1)
            existing.vote = kind
            existing.save()
        except QuoteVote.DoesNotExist:
            QuoteVote.objects.create(user=user, quote=self, vote=kind)

        if kind == "like":
            Quote.objects.filter(pk=self.pk).update(likes=F("likes") + 1)
        else:
            Quote.objects.filter(pk=self.pk).update(dislikes=F("dislikes") + 1)

class QuoteVote(models.Model):
    VOTE_CHOICES = [
        ("like", "Лайк"),
        ("dislike", "Дизлайк"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="votes")
    vote = models.CharField(max_length=7, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "quote")  

    def __str__(self):

        return f"{self.user.username} -> {self.quote.pk}: {self.vote}"

