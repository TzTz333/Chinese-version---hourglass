# 导入基础视图集
from .base import IntegrationViewSet, WorkspaceIntegrationViewSet
# 这两个基础视图集可能提供了整合和工作空间整合的通用功能，
# 为特定服务（如GitHub）的整合提供了一个共享的基础。

# 导入GitHub相关的视图集
from .github import (
    GithubRepositorySyncViewSet,  # 用于同步GitHub仓库信息到本地系统。
    GithubIssueSyncViewSet,       # 用于同步GitHub上的问题（Issues）到本地系统。
    BulkCreateGithubIssueSyncEndpoint,  # 提供批量创建GitHub问题同步记录的端点，可能用于初始化或大规模更新。
    GithubCommentSyncViewSet,     # 用于同步GitHub上的问题（Issues）评论到本地系统。
    GithubRepositoriesEndpoint,   # 提供获取单个或多个GitHub仓库信息的端点。
)

# 这些视图集和端点特别针对GitHub服务，使得与GitHub相关的数据能够被导入、同步和管理。
# 每个视图集可能实现了一组特定的方法来处理HTTP请求（如GET，POST等），以支持对应的数据操作，
# 如读取GitHub数据、创建新的同步记录、更新本地缓存的数据等。

# 使用这种模块化方式组织代码可以增强其可维护性和扩展性，同时也便于在需要时添加更多服务的支持，
# 或者更新现有服务整合逻辑以适应API变化等情况。
