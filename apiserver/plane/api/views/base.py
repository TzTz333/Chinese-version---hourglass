# Django imports
from django.urls import resolve
from django.conf import settings

# Third part imports
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend

# Module imports
from plane.db.models import Workspace, Project
from plane.utils.paginator import BasePaginator


class BaseViewSet(ModelViewSet, BasePaginator):
    # 指定视图集使用的模型，默认为 None，继承时需要指定具体模型
    model = None

    # 定义权限类，这里要求用户必须通过认证
    permission_classes = [
        IsAuthenticated,
    ]

    # 配置过滤后端为 Django 的过滤器和搜索过滤器
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )

    # 可以过滤的字段列表，默认为空
    filterset_fields = []

    # 可以搜索的字段列表，默认为空
    search_fields = []

    def get_queryset(self):
        try:
            # 尝试获取模型的所有对象
            return self.model.objects.all()
        except Exception as e:
            print(e)
            # 如果出现异常，则抛出 API 异常
            raise APIException("Please check the view", status.HTTP_400_BAD_REQUEST)

    def dispatch(self, request, *args, **kwargs):
        # 调用父类的 dispatch 方法处理请求
        response = super().dispatch(request, *args, **kwargs)

        if settings.DEBUG:
            from django.db import connection

            # 如果处于调试模式，打印出处理当前请求执行的 SQL 查询数量
            print(
                f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
            )
        return response

    @property
    def workspace_slug(self):
        # 从 URL 中获取工作区 slug（如果有）
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        project_id = self.kwargs.get("project_id", None)
        if project_id:
            return project_id

        # 如果 URL 名称为 "project"，则尝试从 URL 中获取项目 ID，
        # 这通常用于处理嵌套资源或特定于项目的视图。
        if resolve(self.request.path_info).url_name == "project":
            return self.kwargs.get("pk", None)


class BaseAPIView(APIView, BasePaginator):
    # 定义权限类，这里设置为只有通过认证的用户才能访问
    permission_classes = [
        IsAuthenticated,
    ]

    # 配置过滤后端为 Django 的过滤器和搜索过滤器
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )

    # 可以通过过滤器进行过滤的字段列表，默认为空
    filterset_fields = []

    # 可以通过搜索进行过滤的字段列表，默认为空
    search_fields = []

    def filter_queryset(self, queryset):
        # 对查询集合应用配置的过滤后端
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        # 调用父类方法处理请求，并记录调试信息（如果处于 DEBUG 模式）
        response = super().dispatch(request, *args, **kwargs)

        if settings.DEBUG:
            from django.db import connection

            # 如果处于调试模式，打印出处理当前请求执行的 SQL 查询数量
            print(
                f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
            )
        return response

    @property
    def workspace_slug(self):
        # 从 URL 路径参数中获取 "slug"，如果不存在则返回 None
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        # 从 URL 路径参数中获取 "project_id"，如果不存在则返回 None
        return self.kwargs.get("project_id", None)
