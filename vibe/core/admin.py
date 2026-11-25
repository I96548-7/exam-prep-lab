from django.contrib import admin

from .models import Question, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("title", "description")
    ordering = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ("text",)
    list_filter = ("topic",)
    list_display = ("topic", "text", "correct_index", "is_active")
    ordering = ("topic", "id")
