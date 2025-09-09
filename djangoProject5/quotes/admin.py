from django.contrib import admin
from .models import Source, Quote

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    search_fields = ("name",)

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("short_text", "get_source", "weight", "views", "likes", "dislikes", "created_at")
    list_filter = ("source__type",)
    search_fields = ("text", "source__name")
    actions = ("reset_votes",)

    def short_text(self, obj):
        return (obj.text[:80] + "...") if len(obj.text) > 80 else obj.text
    short_text.short_description = "Цитата"

    def get_source(self, obj):
        return obj.source.name
    get_source.short_description = "Источник"

    def reset_votes(self, request, queryset):
        queryset.update(likes=0, dislikes=0)
    reset_votes.short_description = "Сбросить лайки/дизлайки для выбранных цитат"
