# 从plane.api.serializers模块导入BaseSerializer基类。
from plane.api.serializers import BaseSerializer
# 从plane.db.models模块导入Integration和WorkspaceIntegration模型。
from plane.db.models import Integration, WorkspaceIntegration

# 定义IntegrationSerializer，继承自BaseSerializer。
class IntegrationSerializer(BaseSerializer):
    class Meta:
        model = Integration  # 指定此序列化器关联的Django模型为Integration。
        fields = "__all__"  # 指定序列化/反序列化所有字段。
        read_only_fields = [
            "verified",  # 将“verified”字段设置为只读，即在API中不能被外部修改。
        ]

# 定义WorkspaceIntegrationSerializer，同样继承自BaseSerializer。
class WorkspaceIntegrationSerializer(BaseSerializer):
    # 在WorkspaceIntegrationSerializer内部定义一个字段来表示关联的Integration实例详情，
    # 使用IntegrationSerializer来序列化该关联对象。
    integration_detail = IntegrationSerializer(read_only=True, source="integration")

    class Meta:
        model = WorkspaceIntegration  # 指定此序列化器关联的Django模型为WorkspaceIntegration。
        fields = "__all__"  # 同样指定序列化/反序列化所有字段。

# 转换为JSON格式