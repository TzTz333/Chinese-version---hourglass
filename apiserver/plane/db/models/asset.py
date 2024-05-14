# Python 标准库导入
from uuid import uuid4

# Django 导入
from django.db import models
from django.core.exceptions import ValidationError

# 本地模块导入
from . import BaseModel

# 定义文件上传路径函数
def get_upload_path(instance, filename):
    # 如果实例有 workspace_id，则使用 workspace ID 和唯一 UUID 构建文件路径
    if instance.workspace_id is not None:
        return f"{instance.workspace.id}/{uuid4().hex}-{filename}"
    # 如果实例没有 workspace_id，则使用用户相关的路径和 UUID
    return f"user-{uuid4().hex}-{filename}"

# 定义文件大小验证函数
def file_size(value):
    limit = 5 * 1024 * 1024  # 设置文件大小限制为 5MB
    if value.size > limit:
        raise ValidationError("上传文件不得超过5MB！")  # 如果超过限制，抛出验证错误

# 定义文件资产模型
class FileAsset(BaseModel):
    """
    文件资产模型。
    """

    # 文件的属性，使用 JSONField 存储，允许存入一个字典
    attributes = models.JSONField(default=dict)
    # 文件字段，用于上传文件，上传路径通过 get_upload_path 函数获取
    # 还包含了一个验证器，用于限制文件大小
    asset = models.FileField(
        upload_to=get_upload_path,
        validators=[
            file_size,
        ],
    )
    # 外键，关联到 Workspace 模型。当对应的 Workspace 被删除时，该文件资产也会被级联删除
    # related_name="assets" 允许通过 Workspace 实例直接访问其所有的文件资产
    workspace = models.ForeignKey(
        "db.Workspace", on_delete=models.CASCADE, null=True, related_name="assets"
    )

    # 元数据选项
    class Meta:
        verbose_name = "File Asset"  # 模型名
        verbose_name_plural = "File Assets"  # 复数模型名
        db_table = "file_assets"  # 数据库表名
        ordering = ("-created_at",)  # 默认排序方式，按创建时间降序

    # 定义对象的字符串表示方法，这里返回文件字段的字符串表示
    def __str__(self):
        return str(self.asset)