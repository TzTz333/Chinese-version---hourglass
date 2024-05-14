import time  # 导入time模块用于暂停执行
from django.db import connections  # 从django.db模块导入connections字典
from django.db.utils import OperationalError  # 导入可能抛出的异常类
from django.core.management import BaseCommand  # 从django.core.management导入BaseCommand用于创建自定义命令
 
# 定义一个命令类，继承自BaseCommand
class Command(BaseCommand):
    """Django命令，用于暂停执行直到数据库可用"""

    # handle是必须实现的方法，它将在命令执行时被调用
    def handle(self, *args, **options):
        # 打印消息，指示正在等待数据库
        self.stdout.write('Waiting for database...')
        db_conn = None  # 初始化数据库连接变量为None
        # 使用while循环等待数据库连接
        while not db_conn:
            try:
                # 尝试获取默认数据库连接
                db_conn = connections['default']
            except OperationalError:  # 如果抛出OperationalError异常，说明数据库不可用
                # 打印数据库不可用的消息，并等待1秒
                self.stdout.write('Database unavailable, waititng 1 second...')
                time.sleep(1)  # 暂停执行1秒
 
        # 当数据库变得可用时，打印成功消息
        self.stdout.write(self.style.SUCCESS('Database available!'))