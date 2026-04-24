"""
JSON Schema 验证工具

用于验证 API 响应是否符合预定义的 JSON Schema
"""
import json
import jsonschema
from jsonschema import validate, ValidationError
from pathlib import Path
from typing import Any, Dict, Optional


class SchemaValidator:
    """JSON Schema 验证器"""
    
    def __init__(self, schema_dir: str = "schemas"):
        """
        初始化 Schema 验证器
        
        Args:
            schema_dir: Schema 文件目录
        """
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载所有 Schema 文件"""
        if not self.schema_dir.exists():
            raise FileNotFoundError(f"Schema 目录不存在: {self.schema_dir}")
        
        for schema_file in self.schema_dir.glob("*.json"):
            schema_name = schema_file.stem
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    self.schemas[schema_name] = schema
            except json.JSONDecodeError as e:
                raise ValueError(f"Schema 文件 {schema_file} 格式错误: {e}")
    
    def validate_response(self, response_data: Any, schema_name: str) -> bool:
        """
        验证响应数据是否符合指定的 Schema
        
        Args:
            response_data: 要验证的响应数据
            schema_name: Schema 名称（不带 .json 扩展名）
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        if schema_name not in self.schemas:
            raise ValueError(f"Schema {schema_name} 不存在")
        
        schema = self.schemas[schema_name]
        validate(instance=response_data, schema=schema)
        return True
    
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的 Schema
        
        Args:
            schema_name: Schema 名称
            
        Returns:
            Optional[Dict[str, Any]]: Schema 字典
        """
        return self.schemas.get(schema_name)


# 创建全局验证器实例
schema_validator = SchemaValidator()


def validate_schema(response_data: Any, schema_name: str) -> bool:
    """
    验证响应数据是否符合指定的 Schema
    
    Args:
        response_data: 要验证的响应数据
        schema_name: Schema 名称
        
    Returns:
        bool: 验证是否通过
    """
    return schema_validator.validate_response(response_data, schema_name)


def get_schema(schema_name: str) -> Optional[Dict[str, Any]]:
    """
    获取指定的 Schema
    
    Args:
        schema_name: Schema 名称
        
    Returns:
        Optional[Dict[str, Any]]: Schema 字典
    """
    return schema_validator.get_schema(schema_name)
