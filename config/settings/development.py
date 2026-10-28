from email.charset import add_charset, SHORTEST

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'eseninbeg.ru <run@eseninbeg.ru>'

# Console backend prints email bodies as base64-encoded UTF-8, which is unreadable.
# Register utf-8 as pass-through (8bit) so the console shows plain Cyrillic text.
add_charset('utf-8', SHORTEST, None, 'utf-8')
