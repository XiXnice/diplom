from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class KnowledgeBase(models.Model):
    theme = models.CharField(max_length=200, verbose_name='Тема')
    text = models.TextField(verbose_name='Текст')
    date_time_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, related_name='knowledge_bases')

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = 'База знаний'
        verbose_name_plural = "Список баз знаний"
        ordering = ('-date_time_creation',)


class Forum(models.Model):
    theme = models.CharField(max_length=200, verbose_name='Тема')
    date_time_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    condition = models.BooleanField(default=False, verbose_name='Опубликовано')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, related_name='forums')

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = 'Форум'
        verbose_name_plural = "Список форумов"
        ordering = ('-date_time_creation',)


class Patterns(models.Model):
    theme = models.CharField(max_length=200, verbose_name='Тема')
    path_file = models.FileField(upload_to='uploads/', verbose_name='Путь к шаблону')
    date_time_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, related_name='patterns')

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = "Список шаблонов"
        ordering = ('-date_time_creation',)


class MessageForum(models.Model):
    text = models.TextField(verbose_name='Текст')
    date_time_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='forum_messages', blank=True)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, verbose_name='Форум', blank=True, related_name='forum_messages')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Сообщение в форуме'
        verbose_name_plural = "Сообщения в форуме"
        ordering = ('-date_time_creation',)


class MessagePatterns(models.Model):
    text = models.TextField(verbose_name='Текст')
    path_file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='Путь к файлу', blank=True, null=True)
    date_time_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True,)
    patterns = models.ForeignKey(Patterns, on_delete=models.CASCADE, verbose_name='Шаблон', blank=True,)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Сообщение в шаблоне'
        verbose_name_plural = "Сообщения в шаблоне"
        ordering = ('-date_time_creation',)


class EstimationPatterns(models.Model):
    estimation = models.IntegerField(verbose_name='Оценка')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, related_name='estimations')
    patterns = models.ForeignKey(Patterns, on_delete=models.CASCADE, verbose_name='Шаблон', blank=True, related_name='estimations')

    def __str__(self):
        return self.estimation

    class Meta:
        verbose_name = 'Оценка шаблона'
        verbose_name_plural = "Оценки шаблонов"


class ConfirmEmailToken(models.Model):
    objects = models.manager.Manager()
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)