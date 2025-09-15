class AuthManagerValidateConstants:
    """
    Базовый класс констант для валидации пароля в UserManager.

    Атрибуты:
    - REGULAR_EXPR_PASSWORD (str): Регуляроное выражение для проверки пароля.
    - ERROR_TEXT_PASSWORD (str): Сообщение о несоответствии пароля.
    - ERROR_EMAIL_IN_PASSWORD (str): Сообщение о том, что пароль не должен содержать почты e-mail.
    - ERROR_PALINDROM (str): Сообщение о том, что пароль не должен быть палиндромом.
    """

    REGULAR_EXPR_PASSWORD: str = r'^(?=.*[A-Z])(?=.*\d)(?=.*[_#%])[A-Za-z0-9_#%]{8,}$'
    ERROR_TEXT_PASSWORD: str = (
        'Пароль должен содержать символы английского алфавита, '
        'минимум одну заглавную букву, '
        'минимум 1 допустимый символ (_, #, %), '
        'и не короче 8 символов.'
    )
    ERROR_EMAIL_IN_PASSWORD: str = 'Пароль не должен содержать почты e-mail!'
    ERROR_PALINDROM: str = 'Пароль не должен являтся палиндромом!'
