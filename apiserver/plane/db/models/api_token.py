# 导入Python的uuid模块，用于生成唯一的UUID
from uuid import uuid4

# 导入Django的模型和配置模块
from django.db import models
from django.conf import settings

# 导入本地的BaseModel
from .base import BaseModel


# 定义生成标签令牌的函数
def generate_label_token():
    return uuid4().hex  # 返回一个随机生成的UUID的16进制字符串

# 定义生成令牌的函数
def generate_token():
    return uuid4().hex + uuid4().hex  # 返回两个随机生成的UUID的16进制字符串的连接


# 定义APIToken模型，继承自BaseModel
class APIToken(BaseModel):
    token = models.CharField(max_length=255, unique=True, default=generate_token)  # 令牌字段，唯一，长度最大255，默认值由generate_token函数生成
    label = models.CharField(max_length=255, default=generate_label_token)  # 标签字段，长度最大255，默认值由generate_label_token函数生成
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关联到AUTH_USER_MODEL设置的用户模型
        on_delete=models.CASCADE,  # 当关联的用户被删除时，该APIToken也会被删除
        related_name="bot_tokens",  # 在用户模型中反向关联APIToken的名称
    )
    user_type = models.PositiveSmallIntegerField(
        choices=((0, "Human"), (1, "Bot")),  # 用户类型，0代表人类，1代表机器人
        default=0  # 默认为0，即人类
    )
    workspace = models.ForeignKey(
        "db.Workspace",  # 关联到Workspace模型
        related_name="api_tokens",  # 在Workspace模型中反向关联APIToken的名称
        on_delete=models.CASCADE,  # 当关联的Workspace被删除时，该APIToken也会被删除
        null=True  # 允许为空
    )

    class Meta:
        verbose_name = "API Token"  # 在Django admin中显示的名称
        verbose_name_plural = "API Tokens"  # 在Django admin中显示的复数名称
        db_table = "api_tokens"  # 数据库中的表名
        ordering = ("-created_at",)  # 默认的排序字段，按照创建时间的倒序排序

    def __str__(self):
        return str(self.user.name)  # 定义对象的字符串表示形式为用户的名称