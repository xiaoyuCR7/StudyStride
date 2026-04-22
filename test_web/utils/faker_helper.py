from faker import Faker

class FakerHelper:
    """Faker辅助类，用于生成测试数据"""
    
    def __init__(self):
        self.faker = Faker('zh_CN')
    
    def generate_email(self):
        """生成随机邮箱"""
        return self.faker.email()
    
    def generate_username(self):
        """生成随机用户名"""
        return self.faker.user_name()
    
    def generate_password(self):
        """生成随机密码"""
        return self.faker.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
    
    def generate_name(self):
        """生成随机姓名"""
        return self.faker.name()
    
    def generate_phone_number(self):
        """生成随机电话号码"""
        return self.faker.phone_number()
    
    def generate_address(self):
        """生成随机地址"""
        return self.faker.address()
    
    def generate_subject_name(self):
        """生成随机科目名称"""
        subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        return self.faker.random_element(subjects)
    
    def generate_study_time(self):
        """生成随机学习时间（分钟）"""
        return self.faker.random_int(min=15, max=180)

# 创建全局实例
faker_helper = FakerHelper()
