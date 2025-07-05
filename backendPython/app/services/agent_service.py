from typing import Any, Iterator

from app.models.schemas import AgentTask
from app.agents.supervisorAgent import initialize_supervisor_agent

class AgentService:

    def __init__(self):
        # 初始化服务
        self.init_hierarchial_agent()

    def init_hierarchial_agent(self):
        """初始化Hierarchial Agent Teams"""
        self.super_graph = initialize_supervisor_agent()
        # 初始化成功
        print("Hierarchial Agent Teams initialized.")

    def execute_agent_task(self, agent_task: AgentTask) -> Iterator[dict[str, Any] | Any]:
        """执行代理任务"""
        if not self.super_graph:
            raise Exception("Hierarchial Agent Teams not initialized.")
        # 将任务消息传递给super_graph
        if not agent_task.messages:
            raise ValueError("No messages provided in the agent task.")
        message = agent_task.messages[-1]
        limits = agent_task.max_depth
        return self.super_graph.stream(
            {
                "messages": [
                    ("user", message)
                ],
            },
            {"recursion_limit": limits},
        )