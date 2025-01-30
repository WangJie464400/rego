import os
from pathlib import Path
import environ
# Build paths inside the project like this: BASE_D                                                                                                                                                                                                                                                                                                                                                                                    IR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2$rzn2(t)8j_dsg2z-1b2o-qo7jbqkk6x!4s^*j39)*z=7q1ac"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

AUTH_USER_MODEL = 'api.CustomUser'

CORS_ALLOW_CREDENTIALS = True  # 允许携带凭证

ALLOWED_HOSTS=[
    "localhost",
    "127.0.0.1",
    "172.20.10.8",
    "172.20.10.1",
    "192.168.108.121",
    "just-clean-killdeer.ngrok-free.app"
]
# 允许的前端源列表
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'https://just-clean-killdeer.ngrok-free.app',
    'http://172.20.10.8:8080',
    'http://172.20.10.1:8080',

]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'https://just-clean-killdeer.ngrok-free.app',
    'http://172.20.10.8:8080',
    'http://172.20.10.1:8080',
]


APPEND_SLASH = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_DOMAIN = None

# 初始化环境变量
env = environ.Env(
    # 这里可以定义环境变量的类型及默认值
    YOLOV7_WEIGHTS=(str, f'{str(BASE_DIR).replace("\\", "/")}/api/yolov7/yolov7.pt'),
    YOLOV7_DEVICE=(str, '0'),
    YOLOV7_IMG_SIZE=(int, 640),
    YOLOV7_CONF_THRESH=(float, 0.25),
    YOLOV7_IOU_THRESH=(float, 0.45),
    YOLOV7_PROJECT=(str, 'results'),
    YOLOV7_NAME=(str, 'exp'),
)

# 环境变量了
YOLOV7_WEIGHTS = env('YOLOV7_WEIGHTS')
YOLOV7_DEVICE = env('YOLOV7_DEVICE')
YOLOV7_IMG_SIZE = env('YOLOV7_IMG_SIZE')
YOLOV7_CONF_THRESH = env('YOLOV7_CONF_THRESH')
YOLOV7_IOU_THRESH = env('YOLOV7_IOU_THRESH')
YOLOV7_PROJECT = env('YOLOV7_PROJECT')
YOLOV7_NAME = env('YOLOV7_NAME')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

ROOT_URLCONF = "food_calorie_detection.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "food_calorie_detection.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "food",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "3306",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/results/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# 输出文件夹
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'results'),  # 项目中的static目录
]
# 部署时的静态文件收集路径
# STATIC_ROOT = os.path.join(BASE_DIR, 'images')  # 用于生产环境的静态文件收集


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_NUMBER_FILES = 1000000
DATA_UPLOAD_MAX_MEMORY_SIZE = 1000000000
