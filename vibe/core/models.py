from django.db import models


class Topic(models.Model):
    title = models.CharField("Название темы", max_length=200, unique=True)
    description = models.TextField("Описание темы", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.title


class Question(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Тема",
    )
    text = models.TextField("Текст вопроса")
    options = models.JSONField("Варианты ответов (список)")
    correct_index = models.PositiveSmallIntegerField(
        "Номер правильного ответа (индекс из списка, с 0)", default=0
    )
    is_active = models.BooleanField("Активный", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text[:80]

    @property
    def correct_answer(self):
        if 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return ""


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Пользователь",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attempts",
        verbose_name="Тема",
    )
    question_ids = models.JSONField("Список ID вопросов", default=list)
    answers = models.JSONField(
        "Ответы (ID вопроса → выбранный индекс)", default=dict
    )
    results = models.JSONField("Детали результата", default=list)
    score = models.PositiveSmallIntegerField("Количество правильных", default=0)
    total = models.PositiveSmallIntegerField("Всего вопросов", default=0)
    created_at = models.DateTimeField("Дата попытки", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Попытка теста"
        verbose_name_plural = "Попытки теста"

    def __str__(self):
        return f"{self.user} — {self.topic or 'тема удалена'} ({self.score}/{self.total})"
