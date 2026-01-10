"""
测试验证器选择逻辑
"""
import logging
from src.data.database import IdiomDatabase
from src.data.models import GameConfig
from src.ai.lmstudio_client import LMStudioClient
from src.core.game_manager import GameManager

# 设置日志
logging.basicConfig(level=logging.INFO)

# 初始化
database = IdiomDatabase("resources/idioms.db")
ai_client = LMStudioClient("http://localhost:1234", "")
config = GameConfig(difficulty="normal", time_limit=60, allow_homophone=False, max_hints=3)

print("=" * 50)
print("测试1: use_llm_validator=False (数据库验证器)")
print("=" * 50)
gm_db = GameManager(config, database, ai_client, use_llm_validator=False)
print(f"验证器类型: {type(gm_db.validator).__name__}")
print(f"验证器模块: {type(gm_db.validator).__module__}")
print()

print("=" * 50)
print("测试2: use_llm_validator=True (LLM验证器)")
print("=" * 50)
gm_llm = GameManager(config, database, ai_client, use_llm_validator=True)
print(f"验证器类型: {type(gm_llm.validator).__name__}")
print(f"验证器模块: {type(gm_llm.validator).__module__}")
print()

# 清理
database.close()
