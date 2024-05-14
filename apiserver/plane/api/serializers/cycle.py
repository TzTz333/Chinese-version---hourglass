# 第三方导入
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from .user import UserLiteSerializer
from .issue import IssueStateSerializer
from .workspace import WorkspaceLiteSerializer
from .project import ProjectLiteSerializer
from plane.db.models import Cycle, CycleIssue, CycleFavorite

# 周期序列化器
class CycleSerializer(BaseSerializer):
    # 使用UserLiteSerializer序列化所有者信息，只读。
    owned_by = UserLiteSerializer(read_only=True)
    # 标识当前用户是否已将此周期标为收藏，只读。
    is_favorite = serializers.BooleanField(read_only=True)
    # 关于周期内的问题统计字段，包括总数、已取消、已完成等，均为只读。
    total_issues = serializers.IntegerField(read_only=True)
    cancelled_issues = serializers.IntegerField(read_only=True)
    completed_issues = serializers.IntegerField(read_only=True)
    started_issues = serializers.IntegerField(read_only=True)
    unstarted_issues = serializers.IntegerField(read_only=True)
    backlog_issues = serializers.IntegerField(read_only=True)

    # 使用WorkspaceLiteSerializer和ProjectLiteSerializer分别序列化工作空间和项目详情，只读。
    workspace_detail = WorkspaceLiteSerializer(read_only=True, source="workspace")
    project_detail = ProjectLiteSerializer(read_only=True, source="project")

    class Meta:
        model = Cycle  # 指定DRF模型为Cycle
        fields = "__all__"  # 包含所有模型字段
        read_only_fields = [
            "workspace",  # 工作空间字段只读
            "project",  # 项目字段只读
            "owned_by",  # 所有者字段只读
        ]


# 周期问题序列化器
class CycleIssueSerializer(BaseSerializer):
    # 使用IssueStateSerializer序列化关联到的问题详情，只读，并通过source指定源字段为"issue"。
    issue_detail = IssueStateSerializer(read_only=True, source="issue")
    # 子问题数量字段，只读。
    sub_issues_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CycleIssue  # 指定DRF模型为CycleIssue
        fields = "__all__"  # 包含所有模型字段
        read_only_fields = [
            "workspace",  # 工作空间字段只读
            "project",  # 项目字段只读
            "cycle",  # 所属周期字段只读
        ]


# 周期收藏序列化器
class CycleFavoriteSerializer(BaseSerializer):
    # 使用CycleSerializer序列化被收藏的周期详情，只读，并通过source指定源字段为"cycle"。
    cycle_detail = CycleSerializer(source="cycle", read_only=True)

    class Meta:
        model = CycleFavorite  # 指定DRF模型为CycleFavorite
        fields = "__all__"  # 包含所有模型字段
        read_only_fields = [
            "workspace",  # 工作空间字段只读
            "project",   # 项目字段只读
            "user",      # 用户字段只读，表示收藏的用户身份
        ]

