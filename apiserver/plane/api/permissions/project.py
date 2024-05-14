# 引入第三方库：DRF的BasePermission类和SAFE_METHODS常量
from rest_framework.permissions import BasePermission, SAFE_METHODS

# 从应用的模型文件中导入WorkspaceMember和ProjectMember类
from plane.db.models import WorkspaceMember, ProjectMember

# 定义角色对应的权限等级，这有助于在权限逻辑中进行比较和判断
Admin = 20
Member = 15
Viewer = 10
Guest = 5

# 基础权限验证
class ProjectBasePermission(BasePermission):
    def has_permission(self, request, view):
        # 防止匿名用户访问资源
        if request.user.is_anonymous:
            return False
        # 允许安全方法（GET, HEAD, OPTIONS等）的请求，
        # 这些请求通常不会修改资源，因此被认为是"安全"的。
        if request.method in SAFE_METHODS:
            return WorkspaceMember.objects.filter(
                workspace__slug=view.workspace_slug, member=request.user
            ).exists()

        # 只允许工作空间的所有者或管理员创建项目。
        if request.method == "POST":
            return WorkspaceMember.objects.filter(
                workspace__slug=view.workspace_slug,
                member=request.user,
                role__in=[Admin, Member],
            ).exists()

        # 只有项目管理员可以更新项目属性。
        return ProjectMember.objects.filter(
            workspace__slug=view.workspace_slug,
            member=request.user,
            role=Admin,
            project_id=view.project_id,
        ).exists()

# 控制对项目成员操作的访问，定义项目成员权限类
class ProjectMemberPermission(BasePermission):
    def has_permission(self, request, view):

        if request.user.is_anonymous:
            return False

        # 对于安全方法，检查用户是否为项目成员。
        if request.method in SAFE_METHODS:
            return ProjectMember.objects.filter(
                workspace__slug=view.workspace_slug, member=request.user
            ).exists()
        # 创建项目的权限控制与ProjectBasePermission相同。
        if request.method == "POST":
            return WorkspaceMember.objects.filter(
                workspace__slug=view.workspace_slug,
                member=request.user,
                role__in=[Admin, Member],
            ).exists()

        # 更新项目属性时，允许管理员和成员操作。
        return ProjectMember.objects.filter(
            workspace__slug=view.workspace_slug,
            member=request.user,
            role__in=[Admin, Member],
            project_id=view.project_id,
        ).exists()

# 定义对特定项目实体（如任务、文档等）的操作权限
class ProjectEntityPermission(BasePermission):
    def has_permission(self, request, view):

        if request.user.is_anonymous:
            return False

        # 对于安全方法，检查用户是否有权访问该项目实体。
        if request.method in SAFE_METHODS:
            return ProjectMember.objects.filter(
                workspace__slug=view.workspace_slug,
                member=request.user,
                project_id=view.project_id,
            ).exists()

        # 创建或编辑项目实体时，只允许项目成员或管理员操作。
        return ProjectMember.objects.filter(
            workspace__slug=view.workspace_slug,
            member=request.user,
            role__in=[Admin, Member],
            project_id=view.project_id,
        ).exists()

# 每个方法都通过查询数据库来决定当前请求是否应该被授权。
# 这涉及到检查请求者是否为特定工作空间或项目的成员、他们在其中担任什么角色（如管理员、普通成员等），
# 以及根据HTTP请求类型（如GET请求与POST请求）进行不同的权限验证逻辑。
