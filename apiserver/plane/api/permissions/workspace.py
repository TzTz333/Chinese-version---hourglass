# 定义对工作空间资源的访问权限

# 第三方导入：从DRF导入BasePermission类和SAFE_METHODS常量
from rest_framework.permissions import BasePermission, SAFE_METHODS

# 模块导入：从当前项目的数据库模型中导入WorkspaceMember模型
from plane.db.models import WorkspaceMember

# 权限映射：定义不同角色对应的权限等级
Owner = 20
Admin = 15
Member = 10
Guest = 5

# 定义工作空间基础权限类
class WorkSpaceBasePermission(BasePermission):
    def has_permission(self, request, view):
        # 如果用户未登录（匿名用户），则不允许创建工作空间
        if request.user.is_anonymous:
            return False

        # 允许任何已登录用户执行POST请求来创建工作空间
        if request.method == "POST":
            return True

        # 对于安全方法（GET、HEAD、OPTIONS等），允许所有请求。安全方法通常用于获取数据而不修改数据。
        if request.method in SAFE_METHODS:
            return True

        # 只允许管理员和所有者使用PUT或PATCH方法更新工作空间设置。
        # 这里通过查询WorkspaceMember模型来检查用户是否具有相应角色和权限。
        if request.method in ["PUT", "PATCH"]:
            return WorkspaceMember.objects.filter(
                member=request.user,
                workspace__slug=view.workspace_slug,
                role__in=[Owner, Admin],
            ).exists()

        # 只允许所有者使用DELETE方法删除工作空间。
        if request.method == "DELETE":
            return WorkspaceMember.objects.filter(
                member=request.user, workspace__slug=view.workspace_slug, role=Owner
            ).exists()

# 定义工作空间管理员权限类
class WorkSpaceAdminPermission(BasePermission):
    def has_permission(self, request, view):

        # 如果用户未登录（匿名用户），则不允许进行任何操作。
        if request.user.is_anonymous:
            return False

        # 检查请求的用户是否为指定工作空间的管理员或所有者。
        # 这一检查通过在WorkspaceMember模型中查询用户角色来实现。
        return WorkspaceMember.objects.filter(
            member=request.user,
            workspace__slug=view.workspace_slug,
            role__in=[Owner, Admin],
        ).exists()
