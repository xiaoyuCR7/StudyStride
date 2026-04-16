"""
数据提供器

支持多种数据格式的数据驱动测试：
- YAML
- JSON
- CSV
- Excel
"""
import os
import json
import csv
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Callable
from dataclasses import dataclass
import pytest

from utils.logger import get_logger


@dataclass
class TestData:
    """测试数据类"""
    name: str
    data: Dict[str, Any]
    expected: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DataProvider:
    """
    数据提供器
    
    支持从多种数据源加载测试数据
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent.parent / 'data'
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_yaml(self, filename: str) -> List[TestData]:
        """
        加载YAML数据文件
        
        Args:
            filename: 文件名
        
        Returns:
            TestData列表
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._parse_test_data(data)
    
    def load_json(self, filename: str) -> List[TestData]:
        """
        加载JSON数据文件
        
        Args:
            filename: 文件名
        
        Returns:
            TestData列表
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._parse_test_data(data)
    
    def load_csv(self, filename: str) -> List[TestData]:
        """
        加载CSV数据文件
        
        Args:
            filename: 文件名
        
        Returns:
            TestData列表
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        test_data_list = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                # 解析JSON字段
                data = {}
                expected = {}
                
                for key, value in row.items():
                    if key.startswith('expected_'):
                        expected_key = key[9:]  # 去掉expected_前缀
                        try:
                            expected[expected_key] = json.loads(value)
                        except json.JSONDecodeError:
                            expected[expected_key] = value
                    elif key == 'expected':
                        try:
                            expected = json.loads(value)
                        except json.JSONDecodeError:
                            expected = {'result': value}
                    else:
                        try:
                            data[key] = json.loads(value)
                        except json.JSONDecodeError:
                            data[key] = value
                
                test_data = TestData(
                    name=row.get('name', f'case_{idx}'),
                    data=data,
                    expected=expected if expected else None,
                    description=row.get('description'),
                    tags=row.get('tags', '').split(',') if row.get('tags') else None
                )
                test_data_list.append(test_data)
        
        return test_data_list
    
    def load_excel(self, filename: str, sheet_name: Optional[str] = None) -> List[TestData]:
        """
        加载Excel数据文件
        
        Args:
            filename: 文件名
            sheet_name: 工作表名称
        
        Returns:
            TestData列表
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError("请安装openpyxl: pip install openpyxl")
        
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        workbook = openpyxl.load_workbook(filepath)
        
        if sheet_name:
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.active
        
        # 获取表头
        headers = [cell.value for cell in sheet[1]]
        
        test_data_list = []
        
        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            row_data = dict(zip(headers, row))
            
            # 解析数据
            data = {}
            expected = {}
            
            for key, value in row_data.items():
                if key is None:
                    continue
                    
                if key.startswith('expected_'):
                    expected_key = key[9:]
                    try:
                        expected[expected_key] = json.loads(value) if value else None
                    except (json.JSONDecodeError, TypeError):
                        expected[expected_key] = value
                elif key == 'expected':
                    try:
                        expected = json.loads(value) if value else {}
                    except (json.JSONDecodeError, TypeError):
                        expected = {'result': value}
                elif key not in ['name', 'description', 'tags']:
                    try:
                        data[key] = json.loads(value) if value else None
                    except (json.JSONDecodeError, TypeError):
                        data[key] = value
            
            tags = row_data.get('tags')
            if tags and isinstance(tags, str):
                tags = tags.split(',')
            
            test_data = TestData(
                name=row_data.get('name', f'case_{idx-1}'),
                data=data,
                expected=expected if expected else None,
                description=row_data.get('description'),
                tags=tags
            )
            test_data_list.append(test_data)
        
        workbook.close()
        
        return test_data_list
    
    def _parse_test_data(self, data: Any) -> List[TestData]:
        """解析测试数据"""
        test_data_list = []
        
        if isinstance(data, list):
            for item in data:
                test_data_list.append(self._create_test_data(item))
        elif isinstance(data, dict):
            if 'test_cases' in data:
                for item in data['test_cases']:
                    test_data_list.append(self._create_test_data(item))
            else:
                test_data_list.append(self._create_test_data(data))
        
        return test_data_list
    
    def _create_test_data(self, item: Dict) -> TestData:
        """创建TestData对象"""
        return TestData(
            name=item.get('name', 'unnamed'),
            data=item.get('data', item),
            expected=item.get('expected'),
            description=item.get('description'),
            tags=item.get('tags', [])
        )
    
    def load(self, filename: str, **kwargs) -> List[TestData]:
        """
        自动根据文件扩展名加载数据
        
        Args:
            filename: 文件名
            **kwargs: 额外参数
        
        Returns:
            TestData列表
        """
        ext = Path(filename).suffix.lower()
        
        loaders = {
            '.yaml': self.load_yaml,
            '.yml': self.load_yaml,
            '.json': self.load_json,
            '.csv': self.load_csv,
            '.xlsx': self.load_excel,
            '.xls': self.load_excel
        }
        
        loader = loaders.get(ext)
        if not loader:
            raise ValueError(f"不支持的数据文件格式: {ext}")
        
        return loader(filename, **kwargs)


def parametrize_data(
    data_provider: DataProvider,
    filename: str,
    ids_field: str = 'name',
    **kwargs
):
    """
    为pytest提供参数化数据
    
    Args:
        data_provider: 数据提供器实例
        filename: 数据文件名
        ids_field: 用例ID字段
        **kwargs: 传递给load方法的参数
    
    Returns:
        pytest参数化装饰器
    
    使用示例：
        @parametrize_data(DataProvider(), 'login_data.yaml')
        def test_login(test_data: TestData):
            # 测试逻辑
            pass
    """
    test_data_list = data_provider.load(filename, **kwargs)
    
    # 生成用例ID
    ids = [getattr(td, ids_field, f'case_{i}') for i, td in enumerate(test_data_list)]
    
    return pytest.mark.parametrize(
        'test_data',
        test_data_list,
        ids=ids
    )


class DataDrivenTest:
    """
    数据驱动测试基类
    
    使用示例：
        class TestLogin(DataDrivenTest):
            data_file = 'login_data.yaml'
            
            def run_test(self, test_data: TestData):
                # 执行测试
                pass
    """
    
    data_file: str = ''
    data_provider: Optional[DataProvider] = None
    
    @classmethod
    def setup_class(cls):
        if cls.data_provider is None:
            cls.data_provider = DataProvider()
    
    @classmethod
    def get_test_data(cls) -> List[TestData]:
        """获取测试数据"""
        if not cls.data_file:
            return []
        return cls.data_provider.load(cls.data_file)
    
    @pytest.mark.parametrize('test_data', get_test_data, ids=lambda x: x.name)
    def test_data_driven(self, test_data: TestData):
        """数据驱动测试方法"""
        self.run_test(test_data)
    
    def run_test(self, test_data: TestData):
        """子类需要实现的测试逻辑"""
        raise NotImplementedError("子类必须实现run_test方法")
