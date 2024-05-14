# Python imports
import uuid
import random
import string
import json
import requests

# Django imports
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Third party imports
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from sentry_sdk import capture_exception, capture_message

# Module imports
from . import BaseAPIView
from plane.db.models import User
from plane.api.serializers import UserSerializer
from plane.settings.redis import redis_instance
from plane.bgtasks.magic_link_code_task import magic_link

# 定义获取用户令牌的函数
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return (
        str(refresh.access_token),
        str(refresh),
    )

# SignInEndpoint 用于处理用户的登录或注册请求
class SignInEndpoint(BaseAPIView):
    # 允许任何用户（无论是否认证）访问这个视图
    permission_classes = (AllowAny,)

    # 处理 POST 请求
    def post(self, request):
        try:
            email = request.data.get("email", False)
            password = request.data.get("password", False)

            # 如果缺少电子邮件或密码，则返回错误响应
            if not email or not password:
                return Response(
                    {"error": "Both email and password are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = email.strip().lower()

            # 验证电子邮件格式
            try:
                validate_email(email)
            except ValidationError as e:
                return Response(
                    {"error": "Please provide a valid email address."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(email=email).first()

            # 注册过程：如果用户不存在，则创建新用户
            if user is None:
                user = User.objects.create(email=email, username=uuid.uuid4().hex)
                user.set_password(password)

                # 设置用户的最后活跃、登录时间、IP 和 User Agent 等信息
                user.last_active = timezone.now()
                user.last_login_time = timezone.now()
                user.last_login_ip = request.META.get("REMOTE_ADDR")
                user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
                user.token_updated_at = timezone.now()
                user.save()

                serialized_user = UserSerializer(user).data

                access_token, refresh_token = get_tokens_for_user(user)

                data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": serialized_user,
                }

                # 检查是否配置了分析基础API的URL
                if settings.ANALYTICS_BASE_API:
                    # 使用requests库发起POST请求到分析API
                    _ = requests.post(
                        settings.ANALYTICS_BASE_API,  # 分析API的URL，从Django设置中获取
                        headers={
                            "Content-Type": "application/json",  # 设置请求头，标明发送的数据类型为JSON
                            "X-Auth-Token": settings.ANALYTICS_SECRET_KEY,  # 设置请求头，包含认证信息，值为配置的秘钥
                        },
                        json={
                            "event_id": uuid.uuid4().hex,  # 生成一个唯一的事件ID
                            "event_data": {
                                "medium": "email",  # 事件相关数据，这里指示通过电子邮件进行的动作
                            },
                            "user": {"email": email, "id": str(user.id)},  # 用户信息，包括电子邮件和用户ID
                            "device_ctx": {
                                "ip": request.META.get("REMOTE_ADDR"),  # 设备上下文信息，如IP地址
                                "user_agent": request.META.get("HTTP_USER_AGENT"),  # 设备上下文信息，如用户代理字符串（浏览器类型等）
                            },
                            "event_type": "SIGN_UP",  # 事件类型，在这个场景中为“SIGN_UP”（注册）
                        },
                    )

                # 返回响应给客户端，状态码为200 OK。`data`变量未展示其定义或赋值，假设它包含了要返回给客户端的数据。
                return Response(data, status=status.HTTP_200_OK)

            else:
                # 检查提交的密码是否与数据库中存储的密码匹配
                if not user.check_password(password):
                    # 如果密码不匹配，返回403禁止访问状态和错误信息
                    return Response(
                        {
                            "error": "Sorry, we could not find a user with the provided credentials. Please try again."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                
                # 检查用户是否被标记为非活跃状态
                if not user.is_active:
                    # 如果用户被标记为非活跃，返回403禁止访问状态和错误信息
                    return Response(
                        {
                            "error": "Your account has been deactivated. Please contact your site administrator."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # 使用UserSerializer序列化用户数据，这通常包括用户名、电子邮件等信息，但具体取决于UserSerializer的实现
                serialized_user = UserSerializer(user).data

                # 更新用户最后活跃时间、最后登录时间、最后登录IP地址和最后登录设备的用户代理字符串
                user.last_active = timezone.now()
                user.last_login_time = timezone.now()
                user.last_login_ip = request.META.get("REMOTE_ADDR")
                user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
                user.token_updated_at = timezone.now()  # 更新token更新时间
                user.save()  # 保存更新到数据库

                # 为该用户生成访问令牌和刷新令牌
                access_token, refresh_token = get_tokens_for_user(user)

                # 检查是否配置了分析基础API的URL
                if settings.ANALYTICS_BASE_API:
                    # 使用requests库发起POST请求到分析API
                    _ = requests.post(
                        settings.ANALYTICS_BASE_API,  # 分析API的URL，从Django设置中获取
                        headers={
                            "Content-Type": "application/json",  # 设置请求头，标明发送的数据类型为JSON
                            "X-Auth-Token": settings.ANALYTICS_SECRET_KEY,  # 设置请求头，包含认证信息，值为配置的秘钥
                        },
                        json={
                            "event_id": uuid.uuid4().hex,  # 生成一个唯一的事件ID
                            "event_data": {
                                "medium": "email",  # 事件相关数据，指示通过电子邮件进行的动作
                            },
                            "user": {"email": email, "id": str(user.id)},  # 用户信息，包括电子邮件和用户ID
                            "device_ctx": {
                                "ip": request.META.get("REMOTE_ADDR"),  # 设备上下文信息，如IP地址
                                "user_agent": request.META.get("HTTP_USER_AGENT"),  # 设备上下文信息，如用户代理字符串（浏览器类型等）
                            },
                            "event_type": "SIGN_IN",  # 事件类型，在这个场景中为“SIGN_IN”（登录）
                        },
                    )
                # 准备返回给客户端的数据，包括访问令牌、刷新令牌和序列化后的用户信息
                data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": serialized_user,
                }

                # 返回响应给客户端，状态码为200 OK。
                return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # 若上述任何步骤出现异常，则捕获异常并记录（例如使用Sentry）
            capture_exception(e)
            # 返回一个含有错误信息的400 Bad Request响应给客户端
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class SignOutEndpoint(BaseAPIView):
    # 定义一个post方法来处理POST请求
    def post(self, request):
        try:
            # 尝试从请求数据中获取refresh_token
            refresh_token = request.data.get("refresh_token", False)

            # 如果没有提供refresh_token，则记录一条消息并返回一个400响应
            if not refresh_token:
                capture_message("No refresh token provided")
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 根据请求中的用户ID，获取当前用户对象
            user = User.objects.get(pk=request.user.id)

            # 更新用户的最后登出时间和IP地址信息
            user.last_logout_time = timezone.now()
            user.last_logout_ip = request.META.get("REMOTE_ADDR")

            # 保存更改到数据库
            user.save()

            # 使用提供的refresh_token创建RefreshToken对象，然后将其列入黑名单（作废）
            token = RefreshToken(refresh_token)
            token.blacklist()

            # 返回成功消息和200 OK状态码
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            # 如果在处理过程中出现异常，记录异常并返回一个400响应
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

# 定义一个继承自BaseAPIView的类，用于处理生成魔法链接的请求
class MagicSignInGenerateEndpoint(BaseAPIView):
    # 允许任何用户（无论是否认证）访问这个端点
    permission_classes = [
        AllowAny,
    ]

    # 定义处理POST请求的方法
    def post(self, request):
        try:
            # 尝试从请求数据中获取email字段
            email = request.data.get("email", False)

            # 如果没有提供email或值为False，则返回错误响应
            if not email:
                return Response(
                    {"error": "Please provide a valid email address"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 使用Django内置函数验证邮箱地址格式是否正确
            validate_email(email)

            ## 生成一个随机token，格式为xxxx-xxxx-xxxx，每个x代表小写字母或数字
            token = (
                "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
                + "-"
                + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
                + "-"
                + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            )

            # 获取Redis实例
            ri = redis_instance()

            # 构造一个存储在Redis中的key，以"magic_"加上邮箱作为键名
            key = "magic_" + str(email)

            # 检查这个key是否已经存在于Redis中
            if ri.exists(key):
                data = json.loads(ri.get(key))  # 如果存在，获取其值并解析JSON

                current_attempt = data["current_attempt"] + 1  # 更新尝试次数

                # 如果当前尝试次数超过2次，则返回错误响应
                if data["current_attempt"] > 2:
                    return Response(
                        {"error": "Max attempts exhausted. Please try again later."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                value = {
                    "current_attempt": current_attempt,
                    "email": email,
                    "token": token,
                }
                expiry = 600  # 设置过期时间为600秒（10分钟）

                ri.set(key, json.dumps(value), ex=expiry)  # 更新Redis中的数据

            else:
                # 如果key不存在，则创建新的记录，并初始化尝试次数为0
                value = {"current_attempt": 0, "email": email, "token": token}
                expiry = 600  # 设置过期时间为600秒（10分钟）

                ri.set(key, json.dumps(value), ex=expiry)  # 存储到Redis中

            current_site = settings.WEB_URL  # 获取当前网站的URL
            magic_link.delay(email, key, token, current_site)  # 异步发送魔法链接邮件

            return Response({"key": key}, status=status.HTTP_200_OK)  # 返回成功响应，包含key信息
        except ValidationError:
            return Response(
                {"error": "Please provide a valid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )



class MagicSignInEndpoint(BaseAPIView):
    permission_classes = [
        AllowAny,  # 允许任何人调用此API端点，不需要先前认证。
    ]

    def post(self, request):
        try:
            # 从请求体中提取用户提交的token和key，并对token进行小写转换和去除两端空白。
            user_token = request.data.get("token", "").strip().lower()
            key = request.data.get("key", False)

            # 如果未提供token或key，则返回400错误响应。
            if not key or user_token == "":
                return Response(
                    {"error": "User token and key are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 获取Redis实例
            ri = redis_instance()

            # 检查Redis中是否存在与提供的key对应的记录。
            if ri.exists(key):
                # 如果存在，解析存储的数据（包括预期的token和关联电子邮件地址）。
                data = json.loads(ri.get(key))

                token = data["token"]
                email = data["email"]

                # 检查用户提交的token是否与存储在Redis中的预期token一致。
                if str(token) == str(user_token):
                    # 检查系统中是否已存在与电子邮件地址关联的用户账户。
                    if User.objects.filter(email=email).exists():
                        user = User.objects.get(email=email)
                        # 如果设置了分析API，发送一个事件到分析平台跟踪这次登录行为。
                        if settings.ANALYTICS_BASE_API:
                            _ = requests.post(
                                settings.ANALYTICS_BASE_API,
                                headers={
                                    "Content-Type": "application/json",
                                    "X-Auth-Token": settings.ANALYTICS_SECRET_KEY,
                                },
                                json={
                                    "event_id": uuid.uuid4().hex,
                                    "event_data": {"medium": "code",},
                                    "user": {"email": email, "id": str(user.id)},
                                    "device_ctx": {
                                        "ip": request.META.get("REMOTE_ADDR"),
                                        "user_agent": request.META.get("HTTP_USER_AGENT"),
                                    },
                                    "event_type": "SIGN_IN",
                                },
                            )
                    else:
                        # 如果不存在与该电子邮件地址关联的用户账户，则自动创建一个新账户。
                        user = User.objects.create(
                            email=email,
                            username=uuid.uuid4().hex,  # 使用uuid作为用户名生成唯一性
                            password=make_password(uuid.uuid4().hex),  # 生成随机密码
                            is_password_autoset=True,  # 标记密码是自动生成的
                        )

                        # 如果设置了分析API，向该API发送一个POST请求来记录登录或注册事件
                        if settings.ANALYTICS_BASE_API:
                            _ = requests.post(
                                settings.ANALYTICS_BASE_API,
                                headers={
                                    "Content-Type": "application/json",
                                    "X-Auth-Token": settings.ANALYTICS_SECRET_KEY,
                                },
                                json={
                                    "event_id": uuid.uuid4().hex,   # 为每个事件生成一个唯一的ID
                                    "event_data": {
                                        "medium": "code",  # 指明用户通过代码（魔法链接）进行登录/注册
                                    },
                                    "user": {"email": email, "id": str(user.id)},  # 包含用户邮箱和ID信息
                                    "device_ctx": {  # 设备上下文信息，包括IP地址和用户代理字符串
                                        "ip": request.META.get("REMOTE_ADDR"),
                                        "user_agent": request.META.get(
                                            "HTTP_USER_AGENT"
                                        ),
                                    },
                                    "event_type": "SIGN_UP",
                                },
                            )

                    # 更新用户的最后活跃时间、最后登录时间、最后登录IP和用户代理信息，并保存更改
                    user.last_active = timezone.now()
                    user.last_login_time = timezone.now()
                    user.last_login_ip = request.META.get("REMOTE_ADDR")
                    user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
                    user.token_updated_at = timezone.now()
                    user.save()

                    # 使用UserSerializer序列化用户信息，并为用户生成访问令牌和刷新令牌
                    serialized_user = UserSerializer(user).data
                    access_token, refresh_token = get_tokens_for_user(user)

                    # 准备返回给客户端的数据，包括访问令牌、刷新令牌和序列化后的用户信息
                    data = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": serialized_user,
                    }

                    # 返回成功响应给客户端，状态码为200 OK
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    # 如果提交的token与存储在Redis中的token不匹配，返回错误响应
                    return Response(
                        {"error": "Your login code was incorrect. Please try again."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            else:
                # 如果Redis中不存在该key（可能因为过期），返回错误响应
                return Response(
                    {"error": "The magic code/link has expired please try again"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            # 如果执行过程中发生任何异常，捕获并记录异常信息，然后返回错误响应
            capture_exception(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )
