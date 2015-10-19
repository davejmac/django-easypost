DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_TZ = True

MIDDLEWARE_CLASSES = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

SECRET_KEY = 'fake-key'
EASYPOST_API_KEY = 'test-key'  # for testing, set this key to the test key that EasyPost generates for your account

ROOT_URLCONF = 'easypost.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'easypost',
]

SITE_ID = 1
