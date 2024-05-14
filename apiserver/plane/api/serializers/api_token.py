# 处理与APIToken模型相关的数据

# 导入基类序列化器BaseSerializer。
from .base import BaseSerializer
# 从plane.db.models模块导入APIToken模型。
from plane.db.models import APIToken

# 定义APITokenSerializer类，继承自BaseSerializer。
class APITokenSerializer(BaseSerializer):
    class Meta:
        model = APIToken  # 指定此序列化器关联的Django模型为APIToken。
        fields = [
            "label",  # API令牌的标签。
            "user",  # 关联的用户。
            "user_type",  # 用户类型字段，可能指示用户角色或权限级别。
            "workspace",  # API令牌关联的工作空间。
            "created_at",  # API令牌的创建时间。
        ]
