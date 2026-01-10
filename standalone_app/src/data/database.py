"""
成语数据库管理
使用SQLite存储成语数据
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List
from src.data.models import Idiom
from src.utils.exceptions import DatabaseException


logger = logging.getLogger(__name__)


class IdiomDatabase:
    """成语数据库类"""

    def __init__(self, db_path: str = "resources/idioms.db"):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """连接数据库"""
        try:
            # 确保目录存在
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
            logger.info(f"成功连接数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"连接数据库失败: {str(e)}")
            raise DatabaseException(f"连接数据库失败: {str(e)}")

    def _create_tables(self) -> None:
        """创建数据表"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idioms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
                    pinyin TEXT NOT NULL,
                    first_char TEXT NOT NULL,
                    last_char TEXT NOT NULL,
                    first_pinyin TEXT NOT NULL,
                    last_pinyin TEXT NOT NULL,
                    explanation TEXT,
                    example TEXT,
                    difficulty INTEGER DEFAULT 1,
                    frequency REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_first_char
                ON idioms(first_char)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_char
                ON idioms(last_char)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_first_pinyin
                ON idioms(first_pinyin)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_pinyin
                ON idioms(last_pinyin)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_difficulty
                ON idioms(difficulty)
            """)

            self.conn.commit()
            logger.info("数据表创建成功")
        except Exception as e:
            logger.error(f"创建数据表失败: {str(e)}")
            raise DatabaseException(f"创建数据表失败: {str(e)}")

    def add_idiom(self, idiom: Idiom) -> bool:
        """
        添加成语

        Args:
            idiom: 成语对象

        Returns:
            是否添加成功
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO idioms
                (word, pinyin, first_char, last_char, first_pinyin, last_pinyin,
                 explanation, example, difficulty, frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idiom.word, idiom.pinyin,
                idiom.first_char, idiom.last_char,
                idiom.first_pinyin, idiom.last_pinyin,
                idiom.explanation, idiom.example,
                idiom.difficulty, idiom.frequency
            ))
            self.conn.commit()
            logger.debug(f"添加成语: {idiom.word}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"添加成语失败: {str(e)}")
            return False

    def get_idiom_by_name(self, word: str) -> Optional[Idiom]:
        """
        根据名称获取成语

        Args:
            word: 成语名称

        Returns:
            成语对象，不存在则返回None
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT word, pinyin, first_char, last_char,
                       first_pinyin, last_pinyin, explanation, example,
                       difficulty, frequency
                FROM idioms WHERE word = ?
            """, (word,))
            row = cursor.fetchone()
            if row:
                return Idiom(
                    word=row['word'],
                    pinyin=row['pinyin'],
                    first_char=row['first_char'],
                    last_char=row['last_char'],
                    first_pinyin=row['first_pinyin'],
                    last_pinyin=row['last_pinyin'],
                    explanation=row['explanation'],
                    example=row['example'],
                    difficulty=row['difficulty'],
                    frequency=row['frequency']
                )
            return None
        except Exception as e:
            logger.error(f"查询成语失败: {str(e)}")
            return None

    def get_idioms_by_starting_char(self, char: str) -> List[Idiom]:
        """
        根据首字获取成语列表

        Args:
            char: 首字

        Returns:
            成语列表
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT word, pinyin, first_char, last_char,
                       first_pinyin, last_pinyin, explanation, example,
                       difficulty, frequency
                FROM idioms WHERE first_char = ?
                ORDER BY frequency DESC, difficulty ASC
            """, (char,))
            rows = cursor.fetchall()
            return [
                Idiom(
                    word=row['word'],
                    pinyin=row['pinyin'],
                    first_char=row['first_char'],
                    last_char=row['last_char'],
                    first_pinyin=row['first_pinyin'],
                    last_pinyin=row['last_pinyin'],
                    explanation=row['explanation'],
                    example=row['example'],
                    difficulty=row['difficulty'],
                    frequency=row['frequency']
                ) for row in rows
            ]
        except Exception as e:
            logger.error(f"查询成语列表失败: {str(e)}")
            return []

    def get_random_idiom(self, difficulty: int = None) -> Optional[Idiom]:
        """
        获取随机成语

        Args:
            difficulty: 难度等级（1-5），None表示随机

        Returns:
            随机成语对象
        """
        cursor = self.conn.cursor()
        try:
            if difficulty:
                cursor.execute("""
                    SELECT word, pinyin, first_char, last_char,
                           first_pinyin, last_pinyin, explanation, example,
                           difficulty, frequency
                    FROM idioms WHERE difficulty = ?
                    ORDER BY RANDOM() LIMIT 1
                """, (difficulty,))
            else:
                cursor.execute("""
                    SELECT word, pinyin, first_char, last_char,
                           first_pinyin, last_pinyin, explanation, example,
                           difficulty, frequency
                    FROM idioms ORDER BY RANDOM() LIMIT 1
                """)
            row = cursor.fetchone()
            if row:
                return Idiom(
                    word=row['word'],
                    pinyin=row['pinyin'],
                    first_char=row['first_char'],
                    last_char=row['last_char'],
                    first_pinyin=row['first_pinyin'],
                    last_pinyin=row['last_pinyin'],
                    explanation=row['explanation'],
                    example=row['example'],
                    difficulty=row['difficulty'],
                    frequency=row['frequency']
                )
            return None
        except Exception as e:
            logger.error(f"获取随机成语失败: {str(e)}")
            return None

    def search_idioms(self, keyword: str, limit: int = 10) -> List[Idiom]:
        """
        搜索成语

        Args:
            keyword: 关键词
            limit: 返回数量限制

        Returns:
            匹配的成语列表
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT word, pinyin, first_char, last_char,
                       first_pinyin, last_pinyin, explanation, example,
                       difficulty, frequency
                FROM idioms WHERE word LIKE ?
                ORDER BY frequency DESC
                LIMIT ?
            """, (f'%{keyword}%', limit))
            rows = cursor.fetchall()
            return [
                Idiom(
                    word=row['word'],
                    pinyin=row['pinyin'],
                    first_char=row['first_char'],
                    last_char=row['last_char'],
                    first_pinyin=row['first_pinyin'],
                    last_pinyin=row['last_pinyin'],
                    explanation=row['explanation'],
                    example=row['example'],
                    difficulty=row['difficulty'],
                    frequency=row['frequency']
                ) for row in rows
            ]
        except Exception as e:
            logger.error(f"搜索成语失败: {str(e)}")
            return []

    def is_valid_idiom(self, word: str) -> bool:
        """
        验证成语是否存在

        Args:
            word: 成语名称

        Returns:
            是否存在
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM idioms WHERE word = ?", (word,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"验证成语失败: {str(e)}")
            return False

    def get_total_count(self) -> int:
        """
        获取成语总数

        Returns:
            成语总数
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) as count FROM idioms")
            row = cursor.fetchone()
            return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取成语总数失败: {str(e)}")
            return 0

    def load_from_file(self, file_path: str) -> int:
        """
        从文件批量导入成语

        Args:
            file_path: 文件路径，每行一个成语，格式：成语,拼音,解释,例句

        Returns:
            导入成功数量
        """
        from src.utils.pinyin import PinyinUtils

        count = 0
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(',', 3)
                    if len(parts) < 1:
                        continue

                    word = parts[0].strip()
                    if len(word) != 4:
                        continue

                    # 生成拼音
                    pinyin = PinyinUtils.get_pinyin(word, style='tone')
                    first_char = word[0]
                    last_char = word[-1]
                    first_pinyin = PinyinUtils.get_first_char_pinyin(first_char)
                    last_pinyin = PinyinUtils.get_first_char_pinyin(last_char)

                    idiom = Idiom(
                        word=word,
                        pinyin=pinyin,
                        first_char=first_char,
                        last_char=last_char,
                        first_pinyin=first_pinyin,
                        last_pinyin=last_pinyin,
                        explanation=parts[2].strip() if len(parts) > 2 else None,
                        example=parts[3].strip() if len(parts) > 3 else None,
                        difficulty=1,
                        frequency=0.0
                    )

                    if self.add_idiom(idiom):
                        count += 1

            logger.info(f"成功导入 {count} 个成语")
            return count
        except Exception as e:
            logger.error(f"导入成语失败: {str(e)}")
            return 0

    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
