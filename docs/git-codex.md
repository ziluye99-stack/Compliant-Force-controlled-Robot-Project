# Git 与 GitHub 使用指南

本仓库已经配置好 Git 身份、GitHub SSH 认证和 `origin` 远端。Codex、VS Code
终端和普通终端使用的是同一份工作区，因此 Git 操作结果是一致的。

## 每次开始工作

在 Codex 的终端中进入仓库并确认状态：

```bash
cd /home/yzl/Documents/Codex/Compliant-Force-controlled-Robot-Project
git status
git remote -v
git branch --show-current
git fetch origin
```

开始新的实验或较大的修改时，先阅读 `docs/PROJECT_VISION.md`，然后从最新的
`main` 建立一个聚焦分支：

```bash
git switch main
git pull --rebase origin main
git switch -c codex/<short-task-name>
```

例如：

```bash
git switch -c codex/dual-contact-mujoco
```

## 修改、验证、提交

先让 Codex 完成代码或文档修改，再在终端检查差异并运行对应测试：

```bash
git status --short
git diff --check
git diff
bash scripts/preflight.sh local
.mamba-env/bin/python -m pytest -q
```

只添加本次任务的文件，确认没有密钥、数据、checkpoint、视频或日志：

```bash
git add docs/ src/ configs/ scripts/ slurm/ AGENTS.md README.md
git status
git commit -m "Describe the focused change"
```

提交信息应说明实际变化，例如 `Add dual-contact MuJoCo baseline`。

## 推送到 GitHub

首次推送当前分支：

```bash
git push -u origin HEAD
```

后续提交直接运行：

```bash
git push
```

推送前可验证 GitHub SSH 和远端访问：

```bash
ssh -T git@github.com
git ls-remote origin HEAD
```

本仓库的远端是
`git@github.com:ziluye99-stack/Compliant-Force-controlled-Robot-Project.git`。

## 用 GitHub CLI 创建 Pull Request

如果 `gh auth status` 显示已登录，可以从当前分支创建 PR：

```bash
gh auth status
gh pr create --base main --head "$(git branch --show-current)" \
  --title "Describe the change" \
  --body "Summary, verification command, and experiment artifact."
```

查看、合并或关闭 PR 前先确认目标分支和变更范围：

```bash
gh pr view
gh pr checks
```

## 在 Codex 中怎么说

可以直接给 Codex 下这种仓库内任务：

> 在当前仓库阅读 `docs/PROJECT_VISION.md`，实现 XXX，运行指定测试，检查
> `git diff`，提交为 `codex/...` 分支，并在推送前报告将要执行的 GitHub 操作。

涉及推送、创建 PR 或合并时，明确写出目标分支和范围。Codex 会先展示或执行
本地验证；不要把密码、个人访问令牌或私钥粘贴到对话或仓库中。

## 常用恢复操作

放弃一个尚未提交文件的本地修改前，先确认文件确实属于本次任务：

```bash
git diff -- path/to/file
git restore -- path/to/file
```

同步远端最新提交并保留自己的提交：

```bash
git pull --rebase origin "$(git branch --show-current)"
```

如果发生冲突，解决文件后运行 `git add <file>`、`git rebase --continue`；不确定
时保留现场并让 Codex 检查，不要使用 `git reset --hard`。
