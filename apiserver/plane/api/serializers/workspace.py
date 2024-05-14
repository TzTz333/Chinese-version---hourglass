# 引入Django REST Framework的序列化器库
from rest_framework import serializers

# 引入自定义的基础序列化器，用于扩展通用功能
from .base import BaseSerializer
# 引入用户简要信息序列化器，用于展示用户相关信息
from .user import UserLiteSerializer

# 引入数据库模型：用户、工作区及其成员、团队及其成员和邀请
from plane.db.models import User, Workspace, WorkspaceMember, Team, TeamMember, WorkspaceMemberInvite


# 工作区详细信息序列化器
class WorkSpaceSerializer(BaseSerializer):
    # 展示工作区拥有者的简要信息
    owner = UserLiteSerializer(read_only=True)
    # 计算并展示工作区成员总数，只读字段
    total_members = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workspace  # 指定序列化器对应的数据库模型是Workspace
        fields = "__all__"  # 序列化所有字段，包括模型中定义的所有字段
        read_only_fields = [
            "id",  # 工作区ID自动生成，不允许修改
            "created_by",  # 创建者信息自动记录，不允许修改
            "updated_by",  # 更新者信息自动记录，不允许修改
            "created_at",  # 创建时间自动记录，不允许修改
            "updated_at",  # 更新时间自动记录，不允许修改
            "owner",  # 拥有者信息通过关联实现，不直接修改
        ]


# 工作区成员序列化器
class WorkSpaceMemberSerializer(BaseSerializer):
    member = UserLiteSerializer(read_only=True)  # 展示成员的简要信息，只读字段
    workspace = WorkSpaceSerializer(read_only=True)  # 展示所属工作区的详细信息，只读字段

    class Meta:
        model = WorkspaceMember  # 指定序列化器对应的数据库模型是WorkspaceMember
        fields = "__all__"  # 序列化所有字段


# 工作区成员邀请序列化器
class WorkSpaceMemberInviteSerializer(BaseSerializer):
    workspace = WorkSpaceSerializer(read_only=True)  # 展示被邀请加入的工作区详细信息

    class Meta:
        model = WorkspaceMemberInvite  # 指定序列化器对应的数据库模型是WorkspaceMemberInvite
        fields = "__all__"  # 序列化所有字段


# 定义团队序列化器，处理团队的创建、更新和展示逻辑
class TeamSerializer(BaseSerializer):
    # 展示团队成员的详细信息，只读，允许多个成员
    members_detail = UserLiteSerializer(read_only=True, source="members", many=True)
    # 用于创建或更新团队时指定成员，仅写入，不在序列化的输出中显示
    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,  # 不是必须的字段，在创建或更新团队时可以不提供成员信息
    )

    class Meta:
        model = Team  # 指定序列化器关联的模型是Team
        fields = "__all__"  # 包括模型定义的所有字段
        read_only_fields = [
            "workspace",  # 工作空间字段为只读，通常在创建团队时自动设置
            "created_by",  # 创建者字段为只读，自动记录谁创建了这个团队
            "updated_by",  # 更新者字段为只读，自动记录最后更新团队信息的用户
            "created_at",  # 创建时间为只读，自动记录团队被创建的时间
            "updated_at",  # 更新时间为只读，自动记录团队信息最后一次更新的时间
        ]

    def create(self, validated_data, **kwargs):
        # 在验证数据中检查是否提供了成员信息
        if "members" in validated_data:
            members = validated_data.pop("members")
            workspace = self.context["workspace"]  # 获取当前工作空间上下文
            team = Team.objects.create(**validated_data, workspace=workspace)  # 创建团队并指定工作空间
            
            team_members = [
                TeamMember(member=member, team=team, workspace=workspace)
                for member in members  # 对每个指定成员创建TeamMember实例
            ]
            
            TeamMember.objects.bulk_create(team_members, batch_size=10)  # 批量插入TeamMember实例以提高性能
            
            return team
        
        else:
            return Team.objects.create(**validated_data)  # 如果没有指定成员，则直接创建团队

    def update(self, instance, validated_data):
        if "members" in validated_data:
            members = validated_data.pop("members")
            
            TeamMember.objects.filter(team=instance).delete()  # 删除现有的团队成员关系
            
            team_members = [
                TeamMember(member=member, team=instance, workspace=instance.workspace)
                for member in members  # 对每个新指定成员创建TeamMember实例
            ]
            
            TeamMember.objects.bulk_create(team_members, batch_size=10)  # 批量插入新的TeamMember实例
            
            return super().update(instance, validated_data)  # 更新其它字段
        
        else:
            return super().update(instance, validated_data)  # 如果没有提供新的成员列表，则正常更新其它字段


# 定义一个轻量级工作空间序列化器，用于快速展示工作空间的基本信息
class WorkspaceLiteSerializer(BaseSerializer):
    class Meta:
        model = Workspace  # 指定序列化器关联的模型是Workspace
        fields = [
            "name",   # 工作空间名称
            "slug",   # 工作空间URL中使用的短标识符
            "id",     # 工作空间ID，系统自动生成且唯一标识一个工作空间
        ]
        read_only_fields = fields  # 所有这些字段都是只读的，不允许通过API修改

