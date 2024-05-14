# 引入第三方库：Django REST Framework的序列化器功能
from rest_framework import serializers

# 引入自定义的基础序列化器，为了继承其通用功能
from .base import BaseSerializer
# 引入其他模型的Lite版本序列化器，用于关联字段的展示
from .workspace import WorkspaceLiteSerializer
from .project import ProjectLiteSerializer

# 引入数据库模型：IssueView和IssueViewFavorite
from plane.db.models import IssueView, IssueViewFavorite
# 引入工具函数issue_filters，用于处理查询参数并生成查询条件
from plane.utils.issue_filters import issue_filters


# 定义IssueView对象的序列化器，负责将IssueView对象数据转换为JSON格式，以及将JSON格式数据转换回IssueView对象。
class IssueViewSerializer(BaseSerializer):
    # 定义只读字段is_favorite，标记当前用户是否收藏了该视图
    is_favorite = serializers.BooleanField(read_only=True)
    # 使用ProjectLiteSerializer展示所属项目的简略信息，只读
    project_detail = ProjectLiteSerializer(source="project", read_only=True)
    # 使用WorkspaceLiteSerializer展示所属工作区的简略信息，只读
    workspace_detail = WorkspaceLiteSerializer(source="workspace", read_only=True)

    class Meta:
        model = IssueView  # 指定序列化器对应的数据库模型是IssueView
        fields = "__all__"  # 序列化所有字段
        read_only_fields = [
            "workspace",  # 工作区字段为只读，因为视图所属工作区在创建后不应更改
            "project",  # 项目字段为只读，因为视图所属项目在创建后不应更改
            "query",  # 查询字段为只读，在创建和更新时通过特殊逻辑处理而非直接赋值
        ]

    def create(self, validated_data):
        # 处理新建视图时提交的查询参数（query_data）
        query_params = validated_data.get("query_data", {})
        if not bool(query_params):
            raise serializers.ValidationError({"query_data": ["Query data field cannot be empty"]})
        validated_data["query"] = issue_filters(query_params, "POST")  # 调用issue_filters函数生成查询字符串并保存至validated_data中
        return IssueView.objects.create(**validated_data)  # 创建IssueView实例并返回

    def update(self, instance, validated_data):
        # 处理更新视图时提交的查询参数（query_data）
        query_params = validated_data.get("query_data", {})
        if not bool(query_params):
            raise serializers.ValidationError({"query_data": ["Query data field cannot be empty"]})
        validated_data["query"] = issue_filters(query_params, "PATCH")  # 更新查询字符串并保存至validated_data中
        return super().update(instance, validated_data)  # 调用父类方法更新实例并返回


# 定义IssueViewFavorite对象的序列化器，主要用于处理用户收藏的问题视图数据。
class IssueViewFavoriteSerializer(BaseSerializer):
    # 使用IssueViewSerializer展示收藏的问题视图详情，只读，并指定source为"issue_view"以匹配模型字段名
    view_detail = IssueViewSerializer(source="issue_view", read_only=True)

    class Meta:
        model = IssueViewFavorite  # 指定序列化器对应的数据库模型是IssueViewFavorite
        fields = "__all__"  # 序列化所有字段
        read_only_fields = [
            "workspace",  # 工作区字段为只读，因为收藏项所属工作区在创建后不应更改
            "project",  # 项目字段为只读，因为收藏项所属项目在创建后不应更改
            "user",  # 用户字段为只读，因为收藏项所属用户在创建后不应更改
        ]
