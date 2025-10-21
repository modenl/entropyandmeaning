# GitHub发布完整指南

本指南将帮助你将《构建统一的世界观》网站发布到GitHub Pages。

## 📋 准备工作

### 1. 确保已安装Git

```bash
# 检查Git是否已安装
git --version

# 如果未安装，访问 https://git-scm.com/ 下载安装
```

### 2. 配置Git（首次使用）

```bash
# 设置你的用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 创建GitHub账号

如果还没有GitHub账号，访问 https://github.com 注册。

## 🚀 发布步骤

### 步骤1：初始化本地Git仓库

```bash
# 进入项目目录
cd ~/work/entropyandmeaning

# 初始化Git仓库
git init

# 查看当前状态
git status
```

### 步骤2：添加文件到Git

```bash
# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 提交到本地仓库
git commit -m "Initial commit: 完整书稿与网站"
```

### 步骤3：在GitHub创建远程仓库

1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - **Repository name**: `entropyandmeaning` （或其他你喜欢的名字）
   - **Description**: `《构建统一的世界观》- 从物理到意识，从演化到意义的自然主义框架`
   - **Public** （选择公开，这样才能使用GitHub Pages）
   - ❌ **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 步骤4：连接并推送到GitHub

```bash
# 添加远程仓库（替换yourusername为你的GitHub用户名）
git remote add origin https://github.com/yourusername/entropyandmeaning.git

# 重命名主分支为main（GitHub新标准）
git branch -M main

# 推送到GitHub
git push -u origin main
```

如果推送失败，可能需要身份验证：
- **推荐方式**：使用Personal Access Token
  1. GitHub设置 → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token → 勾选 `repo` 权限
  3. 复制token（只显示一次！）
  4. 推送时用token替代密码

### 步骤5：启用GitHub Pages

1. 进入你的GitHub仓库页面
2. 点击 **Settings**（设置）
3. 左侧菜单找到 **Pages**
4. 在 **Source** 部分：
   - **Branch**: 选择 `main`
   - **Folder**: 选择 `/docs`
   - 点击 **Save**

5. 等待1-2分钟，页面会显示：
   ```
   ✓ Your site is live at https://yourusername.github.io/entropyandmeaning/
   ```

### 步骤6：访问你的网站

打开浏览器，访问：
```
https://yourusername.github.io/entropyandmeaning/
```

🎉 **恭喜！你的书稿网站已成功发布！**

## 🔄 后续更新流程

当你修改了Markdown源文件或网站代码：

```bash
# 1. 重新生成HTML（如果修改了Markdown）
python3 generate_html.py

# 2. 查看修改
git status
git diff

# 3. 添加修改
git add .

# 4. 提交修改
git commit -m "Update: 修改说明"

# 5. 推送到GitHub
git push

# GitHub Pages会自动更新（可能需要几分钟）
```

## 🛠️ 常见问题

### Q1: 推送时提示"Permission denied"

**解决方案**：使用Personal Access Token
```bash
# 推送时输入：
Username: yourusername
Password: ghp_你的PersonalAccessToken
```

### Q2: GitHub Pages不显示最新内容

**解决方案**：
1. 清除浏览器缓存（Ctrl/Cmd + Shift + R 强制刷新）
2. 等待5-10分钟（GitHub Pages有部署延迟）
3. 检查仓库 Actions 标签，查看部署状态

### Q3: 404 Not Found错误

**解决方案**：
1. 确认 Settings → Pages 中选择了 `/docs` 文件夹
2. 确认 `docs/index.html` 文件存在
3. 等待几分钟让部署完成

### Q4: 样式/图片不显示

**解决方案**：
检查HTML中的资源路径是否正确：
- 相对路径：`<link href="style.css">` ✓
- 绝对路径：`<link href="/style.css">` （可能需要调整为相对路径）

### Q5: 想使用自定义域名

**步骤**：
1. 购买域名（如 `yourdomain.com`）
2. 在DNS设置中添加CNAME记录指向 `yourusername.github.io`
3. GitHub仓库 Settings → Pages → Custom domain 输入你的域名
4. 等待DNS生效（可能需要24-48小时）

## 📊 仓库统计（可选）

### 添加Badge到README

在 `README.md` 顶部已包含以下badge：
- GitHub Pages状态
- License信息

你可以添加更多：
```markdown
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=yourusername.entropyandmeaning)
![GitHub stars](https://img.shields.io/github/stars/yourusername/entropyandmeaning?style=social)
```

### 启用GitHub Analytics

1. Settings → Options → Features → Issues （启用Issue追踪）
2. Settings → Options → Features → Wikis （启用Wiki）
3. Insights标签查看访问统计

## 🔐 许可协议

确保在仓库根目录添加LICENSE文件：

```bash
# 创建CC BY-NC-SA 4.0 许可协议文件
# 访问 https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt
# 复制内容保存为 LICENSE 文件
```

## 📢 推广你的网站

1. **社交媒体**：分享到Twitter、微博、知乎
2. **学术社区**：发布到相关论坛（如豆瓣、Reddit）
3. **添加到目录**：
   - Awesome lists（如awesome-philosophy）
   - 学术资源网站
4. **SEO优化**：
   - 在README中添加关键词
   - 确保HTML有合适的meta标签

## ✅ 检查清单

发布前确认：

- [ ] 所有Markdown文件已转换为HTML
- [ ] 本地测试网站正常（`python3 -m http.server --directory docs 8000`）
- [ ] README.md中的链接已更新为实际地址
- [ ] .gitignore文件已创建
- [ ] LICENSE文件已添加
- [ ] GitHub仓库已创建
- [ ] 代码已推送到GitHub
- [ ] GitHub Pages已启用
- [ ] 网站可正常访问

## 📞 获取帮助

遇到问题？

1. **查看GitHub文档**: https://docs.github.com/pages
2. **Stack Overflow**: 搜索相关问题
3. **GitHub Issues**: 在本仓库提交Issue

---

**祝你发布顺利！分享给更多人吧！🚀**
