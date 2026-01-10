#!/usr/bin/env python3
"""
成语搜索工具 - 帮助快速查找可用的成语
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import IdiomDatabase


def search_idioms():
    """搜索成语"""
    db = IdiomDatabase('resources/idioms.db')

    print("=" * 60)
    print("成语接龙 - 成语搜索工具")
    print("=" * 60)
    print(f"数据库共有 {db.get_total_count()} 个成语\n")

    while True:
        print("\n请选择操作:")
        print("1. 按首字搜索")
        print("2. 按尾字搜索")
        print("3. 搜索包含特定字的成语")
        print("4. 显示所有可用的起始字")
        print("5. 退出")

        choice = input("\n请输入选项 (1-5): ").strip()

        if choice == '1':
            char = input("请输入首字: ").strip()
            if char:
                idioms = db.get_idioms_by_starting_char(char)
                if idioms:
                    print(f"\n以'{char}'字开头的成语 ({len(idioms)}个):")
                    for i, idiom in enumerate(idioms, 1):
                        print(f"  {i}. {idiom.word} - {idiom.explanation}")
                else:
                    print(f"\n没有找到以'{char}'字开头的成语")

        elif choice == '2':
            # 按尾字搜索
            import sqlite3
            char = input("请输入尾字: ").strip()
            if char:
                conn = sqlite3.connect('resources/idioms.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT word, explanation FROM idioms WHERE last_char = ? LIMIT 20",
                    (char,)
                )
                results = cursor.fetchall()
                conn.close()

                if results:
                    print(f"\n以'{char}'字结尾的成语 (最多显示20个):")
                    for i, (word, explanation) in enumerate(results, 1):
                        print(f"  {i}. {word} - {explanation}")
                else:
                    print(f"\n没有找到以'{char}'字结尾的成语")

        elif choice == '3':
            keyword = input("请输入要搜索的字: ").strip()
            if keyword:
                idioms = db.search_idioms(keyword, limit=20)
                if idioms:
                    print(f"\n包含'{keyword}'的成语 (最多显示20个):")
                    for i, idiom in enumerate(idioms, 1):
                        print(f"  {i}. {idiom.word} - {idiom.explanation}")
                else:
                    print(f"\n没有找到包含'{keyword}'的成语")

        elif choice == '4':
            # 显示所有可用的起始字
            import sqlite3
            from collections import Counter

            conn = sqlite3.connect('resources/idioms.db')
            cursor = conn.cursor()
            cursor.execute('SELECT first_char FROM idioms')
            chars = [row[0] for row in cursor.fetchall()]
            conn.close()

            char_count = Counter(chars)
            print(f"\n可用的起始字 ({len(char_count)}个):")
            print(" ".join(sorted(char_count.keys())))

            # 显示每个字开头的成语数量
            print("\n按成语数量排序:")
            for char, count in char_count.most_common():
                print(f"  {char}: {count}个")

        elif choice == '5':
            print("\n再见！")
            break

        else:
            print("\n无效的选项，请重新选择")


if __name__ == '__main__':
    search_idioms()
