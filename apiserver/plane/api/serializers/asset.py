# 导入项目自定义的基类序列化器 BaseSerializer。
from .base import BaseSerializer
# 从 plane.db.models 模块导入 FileAsset 模型。
from plane.db.models import FileAsset

# 定义 FileAssetSerializer 类，它继承自 BaseSerializer。
class FileAssetSerializer(BaseSerializer):
    class Meta:
        # 指定此序列化器关联的 Django 模型为 FileAsset。
        model = FileAsset
        # 指定需要序列化/反序列化的字段为模型中定义的所有字段。
        fields = "__all__"
        # 指定一些字段为只读，即它们可以被序列化输出，但不能通过反序列化更新。
        read_only_fields = [
            "created_by",  # 文件创建者
            "updated_by",  # 文件最后更新者
            "created_at",  # 文件创建时间
            "updated_at",  # 文件最后更新时间
        ]
