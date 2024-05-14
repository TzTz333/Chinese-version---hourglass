# 创建一个默认用户的脚本
import os, sys  # 导入os和sys模块，用于操作系统环境变量和Python路径等。
import uuid  # 导入uuid模块，用于生成唯一的用户ID。

sys.path.append("/code")  # 将"/code"目录添加到Python的搜索路径中，这样可以导入项目中的模块。

# 设置Django的环境变量，指定使用哪个设置文件(settings)来配置Django。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plane.settings.production")

import django  # 导入Django模块。
django.setup()  # 配置Django环境，使得Django项目中的模型等可以被正常使用。

from plane.db.models import User  # 从项目的模型定义中导入User模型。

def populate():
    # 从环境变量获取默认用户邮箱和密码，如果没有设置，则使用默认值。
    default_email = os.environ.get("DEFAULT_EMAIL", "captain@plane.so")
    default_password = os.environ.get("DEFAULT_PASSWORD", "password123")

    # 检查是否已存在具有指定邮箱的用户，如果不存在，则创建新用户。
    if not User.objects.filter(email=default_email).exists():
        user = User.objects.create(email=default_email, username=uuid.uuid4().hex)  # 创建新用户，用户名为随机生成的UUID。
        user.set_password(default_password)  # 设置用户密码。
        user.save()  # 保存用户信息到数据库。
        print("User created")  # 打印提示信息。

    print("Success")  # 打印成功信息。

if __name__ == "__main__":
    populate()  # 当脚本被直接运行时，调用populate函数创建默认用户。
