import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据存储路径
DATA_DIR = BASE_DIR / "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 默认配置
DEFAULT_MAX_AGENTS = 10
DEFAULT_MAX_TEAMS = 5
DEFAULT_STREAM_DELAY = 0.1  # 流输出延迟(秒)