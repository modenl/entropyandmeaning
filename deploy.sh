#!/bin/bash
# 快速部署脚本 - 发布到GitHub

echo "📚 《构建统一的世界观》GitHub Pages 部署脚本"
echo "================================================"

# 检查git是否已初始化
if [ ! -d ".git" ]; then
    echo "🔧 初始化Git仓库..."
    git init
    git branch -M main
fi

# 生成HTML文件
echo "🔨 重新生成HTML文件..."
python3 generate_html.py

# 添加所有文件
echo "📦 添加文件到Git..."
git add .

# 提交
echo "💾 提交更改..."
read -p "请输入提交信息 (直接回车使用默认信息): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update book content - $(date +%Y-%m-%d)"
fi
git commit -m "$commit_msg"

# 检查是否已添加远程仓库
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  尚未添加远程仓库"
    echo "请手动执行以下命令（替换yourusername为你的GitHub用户名）："
    echo ""
    echo "  git remote add origin https://github.com/yourusername/entropyandmeaning.git"
    echo "  git push -u origin main"
    echo ""
else
    # 推送到GitHub
    echo "🚀 推送到GitHub..."
    git push origin main

    echo ""
    echo "✅ 部署完成！"
    echo ""
    echo "📍 你的网站将在几分钟后可访问："
    echo "   https://yourusername.github.io/entropyandmeaning/"
    echo ""
    echo "💡 提示：首次发布需要在GitHub仓库设置中启用Pages（选择main分支的/docs文件夹）"
fi

echo ""
echo "================================================"
echo "感谢使用！如有问题请查看 GITHUB_PUBLISH_GUIDE.md"
