#!/usr/bin/env python3
"""
笔记本验证测试
测试 La_Jolla_Blue_Tears_Feasibility_Study.ipynb 是否能正确运行
"""

import subprocess
import sys

def test_notebook():
    """使用 jupyter nbconvert 测试笔记本执行"""
    notebook_path = "La_Jolla_Blue_Tears_Feasibility_Study.ipynb"
    
    print("=" * 70)
    print("🧪 测试笔记本执行")
    print("=" * 70)
    print(f"笔记本: {notebook_path}")
    print()
    
    # 使用 nbconvert 执行笔记本
    cmd = [
        "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        "--ExecutePreprocessor.timeout=300",
        notebook_path
    ]
    
    try:
        print("▶️  开始执行笔记本...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print("✅ 笔记本执行成功！")
            print()
            print("所有单元格都已正确执行，没有错误。")
            return True
        else:
            print("❌ 笔记本执行失败")
            print()
            print("错误输出:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 执行超时（超过10分钟）")
        return False
    except FileNotFoundError:
        print("❌ 未找到 jupyter 命令")
        print("请先安装 Jupyter: pip install jupyter")
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

def quick_check():
    """快速检查关键文件是否存在"""
    import os
    
    print("=" * 70)
    print("🔍 快速检查")
    print("=" * 70)
    
    files_to_check = [
        "La_Jolla_Blue_Tears_Feasibility_Study.ipynb",
        "data/water_temp_lajolla.csv",
        "data/wind_lajolla.csv",
        "data/waves_lajolla.csv",
        "data/biolum_events_2020.csv"
    ]
    
    all_exist = True
    for file in files_to_check:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    print()
    return all_exist

if __name__ == "__main__":
    print()
    print("🌊 La Jolla Blue Tears Feasibility Study - 笔记本验证")
    print()
    
    # 快速检查
    if not quick_check():
        print("⚠️  部分文件缺失，但笔记本有fallback机制")
        print("   可以继续测试执行")
        print()
    
    # 提示用户
    print("此测试将执行整个笔记本，可能需要几分钟时间。")
    response = input("是否继续？ (y/n): ")
    
    if response.lower() != 'y':
        print("已取消测试")
        sys.exit(0)
    
    print()
    
    # 执行测试
    success = test_notebook()
    
    if success:
        print()
        print("=" * 70)
        print("🎉 恭喜！笔记本可以完全正常运行")
        print("=" * 70)
        sys.exit(0)
    else:
        print()
        print("=" * 70)
        print("⚠️  笔记本执行遇到问题，请检查错误信息")
        print("=" * 70)
        sys.exit(1)
