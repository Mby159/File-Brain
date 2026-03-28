# Contributing Guide

[中文版](#中文版)

Thank you for your interest in and support of the File Brain project! We welcome and appreciate community contributions. This guide will help you understand how to participate in the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Environment Setup](#development-environment-setup)
- [Code Style Guide](#code-style-guide)
- [Contribution Process](#contribution-process)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Code Review](#code-review)
- [Testing](#testing)
- [Documentation Contributions](#documentation-contributions)
- [Becoming a Maintainer](#becoming-a-maintainer)

## Code of Conduct

All contributors participating in this project should adhere to the following code of conduct:

- Be respectful and use welcoming and inclusive language
- Accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/file-brain.git
cd file-brain
```

### 2. Create Virtual Environment

```bash
# Using venv
python3 -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
python -m pytest
```

## Code Style Guide

- Follow PEP 8 code style guidelines
- Use 4 spaces for indentation
- Maximum line length is 88 characters
- Use type hints
- Write clear docstrings
- Add comments for complex logic

## Contribution Process

1. **Fork the Repository**: Fork the project repository on GitHub
2. **Create Branch**: Create a new branch in your fork
3. **Make Changes**: Implement features or fix bugs
4. **Run Tests**: Ensure all tests pass
5. **Commit Changes**: Use standardized commit message format
6. **Create Pull Request**: Submit PR to the main repository
7. **Code Review**: Respond to review comments and make necessary modifications
8. **Merge**: PR is merged into the main branch

## Commit Message Format

Commit messages should follow this format:

```
<type>: <description>

<detailed description>

<optional footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (not affecting functionality)
- `refactor`: Code refactoring (not adding features or fixing bugs)
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Changes to build process or auxiliary tools

### Example

```
feat: Add file monitoring feature

- Implemented file monitoring based on watchdog
- Support real-time indexing of new and modified files
- Added monitoring configuration options

Closes #123
```

## Pull Request Process

1. **Title**: Use a clear and concise title describing the PR content
2. **Description**:
   - Detailed explanation of your changes
   - Explain why these changes are needed
   - Mention related issues
   - Include test results
3. **Checklist**:
   - Ensure all tests pass
   - Ensure code follows style guidelines
   - Ensure documentation is updated

## Issue Reporting

If you find a bug, please report it following these steps:

1. **Search Existing Issues**: Check if someone has already reported the same issue
2. **Create New Issue**: Create a new issue using the provided template
3. **Provide Detailed Information**:
   - Description of the problem
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment information (OS, Python version, etc.)
   - Error logs (if any)

## Feature Requests

If you have a feature request, please submit it following these steps:

1. **Search Existing Requests**: Check if someone has already made the same request
2. **Create New Request**: Create a new feature request using the provided template
3. **Detailed Description**:
   - Description of the feature
   - Why this feature would be useful
   - Possible implementation approach
   - Any related reference materials

## Code Review

All PRs will undergo code review. The review process aims to ensure:

- High code quality
- Correct functionality
- Adequate test coverage
- Complete documentation

Please be patient during the review and actively respond to review comments.

## Testing

We encourage adding tests for all changes. Tests should:

- Cover new features and bug fixes
- Be concise and clear
- Run quickly

Run tests:

```bash
python -m pytest
```

## Documentation Contributions

Documentation contributions are equally important! You can:

- Improve existing documentation
- Add new tutorials or guides
- Fix errors in documentation
- Translate documentation

## Becoming a Maintainer

As the project grows, we may invite active contributors to become maintainers. Maintainer responsibilities include:

- Reviewing PRs
- Managing issues
- Releasing new versions
- Setting project roadmap

If you are interested in becoming a maintainer, please contact the project lead.

---

Thank you again for your contribution to the File Brain project! Your participation will help us build a better file management tool.

---

# 中文版

感谢您对 File Brain 项目的兴趣和支持！我们非常欢迎并感谢社区的贡献。本指南将帮助您了解如何参与到项目中来。

## 目录

- [行为准则](#行为准则)
- [开发环境设置](#开发环境设置)
- [代码风格指南](#代码风格指南)
- [贡献流程](#贡献流程)
- [提交信息格式](#提交信息格式)
- [Pull Request 流程](#pull-request-流程)
- [问题报告](#问题报告)
- [功能请求](#功能请求)
- [代码审查](#代码审查)
- [测试](#测试)
- [文档贡献](#文档贡献)
- [成为维护者](#成为维护者)

## 行为准则

参与本项目的所有贡献者都应遵守以下行为准则：

- 尊重他人，使用友好和包容的语言
- 接受建设性的批评
- 关注社区的最佳利益
- 对其他社区成员表示同理心

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/file-brain.git
cd file-brain
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行测试

```bash
python -m pytest
```

## 代码风格指南

- 遵循 PEP 8 代码风格规范
- 使用 4 个空格进行缩进
- 最大行长度为 88 字符
- 使用类型提示
- 编写清晰的文档字符串
- 为复杂逻辑添加注释

## 贡献流程

1. **Fork 仓库**：在 GitHub 上 fork 项目仓库
2. **创建分支**：在您的 fork 中创建一个新分支
3. **进行更改**：实现功能或修复 bug
4. **运行测试**：确保所有测试通过
5. **提交更改**：使用规范的提交信息格式
6. **创建 Pull Request**：向主仓库提交 PR
7. **代码审查**：回应审查意见并进行必要的修改
8. **合并**：PR 被合并到主分支

## 提交信息格式

提交信息应遵循以下格式：

```
<类型>: <描述>

<详细描述>

<可选的脚注>
```

### 类型

- `feat`：新功能
- `fix`：bug 修复
- `docs`：文档更改
- `style`：代码风格更改（不影响功能）
- `refactor`：代码重构（不添加功能或修复 bug）
- `perf`：性能改进
- `test`：添加或修改测试
- `chore`：构建过程或辅助工具的更改

### 示例

```
feat: 添加文件监控功能

- 实现了基于 watchdog 的文件监控
- 支持实时索引新文件和修改的文件
- 添加了监控配置选项

Closes #123
```

## Pull Request 流程

1. **标题**：使用清晰简洁的标题描述 PR 的内容
2. **描述**：
   - 详细说明您的更改
   - 解释为什么需要这些更改
   - 提及相关的 issue
   - 包括测试结果
3. **检查**：
   - 确保所有测试通过
   - 确保代码遵循风格指南
   - 确保文档已更新

## 问题报告

如果您发现了 bug，请按照以下步骤报告：

1. **搜索现有问题**：查看是否已经有人报告了同样的问题
2. **创建新问题**：使用提供的模板创建一个新问题
3. **提供详细信息**：
   - 问题的描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 错误日志（如果有）

## 功能请求

如果您有功能请求，请按照以下步骤提交：

1. **搜索现有请求**：查看是否已经有人提出了同样的请求
2. **创建新请求**：使用提供的模板创建一个新的功能请求
3. **详细描述**：
   - 功能的描述
   - 为什么这个功能是有用的
   - 可能的实现方案
   - 任何相关的参考资料

## 代码审查

所有 PR 都将经过代码审查。审查过程旨在确保：

- 代码质量高
- 功能正确
- 测试覆盖充分
- 文档完整

请耐心等待审查，并积极回应审查意见。

## 测试

我们鼓励为所有更改添加测试。测试应：

- 覆盖新功能和 bug 修复
- 保持简洁明了
- 运行速度快

运行测试：

```bash
python -m pytest
```

## 文档贡献

文档贡献同样重要！您可以：

- 改进现有文档
- 添加新的教程或指南
- 修复文档中的错误
- 翻译文档

## 成为维护者

随着项目的发展，我们可能会邀请活跃的贡献者成为维护者。维护者的职责包括：

- 审查 PR
- 管理问题
- 发布新版本
- 制定项目路线图

如果您有兴趣成为维护者，请联系项目负责人。

---

再次感谢您对 File Brain 项目的贡献！您的参与将帮助我们构建一个更好的文件管理工具。