# Third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from sentry_sdk import capture_exception

# Module imports
from .base import BaseAPIView
from plane.db.models import FileAsset
from plane.api.serializers import FileAssetSerializer


# FileAssetEndpoint 类用于处理文件资产相关的请求。
class FileAssetEndpoint(BaseAPIView):
    # 指定解析器类，支持多部分表单数据和表单数据的解析，以便能够处理文件上传。
    parser_classes = (MultiPartParser, FormParser)

    """
    A viewset for viewing and editing task instances.
    """

    # GET 方法用于根据 workspace_id 和 asset_key 获取文件资产列表。
    def get(self, request, workspace_id, asset_key):
        # 构造完整的 asset_key，格式为 "workspace_id/asset_key"。
        asset_key = str(workspace_id) + "/" + asset_key
        # 根据完整的 asset_key 从数据库中过滤出对应的文件资产对象。
        files = FileAsset.objects.filter(asset=asset_key)
        # 使用 FileAssetSerializer 序列化查询到的文件资产对象列表。
        serializer = FileAssetSerializer(files, context={"request": request}, many=True)
        # 返回序列化后的数据和状态码200 OK。
        return Response(serializer.data)

    # POST 方法用于上传新的文件资产。
    def post(self, request, slug):
        try:
            # 首先使用 FileAssetSerializer 对请求数据进行序列化。
            serializer = FileAssetSerializer(data=request.data)
            # 验证序列化器中的数据是否有效。
            if serializer.is_valid():
                if request.user.last_workspace_id is None:
                    return Response(
                        {"error": "Workspace id is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # 如果数据有效，则保存序列化器，并将最后一个工作空间 ID 作为 workspace_id 保存。
                serializer.save(workspace_id=request.user.last_workspace_id)
                # 返回序列化后的数据和状态码201 CREATED，表示资源创建成功。
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # 如果数据无效，则返回错误信息和状态码400 BAD REQUEST。
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # DELETE 方法用于删除指定的文件资产。
    def delete(self, request, workspace_id, asset_key):
        try:
            # 构造完整的 asset_key，格式为 "workspace_id/asset_key"。
            asset_key = str(workspace_id) + "/" + asset_key
            # 根据完整的 asset_key 获取对应的文件资产对象实例。
            file_asset = FileAsset.objects.get(asset=asset_key)
            # 从存储中删除该文件
            file_asset.asset.delete(save=False)
            # 删除数据库中对应的对象记录
            file_asset.delete()
            # 返回状态码204 NO CONTENT，表示删除成功且不返回任何内容。
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FileAsset.DoesNotExist:
             return Response(
                 {"error": "File Asset doesn't exist"}, status=status.HTTP_404_NOT_FOUND
             )
        except Exception as e:
             capture_exception(e)  # 捕获并记录异常信息
             return Response(
                 {"error": "Something went wrong please try again later"},
                 status=status.HTTP_400_BAD_REQUEST,
             )

# UserAssetsEndpoint 类用于处理与用户文件资产相关的请求。
class UserAssetsEndpoint(BaseAPIView):

    # GET 方法用于获取与特定 asset_key 相关联且由请求用户创建的文件资产列表。
    def get(self, request, asset_key):
        
        print("asset_key", asset_key)

        try:
            # 从数据库中过滤出符合条件的文件资产对象。
            files = FileAsset.objects.filter(asset=asset_key, created_by=request.user)
            # 使用 FileAssetSerializer 序列化查询到的文件资产对象。
            serializer = FileAssetSerializer(files, context={"request": request})
            # 返回序列化后的数据和状态码200 OK。
            return Response(serializer.data)
        except FileAsset.DoesNotExist:
            # 如果没有找到对应的文件资产，则返回错误信息和状态码404 NOT FOUND。
            return Response(
                {"error": "File Asset does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        

    # POST 方法用于上传新的文件资产。
    def post(self, request):
        try:
            # 首先使用 FileAssetSerializer 对请求数据进行序列化。
            serializer = FileAssetSerializer(data=request.data)
            # 验证序列化器中的数据是否有效。
            if serializer.is_valid():
                # 如果数据有效，则保存序列化器。
                serializer.save()
                # 返回序列化后的数据和状态码201 CREATED，表示资源创建成功。
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # 如果数据无效，则返回错误信息和状态码400 BAD REQUEST。
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)  # 捕获并记录异常信息
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # DELETE 方法用于删除指定的文件资产。
    def delete(self, request, asset_key):
        try:
            # 根据 asset_key 和创建者信息获取对应的文件资产对象实例。
            file_asset = FileAsset.objects.get(asset=asset_key, created_by=request.user)
            
            # 从存储中删除该文件
            file_asset.asset.delete(save=False)
            
            # 删除数据库中对应的对象记录
            file_asset.delete()
            
            # 返回状态码204 NO CONTENT，表示删除成功且不返回任何内容。
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FileAsset.DoesNotExist:
             return Response(
                 {"error": "File Asset doesn't exist"}, status=status.HTTP_404_NOT_FOUND
             )
        except Exception as e:
             capture_exception(e)  # 捕获并记录异常信息
             return Response(
                 {"error": "Something went wrong please try again later"},
                 status=status.HTTP_400_BAD_REQUEST,
             )
