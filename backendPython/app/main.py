import json
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.models.schemas import AgentTask
from app.services.agent_service import AgentService

app = FastAPI(
    title="Hierarchial Agent Teams",
    description="实现Hierarchial Agent Teams的后端服务，支持流式输出",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_service = AgentService()

@app.post("/agentTask", response_class=StreamingResponse)
def execute_agent_task(agentTask: AgentTask):
    """获取代理团队响应（支持流式输出）"""
    response = agent_service.execute_agent_task(agentTask)
    
    def generate_ndjson():
        """生成NDJSON格式的流式响应"""
        for output in response:
            if 'supervisor' in output:
                current_agent = 'supervisor'
                next_agent = output['supervisor']['next']
                yield json.dumps({
                    "currentAgent": current_agent,
                    "nextAgent": next_agent,
                    "messages": 'Routing to next node: ' + next_agent
                }) + "\n"
            else:
                current_agent = next_agent
                next_agent = 'supervisor'
                human_message = output[current_agent]['messages']
                yield json.dumps({
                    "currentAgent": current_agent,
                    "nextAgent": next_agent,
                    "messages": human_message[-1].content
                }) + "\n"

    if agentTask.stream:
        # 流式响应
        # return StreamingResponse(
        #     response,
        #     media_type="text/event-stream"
        # )
        return StreamingResponse(
            generate_ndjson(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应 - 收集所有输出并返回
        pass