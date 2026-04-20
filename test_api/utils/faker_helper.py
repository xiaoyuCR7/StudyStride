"""Faker工具类，用于生成测试数据"""
from faker import Faker


class FakerHelper:
    """Faker帮助类"""
    
    def __init__(self):
        self.faker = Faker('zh_CN')
    
    def generate_email(self, prefix='test'):
        """生成测试邮箱"""
        return f"{prefix}_{self.faker.unique.user_name()}@{self.faker.domain_name()}"
    
    def generate_password(self, length=12):
        """生成测试密码"""
        return self.faker.password(length=length, special_chars=True, digits=True, upper_case=True, lower_case=True)
    
    def generate_name(self):
        """生成测试姓名"""
        return self.faker.name()
    
    def generate_user_metadata(self):
        """生成用户元数据"""
        return {
            "name": self.generate_name(),
            "age": self.faker.random_int(min=18, max=60),
            "gender": self.faker.random_element(elements=('male', 'female')),
            "phone": self.faker.phone_number()
        }


# 单例模式
faker_helper = FakerHelper()
