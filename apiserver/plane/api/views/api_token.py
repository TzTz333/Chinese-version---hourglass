# Python import
from uuid import uuid4

# Third party
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk import capture_exception

# Module import
from .base import BaseAPIView
from plane.db.models import APIToken
from plane.api.serializers import APITokenSerializer


# ApiTokenEndpoint 类用于处理 API 令牌相关的请求。
class ApiTokenEndpoint(BaseAPIView):
    # POST 方法用于创建新的 API 令牌。
    def post(self, request):
        try:
            # 尝试从请求数据中获取标签（label），如果未提供，则生成一个唯一的 UUID 作为标签。
            label = request.data.get("label", str(uuid4().hex))
            # 尝试从请求数据中获取工作空间 ID。
            workspace = request.data.get("workspace", False)

            # 如果没有提供工作空间 ID，则返回错误响应。
            if not workspace:
                return Response(
                    {"error": "Workspace is required"}, status=status.HTTP_200_OK
                )

            # 使用提供的数据创建一个新的 APIToken 对象。
            api_token = APIToken.objects.create(
                label=label, user=request.user, workspace_id=workspace
            )

            # 序列化新创建的 APIToken 对象。
            serializer = APITokenSerializer(api_token)
            
            # 返回含有序列化数据和令牌字符串的响应，状态码为201 CREATED。
            return Response(
                {"api_token": serializer.data, "token": api_token.token},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # GET 方法用于获取当前用户所有的 API 令牌。
    def get(self, request):
        try:
            # 过滤出属于当前请求用户的所有 APIToken 对象。
            api_tokens = APIToken.objects.filter(user=request.user)
            
            # 序列化这些 APIToken 对象。
            serializer = APITokenSerializer(api_tokens, many=True)
            
            # 返回序列化数据和状态码200 OK。
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # DELETE 方法用于删除指定的 API 令牌。
    def delete(self, request, pk):
        try:
            # 根据主键（pk）获取特定的 APIToken 对象。
            api_token = APIToken.objects.get(pk=pk)
            
            # 删除该对象。
            api_token.delete()
            
            # 返回状态码204 NO CONTENT，表示删除成功但不返回任何内容。
            return Response(status=status.HTTP_204_NO_CONTENT)
        except APIToken.DoesNotExist:
             return Response(
                 {"error": "Token does not exists"}, status=status.HTTP_400_BAD_REQUEST
             )
        except Exception as e:
             capture_exception(e)  # 捕获并记录异常信息
             return Response(
                 {"error": "Something went wrong please try again later"},
                 status=status.HTTP_400_BAD_REQUEST,
             )

