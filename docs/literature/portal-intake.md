# 学校门户文献交接清单

这份清单把学校图书馆门户中的检索和下载，交接到仓库的可复现论文研读流程。门户登录、密码、Cookie 和一次性验证码只由用户在学校 App/浏览器中操作；它们不发送给 Codex，也不写入 Git。

## 检索来源和优先级

按证据强度优先检查以下来源：

1. Web of Science/SCI 记录对应的正式出版物；SCI 是索引，不等于全文来源。
2. Nature、Nature Machine Intelligence、Science、Science Robotics。
3. IEEE T-RO、RA-L、T-ASE、T-MECH、IJRR、Automatica，以及 RSS、CoRL、ICRA、IROS 正式论文。
4. 中国知网、万方和学校发现系统中的中文论文。
5. OpenAlex、Crossref、Semantic Scholar、arXiv 只用于发现、DOI 核验和引用链；GitHub/Papers with Code 只用于代码线索。

## 推荐检索轴

英文检索可逐步组合 embodiment、contact、sensor、controller 和 metric：

```text
"force control" contact-rich manipulation robot
"admittance control" force torque sensor assembly
"residual reinforcement learning" compliant manipulation
humanoid whole-body multi-contact force control tactile
sim-to-real compliant contact force control
```

中文检索建议分别在“篇名”“关键词”“摘要”字段使用：

```text
机械臂 接触 力控制
机械臂 导纳控制 力传感器
机械臂 阻抗控制 插入装配
混合位置力控制 接触
人形机器人 全身 柔顺控制 多接触
具身智能 力控 仿真 迁移
```

每次检索只保留与当前问题直接相关的论文，并记录筛选理由。优先选择有 MuJoCo/Gazebo/Isaac 或真实机器人实验、明确力/接触指标、可复现实验设置的论文。

## 下载和登记

1. 在门户中先用 DOI 搜索，再用完整标题和第一作者核对题名、版本、期刊、年份和文章类型。
2. 下载正式出版 PDF、允许下载的 supplementary material 到 `/mnt/research-data/literature/pdfs/`。
3. 文件名使用小写短标题和 arXiv/DOI 尾部，例如 `contact-survey-104224.pdf`、`cnki-admittance-2024.pdf`。
4. 在本地终端生成哈希：

```bash
sha256sum /mnt/research-data/literature/pdfs/<file>.pdf
```

下载三篇论文后，也可以用项目预检器一次性检查 PDF 头、文件大小、重复
路径并生成交接 manifest（manifest 放在论文目录之外，不会进入 Git）：

```bash
./.mamba-env/bin/python scripts/check-portal-pdfs.py \
  --admittance cnki-admittance.pdf \
  --impedance-hybrid cnki-impedance.pdf \
  --humanoid-multicontact cnki-humanoid.pdf \
  --output /mnt/research-data/literature/portal-manifest.json
```

相对路径默认相对于 `/mnt/research-data/literature/pdfs/`；也可以为每个
参数传入绝对路径。命令返回非零状态时，先修复缺失、空文件、非 PDF 或
重复路径，再交接 manifest。

5. 将 DOI、正式出版链接、数据库标识（WoS/CNKI/万方）、下载日期、PDF 路径和 SHA-256 交给 Codex。Codex 用 `scripts/create-paper-note.py` 建立笔记，再填充翻译、方法、接口、基线、指标、优缺点、失败案例和 MuJoCo 后续实验。

示例：

```bash
./.mamba-env/bin/python scripts/create-paper-note.py \
  --short-title cnki-admittance-2024 \
  --title "论文完整题名" \
  --authors "作者一; 作者二" \
  --venue-year "期刊, 2024" \
  --discovery-source "学校门户; CNKI" \
  --full-text-route "学校门户 -> CNKI" \
  --pdf /mnt/research-data/literature/pdfs/cnki-admittance-2024.pdf \
  --output docs/literature/notes/cnki-admittance-2024.md
```

## 交给 Codex 的最小信息

```text
PDF: /mnt/research-data/literature/pdfs/<file>.pdf
DOI/数据库标识: <DOI 或 CNKI/万方编号>
正式出版链接: <URL>
门户来源: <WoS/IEEE/CNKI/万方/学校发现系统>
SHA-256: <64 位哈希>
```

收到这些信息后，Codex 可以在不接触门户凭据的前提下完成全文提取、中文翻译、术语表、实验设计审查、与当前 MuJoCo 方案的差距映射和结构化笔记验证。只有 `check-paper-notes.py --require-primary-evidence --verify-files` 通过的论文，才能作为正式项目设计证据；预印本和作者稿可供研读，但不能单独支撑正式结论。

## 当前队列

- 接触操作综述：待从学校门户取得正式 PDF 或授权存档版本。
- 中文力控/柔顺控制：待取得至少三篇 CNKI/万方全文，分别覆盖导纳、阻抗/混合位置力和人形多接触方向。
- 已完成的公开全文笔记：力控 RL、全身多接触力控、DMP 残差学习；见 `docs/literature/notes/`。
