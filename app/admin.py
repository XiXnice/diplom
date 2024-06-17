from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import User, ConfirmEmailToken, KnowledgeBase, Forum, Patterns, MessageForum, MessagePatterns


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'patronymic')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'last_name', 'first_name', 'patronymic')
    list_filter = ('is_active', 'is_staff', 'is_superuser',)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('theme', 'text', 'date_time_creation', 'user_id')


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('theme', 'date_time_creation', 'condition', 'user_id')


@admin.register(Patterns)
class PatternsAdmin(admin.ModelAdmin):
    pass


@admin.register(MessageForum)
class MessageForumAdmin(admin.ModelAdmin):
    pass


@admin.register(MessagePatterns)
class MessagePatternsAdmin(admin.ModelAdmin):
    pass


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
