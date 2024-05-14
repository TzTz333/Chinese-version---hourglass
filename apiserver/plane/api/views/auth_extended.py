## Python imports
import jwt

## Django imports
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

## Third Party Imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken

from sentry_sdk import capture_exception

## Module imports
from . import BaseAPIView
from plane.api.serializers.people import (
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)
from plane.db.models import User
from plane.bgtasks.email_verification_task import email_verification
from plane.bgtasks.forgot_password_task import forgot_password


# RequestEmailVerificationEndpoint 类用于生成并发送电子邮件验证链接。
class RequestEmailVerificationEndpoint(BaseAPIView):
    def get(self, request):
        # 为请求的用户生成一个新的访问令牌（access token）。
        token = RefreshToken.for_user(request.user).access_token
        # 获取当前站点的 URL，这通常在 settings.py 文件中配置。
        current_site = settings.WEB_URL
        # 调用异步任务 email_verification 发送验证邮件。
        # 这个任务可能使用 Celery 进行异步处理以提高性能。
        email_verification.delay(
            request.user.first_name, request.user.email, token, current_site
        )
        # 返回一个响应，说明电子邮件发送成功。
        return Response(
            {"message": "Email sent successfully"}, status=status.HTTP_200_OK
        )

# VerifyEmailEndpoint 类用于处理用户点击电子邮件中的验证链接时的请求。
class VerifyEmailEndpoint(BaseAPIView):
    def get(self, request):
        # 从请求的查询参数中获取令牌。
        token = request.GET.get("token")
        try:
            # 使用 JWT 库和 Django 设置中的密钥解码令牌。
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            # 根据令牌中的 user_id 获取对应的用户对象。
            user = User.objects.get(id=payload["user_id"])

            # 如果用户还未验证邮箱，则设置为已验证并保存更改。
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            # 返回响应表示邮箱成功激活。
            return Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )
        
        except jwt.ExpiredSignatureError as indentifier:
            # 如果令牌签名过期，则返回错误响应。
            return Response(
                {"email": "Activation expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        except jwt.exceptions.DecodeError as indentifier:
            # 如果无法解码令牌，则返回错误响应。
            return Response(
                {"email": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

# ForgotPasswordEndpoint 类用于处理忘记密码请求，继承自 BaseAPIView。
class ForgotPasswordEndpoint(BaseAPIView):
    # 允许任何用户（无论是否认证）访问这个视图。
    permission_classes = [permissions.AllowAny]

    # 处理 POST 请求。
    def post(self, request):
        # 从请求数据中获取电子邮件地址。
        email = request.data.get("email")

        # 检查数据库中是否存在该电子邮件对应的用户。
        if User.objects.filter(email=email).exists():
            # 获取该电子邮件对应的用户对象。
            user = User.objects.get(email=email)
            # 使用 Django 的 urlsafe_base64_encode 和 smart_bytes 方法生成用户ID的安全编码字符串。
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            # 生成密码重置令牌。
            token = PasswordResetTokenGenerator().make_token(user)

            # 获取当前站点的 URL，通常在 settings.py 文件中配置。
            current_site = settings.WEB_URL

            # 调用 forgot_password 异步任务发送密码重置邮件。
            forgot_password.delay(
                user.first_name, user.email, uidb64, token, current_site
            )

            # 返回响应，提示用户检查他们的电子邮件以重置密码。
            return Response(
                {"message": "Check your email to reset your password"},
                status=status.HTTP_200_OK,
            )
        
        # 如果未找到电子邮件对应的用户，则返回错误响应。
        return Response(
            {"error": "Please check the email"}, status=status.HTTP_400_BAD_REQUEST
        )


# ResetPasswordEndpoint 类用于处理密码重置请求。
class ResetPasswordEndpoint(BaseAPIView):
    # 允许任何用户（无论是否认证）访问这个视图。
    permission_classes = [permissions.AllowAny]

    # 处理 POST 请求，需要传入用户ID的 base64 编码（uidb64）和令牌（token）作为参数。
    def post(self, request, uidb64, token):
        try:
            # 从 base64 编码中解码出用户 ID，并尝试获取对应的用户对象。
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            
            # 使用 Django 内置的 PasswordResetTokenGenerator 检查提供的令牌是否有效。
            if not PasswordResetTokenGenerator().check_token(user, token):
                # 如果令牌无效，则返回错误响应。
                return Response(
                    {"error": "token is not valid, please request a new one"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
            # 使用 ResetPasswordSerializer 序列化请求数据。
            serializer = ResetPasswordSerializer(data=request.data)

            if serializer.is_valid():
                # 如果序列化器中的数据有效，则使用 set_password 方法更新用户密码。
                # set_password 方法也会负责对密码进行加密处理。
                user.set_password(serializer.data.get("new_password"))
                user.save()
                
                # 构建成功响应信息，并返回更新成功消息。
                response = {
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Password updated successfully",
                }

                return Response(response)
            
            # 如果序列化器中的数据无效，则返回错误信息和状态码400 BAD REQUEST。
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except DjangoUnicodeDecodeError as identifier:
            # 如果在解码过程中遇到编码错误，则认为令牌无效，并返回错误响应。
            return Response(
                {"error": "The provided token is not valid, please request a new one"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

# ChangePasswordEndpoint 类用于处理密码更改请求。
class ChangePasswordEndpoint(BaseAPIView):
    def post(self, request):
        try:
            # 使用 ChangePasswordSerializer 对请求数据进行序列化。
            serializer = ChangePasswordSerializer(data=request.data)

            # 获取当前登录用户对象。
            user = User.objects.get(pk=request.user.id)
            
            if serializer.is_valid():
                # 检查旧密码是否正确。
                if not user.check_password(serializer.data.get("old_password")):
                    # 如果旧密码不正确，则返回错误响应。
                    return Response(
                        {"old_password": ["Wrong password."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # 如果旧密码正确，则使用 set_password 方法设置新密码，该方法还会对新密码进行哈希处理。
                user.set_password(serializer.data.get("new_password"))
                user.save()
                
                # 返回成功响应消息，表示密码已成功更新。
                response = {
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Password updated successfully",
                }

                return Response(response)

            # 如果序列化器验证失败，返回错误信息。
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # 捕获并记录异常信息。
            capture_exception(e)
            
            # 返回服务器内部错误响应。
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )
