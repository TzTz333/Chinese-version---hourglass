# 组织和管理多个序列化器，Serializer
# 序列化器在Django REST Framework（DRF）中用于将模型实例转换为JSON格式，
#便于前后端数据交换，或者将接收到的JSON数据反序列化回模型实例。

from .base import BaseSerializer
from .people import (
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    TokenSerializer,
)
from .user import UserSerializer, UserLiteSerializer
from .workspace import (
    WorkSpaceSerializer,
    WorkSpaceMemberSerializer,
    TeamSerializer,
    WorkSpaceMemberInviteSerializer,
    WorkspaceLiteSerializer,
)
from .project import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ProjectMemberSerializer,
    ProjectMemberInviteSerializer,
    ProjectIdentifierSerializer,
    ProjectFavoriteSerializer,
    ProjectLiteSerializer,
)
from .state import StateSerializer, StateLiteSerializer
from .shortcut import ShortCutSerializer
from .view import IssueViewSerializer, IssueViewFavoriteSerializer
from .cycle import CycleSerializer, CycleIssueSerializer, CycleFavoriteSerializer
from .asset import FileAssetSerializer
from .issue import (
    IssueCreateSerializer,
    IssueActivitySerializer,
    IssueCommentSerializer,
    TimeLineIssueSerializer,
    IssuePropertySerializer,
    BlockerIssueSerializer,
    BlockedIssueSerializer,
    IssueAssigneeSerializer,
    LabelSerializer,
    IssueSerializer,
    IssueFlatSerializer,
    IssueStateSerializer,
    IssueLinkSerializer,
    IssueLiteSerializer,
)

from .module import (
    ModuleWriteSerializer,
    ModuleSerializer,
    ModuleIssueSerializer,
    ModuleLinkSerializer,
    ModuleFavoriteSerializer,
)

from .api_token import APITokenSerializer

from .integration import (
    IntegrationSerializer,
    WorkspaceIntegrationSerializer,
    GithubIssueSyncSerializer,
    GithubRepositorySerializer,
    GithubRepositorySyncSerializer,
    GithubCommentSyncSerializer,
)

from .importer import ImporterSerializer

from .page import PageSerializer, PageBlockSerializer, PageFavoriteSerializer
