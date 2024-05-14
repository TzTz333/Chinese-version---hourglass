# 引入第三方库：Django REST Framework 中的序列化器模块
from rest_framework import serializers

# 引入项目内定义的其他序列化器以及基础序列化器
from .base import BaseSerializer  # 基础序列化器，可能包含通用配置或方法
from .user import UserLiteSerializer  # 用户简要信息序列化器
from .state import StateSerializer, StateLiteSerializer  # 状态信息及其简要版本的序列化器
from .project import ProjectSerializer, ProjectLiteSerializer  # 项目信息及其简要版本的序列化器
from .workspace import WorkspaceLiteSerializer  # 工作区简要信息序列化器

# 引入数据库模型，这些模型是Django ORM用来表示数据库表的Python类
from plane.db.models import (
    User,
    Issue,
    IssueActivity,
    IssueComment,
    TimelineIssue,
    IssueProperty,
    IssueBlocker,
    IssueAssignee,
    IssueLabel,
    Label,
    IssueBlocker,
    CycleIssue,
    Cycle,
    Module,
    ModuleIssue,
    IssueLink,
)


class IssueFlatSerializer(BaseSerializer):
    
    # 问题平铺式序列化器：
    # 仅包含问题对象的扁平字段，适用于需要快速查看问题概览时使用。
    
    class Meta:
        model = Issue  # 指定对应的数据库模型为Issue
        fields = [  # 指定需要序列化/反序列化的字段
            "id",
            "name",
            "description",
            "priority",
            "start_date",
            "target_date",
            "sequence_id",
            "sort_order",
        ]


#     创建问题时使用的序列化器：
#     在创建问题记录时，处理与其他对象（如用户、状态、项目等）之间复杂关联关系，
#     包括但不限于读取某些关联对象详情和处理写入多对多字段。
#     此处自定义了create方法来处理复杂逻辑，例如批量创建关联对象。
class IssueCreateSerializer(BaseSerializer):
    state_detail = StateSerializer(read_only=True, source="state")  # 状态详情，只读
    created_by_detail = UserLiteSerializer(read_only=True, source="created_by")  
    project_detail = ProjectLiteSerializer(read_only=True, source="project")  # 项目详情，只读
    workspace_detail = WorkspaceLiteSerializer(read_only=True, source="workspace")  # 工作区详情，只读
     
    # 处理多对多字段；assignees_list、blockers_list、labels_list、blocks_list均为写入时使用的字段
    assignees_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,
    )

    # List of issues that are blocking this issue
    blockers_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all()),
        write_only=True,
        required=False,
    )
    labels_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Label.objects.all()),
        write_only=True,
        required=False,
    )

    # List of issues that are blocked by this issue
    blocks_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all()),
        write_only=True,
        required=False,
    )

    class Meta:
         model = Issue
         fields = "__all__"  # 序列化所有字段
         read_only_fields = [  # 指定哪些字段是只读的，不应在创建或更新时被修改
             "workspace",
             "project",
             "created_by",
             "updated_by",
             "created_at",
             "updated_at",
         ]

# 自定义创建方法。从validated_data中提取相关联对象列表，
# 分别处理并创建相关联对象实例。
        
# :param validated_data: 经过验证的数据字典。
# :return: 新创建的Issue对象实例。

    def create(self, validated_data):
    # 从传入的数据中移除关于blockers、assignees、labels和blocks的列表，
    # 如果这些键不存在，则返回None。
        blockers = validated_data.pop("blockers_list", None)
        assignees = validated_data.pop("assignees_list", None)
        labels = validated_data.pop("labels_list", None)
        blocks = validated_data.pop("blocks_list", None)

        # 从序列化器上下文中获取当前项目对象，这通常在视图层设置传递给序列化器。
        project = self.context["project"]
        
        # 使用剩余的validated_data（已经移除了列表字段）和项目信息创建新的Issue对象。
        issue = Issue.objects.create(**validated_data, project=project)

        # 如果blockers列表不为空，则为每个blocker创建一个IssueBlocker对象，
        # 并设置其与当前问题(issue)的关联以及其他必要信息，并批量创建这些记录。
        if blockers is not None:
            IssueBlocker.objects.bulk_create(
                [
                    IssueBlocker(
                        block=issue,  # 当前问题
                        blocked_by=blocker,  # 阻碍当前问题解决的其他问题
                        project=project,
                        workspace=project.workspace,  # 从项目获取工作区信息
                        created_by=issue.created_by,
                        updated_by=issue.updated_by,
                    )
                    for blocker in blockers
                ],
                batch_size=10,  # 指定每次数据库操作批量处理的记录数量
            )

        # 类似地处理assignees，为每个分配的用户创建IssueAssignee记录。
        if assignees is not None:
            IssueAssignee.objects.bulk_create(
                [
                    IssueAssignee(
                        assignee=user,
                        issue=issue,
                        project=project,
                        workspace=project.workspace,
                        created_by=issue.created_by,
                        updated_by=issue.updated_by,
                    )
                    for user in assignees
                ],
                batch_size=10,
            )

        # 处理labels，为当前问题(issue)添加指定标签。
        if labels is not None:
            IssueLabel.objects.bulk_create(
                [
                    IssueLabel(
                        label=label,
                        issue=issue,
                        project=project,
                        workspace=project.workspace,
                        created_by=issue.created_by,
                        updated_by=issue.updated_by,
                    )
                    for label in labels
                ],
                batch_size=10,
            )

        # 处理blocks，即当前问题阻碍解决的其他问题。
        if blocks is not None:
            IssueBlocker.objects.bulk_create(
                [
                    IssueBlocker(
                        block=block,  # 被当前问题阻碍解决的其他问题
                        blocked_by=issue,  # 当前问题作为阻碍者
                        project=project,
                        workspace=project.workspace,
                        created_by=issue.created_by,
                        updated_by=issue.updated_by,
                    )
                    for block in blocks
                ],
                batch_size=10,
            )

        # 创建完毕后返回新创建的Issue对象实例。
        return issue


    def update(self, instance, validated_data):
        # 从传入的数据中移除关于blockers、assignees、labels和blocks的列表，
        # 如果这些键不存在，则返回None。
        blockers = validated_data.pop("blockers_list", None)
        assignees = validated_data.pop("assignees_list", None)
        labels = validated_data.pop("labels_list", None)
        blocks = validated_data.pop("blocks_list", None)

        # 如果存在blockers列表，则首先删除所有当前问题(instance)作为阻塞对象的旧记录，
        # 然后根据新列表创建新的IssueBlocker记录。
        if blockers is not None:
            IssueBlocker.objects.filter(block=instance).delete()  # 删除旧记录
            IssueBlocker.objects.bulk_create(
                [
                    IssueBlocker(
                        block=instance,  # 当前问题
                        blocked_by=blocker,  # 阻碍当前问题解决的其他问题
                        project=instance.project,
                        workspace=instance.project.workspace,  # 从项目获取工作区信息
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for blocker in blockers
                ],
                batch_size=10,  # 指定每次数据库操作批量处理的记录数量
            )

        # 类似地，如果存在assignees列表，则更新当前问题(instance)的分配用户（assignees）。
        if assignees is not None:
            IssueAssignee.objects.filter(issue=instance).delete()  # 删除旧记录
            IssueAssignee.objects.bulk_create(
                [
                    IssueAssignee(
                        assignee=user,
                        issue=instance,
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for user in assignees
                ],
                batch_size=10,
            )

        # 如果存在labels列表，则更新当前问题(instance)关联的标签（labels）。
        if labels is not None:
            IssueLabel.objects.filter(issue=instance).delete()  # 删除旧记录
            IssueLabel.objects.bulk_create(
                [
                    IssueLabel(
                        label=label,
                        issue=instance,
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for label in labels
                ],
                batch_size=10,
            )

        # 如果存在blocks列表，则更新由当前问题(instance)阻碍解决的其他问题（blocks）。
        if blocks is not None:
            IssueBlocker.objects.filter(blocked_by=instance).delete()  # 删除旧记录
            IssueBlocker.objects.bulk_create(
                [
                    IssueBlocker(
                        block=block,  # 被当前问题阻碍解决的其他问题
                        blocked_by=instance,  # 当前问题作为阻碍者
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for block in blocks
                ],
                batch_size=10,
            )

        # 调用父类的update方法来处理validated_data中剩余的字段，
        # 并返回更新后的实例。
        return super().update(instance, validated_data)


# 问题活动序列化器
class IssueActivitySerializer(BaseSerializer):
    # 执行者的简要信息，只读
    actor_detail = UserLiteSerializer(read_only=True, source="actor")
    # 工作区的简要信息，只读
    workspace_detail = WorkspaceLiteSerializer(read_only=True, source="workspace")

    class Meta:
        model = IssueActivity  # 指定序列化器对应的模型
        fields = "__all__"  # 指定序列化所有字段


# 问题评论序列化器
class IssueCommentSerializer(BaseSerializer):
    # 评论者的简要信息，只读
    actor_detail = UserLiteSerializer(read_only=True, source="actor")
    # 相关联的问题的简要信息，只读
    issue_detail = IssueFlatSerializer(read_only=True, source="issue")
    # 相关联的项目的详细信息，只读
    project_detail = ProjectSerializer(read_only=True, source="project")

    class Meta:
        model = IssueComment  # 指定序列化器对应的模型
        fields = "__all__"  # 指定序列化所有字段
        read_only_fields = [  # 指定哪些字段是只读的
            "workspace",
            "project",
            "issue",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# 时间线问题序列化器
class TimeLineIssueSerializer(BaseSerializer):
    
    class Meta:
        model = TimelineIssue  # 指定序列化器对应的模型
        fields = "__all__"  # 指定序列化所有字段
        read_only_fields = [  # 指定哪些字段是只读的
            "workspace",
            "project",
            "issue",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# 问题属性序列化器
class IssuePropertySerializer(BaseSerializer):

    class Meta:
        model = IssueProperty  # 指定序列化器对应的模型
        fields = "__all__"  # 指定序列化所有字段
        read_only_fields = [  # 指定哪些字段是只读的
            "user", 
            "workspace", 
            "project",
        ]


# 标签信息完整版序列化器
class LabelSerializer(BaseSerializer):

    class Meta:
        model = Label  # 指定序列化器对应的模型
        fields = "__all__"   # 指定序列化所有字段 
        read_only_fields = [  # 指定哪些字段是只读的
            "workspace", 
            "project", 
        ]


# 标签信息精简版序列化器（主要用于列表展示）
class LabelLiteSerializer(BaseSerializer):

    class Meta:
        model = Label   # 指定序列化器对应的模型 
        fields = [      # 定义要展示或操作的字段列表
            "id",       # 标签ID（唯一标识符）
            "name",     # 标签名称 
            "color",    # 标签颜色（通常用于前端显示）
        ]

class IssueLabelSerializer(BaseSerializer):
    # 已被注释掉的部分表示这个序列化器原本可能想要包含标签的详细信息
    # label_details = LabelSerializer(read_only=True, source="label")

    class Meta:
        model = IssueLabel  # 指定模型为IssueLabel
        fields = "__all__"  # 表示序列化所有字段
        read_only_fields = [
            "workspace",  # workspace字段为只读
            "project",  # project字段为只读
        ]


class BlockedIssueSerializer(BaseSerializer):
    blocked_issue_detail = IssueFlatSerializer(source="block", read_only=True)  # 获取被阻塞问题的详情

    class Meta:
        model = IssueBlocker  # 指定模型为IssueBlocker
        fields = "__all__"  # 表示序列化所有字段


class BlockerIssueSerializer(BaseSerializer):
    blocker_issue_detail = IssueFlatSerializer(source="blocked_by", read_only=True)  # 获取阻塞者问题的详情

    class Meta:
        model = IssueBlocker  # 指定模型为IssueBlocker
        fields = "__all__"  # 表示序列化所有字段


class IssueAssigneeSerializer(BaseSerializer):
    # 指派人详情，只读
    assignee_details = UserLiteSerializer(read_only=True, source="assignee")

    class Meta:
        model = IssueAssignee  # 指定模型为IssueAssignee
        fields = "__all__"  # 序列化所有字段


class CycleBaseSerializer(BaseSerializer):
    class Meta:
        model = Cycle  # 指定模型为Cycle
        fields = "__all__"  # 序列化所有字段
        read_only_fields = [
            "workspace",  # 工作区字段，只读
            "project",  # 项目字段，只读
            "created_by",  # 创建者字段，只读
            "updated_by",  # 更新者字段，只读
            "created_at",  # 创建时间，只读
            "updated_at",  # 更新时间，只读
        ]


class IssueCycleDetailSerializer(BaseSerializer):
    cycle_detail = CycleBaseSerializer(read_only=True, source="cycle")  # 周期详情，从关联的周期实体获取

    class Meta:
        model = CycleIssue  # 指定模型为CycleIssue
        fields = "__all__"  # 序列化所有字段
        read_only_fields = [
            "workspace",  # 工作区字段，只读
            "project",  # 项目字段，只读
            "created_by",  # 创建者字段，只读
            "updated_by",  # 更新者字段，只读
            "created_at",  # 创建时间，只读
            "updated_at",  # 更新时间，只读
        ]


# 模块基础信息序列化器
class ModuleBaseSerializer(BaseSerializer):
    class Meta:
        model = Module
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

# 问题与模块关系详情序列化器
class IssueModuleDetailSerializer(BaseSerializer):
    module_detail = ModuleBaseSerializer(read_only=True, source="module")

    class Meta:
        model = ModuleIssue
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

# 问题链接序列化器
class IssueLinkSerializer(BaseSerializer):
    created_by_detail = UserLiteSerializer(read_only=True, source="created_by")

    class Meta:
        model = IssueLink
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "issue",
        ]

    def create(self, validated_data):
        # 验证传入的URL是否已经存在于同一问题(issue_id)下。
        if IssueLink.objects.filter(
            url=validated_data.get("url"), issue_id=validated_data.get("issue_id")
        ).exists():
            # 如果已存在，则抛出验证错误，提示URL已经存在于该问题下。
            raise serializers.ValidationError(
                {"error": "URL already exists for this Issue"}
            )
        # 如果验证通过，则使用传入的验证过的数据创建并返回一个新的IssueLink实例。
        return IssueLink.objects.create(**validated_data)


class IssueStateSerializer(BaseSerializer):
    # 使用StateSerializer来只读展示状态详情。
    state_detail = StateSerializer(read_only=True, source="state")
    # 使用ProjectSerializer来只读展示项目详情。
    project_detail = ProjectSerializer(read_only=True, source="project")
    # 使用LabelSerializer来只读展示标签详情，因为可能有多个标签，故设置many=True。
    label_details = LabelSerializer(read_only=True, source="labels", many=True)
    # 使用UserLiteSerializer来只读展示指派给该问题的所有用户详情，设置many=True以处理多对多关系。
    assignee_details = UserLiteSerializer(read_only=True, source="assignees", many=True)
    # 以整数形式只读展示子问题数量。
    sub_issues_count = serializers.IntegerField(read_only=True)
    # 以UUID字段形式只读展示桥接ID（如果有）。
    bridge_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Issue  # 指定对应的数据库模型为Issue
        fields = "__all__"  # 序列化模型的所有字段



class IssueSerializer(BaseSerializer):
    # 项目详情，只读
    project_detail = ProjectSerializer(read_only=True, source="project")
    # 状态详情，只读
    state_detail = StateSerializer(read_only=True, source="state")
    # 父问题详情，只读
    parent_detail = IssueFlatSerializer(read_only=True, source="parent")
    # 标签详情列表，只读
    label_details = LabelSerializer(read_only=True, source="labels", many=True)
    # 指派人员详情列表，只读
    assignee_details = UserLiteSerializer(read_only=True, source="assignees", many=True)
    # 被此问题阻塞的问题列表，只读
    blocked_issues = BlockedIssueSerializer(read_only=True, many=True)
    # 阻塞此问题的问题列表，只读
    blocker_issues = BlockerIssueSerializer(read_only=True, many=True)
    # 与此问题相关联的开发周期详情，只读
    issue_cycle = IssueCycleDetailSerializer(read_only=True)
    # 与此问题相关联的模块详情，只读
    issue_module = IssueModuleDetailSerializer(read_only=True)
    # 与此问题相关联的链接列表，只读
    issue_link = IssueLinkSerializer(read_only=True, many=True)
    # 子问题计数，整型字段，只读
    sub_issues_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Issue  # 指定对应的数据库模型为Issue
        fields = "__all__"  # 序列化模型的所有字段
        read_only_fields = [  # 指定以下字段为只读字段
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

class IssueLiteSerializer(BaseSerializer):
    # 工作区详情，只读
    workspace_detail = WorkspaceLiteSerializer(read_only=True, source="workspace")
    # 项目简要信息，只读
    project_detail = ProjectLiteSerializer(read_only=True, source="project")
    # 状态简要信息，只读
    state_detail = StateLiteSerializer(read_only=True, source="state")
    # 标签简要信息列表，只读
    label_details = LabelLiteSerializer(read_only=True, source="labels", many=True)
    # 指派人员简要信息列表，只读
    assignee_details = UserLiteSerializer(read_only=True, source="assignees", many=True)
    # 子问题计数，整型字段，只读
    sub_issues_count = serializers.IntegerField(read_only=True)
    
     # 开发周期ID和模块ID为UUID字段，仅提供ID而不展开详细信息以减少数据量和提高性能。
    cycle_id = serializers.UUIDField(read_only=True) 
    module_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Issue  # 指定对应的数据库模型为Issue
        fields = "__all__"  # 序列化模型的所有字段 
        read_only_fields = [   # 指定以下字段为只读字段 
            "start_date",
            "target_date",
            "completed_at",
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
         ]
