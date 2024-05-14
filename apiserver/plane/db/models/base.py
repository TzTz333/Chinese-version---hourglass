# 在保存时更新创建者和更新者信息
import uuid  # 导入uuid模块


from django.db import models  # 导入Django的模型


from crum import get_current_user  # 从第三方库crum中导入获取当前用户的方法


from ..mixins import AuditModel  # 从当前模块的上一层导入AuditModel

# 定义BaseModel类，继承自AuditModel
class BaseModel(AuditModel):
    # 定义id字段，类型为UUID，作为主键
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )

    # Django的内部类，用于定义一些Django模型类的行为特性
    class Meta:
        abstract = True  # 声明这是一个抽象类

    # 重写save方法
    def save(self, *args, **kwargs):
        user = get_current_user()  # 获取当前用户

        # 如果当前用户是匿名用户或者没有获取到用户
        if user is None or user.is_anonymous:
            self.created_by = None  # 设置created_by字段为None
            self.updated_by = None  # 设置updated_by字段为None
            super(BaseModel, self).save(*args, **kwargs)  # 调用父类的save方法
        else:
            # 如果是新增的记录
            if self._state.adding:
                # 设置created_by字段为当前用户
                self.created_by = user
                # 将updated_by字段设置为None
                self.updated_by = None
            # 如果是更新的记录
            self.updated_by = user  # 将updated_by字段设置为当前用户
            super(BaseModel, self).save(*args, **kwargs)  # 调用父类的save方法

    # 重写__str__方法
    def __str__(self):
        return str(self.id)  # 返回id的字符串形式