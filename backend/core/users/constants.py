USER = 'user'
ADMIN = 'admin'

USER_ROLES = (
    (USER, USER),
    (ADMIN, ADMIN),
)

MAX_LENGTH_ROLE = max(len(role) for role, _ in USER_ROLES)
"""Максимальная длина поля роли пользователя."""
