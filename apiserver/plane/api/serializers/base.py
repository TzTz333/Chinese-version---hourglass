# 导入Django REST Framework的serializers模块
from rest_framework import serializers

# 定义一个名为BaseSerializer的基础序列化器类，它继承自DRF的ModelSerializer。
# ModelSerializer类是DRF提供的工具之一，用于快速创建与Django模型(Model)对应的序列化器(Serializer)。
class BaseSerializer(serializers.ModelSerializer):
    # 在这个基础序列化器中定义了一个名为id的字段，
    # 使用PrimaryKeyRelatedField序列化器字段类型，并设置为只读。
    # PrimaryKeyRelatedField通常用于表示关联模型的主键字段。
    # read_only=True属性确保此字段仅用于序列化输出，在反序列化（如API更新操作）过程中不可写，保护数据的完整性。
    id = serializers.PrimaryKeyRelatedField(read_only=True)
