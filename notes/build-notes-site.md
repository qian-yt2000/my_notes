# 搭建个人笔记网站

使用 GitHub Pages 托管静态笔记网站的完整流程。

## 为什么选择静态网站

- **免费托管**：GitHub Pages 提供免费的静态网站托管
- **零服务器维护**：不需要管理服务器或数据库
- **版本控制**：所有笔记自动纳入 Git 版本管理
- **极速加载**：纯静态 HTML，没有后端延迟

## 项目结构

```
notes-site/
├── notes/          ← 在这里写 Markdown 笔记
├── build.js        ← 构建脚本
└── output/         ← 生成的静态网站
    ├── index.html
    ├── style.css
    └── notes/
```

## 使用流程

### 1. 写笔记

在 `notes/` 目录下创建 `.md` 文件，用 Markdown 格式写作。

### 2. 构建网站

```bash
node build.js
```

### 3. 本地预览

直接用浏览器打开 `output/index.html`。

### 4. 部署到 GitHub

将 `output/` 目录推送到 GitHub 仓库的 `gh-pages` 分支，或设置 GitHub Pages 指向 `main` 分支的 `/output` 目录。

## Markdown 写作建议

- 用 `#` 标题作为文章标题
- 代码块指定语言可获得语法高亮样式
- 善用列表和表格组织信息
- 添加合适的空行让排版更舒适
