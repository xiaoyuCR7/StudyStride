"""
请求构建器

提供链式API构建HTTP请求
"""
from typing import Dict, Any, Optional, List
from enum import Enum


class SortOrder(Enum):
    """排序顺序"""
    ASC = "asc"
    DESC = "desc"


class RequestBuilder:
    """
    请求构建器
    
    提供流畅的API构建查询请求
    
    使用示例：
        builder = RequestBuilder()
        builder.select('*').eq('user_id', '123').order('created_at', SortOrder.DESC)
        params = builder.build()
    """
    
    def __init__(self):
        self._select: Optional[str] = None
        self._filters: Dict[str, Any] = {}
        self._orders: List[tuple] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._range: Optional[tuple] = None
    
    def select(self, columns: str = '*') -> 'RequestBuilder':
        """
        选择列
        
        Args:
            columns: 列名，多个列用逗号分隔
        """
        self._select = columns
        return self
    
    def eq(self, column: str, value: Any) -> 'RequestBuilder':
        """等于"""
        self._filters[column] = f"eq.{value}"
        return self
    
    def neq(self, column: str, value: Any) -> 'RequestBuilder':
        """不等于"""
        self._filters[column] = f"neq.{value}"
        return self
    
    def gt(self, column: str, value: Any) -> 'RequestBuilder':
        """大于"""
        self._filters[column] = f"gt.{value}"
        return self
    
    def gte(self, column: str, value: Any) -> 'RequestBuilder':
        """大于等于"""
        self._filters[column] = f"gte.{value}"
        return self
    
    def lt(self, column: str, value: Any) -> 'RequestBuilder':
        """小于"""
        self._filters[column] = f"lt.{value}"
        return self
    
    def lte(self, column: str, value: Any) -> 'RequestBuilder':
        """小于等于"""
        self._filters[column] = f"lte.{value}"
        return self
    
    def like(self, column: str, pattern: str) -> 'RequestBuilder':
        """模糊匹配"""
        self._filters[column] = f"like.{pattern}"
        return self
    
    def ilike(self, column: str, pattern: str) -> 'RequestBuilder':
        """不区分大小写模糊匹配"""
        self._filters[column] = f"ilike.{pattern}"
        return self
    
    def is_null(self, column: str, is_null: bool = True) -> 'RequestBuilder':
        """是否为空"""
        self._filters[column] = f"is.{'' if is_null else 'not.'}null"
        return self
    
    def in_(self, column: str, values: List[Any]) -> 'RequestBuilder':
        """IN查询"""
        values_str = ','.join(str(v) for v in values)
        self._filters[column] = f"in.({values_str})"
        return self
    
    def between(self, column: str, start: Any, end: Any) -> 'RequestBuilder':
        """范围查询"""
        self._filters[column] = f"btwn.{start},{end}"
        return self
    
    def order(self, column: str, order: SortOrder = SortOrder.ASC) -> 'RequestBuilder':
        """
        排序
        
        Args:
            column: 排序列
            order: 排序顺序
        """
        self._orders.append((column, order.value))
        return self
    
    def limit(self, count: int) -> 'RequestBuilder':
        """限制返回数量"""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'RequestBuilder':
        """跳过指定数量"""
        self._offset = count
        return self
    
    def range(self, start: int, end: int) -> 'RequestBuilder':
        """范围限制"""
        self._range = (start, end)
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        构建请求参数
        
        Returns:
            请求参数字典
        """
        params = {}
        
        # 选择列
        if self._select:
            params['select'] = self._select
        
        # 过滤条件
        params.update(self._filters)
        
        # 排序
        if self._orders:
            order_parts = []
            for col, order in self._orders:
                if order == SortOrder.DESC.value:
                    order_parts.append(f"{col}.desc")
                else:
                    order_parts.append(f"{col}.asc")
            params['order'] = ','.join(order_parts)
        
        # 限制和偏移
        if self._limit is not None:
            params['limit'] = self._limit
        
        if self._offset is not None:
            params['offset'] = self._offset
        
        # 范围
        if self._range:
            params['range'] = f"{self._range[0]}-{self._range[1]}"
        
        return params
    
    def reset(self) -> 'RequestBuilder':
        """重置构建器"""
        self._select = None
        self._filters.clear()
        self._orders.clear()
        self._limit = None
        self._offset = None
        self._range = None
        return self
