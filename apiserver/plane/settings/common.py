import os
import datetime
from datetime import timedelta
from django.core.management.utils import get_random_secret_key


# 获取当前文件的绝对路径的上两级目录，作为项目的基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 从环境变量获取秘密密钥，如果没有则生成一个随机的秘密密钥
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

# 安全警告：生产环境中不应该开启DEBUG模式！
DEBUG = True

# 允许处理请求的主机/域名列表，为空表示不限制
ALLOWED_HOSTS = []


# 应用定义部分
INSTALLED_APPS = [
    # Django自带应用
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # 自定义应用
    "plane.analytics",
    "plane.api",
    "plane.bgtasks",
    "plane.db",
    "plane.utils",
    "plane.web",
    "plane.middleware",
    # 第三方应用
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders", # 跨域请求处理
    "taggit", # 标签管理
    "django_rq", # Redis队列
]

MIDDLEWARE = [
    # 中间件配置，执行请求|响应处理的各个阶段
    "corsheaders.middleware.CorsMiddleware", # 处理跨域请求的中间件
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",  # 静态文件压缩、缓存管理
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 获取当前请求用户信息的中间件
    "crum.CurrentRequestUserMiddleware",
    # Gzip压缩中间件
    "django.middleware.gzip.GZipMiddleware",
]

REST_FRAMEWORK = {
     # DRF（Django Rest Framework）相关配置，默认认证类、权限类等设置。
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

AUTHENTICATION_BACKENDS = (
     # 认证后端配置，默认使用Django内置的模型后端。
    "django.contrib.auth.backends.ModelBackend",  # default
    # "guardian.backends.ObjectPermissionBackend",
)

ROOT_URLCONF = "plane.urls"

TEMPLATES = [
    # 模板引擎设置
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
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


JWT_AUTH = {
    # JWT相关配置
    "JWT_ENCODE_HANDLER": "rest_framework_jwt.utils.jwt_encode_handler",
    "JWT_DECODE_HANDLER": "rest_framework_jwt.utils.jwt_decode_handler",
    "JWT_PAYLOAD_HANDLER": "rest_framework_jwt.utils.jwt_payload_handler",
    "JWT_PAYLOAD_GET_USER_ID_HANDLER": "rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler",
    "JWT_RESPONSE_PAYLOAD_HANDLER": "rest_framework_jwt.utils.jwt_response_payload_handler",
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_GET_USER_SECRET_KEY": None,
    "JWT_PUBLIC_KEY": None,
    "JWT_PRIVATE_KEY": None,
    "JWT_ALGORITHM": "HS256",
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LEEWAY": 0,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=604800),
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_ALLOW_REFRESH": False,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_AUTH_COOKIE": None,
}

WSGI_APPLICATION = "plane.wsgi.application"
ASGI_APPLICATION = "plane.asgi.application"

# Django Sites

SITE_ID = 1

# 自定义用户模型
AUTH_USER_MODEL = "db.User"

# Database
# 数据库连接配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# 密码验证器配置
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

# Static files (CSS, JavaScript, Images)
# 静态文件，CSS、JS、图片等资源的配置
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static-assets", "collected-static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# 静态文件压缩、缓存管理
# Media Settings
MEDIA_ROOT = "mediafiles"
MEDIA_URL = "/media/"


# Internationalization
# 国际化配置
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 邮箱配置，用于发送邮件，如用户注册、密码重置等
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# 用于发送电子邮件的host。
EMAIL_HOST = os.environ.get("EMAIL_HOST")
# 用于发送电子邮件的端口
EMAIL_PORT = 587
# EMAIL_HOST的可选 SMTP 身份验证信息
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# SIMPLE_JWT库相关配置，用于简化JWT操作。
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10080),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=43200),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}
