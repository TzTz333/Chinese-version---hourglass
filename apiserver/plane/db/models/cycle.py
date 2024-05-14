# Django imports
from django.db import models  # 导入Django的模型类
from django.conf import settings  # 导入Django的设置模块

# Module imports
from . import ProjectBaseModel  # 从当前目录导入ProjectBaseModel类


# 定义Cycle类，它继承自ProjectBaseModel
class Cycle(ProjectBaseModel):
    # 定义名称字段，最大长度255，带有一个人类可读的名称
    name = models.CharField(max_length=255, verbose_name="Cycle Name")
    # 定义描述字段，可以为空
    description = models.TextField(verbose_name="Cycle Description", blank=True)
    # 定义开始日期字段，可以为空或为空值
    start_date = models.DateField(verbose_name="Start Date", blank=True, null=True)
    # 定义结束日期字段，可以为空或为空值
    end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    # 定义外键，关联到用户模型，当用户被删除时，这个字段也会被删除
    owned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_by_cycle",
    )

    # 内部Meta类用于定义模型的一些额外信息
    class Meta:
        verbose_name = "Cycle"  # 单数形式的名称
        verbose_name_plural = "Cycles"  # 复数形式的名称
        db_table = "cycles"  # 数据库中的表名
        ordering = ("-created_at",)  # 默认排序字段

    # __str__方法返回对象的字符串表示
    def __str__(self):
        return f"{self.name} <{self.project.name}>"


# 定义CycleIssue类，它继承自ProjectBaseModel
class CycleIssue(ProjectBaseModel):

    # 定义一对一字段，关联到Issue模型，当Issue被删除时，这个字段也会被删除
    issue = models.OneToOneField(
        "db.Issue", on_delete=models.CASCADE, related_name="issue_cycle"
    )
    # 定义外键，关联到Cycle模型，当Cycle被删除时，这个字段也会被删除
    cycle = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, related_name="issue_cycle"
    )

    # 内部Meta类用于定义模型的一些额外信息
    class Meta:
        verbose_name = "Cycle Issue"  # 单数形式的名称
        verbose_name_plural = "Cycle Issues"  # 复数形式的名称
        db_table = "cycle_issues"  # 数据库中的表名
        ordering = ("-created_at",)  # 默认排序字段

    # __str__方法返回对象的字符串表示
    def __str__(self):
        return f"{self.cycle}"


# 定义CycleFavorite类，它继承自ProjectBaseModel
class CycleFavorite(ProjectBaseModel):

    # 定义外键，关联到用户模型，当用户被删除时，这个字段也会被删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cycle_favorites",
    )
    # 定义外键，关联到Cycle模型，当Cycle被删除时，这个字段也会被删除
    cycle = models.ForeignKey(
        "db.Cycle", on_delete=models.CASCADE, related_name="cycle_favorites"
    )

    # 内部Meta类用于定义模型的一些额外信息
    class Meta:
        unique_together = ["cycle", "user"]  # 设置cycle和user的组合是唯一的
        verbose_name = "Cycle Favorite"  # 单数形式的名称
        verbose_name_plural = "Cycle Favorites"  # 复数形式的名称
        db_table = "cycle_favorites"  # 数据库中的表名
        ordering = ("-created_at",)  # 默认排序字段

    # __str__方法返回对象的字符串表示
    def __str__(self):
        """Return user and the cycle"""
        return f"{self.user.email} <{self.cycle.name}>"
