# 第三方库导入
from rest_framework import serializers

# 同模块内的其他序列化器导入
from .base import BaseSerializer
from .user import UserLiteSerializer
from .project import ProjectSerializer, ProjectLiteSerializer
from .workspace import WorkspaceLiteSerializer
from .issue import IssueStateSerializer

# 数据模型导入
from plane.db.models import (
    User,
    Module,
    ModuleMember,
    ModuleIssue,
    ModuleLink,
    ModuleFavorite,
)

class ModuleWriteSerializer(BaseSerializer):
    # 定义成员列表字段，用于创建或更新模块时指定成员。该字段仅用于写操作。
    members_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),  # 指定查询集为所有用户
        write_only=True,  # 仅用于写操作
        required=False,  # 非必须字段
    )

    # 项目和工作区的简化信息，仅用于读取展示，不参与写操作
    project_detail = ProjectLiteSerializer(source="project", read_only=True)
    workspace_detail = WorkspaceLiteSerializer(source="workspace", read_only=True)

    class Meta:
        model = Module  # 指定数据模型为Module
        fields = "__all__"  # 包含所有模型字段
        read_only_fields = [  # 指定以下字段为只读，不参与写操作
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        # 创建模块时处理成员列表数据，并创建相关的ModuleMember对象
        members = validated_data.pop("members_list", None)  # 提取并移除成员列表数据

        project = self.context["project"]  # 获取上下文中的项目实例

        module = Module.objects.create(**validated_data, project=project)  # 创建模块实例

        if members is not None:
            ModuleMember.objects.bulk_create(  # 批量创建模块成员关系对象
                [
                    ModuleMember(
                        module=module,
                        member=member,
                        project=project,
                        workspace=project.workspace,
                        created_by=module.created_by,
                        updated_by=module.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,  # 批处理数量设置为10
                ignore_conflicts=True,  # 忽略冲突，避免重复创建时报错
            )

        return module

    def update(self, instance, validated_data):
        # 更新模块信息时同样处理成员列表数据，重新建立ModuleMember关系
        members = validated_data.pop("members_list", None)

        if members is not None: 
            ModuleMember.objects.filter(module=instance).delete()  # 删除旧的模块成员关系
            
            ModuleMember.objects.bulk_create(  # 基于新的成员列表重新建立关系
                [
                    ModuleMember(
                        module=instance,
                        member=member,
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,  
                ignore_conflicts=True, 
            )

        return super().update(instance, validated_data)  # 调用父类方法完成其他字段的更新


# ModuleFlatSerializer: 用于序列化模块信息的基础序列化器
class ModuleFlatSerializer(BaseSerializer):
    class Meta:
        model = Module  # 指定对应的Django模型
        fields = "__all__"  # 使用所有模型字段
        read_only_fields = [  # 指定以下字段为只读，不允许通过API修改
            "workspace",  # 工作区字段
            "project",  # 所属项目字段
            "created_by",  # 创建者字段
            "updated_by",  # 更新者字段
            "created_at",  # 创建时间字段
            "updated_at",  # 更新时间字段
        ]

# ModuleIssueSerializer: 序列化模块问题信息，包括问题详情和所关联的模块信息
class ModuleIssueSerializer(BaseSerializer):
    module_detail = ModuleFlatSerializer(read_only=True, source="module")  # 关联的模块详细信息，使用ModuleFlatSerializer序列化
    issue_detail = IssueStateSerializer(read_only=True, source="issue")  # 关联的问题状态详细信息，使用IssueStateSerializer序列化
    sub_issues_count = serializers.IntegerField(read_only=True)  # 子问题数量，只读

    class Meta:
        model = ModuleIssue  # 指定对应的Django模型
        fields = "__all__"  # 使用所有模型字段
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "module",  # 包含关联模块作为只读，避免通过API直接修改这些关系字段
        ]

# ModuleLinkSerializer: 序列化模块链接信息，并在创建时验证链接是否已存在于同一模块下
class ModuleLinkSerializer(BaseSerializer):
    created_by_detail = UserLiteSerializer(read_only=True, source="created_by")  # 创建者详细信息

    class Meta:
        model = ModuleLink  # 指定对应的Django模型
        fields = "__all__"  # 使用所有模型字段
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "module",   # 包含关联模块作为只读，避免通过API直接修改这些关系字段 
        ]

    def create(self, validated_data):
        if ModuleLink.objects.filter(
            url=validated_data.get("url"), module_id=validated_data.get("module_id")
        ).exists():  # 验证同一个模块下是否存在相同的URL链接
            raise serializers.ValidationError(
                {"error": "URL already exists for this Issue"}  # 如果存在，则抛出验证错误
            )
        return ModuleLink.objects.create(**validated_data)  # 如果验证通过，则创建ModuleLink实例

# ModuleSerializer: 序列化完整的模块信息，包括项目详情、负责人、成员列表和相关链接等信息
class ModuleSerializer(BaseSerializer):
    project_detail = ProjectSerializer(read_only=True, source="project")   # 关联项目详细信息
    lead_detail = UserLiteSerializer(read_only=True, source="lead")   # 负责人详细信息
    members_detail = UserLiteSerializer(read_only=True, many=True, source="members")   # 成员列表详细信息，可能有多个成员，因此设定many=True
    link_module = ModuleLinkSerializer(read_only=True, many=True)   # 相关链接列表
    
    is_favorite = serializers.BooleanField(read_only=True)   # 表示当前用户是否已收藏该模块，只读属性。
    total_issues = serializers.IntegerField(read_only=True)   # 总问题数统计，只读属性。
    cancelled_issues = serializers.IntegerField(read_only=True)   # 已取消问题数统计，只读属性。
    completed_issues = serializers.IntegerField(read_only=True)   # 已完成问题数统计，只读属性。
    started_issues = serializers.IntegerField(read_only=True)   # 已开始处理问题数统计，只读属性。
    unstarted_issues = serializers.IntegerField(read_only=True)   # 尚未开始处理问题数统计，只读属性。
    backlog_issues = serializers.IntegerField(read_only=True)   # 备忘录中问题数统计，只读属性。

    class Meta:
        model = Module 
        fields = "__all__"
        read_only_fields=[
            "workspace", 
            "project", 
            "created_by", 
            "updated_by", 
            "created_at", 
            "updated_at"
        ]

# ModuleFavoriteSerializer: 序列化用户收藏的模块信息。仅包含基本的关联模块详细信息。
class ModuleFavoriteSerializer(BaseSerializer):
    module_detail = ModuleFlatSerializer(source="module", read_only=True)

    class Meta: 
        model = ModuleFavorite 
        fields = "__all__" 
        read_only_fields = [
            "workspace", 
            "project", 
            "user", 
        ]
