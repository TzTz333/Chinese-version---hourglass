'''
Importer模型用于表示一个导入操作，它包含了导入服务的类型（如GitHub或Jira），
导入的当前状态，发起导入的用户，以及一些元数据、配置和数据等信息。
其中，元数据、配置和数据字段都是JSON类型，可以存储结构化的数据。
每个导入操作都有一个关联的API令牌，用于进行身份验证。
'''
from django.db import models  # 导入Django的模型类
from django.conf import settings  # 导入Django的设置模块


from . import ProjectBaseModel  # 从当前目录导入ProjectBaseModel类


# 定义Importer类，它继承自ProjectBaseModel
class Importer(ProjectBaseModel):
    # 定义服务字段，为字符串类型，最大长度为50，可选值为'github'或'jira'
    service = models.CharField(
        max_length=50,
        choices=(
            ("github", "GitHub"),
            ("jira", "Jira"),
        ),
    )
    # 定义状态字段，为字符串类型，最大长度为50，
    # 可选值为'queued'，'processing'，'completed'，'failed'，默认值为'queued'
    status = models.CharField(
        max_length=50,
        choices=(
            ("queued", "Queued"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ),
        default="queued",
    )
    # 定义发起人字段，为外键类型，关联到用户模型，当用户被删除时，这个字段也会被删除
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="imports"
    )
    # 定义元数据字段，为JSON类型，默认值为字典
    metadata = models.JSONField(default=dict)
    # 定义配置字段，为JSON类型，默认值为字典
    config = models.JSONField(default=dict)
    # 定义数据字段，为JSON类型，默认值为字典
    data = models.JSONField(default=dict)
    # 定义令牌字段，为外键类型，关联到APIToken模型，当APIToken被删除时，这个字段也会被删除
    token = models.ForeignKey(
        "db.APIToken", on_delete=models.CASCADE, related_name="importer"
    )

    # 内部Meta类用于定义模型的一些额外信息
    class Meta:
        verbose_name = "Importer"  # 单数形式的名称
        verbose_name_plural = "Importers"  # 复数形式的名称
        db_table = "importers"  # 数据库中的表名
        ordering = ("-created_at",)  # 默认排序字段

    # __str__方法返回对象的字符串表示
    def __str__(self):
        """Return name of the service"""
        return f"{self.service} <{self.project.name}>"