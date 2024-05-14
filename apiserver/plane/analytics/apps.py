from django.apps import AppConfig  # 从django.apps模块导入AppConfig基类。

class AnalyticsConfig(AppConfig):  # 定义一个名为AnalyticsConfig的类，它继承自AppConfig。
    name = 'plane.analytics'  # 指定这个应用的全名。这里的'name'属性是必须定义的，它告诉Django这个应用的位置。
