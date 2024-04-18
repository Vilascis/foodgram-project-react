from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator
from django.db import models

from core.abstract.models import AbstarctManager, AbstractModel
from core.users.constants import ADMIN, MAX_LENGTH_ROLE, USER
from core.users.validators import UsernameValidator, validate_me_name


class UserManager(BaseUserManager, AbstarctManager):
    """Кастомный менеджер для создания пользователя, суперюзера."""

    def create_user(self, username, email, password=None, **kwargs):
        """Создаем пользователя с username, email и паролем."""
        if username is None:
            raise TypeError('Пользователь должен иметь username')
        if email is None:
            raise TypeError('Пользователь должен иметь email')
        if password is None:
            raise TypeError('Пользователь должен иметь пароль')

        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None, **kwargs):
        """Создаем пользователя с правами superuser(admin)."""
        if username is None:
            raise TypeError('Суперпользователь должен иметь username')
        if email is None:
            raise TypeError('Суперпользователь должен иметь email')
        if password is None:
            raise TypeError('Суперпользователь должен иметь пароль')

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

    def change_password(self, username, email, current_password, new_password=None):
        """Смена пароля пользователя."""
        user = self.model(username=username, email=self.normalize_email(email))

        if username is None:
            raise TypeError('Пользователь должен иметь username')
        if email is None:
            raise TypeError('Пользователь должен иметь email')
        if current_password is None:
            raise TypeError('Пользователь должен иметь пароль')
        if new_password is None:
            raise TypeError('Пользователь должен иметь пароль')

        user = self.model(username=username, email=self.normalize_email(email))

        if user.check_password(new_password):
            user.set_password(new_password)
            user.save(using=self._db)


class User(AbstractModel, AbstractUser, PermissionsMixin):
    """Пользователь."""

    class UserRoles(models.TextChoices):
        """Выбор роли."""

        user = USER, USER
        admin = ADMIN, ADMIN

    username = models.CharField(
        db_index=True,
        max_length=255,
        unique=True,
        validators=(UsernameValidator(), validate_me_name, MaxLengthValidator(255)),
    )
    first_name = models.CharField(max_length=150, validators=[MaxLengthValidator(150)])
    last_name = models.CharField(max_length=150, validators=[MaxLengthValidator(150)])
    email = models.EmailField(
        db_index=True, unique=True, max_length=254, validators=[MaxLengthValidator(254)]
    )
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=MAX_LENGTH_ROLE,
        choices=UserRoles.choices,
        default=UserRoles.user,
        blank=True,
        help_text='Выберете роль пользователя',
        validators=[MaxLengthValidator(MAX_LENGTH_ROLE)],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.email}'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser


class Subscribe(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчики',
    )
    created = models.DateTimeField('Дата и время подписки', auto_now_add=True)

    class Meta:
        verbose_name = 'подписчики'
        verbose_name_plural = 'Подписчики'

        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='uq_author_user',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан {self.author}'
