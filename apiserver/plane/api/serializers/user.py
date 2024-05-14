# 导入基础序列化器，用作自定义序列化器的基础类
from .base import BaseSerializer
# 导入User模型，表示系统用户
from plane.db.models import User

# 定义UserSerializer，用于处理User模型的详细信息序列化
class UserSerializer(BaseSerializer):
    class Meta:
        model = User  # 指定序列化器对应的模型是User
        fields = "__all__"  # 包含模型中定义的所有字段
        read_only_fields = [
            "id",  # 用户ID，由系统自动生成，不允许修改
            "created_at",  # 用户创建时间，自动生成，不允许修改
            "updated_at",  # 用户信息最后更新时间，自动生成，不允许修改
            "is_superuser",  # 是否为超级用户标志，只读
            "is_staff",  # 是否为员工标志（通常指有后台管理权限），只读
            "last_active",  # 用户最后活跃时间，自动更新，只读
            "last_login_time",  # 上次登录时间，自动记录，只读
            "last_logout_time",  # 上次登出时间，自动记录，只读
            "last_login_ip",  # 上次登录IP地址，自动记录，只读
            "last_logout_ip",  # 上次登出IP地址，自动记录，只读
            "last_login_uagent",  # 上次登录时使用的用户代理信息（浏览器信息等），自动记录，只读
            "token_updated_at",  # 用户token最后更新时间（用于验证等），自动更新，只读
            "is_onboarded",  # 是否已完成新手引导流程的标志，只读
            "is_bot",  # 是否为机器人账户的标志，只读
        ]
        extra_kwargs = {"password": {"write_only": True}}  # 设置密码字段为仅写入

# 定义UserLiteSerializer, 提供了一个简化版的User信息视图，
# 主要用于在不需要全量用户数据的场合减少数据传输量。
class UserLiteSerializer(BaseSerializer):
    class Meta:
        model = User  # 指定序列化器对应的模型是User
        fields = [
            "id",  # 用户ID, 唯一标识符
            "first_name",  # 用户名字
            "last_name",  # 用户姓氏
            "email",  # 用户邮箱地址
            "avatar",  # 用户头像URL或相关标识符
            "is_bot",   # 标记用户是否为机器人账户 
        ]
        read_only_fields = [
            "id",   # 用户ID, 自动分配, 只读 
            "is_bot",   # 是否为机器人账户, 只读 
        ]
