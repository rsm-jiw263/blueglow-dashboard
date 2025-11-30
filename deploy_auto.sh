#!/bin/bash

echo "🚀 Blue Tears Dashboard - 一键部署向导"
echo "=========================================="
echo ""

# 检查依赖
echo "📋 正在检查部署准备情况..."
python3 check_deployment.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 部署检查失败，请先修复上述问题"
    exit 1
fi

echo ""
echo "✅ 所有文件就绪！"
echo ""

# 询问用户
read -p "📌 你是否已经创建了 GitHub 仓库？(y/n): " has_repo

if [ "$has_repo" != "y" ]; then
    echo ""
    echo "📝 请先创建 GitHub 仓库："
    echo "   1. 访问 https://github.com/new"
    echo "   2. 仓库名：blueglow-dashboard"
    echo "   3. 设置为 Public"
    echo "   4. 不要初始化 README"
    echo ""
    read -p "创建好后按回车继续..."
fi

echo ""
read -p "🔗 请输入你的 GitHub 仓库地址 (例如：https://github.com/username/repo.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ 仓库地址不能为空"
    exit 1
fi

echo ""
echo "📦 开始 Git 操作..."
echo ""

# 初始化 git（如果需要）
if [ ! -d .git ]; then
    echo "初始化 Git 仓库..."
    git init
fi

# 添加文件
echo "添加文件到 Git..."
git add .

# 提交
echo "提交更改..."
git commit -m "Blue Tears Dashboard - Initial deployment"

# 添加远程仓库
echo "连接到 GitHub..."
git remote remove origin 2>/dev/null
git remote add origin "$repo_url"

# 推送
echo "推送到 GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 成功推送到 GitHub！"
    echo ""
    echo "🌐 下一步：部署到 Streamlit Cloud"
    echo "=================================="
    echo ""
    echo "1. 访问 https://share.streamlit.io"
    echo "2. 用 GitHub 账号登录"
    echo "3. 点击 'New app'"
    echo "4. 选择你的仓库和分支"
    echo "5. Main file: app_en.py"
    echo "6. Advanced settings:"
    echo "   - Requirements file: requirements_streamlit.txt"
    echo "7. 点击 'Deploy!'"
    echo ""
    echo "几分钟后，你的应用就会上线！"
    echo ""
    echo "应用地址格式："
    echo "https://你的用户名-blueglow-dashboard.streamlit.app"
    echo ""
    echo "🎉 完成后，你可以把链接分享给任何人！"
else
    echo ""
    echo "❌ 推送失败，请检查："
    echo "   - GitHub 仓库地址是否正确"
    echo "   - 是否有权限访问该仓库"
    echo "   - 网络连接是否正常"
fi
