# 导入基础序列化器 BaseSerializer
from .base import BaseSerializer
# 导入用户简略信息的序列化器 UserLiteSerializer
from .user import UserLiteSerializer
# 从数据库模型中导入 Importer 模型
from plane.db.models import Importer

# 定义 Importer 模型的序列化器
class ImporterSerializer(BaseSerializer):
    # 使用 UserLiteSerializer 序列化 initiated_by 字段，并将其重命名为 initiated_by_detail。
    # 这里指定源字段为 "initiated_by"，并设置为只读模式，意味着该字段仅用于展示而不能通过API更新。
    initiated_by_detail = UserLiteSerializer(source="initiated_by", read_only=True)

    class Meta:  # 内部 Meta 类包含了一些关于序列化器行为的元信息。
        model = Importer  # 指明该序列化器对应的 Django 模型是 Importer。
        fields = "__all__"  # 指定包含模型中所有字段。这意味着除了上面显式声明的 initiated_by_detail 外，其他所有模型字段都将被自动包含在序列化输出中。

# 处理与Importer模型相关的数据