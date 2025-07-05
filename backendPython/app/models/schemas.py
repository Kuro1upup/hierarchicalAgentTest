from pydantic import BaseModel

class AgentTask(BaseModel):
    """代理任务数据模型"""
    messages: list[str] = []
    max_depth: int = 150
    stream: bool = False