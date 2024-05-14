# Third party imports
from rest_framework import status
from rest_framework.response import Response
from sentry_sdk import capture_exception

# Module imports
from plane.api.views import BaseViewSet, BaseAPIView
from plane.db.models import (
    GithubIssueSync,
    GithubRepositorySync,
    GithubRepository,
    WorkspaceIntegration,
    ProjectMember,
    Label,
    GithubCommentSync,
    Project,
)
from plane.api.serializers import (
    GithubIssueSyncSerializer,
    GithubRepositorySyncSerializer,
    GithubCommentSyncSerializer,
)
from plane.utils.integrations.github import get_github_repos
from plane.api.permissions import ProjectBasePermission, ProjectEntityPermission


# GithubRepositoriesEndpoint 类继承自 BaseAPIView，用于处理 GitHub 仓库相关的 API 请求
class GithubRepositoriesEndpoint(BaseAPIView):
    # 设置该视图的权限类为 ProjectBasePermission，确保只有具备相应权限的用户可以访问
    permission_classes = [
        ProjectBasePermission,
    ]

    # 处理 GET 请求，用于获取指定工作空间集成的 GitHub 仓库列表
    def get(self, request, slug, workspace_integration_id):
        try:
            # 从请求的查询参数中获取页码，默认为第一页
            page = request.GET.get("page", 1)
            # 根据工作空间的 slug 和集成的 ID 获取对应的 WorkspaceIntegration 对象
            workspace_integration = WorkspaceIntegration.objects.get(
                workspace__slug=slug, pk=workspace_integration_id
            )

            # 检查该集成是否为 GitHub 集成，如果不是，则返回错误响应
            if workspace_integration.integration.provider != "github":
                return Response(
                    {"error": "Not a github integration"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 从集成元数据中获取访问令牌 URL 和仓库 URL
            access_tokens_url = workspace_integration.metadata["access_tokens_url"]
            repositories_url = (
                workspace_integration.metadata["repositories_url"]
                + f"?per_page=100&page={page}"  # 查询参数中指定每页100个项目并设置当前页码
            )
            
            # 调用函数 get_github_repos() 获取 GitHub 仓库列表，并传入访问令牌 URL 和仓库 URL
            repositories = get_github_repos(access_tokens_url, repositories_url)
            
            # 返回仓库列表和状态码200 OK
            return Response(repositories, status=status.HTTP_200_OK)
        except WorkspaceIntegration.DoesNotExist:
            # 如果指定的工作空间集成不存在，则返回错误响应
            return Response(
                {"error": "Workspace Integration Does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# GithubRepositorySyncViewSet 继承自 BaseViewSet，用于处理 GitHub 仓库同步相关的 API 请求
class GithubRepositorySyncViewSet(BaseViewSet):
    # 设置该视图的权限类为 ProjectBasePermission，确保只有具备相应权限的用户可以访问
    permission_classes = [
        ProjectBasePermission,
    ]

    # 设置视图使用的序列化器类
    serializer_class = GithubRepositorySyncSerializer
    # 设置视图关联的模型
    model = GithubRepositorySync

    # 创建对象时的额外处理逻辑
    def perform_create(self, serializer):
        # 在保存序列化器时，添加 project_id 到保存的数据中
        serializer.save(project_id=self.kwargs.get("project_id"))

    # 获取查询集，根据 URL 参数过滤数据
    def get_queryset(self):
        return (
            super()
            .get_queryset()  # 调用父类方法获取查询集
            .filter(workspace__slug=self.kwargs.get("slug"))  # 根据工作空间 slug 过滤
            .filter(project_id=self.kwargs.get("project_id"))  # 根据项目 ID 过滤
        )

    # 处理 POST 请求，创建新的 GitHub 仓库同步对象
    def create(self, request, slug, project_id, workspace_integration_id):
        try:
            # 从请求数据中获取必要的信息
            name = request.data.get("name", False)
            url = request.data.get("url", False)
            config = request.data.get("config", {})
            repository_id = request.data.get("repository_id", False)
            owner = request.data.get("owner", False)

            # 验证必要信息是否完整
            if not name or not url or not repository_id or not owner:
                return Response(
                    {"error": "Name, url, repository_id and owner are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 获取对应的工作空间集成对象
            workspace_integration = WorkspaceIntegration.objects.get(
                pk=workspace_integration_id
            )

            # 删除旧的仓库同步对象和仓库对象（为了重新同步）
            GithubRepositorySync.objects.filter(
                project_id=project_id, workspace__slug=slug
            ).delete()
            GithubRepository.objects.filter(
                project_id=project_id, workspace__slug=slug
            ).delete()

            # 创建新的 GitHub 仓库对象
            repo = GithubRepository.objects.create(
                name=name,
                url=url,
                config=config,
                repository_id=repository_id,
                owner=owner,
                project_id=project_id,
            )

            # 尝试获取或创建用于 GitHub 同步的标签对象（Label）
            label = Label.objects.filter(
                name="GitHub",
                project_id=project_id,
            ).first()
            
            if label is None:
                label = Label.objects.create(
                    name="GitHub",
                    project_id=project_id,
                    description="Label to sync Plane issues with GitHub issues",
                    color="#003773",
                )

            # 创建 GitHub 仓库同步对象（GithubRepositorySync）
            repo_sync = GithubRepositorySync.objects.create(
                repository=repo,
                workspace_integration=workspace_integration,
                actor=workspace_integration.actor,
                credentials=request.data.get("credentials", {}),
                project_id=project_id,
                label=label,
            )

            # 确保工作空间集成操作者为项目成员之一，并设置角色为20（具体角色含义根据系统设定而定）
            _ = ProjectMember.objects.get_or_create(
                member=workspace_integration.actor, role=20, project_id=project_id
            )

            # 返回成功创建的响应，包括新创建的 GitHub 仓库同步对象数据和状态码201 CREATED
            return Response(
                GithubRepositorySyncSerializer(repo_sync).data,
                status=status.HTTP_201_CREATED,
            )
        
        except WorkspaceIntegration.DoesNotExist:
            return Response(
                {"error": "Workspace Integration does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# BulkCreateGithubIssueSyncEndpoint 继承自 BaseAPIView，用于批量创建 GitHub Issue 同步记录
class GithubIssueSyncViewSet(BaseViewSet):
    permission_classes = [
        ProjectEntityPermission,
    ]

    serializer_class = GithubIssueSyncSerializer
    model = GithubIssueSync

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs.get("project_id"),
            repository_sync_id=self.kwargs.get("repo_sync_id"),
        )


class BulkCreateGithubIssueSyncEndpoint(BaseAPIView):
    # 处理 POST 请求
    def post(self, request, slug, project_id, repo_sync_id):
        try:
            # 根据提供的项目 ID 和工作空间 slug 查找项目实例
            project = Project.objects.get(pk=project_id, workspace__slug=slug)

            # 从请求数据中获取 github_issue_syncs 列表
            github_issue_syncs = request.data.get("github_issue_syncs", [])
            # 使用 bulk_create 批量创建 GithubIssueSync 实例，提高性能并减少数据库 I/O 操作
            github_issue_syncs = GithubIssueSync.objects.bulk_create(
                [
                    GithubIssueSync(
                        issue_id=github_issue_sync.get("issue"),
                        repo_issue_id=github_issue_sync.get("repo_issue_id"),
                        issue_url=github_issue_sync.get("issue_url"),
                        github_issue_id=github_issue_sync.get("github_issue_id"),
                        repository_sync_id=repo_sync_id,
                        project_id=project_id,
                        workspace_id=project.workspace_id,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    for github_issue_sync in github_issue_syncs  # 列表推导式用于构造 GithubIssueSync 实例列表
                ],
                batch_size=100,  # 指定每批处理的对象数量
                ignore_conflicts=True,  # 忽略冲突，重复插入时不会报错
            )

            # 序列化操作：将批量创建的实例转换为 JSON 格式返回给客户端
            serializer = GithubIssueSyncSerializer(github_issue_syncs, many=True)
            
            # 返回成功响应，包括新创建的 GitHub Issue 同步记录列表和状态码201 CREATED
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Project.DoesNotExist:
            # 如果项目不存在，则返回错误响应
            return Response(
                {"error": "Project does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息，便于调试和问题追踪 
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

# GithubCommentSyncViewSet 继承自 BaseViewSet，专门用于处理 GitHub 评论同步相关的请求。
class GithubCommentSyncViewSet(BaseViewSet):

    # 设置该视图集所需的权限类。在这里，它使用 ProjectEntityPermission，
    # 表示只有具备特定项目实体权限的用户才能访问此视图集。
    permission_classes = [
        ProjectEntityPermission,
    ]
    
    # 指定该视图集使用的序列化器类为 GithubCommentSyncSerializer。
    # 序列化器用于将模型实例转换为 JSON 格式，以及将传入的 JSON 数据转换为模型实例。
    serializer_class = GithubCommentSyncSerializer
    
    # 指定该视图集关联的模型为 GithubCommentSync。
    # 此模型应包含与 GitHub 评论同步相关的字段和数据。
    model = GithubCommentSync

    # 在创建新记录时执行额外的保存逻辑。
    def perform_create(self, serializer):
        # 调用 serializer.save 方法保存序列化器中的数据，
        # 同时根据 URL 中捕获的 project_id 和 issue_sync_id 参数，
        # 将这些参数添加到正在保存的模型实例中。
        serializer.save(
            project_id=self.kwargs.get("project_id"),  # 从 URL 参数中获取项目 ID
            issue_sync_id=self.kwargs.get("issue_sync_id"),  # 从 URL 参数中获取问题同步 ID
        )
