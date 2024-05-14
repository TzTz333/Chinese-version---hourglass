# 从plane.api.serializers模块导入BaseSerializer基类。
from plane.api.serializers import BaseSerializer
# 从plane.db.models模块导入GitHub相关模型。
from plane.db.models import (
    GithubIssueSync,
    GithubRepository,
    GithubRepositorySync,
    GithubCommentSync,
)

# 定义GitHub仓库的序列化器。
class GithubRepositorySerializer(BaseSerializer):
    class Meta:
        model = GithubRepository  # 指定序列化器关联的Django模型。
        fields = "__all__"  # 指定序列化所有字段。

# 定义GitHub仓库同步的序列化器。
class GithubRepositorySyncSerializer(BaseSerializer):
    repo_detail = GithubRepositorySerializer(source="repository")
    # 使用GithubRepositorySerializer来序列化repository字段，
    # 并将其表示为repo_detail字段。

    class Meta:
        model = GithubRepositorySync  # 指定序列化器关联的Django模型。
        fields = "__all__"  # 指定序列化所有字段。

# 定义GitHub问题同步的序列化器。
class GithubIssueSyncSerializer(BaseSerializer):
    class Meta:
        model = GithubIssueSync  # 指定序列化器关联的Django模型。
        fields = "__all__"  # 指定序列化所有字段。
        read_only_fields = [
            "project",  # 将project字段标记为只读。
            "workspace",  # 将workspace字段标记为只读。
            "repository_sync",  # 将repository_sync字段标记为只读。
        ]

# 定义GitHub评论同步的序列化器。
class GithubCommentSyncSerializer(BaseSerializer):
    class Meta:
        model = GithubCommentSync  # 指定序列化器关联的Django模型。
        fields = "__all__"  # 指定序列化所有字段。
        read_only_fields = [
            "project",  # 将project字段标记为只读。
            "workspace",  # 将workspace字段标记为只读。
            "repository_sync",  # 将repository_sync字段标记为只读。
            "issue_sync",  # 将issue_sync字段标记为只读。
        ]
