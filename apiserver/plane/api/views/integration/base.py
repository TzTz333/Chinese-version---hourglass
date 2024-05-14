# 导入Python内置的uuid库，用于生成唯一标识符
import uuid

# Django框架的导入
from django.db import IntegrityError  # 用于处理数据库完整性异常
from django.contrib.auth.hashers import make_password  # Django的密码哈希工具

# 第三方库导入
from rest_framework.response import Response  # REST框架的HTTP响应类
from rest_framework import status  # HTTP状态码
from sentry_sdk import capture_exception  # Sentry SDK，用于错误跟踪和报告

# 当前模块/应用的导入
from plane.api.views import BaseViewSet  # 基础视图集类，提供了通用视图逻辑
from plane.db.models import (
    Integration,
    WorkspaceIntegration,
    Workspace,
    User,
    WorkspaceMember,
    APIToken,
)  # 导入应用中定义的数据库模型
from plane.api.serializers import IntegrationSerializer, WorkspaceIntegrationSerializer  # 序列化器，用于将模型实例转换为JSON格式和验证输入数据
from plane.utils.integrations.github import (
    get_github_metadata,  # GitHub集成工具函数：获取GitHub元数据
    delete_github_installation,  # GitHub集成工具函数：删除GitHub安装信息
)
from plane.api.permissions import WorkSpaceAdminPermission  # 自定义权限检查类

class IntegrationViewSet(BaseViewSet):
    serializer_class = IntegrationSerializer  # 指定该视图集使用的序列化器类
    model = Integration  # 指定该视图集关联的模型

    def create(self, request):
        #"""创建新的集成"""
        try:
            serializer = IntegrationSerializer(data=request.data)  # 实例化序列化器并传入请求数据进行验证
            if serializer.is_valid():  # 验证数据有效性
                serializer.save()  # 将验证后的数据保存到数据库中创建新的集成实例
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # 返回创建成功的响应及数据
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 返回数据验证失败的错误信息及状态码
            
        except Exception as e:
            capture_exception(e)  # 使用Sentry捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"}, 
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, pk):
        try:
            # 尝试根据主键(pk)获取特定的Integration实例
            integration = Integration.objects.get(pk=pk)
            
            # 检查该Integration实例是否已经被验证，如果是，则不允许更新
            if integration.verified:
                return Response(
                    {"error": "Verified integrations cannot be updated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 使用IntegrationSerializer序列化器来处理部分更新请求，
            # 设置partial=True以允许部分字段更新
            serializer = IntegrationSerializer(
                integration, data=request.data, partial=True
            )

            # 验证传入的数据是否有效
            if serializer.is_valid():
                # 如果数据有效，则保存更新后的实例
                serializer.save()
                # 返回更新后的数据和状态码200（OK）
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # 如果数据无效，返回错误信息和状态码400（Bad Request）
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Integration.DoesNotExist:
            # 如果指定的Integration实例不存在，返回错误信息和状态码404（Not Found）
            return Response(
                {"error": "Integration Does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            # 捕获其他异常，并使用Sentry进行记录
            capture_exception(e)
            # 返回通用错误信息和状态码400（Bad Request）
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk):
        try:
            # 尝试根据主键(pk)获取特定的Integration实例
            integration = Integration.objects.get(pk=pk)
            
            # 检查该Integration实例是否已经被验证，如果是，则不允许删除
            if integration.verified:
                return Response(
                    {"error": "Verified integrations cannot be updated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # 删除指定的Integration实例
            integration.delete()
            
            # 返回状态码204（No Content）表示删除成功且无需返回任何内容
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Integration.DoesNotExist:
            # 如果指定的Integration实例不存在，返回错误信息和状态码404（Not Found）
            return Response(
                {"error": "Integration Does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

# WorkspaceIntegrationViewSet处理工作区中集成的操作，比如创建和管理工作区特定的集成
class WorkspaceIntegrationViewSet(BaseViewSet):
    serializer_class = WorkspaceIntegrationSerializer  # 指定使用的序列化器
    model = WorkspaceIntegration  # 指定视图集关联的模型

    permission_classes = [
        WorkSpaceAdminPermission,  # 设置权限类，确保只有工作区管理员能进行操作
    ]

    # 获取查询集，过滤出对应slug的工作空间下的集成，并预加载相关联的integration数据以优化性能
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("integration")
        )

    # 创建新的工作区集成实例
    def create(self, request, slug, provider):
        try:
            installation_id = request.data.get("installation_id", None)

            if not installation_id:
                return Response(
                    {"error": "Installation ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            workspace = Workspace.objects.get(slug=slug)  # 根据slug获取对应的Workspace实例
            integration = Integration.objects.get(provider=provider)  # 根据provider获取对应的Integration实例

            config = {}
            if provider == "github":
                metadata = get_github_metadata(installation_id)  # 获取GitHub特定元数据
                config = {"installation_id": installation_id}

            # 创建一个bot用户来代表该集成在平台上进行操作
            bot_user = User.objects.create(
                email=f"{uuid.uuid4().hex}@plane.so",  # 使用UUID生成独一无二的email地址
                username=uuid.uuid4().hex,  # UUID生成唯一用户名
                password=make_password(uuid.uuid4().hex),  # 自动生成密码，并进行加密
                is_password_autoset=True,
                is_bot=True,  # 标记为机器人用户
                first_name=integration.title,  # 使用集成标题作为名字
                avatar=integration.avatar_url
                if integration.avatar_url is not None
                else "",
            )

            # 创建API Token给bot用户，用于API认证
            api_token = APIToken.objects.create(
                user=bot_user,
                user_type=1,  # 表示这是一个bot用户
                workspace=workspace,
            )


            # 创建工作区集成实例
            workspace_integration = WorkspaceIntegration.objects.create(
                workspace=workspace,  # 指定所属工作区
                integration=integration,  # 指定关联的集成
                actor=bot_user,  # 指定操作者为bot用户
                api_token=api_token,  # 指定API令牌
                metadata=metadata,  # 存储获取的元数据
                config=config,  # 存储特定配置信息
            )

            # 将bot用户添加为工作区成员
            _ = WorkspaceMember.objects.create(
                workspace=workspace_integration.workspace,  # 指定所属工作区
                member=bot_user,  # 指定成员为bot用户
                role=20,  # 分配角色，数字代表不同的角色权限（这里假设20为某个具体角色）
            )

            return Response(
                WorkspaceIntegrationSerializer(workspace_integration).data,
                status=status.HTTP_201_CREATED,
            )
       # 异常处理 - 当尝试添加一个已经存在于数据库中的记录时触发
        except IntegrityError as e:
            # 如果错误信息中包含"already exists"，表示这个集成已经在工作空间中激活了
            if "already exists" in str(e):
                # 返回一个错误响应，状态码为410（已删除）
                return Response(
                    {"error": "Integration is already active in the workspace"},
                    status=status.HTTP_410_GONE,
                )
            else:
                # 对未预料到的IntegrityError异常进行捕获，并通知错误跟踪系统
                capture_exception(e)
                # 返回一个通用错误响应，状态码为400（坏请求）
                return Response(
                    {"error": "Something went wrong please try again later"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # 处理当Workspace或Integration不存在时抛出的异常
        except (Workspace.DoesNotExist, Integration.DoesNotExist) as e:
            # 通知错误跟踪系统关于这一异常
            capture_exception(e)
            # 返回一个表示未找到工作空间或集成的错误响应
            return Response(
                {"error": "Workspace or Integration not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 捕获处理中发生的其他所有异常
        except Exception as e:
            # 通知错误跟踪系统关于这一异常
            capture_exception(e)
            # 返回一个通用错误响应
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # 删除某个集成的方法定义
    def destroy(self, request, slug, pk):
        try:
            # 尝试根据主键和工作空间slug获取工作空间集成对象
            workspace_integration = WorkspaceIntegration.objects.get(
                pk=pk, workspace__slug=slug
            )

            # 检查该集成是否为GitHub集成
            if workspace_integration.integration.provider == "github":
                # 尝试从配置中获取installation_id
                installation_id = workspace_integration.config.get(
                    "installation_id", False
                )
                if installation_id:
                    # 如果存在installation_id，则调用函数以删除GitHub安装实例
                    delete_github_installation(installation_id=installation_id)

            # 删除找到的工作空间集成记录
            workspace_integration.delete()
            # 返回204无内容状态码，表示删除成功但不返回任何内容
            return Response(status=status.HTTP_204_NO_CONTENT)

        except WorkspaceIntegration.DoesNotExist:
            # 如果未找到指定的工作空间集成，返回错误响应
            return Response(
                {"error": "Workspace Integration Does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # 捕获其他所有异常，并返回通用错误响应
            capture_exception(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )
