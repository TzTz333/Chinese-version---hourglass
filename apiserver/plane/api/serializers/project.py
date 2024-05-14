# Django imports
from django.db import IntegrityError

# Third party imports
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from plane.api.serializers.workspace import WorkSpaceSerializer, WorkspaceLiteSerializer
from plane.api.serializers.user import UserLiteSerializer
from plane.db.models import (
    Project,
    ProjectMember,
    ProjectMemberInvite,
    ProjectIdentifier,
    ProjectFavorite,
)


class ProjectSerializer(BaseSerializer):
    # 定义工作区详情字段，只读，使用WorkspaceLiteSerializer进行序列化
    workspace_detail = WorkspaceLiteSerializer(source="workspace", read_only=True)

    class Meta:
        model = Project  # 指定序列化的模型是Project
        fields = "__all__"  # 序列化所有字段
        read_only_fields = [
            "workspace",  # 将workspace字段设置为只读，不允许通过API直接修改
        ]

    def create(self, validated_data):
        # 提取并处理传入的项目标识符，去除空格并转换为大写
        identifier = validated_data.get("identifier", "").strip().upper()
        
        # 校验项目标识符是否为空，如果为空则抛出验证错误
        if identifier == "":
            raise serializers.ValidationError(detail="Project Identifier is required")

        # 校验项目标识符在当前工作区内是否唯一，如果不唯一则抛出验证错误
        if ProjectIdentifier.objects.filter(
            name=identifier, workspace_id=self.context["workspace_id"]
        ).exists():
            raise serializers.ValidationError(detail="Project Identifier is taken")
        
        # 创建新的项目实例，并关联到当前工作区
        project = Project.objects.create(
            **validated_data, workspace_id=self.context["workspace_id"]
        )
        
        # 为新创建的项目生成一个项目标识符实例
        _ = ProjectIdentifier.objects.create(
            name=project.identifier,
            project=project,
            workspace_id=self.context["workspace_id"],
        )
        
        return project

    def update(self, instance, validated_data):
        identifier = validated_data.get("identifier", "").strip().upper()

        # 如果没有提供新的项目标识符，则直接更新其它字段信息
        if identifier == "":
            project = super().update(instance, validated_data)
            return project

        # 尝试查找匹配的项目标识符实例；如果未找到，则创建新的标识符
        project_identifier = ProjectIdentifier.objects.filter(
            name=identifier, workspace_id=instance.workspace_id
        ).first()
        
        if project_identifier is None:
            project = super().update(instance, validated_data)
            
            project_identifier = ProjectIdentifier.objects.filter(
                project=project
            ).first()
            
            if project_identifier is not None:
                project_identifier.name = identifier
                project_identifier.save()
                
            return project

        # 如果找到了匹配的项目标识符实例且与当前更新的项目ID相同，则正常更新；
        # 否则，说明有另外一个不同的项目已经使用了此标识符，因此抛出验证错误。
        if project_identifier.project_id == instance.id:
            project = super().update(instance, validated_data)
            return project

        raise serializers.ValidationError(detail="Project Identifier is already taken")

# 项目详情序列化器
class ProjectDetailSerializer(BaseSerializer):
    # 使用WorkSpaceSerializer展示所属的工作区信息，只读
    workspace = WorkSpaceSerializer(read_only=True)
    # 使用UserLiteSerializer展示默认指派人信息，只读
    default_assignee = UserLiteSerializer(read_only=True)
    # 使用UserLiteSerializer展示项目负责人信息，只读
    project_lead = UserLiteSerializer(read_only=True)
    # 布尔字段，表示当前用户是否收藏了该项目，只读
    is_favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = Project  # 指定序列化的模型为Project
        fields = "__all__"  # 包含模型中的所有字段


# 项目成员序列化器
class ProjectMemberSerializer(BaseSerializer):
    # 展示成员所属工作区的信息，使用WorkSpaceSerializer序列化，只读
    workspace = WorkSpaceSerializer(read_only=True)
    # 展示成员所属项目的信息，使用ProjectSerializer序列化，只读
    project = ProjectSerializer(read_only=True)
    # 展示成员的用户信息，使用UserLiteSerializer序列化，只读
    member = UserLiteSerializer(read_only=True)

    class Meta:
        model = ProjectMember  # 指定序列化的模型为ProjectMember
        fields = "__all__"  # 包含模型中的所有字段


# 项目成员邀请序列化器
class ProjectMemberInviteSerializer(BaseSerializer):
    # 展示被邀请加入的项目信息，使用ProjectSerializer序列化，只读
    project = ProjectSerializer(read_only=True)
    # 展示邀请所在工作区的信息，使用WorkSpaceSerializer序列化，只读
    workspace = WorkSpaceSerializer(read_only=True)

    class Meta:
        model = ProjectMemberInvite  # 指定序列化的模型为ProjectMemberInvite
        fields = "__all__"  # 包含模型中的所有字段


# 项目标识符序列化器
class ProjectIdentifierSerializer(BaseSerializer):
    class Meta:
        model = ProjectIdentifier  # 指定序列化的模型为ProjectIdentifier
        fields = "__all__"  # 包含模型中的所有字段


# 项目收藏序列化器
class ProjectFavoriteSerializer(BaseSerializer):
    # 使用ProjectSerializer展示收藏的项目详情，仅用于读取
    project_detail = ProjectSerializer(source="project", read_only=True)

    class Meta:
        model = ProjectFavorite  # 指定序列化的模型为ProjectFavorite
        fields = "__all__"  # 包含模型中的所有字段
        read_only_fields = [
            "workspace",  # 将工作区字段设为只读，因为它通过项目关系自动确定
            "user",  # 将用户字段设为只读，通常在创建时自动设置为当前用户
        ]
        # 这里，read_only_fields指定了不允许通过API直接修改的字段，确保数据一致性和安全性


# 精简项目信息序列化器
class ProjectLiteSerializer(BaseSerializer):
    class Meta:
        model = Project  # 指定序列化的模型为Project
        fields = ["id", "identifier", "name"]  # 仅包括id, identifier和name字段，用于提供简洁的项目信息
        read_only_fields = fields  # 将所有包含的字段都设为只读，这个序列化器通常用于列表显示等场合

