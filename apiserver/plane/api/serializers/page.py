# 在创建或更新Page实例时会处理与之相关联的标签(Label)数据，
#并且能够通过批量创建PageLabel实例来建立页面与标签之间的多对多关系。
# 第三方库导入
from rest_framework import serializers

# 内部模块导入
from .base import BaseSerializer  # 基础序列化器，用作其他序列化器的基类
from .issue import IssueFlatSerializer, LabelSerializer  # 问题和标签的序列化器
from .workspace import WorkspaceLiteSerializer  # 工作区的简化序列化器
from .project import ProjectLiteSerializer  # 项目的简化序列化器
from plane.db.models import Page, PageBlock, PageFavorite, PageLabel, Label  # 数据库模型


# 页面块（PageBlock）的序列化器
class PageBlockSerializer(BaseSerializer):
    # 关联的问题详情，使用IssueFlatSerializer进行序列化，仅读取不写入
    issue_detail = IssueFlatSerializer(source="issue", read_only=True)
    # 所属项目详情，使用ProjectLiteSerializer进行序列化，仅读取不写入
    project_detail = ProjectLiteSerializer(source="project", read_only=True)
    # 所属工作区详情，使用WorkspaceLiteSerializer进行序列化，仅读取不写入
    workspace_detail = WorkspaceLiteSerializer(source="workspace", read_only=True)

    class Meta:
        model = PageBlock  # 指定对应的数据库模型为PageBlock
        fields = "__all__"  # 包含所有字段
        read_only_fields = [
            "workspace",  # 工作区字段只读
            "project",  # 项目字段只读
            "page",  # 页面字段只读
        ]


# 页面（Page）的序列化器
class PageSerializer(BaseSerializer):
    is_favorite = serializers.BooleanField(read_only=True)  # 标记页面是否被收藏，仅读取不写入
    label_details = LabelSerializer(read_only=True, source="labels", many=True)  # 关联的标签详情列表，使用LabelSerializer进行序列化，仅读取不写入
    labels_list = serializers.ListField(  
        child=serializers.PrimaryKeyRelatedField(queryset=Label.objects.all()),  
        write_only=True,  # 标签列表字段，用于写操作时指定关联标签的主键列表。该字段不会被直接存储，而是用来处理页面与标签之间的关系。
        required=False,  
    )
    blocks = PageBlockSerializer(read_only=True, many=True)  # 页面包含的块元素列表，使用PageBlockSerializer进行序列化，仅读取不写入
    project_detail = ProjectLiteSerializer(source="project", read_only=True)  # 所属项目详情，仅读取不写入
    workspace_detail = WorkspaceLiteSerializer(source="workspace", read_only=True)  # 所属工作区详情，仅读取不写入

    class Meta:
        model = Page  # 指定对应的数据库模型为Page
        fields = "__all__"  # 包含所有字段
        read_only_fields = [
            "workspace", 
            "project",
            "owned_by",   # 页面拥有者字段只读，不能通过API直接修改拥有者信息。
        ]

    def create(self, validated_data):
        labels = validated_data.pop("labels_list", None)  
        project_id = self.context["project_id"]  
        owned_by_id = self.context["owned_by_id"]  
        
        page = Page.objects.create(
            **validated_data, project_id=project_id, owned_by_id=owned_by_id  
        )

        if labels is not None:
            PageLabel.objects.bulk_create( 
                [
                    PageLabel(
                        label=label,
                        page=page,
                        project_id=project_id,
                        workspace_id=page.workspace_id,
                        created_by_id=page.created_by_id,
                        updated_by_id=page.updated_by_id,
                    )
                    for label in labels 
                ],
                batch_size=10,  
            )
        return page  

    def update(self, instance, validated_data):
        labels = validated_data.pop("labels_list", None) 
         
        if labels is not None:
            PageLabel.objects.filter(page=instance).delete()  
            PageLabel.objects.bulk_create(  
                [
                    PageLabel(
                        label=label,
                        page=instance,
                        project_id=instance.project_id,
                        workspace_id=instance.workspace_id,
                        created_by_id=instance.created_by_id,
                        updated_by_id=instance.updated_by_id,
                    )
                    for label in labels 
                ],
                batch_size=10, 
            )

        return super().update(instance, validated_data)  


# 页面收藏（PageFavorite）的序列化器
class PageFavoriteSerializer(BaseSerializer):
    page_detail = PageSerializer(source="page", read_only=True)  

    class Meta:
        model = PageFavorite  
        fields = "__all__" 
        read_only_fields = [
            "workspace",
            "project",
            "user",
        ]
