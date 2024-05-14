# 导入基础序列化器，用作所有自定义序列化器的基类
from .base import BaseSerializer
# 导入工作区和项目的轻量级（Lite）序列化器，用于在State序列化器中提供关联信息
from .workspace import WorkspaceLiteSerializer
from .project import ProjectLiteSerializer

# 导入State模型，表示状态信息，如任务或项目的不同阶段状态
from plane.db.models import State


# 定义State序列化器，用于详细展示状态信息，并包含相关的工作区和项目信息
class StateSerializer(BaseSerializer):
    # 使用WorkspaceLiteSerializer序列化关联的工作区对象，仅用于读取
    workspace_detail = WorkspaceLiteSerializer(read_only=True, source="workspace")
    # 使用ProjectLiteSerializer序列化关联的项目对象，仅用于读取
    project_detail = ProjectLiteSerializer(read_only=True, source="project")

    class Meta:
        model = State  # 指定这个序列化器是为State模型设计的
        fields = "__all__"  # 表示包括模型中定义的所有字段
        read_only_fields = [
            "workspace",  # 将workspace字段设置为只读，因为状态一旦创建就固定关联到一个特定工作区
            "project",  # 将project字段设置为只读，因为状态一旦创建就固定关联到一个特定项目
        ]
        # 这里read_only_fields确保了上述字段在API操作中不会被意外修改


# 定义StateLiteSerializer，是一个轻量级版本的State序列化器，
# 用于提供状态的简要信息，不包含关联的工作区和项目详情
class StateLiteSerializer(BaseSerializer):
    class Meta:
        model = State  # 指定这个序列化器是为State模型设计的
        fields = [
            "id",  # 状态ID，唯一标识一个状态
            "name",  # 状态名称，如“待处理”，“进行中”等
            "color",  # 状态显示颜色，有助于在界面上直观地区分不同状态
            "group",  # 状态分组，有助于将相似的状态归类管理
        ]
        read_only_fields = fields  # 设置所有字段为只读，确保它们不会通过API被修改

