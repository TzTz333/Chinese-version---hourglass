# 导入Django REST Framework和Simple JWT所需的类
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    SerializerMethodField,
)
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

# 导入自定义的User模型
from plane.db.models import User


# UserSerializer用于序列化用户模型的数据
class UserSerializer(ModelSerializer):
    class Meta:
        model = User  # 指定序列化器关联的模型是自定义的User模型
        fields = "__all__"  # 指定将模型的所有字段包含进序列化结果中
        extra_kwargs = {"password": {"write_only": True}}  # 将密码字段设置为仅写，不在序列化结果中返回


# ChangePasswordSerializer用于处理用户密码更改请求的数据验证
class ChangePasswordSerializer(Serializer):
    model = User  # 指定关联的模型，尽管在Serializer中不强制要求

    old_password = CharField(required=True)  # 要求提供旧密码，必填
    new_password = CharField(required=True)  # 要求提供新密码，必填


# ResetPasswordSerializer用于处理重置密码请求的数据验证
class ResetPasswordSerializer(Serializer):
    model = User  # 指定关联的模型，尽管在Serializer中不强制要求

    new_password = CharField(required=True)  # 要求提供新密码，必填
    confirm_password = CharField(required=True)  # 要求提供确认密码，必须与新密码一致，必填


# TokenSerializer用于序列化认证令牌信息，包括访问令牌和刷新令牌
class TokenSerializer(ModelSerializer):
    user = UserSerializer()  # 使用UserSerializer来序列化关联的用户信息
    
    # 定义方法获取访问令牌字符串
    access_token = SerializerMethodField()
    
    # 定义方法获取刷新令牌字符串
    refresh_token = SerializerMethodField()

    # 获取访问令牌，为关联用户生成一个新的访问令牌并返回其字符串表示形式
    def get_access_token(self, obj):
        refresh_token = RefreshToken.for_user(obj.user)
        return str(refresh_token.access_token)

    # 获取刷新令牌，为关联用户生成一个新的刷新令牌并返回其字符串表示形式
    def get_refresh_token(self, obj):
        refresh_token = RefreshToken.for_user(obj.user)
        return str(refresh_token)

    class Meta:
        model = Token  # 指定序列化器关联的模型是Django REST Framework自带的Token模型
        fields = "__all__"  # 指定将模型的所有字段包含进序列化结果中

