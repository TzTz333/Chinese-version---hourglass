# 导入基础序列化器
from .base import BaseSerializer

# 导入数据库模型Shortcut
from plane.db.models import Shortcut

# 定义快捷方式(ShortCut)的序列化器
class ShortCutSerializer(BaseSerializer):
    # Meta类用于提供序列化器的元数据信息
    class Meta:
        model = Shortcut  # 指定这个序列化器关联的数据库模型是Shortcut
        fields = "__all__"  # 指示序列化器包含模型中的所有字段
        
        # 指定哪些字段应该被设置为只读，即不允许通过API修改它们的值
        read_only_fields = [
            "workspace",  # 工作区字段设为只读，通常在创建快捷方式时自动设置
            "project",  # 项目字段设为只读，因为快捷方式一旦创建就与特定项目相关联
        ]
