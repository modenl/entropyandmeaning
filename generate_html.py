#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将markdown章节转换为HTML网页
"""

import re
import os

# 章节配置
CHAPTERS = [
    {"id": "preface", "file": "前言_完整扩充版.md", "title": "前言", "prev": None, "next": "chapter1"},
    {"id": "chapter1", "file": "第1章_本体论_完整扩充版.md", "title": "第1章 本体论", "prev": "preface", "next": "chapter2"},
    {"id": "chapter2", "file": "第2章_时间逻辑因果_完整扩充版.md", "title": "第2章 时间、逻辑、因果", "prev": "chapter1", "next": "chapter3"},
    {"id": "chapter3", "file": "第3章_数学与物理_完整扩充版.md", "title": "第3章 数学与物理", "prev": "chapter2", "next": "chapter4"},
    {"id": "chapter4", "file": "第4章_量子力学_完整扩充版.md", "title": "第4章 量子力学", "prev": "chapter3", "next": "chapter5"},
    {"id": "chapter5", "file": "第5章_复杂性与涌现_完整扩充版.md", "title": "第5章 复杂性与涌现", "prev": "chapter4", "next": "chapter6"},
    {"id": "chapter6", "file": "第6章_生命与演化_完整扩充版.md", "title": "第6章 生命与演化", "prev": "chapter5", "next": "chapter7"},
    {"id": "chapter7", "file": "第7章_意识_完整扩充版.md", "title": "第7章 意识", "prev": "chapter6", "next": "chapter8"},
    {"id": "chapter8", "file": "第8章_AI_完整扩充版.md", "title": "第8章 人工智能", "prev": "chapter7", "next": "chapter9"},
    {"id": "chapter9", "file": "第9章_意义_完整扩充版.md", "title": "第9章 意义", "prev": "chapter8", "next": "chapter10"},
    {"id": "chapter10", "file": "第10章_结论_完整扩充版.md", "title": "第10章 结论", "prev": "chapter9", "next": None},
]

def convert_md_to_html(markdown_text):
    """简单的markdown到HTML转换"""
    html = markdown_text

    # 步骤1: 提取并保护代码块
    code_blocks = []
    def save_code_block(match):
        code_content = match.group(1)
        placeholder = f'___CODE_BLOCK_{len(code_blocks)}___'
        code_blocks.append(code_content)
        return placeholder

    html = re.sub(r'```\n(.*?)\n```', save_code_block, html, flags=re.DOTALL)

    # 步骤2: 转换标题
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

    # 转换引用块
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # 转换粗体和斜体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # 转换行内代码（单反引号）
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # 转换列表（改进版本）
    lines = html.split('\n')
    new_lines = []
    in_ul = False
    in_ol = False
    in_nested_ul = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_indented = line.startswith('   ')  # 3个或更多空格表示嵌套

        if stripped.startswith('- '):
            # 无序列表项
            if is_indented:
                # 嵌套的无序列表
                if not in_nested_ul:
                    new_lines.append('<ul>')
                    in_nested_ul = True
                new_lines.append('<li>' + stripped[2:] + '</li>')
            else:
                # 顶层无序列表
                if in_nested_ul:
                    new_lines.append('</ul>')
                    in_nested_ul = False
                if in_ol:
                    new_lines.append('</ol>')
                    in_ol = False
                if not in_ul:
                    new_lines.append('<ul>')
                    in_ul = True
                new_lines.append('<li>' + stripped[2:] + '</li>')
        elif re.match(r'^\d+\. ', stripped):
            # 有序列表项（保持连续编号，不重新开始）
            if in_nested_ul:
                new_lines.append('</ul>')
                in_nested_ul = False
            if in_ul and not in_ol:
                # 如果之前是无序列表但不是在有序列表中，关闭它
                new_lines.append('</ul>')
                in_ul = False
            if not in_ol:
                # 只有第一次遇到有序列表时才打开<ol>
                new_lines.append('<ol>')
                in_ol = True
            # 继续在同一个<ol>中添加<li>
            new_lines.append('<li>' + re.sub(r'^\d+\. ', '', stripped) + '</li>')
        else:
            # 非列表行
            # 检查是否应该关闭列表
            should_close_lists = False
            if not stripped:
                # 空行 - 只关闭嵌套的ul，不关闭外层的ol和ul
                if in_nested_ul:
                    new_lines.append('</ul>')
                    in_nested_ul = False
                new_lines.append(line)
            elif stripped and not is_indented and not stripped.startswith('<'):
                # 非缩进的内容行（可能是标题或段落）
                # 只有当真正遇到非列表内容时才关闭所有列表
                # 检查下一行是否还是列表
                next_is_list = False
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    if next_stripped.startswith('-') or re.match(r'^\d+\.', next_stripped):
                        next_is_list = True

                if not next_is_list:
                    should_close_lists = True

                if should_close_lists:
                    if in_nested_ul:
                        new_lines.append('</ul>')
                        in_nested_ul = False
                    if in_ul:
                        new_lines.append('</ul>')
                        in_ul = False
                    if in_ol:
                        new_lines.append('</ol>')
                        in_ol = False

                # 转换段落
                if (stripped.startswith('$$') or
                    (stripped.endswith('$$') and stripped.startswith('$$')) or
                    '___CODE_BLOCK_' in stripped):
                    new_lines.append(stripped)
                elif not (in_ul or in_ol or in_nested_ul):
                    new_lines.append('<p>' + stripped + '</p>')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

    if in_nested_ul:
        new_lines.append('</ul>')
    if in_ul:
        new_lines.append('</ul>')
    if in_ol:
        new_lines.append('</ol>')

    html = '\n'.join(new_lines)

    # 步骤3: 还原代码块（将空格转换为&nbsp;以保证对齐）
    for i, code_content in enumerate(code_blocks):
        placeholder = f'___CODE_BLOCK_{i}___'
        # 将空格转换为&nbsp;，保留换行符
        code_with_nbsp = code_content.replace(' ', '&nbsp;')
        html = html.replace(placeholder, f'<pre><code>{code_with_nbsp}</code></pre>')

    return html

def get_toc_item(chapter_id, current_id, title, link):
    """生成目录项"""
    active_class = 'class="active"' if chapter_id == current_id else ''
    return f'<li><a href="{link}" {active_class}>{title}</a></li>'

def create_chapter_html(chapter_info, base_dir=''):
    """为单个章节创建HTML"""
    chapter_id = chapter_info['id']
    md_file = chapter_info['file']
    title = chapter_info['title']
    prev_link = chapter_info['prev'] + '.html' if chapter_info['prev'] else None
    next_link = chapter_info['next'] + '.html' if chapter_info['next'] else None

    # 读取markdown文件
    md_path = os.path.join(base_dir, md_file)
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"警告: 找不到文件 {md_path}")
        markdown_content = f"# {title}\n\n内容正在生成中..."

    # 转换为HTML
    content_html = convert_md_to_html(markdown_content)

    # 生成目录
    toc_html = '<ul class="toc">'
    toc_html += '<li><a href="index.html">主页</a></li>'
    for ch in CHAPTERS:
        active = 'class="active"' if ch['id'] == chapter_id else ''
        toc_html += f'<li><a href="{ch["id"]}.html" {active}>{ch["title"]}</a></li>'
    toc_html += '</ul>'

    # 生成导航按钮
    nav_buttons = '<div class="chapter-nav">'
    if prev_link:
        nav_buttons += f'<a href="{prev_link}" class="nav-button prev">← 上一章</a>'
    else:
        nav_buttons += '<span></span>'

    if next_link:
        nav_buttons += f'<a href="{next_link}" class="nav-button next">下一章 →</a>'
    else:
        nav_buttons += '<span></span>'
    nav_buttons += '</div>'

    # 完整HTML模板
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 构建统一的世界观</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <h1 class="nav-title">构建统一的世界观</h1>
            <button class="menu-toggle" id="menuToggle">☰</button>
        </div>
    </nav>

    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-content">
                <h2>目录</h2>
                {toc_html}
            </div>
        </aside>

        <main class="content">
            <article class="chapter-content">
                {content_html}
            </article>

            {nav_buttons}
        </main>
    </div>

    <footer class="footer">
        <p>&copy; 2025 《构建统一的世界观》| 基于自然主义与功能主义的世界观框架</p>
        <p><a href="index.html">返回主页</a> | <a href="https://github.com/yourusername/entropyandmeaning">GitHub Repository</a></p>
    </footer>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');

        menuToggle.addEventListener('click', () => {{
            sidebar.classList.toggle('active');
        }});

        document.addEventListener('click', (e) => {{
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {{
                sidebar.classList.remove('active');
            }}
        }});

        // KaTeX 自动渲染
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '$', right: '$', display: false}}
                ],
                throwOnError: false
            }});
        }});
    </script>
</body>
</html>
'''

    return html_content

def main():
    base_dir = '/Users/xueminliu/work/entropyandmeaning'
    output_dir = os.path.join(base_dir, 'docs')

    print("开始生成HTML文件...")

    for chapter in CHAPTERS:
        html_content = create_chapter_html(chapter, base_dir)
        output_file = os.path.join(output_dir, chapter['id'] + '.html')

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ 已生成: {chapter['title']} ({chapter['id']}.html)")

    print(f"\n✅ 所有HTML文件已生成到: {output_dir}")
    print("\n下一步:")
    print("1. cd /Users/xueminliu/work/entropyandmeaning")
    print("2. git init (如果还未初始化)")
    print("3. git add .")
    print('4. git commit -m "Add book website"')
    print("5. 在GitHub创建仓库并推送")
    print("6. 在仓库设置中启用GitHub Pages，选择/docs文件夹")

if __name__ == '__main__':
    main()
