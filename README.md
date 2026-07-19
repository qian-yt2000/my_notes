# 我的笔记网站

基于 Markdown + Python 的个人笔记静态网站，托管在 GitHub Pages 上。

## 快速开始

### 本地预览

```bash
python build.py
```

然后用浏览器打开 `output/index.html` 预览效果。

### 一键发布 🚀

```bash
.\publish.ps1 "提交信息"
```

执行后自动完成：**构建网站 → git 提交 → 推送到 GitHub → Actions 自动部署**

## 如何添加笔记

1. 在 `notes/` 目录下创建或编辑 `.md` 文件
2. 运行 `python build.py` 本地预览（可选）
3. 运行 `.\publish.ps1 "新增: xxx"` 一键发布 🎉

## 功能

- **日/夜间模式**：点击右上角 🌙/☀️ 切换，偏好自动保存
- **可折叠侧边栏**：点击左上角 ☰ 收起/展开
- **实时搜索**：在首页侧边栏搜索框输入关键词过滤笔记
- **响应式设计**：手机端自动适配，侧边栏变为抽屉式
- **自动部署**：推送后 GitHub Actions 自动构建并部署

## 项目结构

```
notes-site/
├── notes/          ← 在这里写 Markdown 笔记
├── build.py        ← 构建脚本
├── publish.ps1     ← 一键发布脚本
├── output/         ← 生成的静态网站（已 gitignore）
└── README.md
```
