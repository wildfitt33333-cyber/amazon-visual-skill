# Amazon Marquee Visual Director
Visual planning and optimization for KT-board marquee number and letter lights on Amazon US.

## 项目定位

专门服务 **Amazon 美国站 KT 板发光灯牌**，支持新品视觉规划与老 Listing 差转优：

- 新品：产品分析、用户画像、场景策划、图片结构规划和 AI Prompt。
- 差转优：现有图片诊断、优秀竞品对比、优化方向、修改优先级和 AI 修改 Prompt。

产品范围限定为数字发光灯、字母发光灯，以及 Birthday marquee numbers、Wedding marquee letters、Proposal marquee lights、Graduation / Holiday marquee lights。活动用途均围绕同一灯牌品类，不扩展到其他 Amazon 产品。

行业判断重点：字形和组合准确、售卖数量清楚、KT 板质感真实、尺寸可信、灯点与光晕合理、活动场景匹配；不凭画面补造功能或夸大发光效果。

核心 Skill 标识为 `amazon-marquee-visual-director`，入口见 [SKILL.md](skills/amazon-visual-optimization/SKILL.md)。保留原目录 `skills/amazon-visual-optimization/`，其中两条工作流及六份模板均用于本范围灯牌任务。

## Amazon Visual Benchmark Library v0.1

新增[视觉图片知识库](case-library/visual-benchmark-library/README.md)，与现有 Benchmark、Creative Reference Group 和 Skill 集成。提供文件式数据库、逐图 metadata.json Schema 与模板、老师 S / A 评分溯源、六维视觉评价及可运行的元数据校验 / 标签检索 / 评分计算工具。老师原始评分与新量表总分分开保存，不自动将已有创意A级案例定为86–89分。

首批86分以上图片尚未提供，当前数据库为空。支持持续逐图导入、SHA-256去重、版本与授权管理；向量相似度、自动图像打标和模型训练尚未接入。heart-light 标签仅用于资料确认的 KT 板心形灯牌，为本次新增形态，不扩展到其他灯具类别。

新增[Benchmark Case Importer](case-library/visual-benchmark-library/importer.md)：扫描 images/ 并生成 CR ID、待审 metadata 与数据库记录；支持 --watch 持续新增。像素与文件名候选本地计算，图片内容分析需显式 --analyze 和视觉模型配置，适配接口已实现但真实远程调用尚未验证。老师分不由图片推断，自动导入不等于复核完成。

完整设计见 [项目架构](docs/architecture.md)。当前仓库处于架构设计阶段，尚未实现应用和运行环境。

仓库已包含可供 Agent 遵循的 Skill、工作流与输出模板；当前定位限定其适用范围。架构中的通用模块作为底座使用，不代表支持其他产品类别，自动化应用与服务仍未实现。

## 市场洞察与合理差异化策略

在判断图片问题的基础上，解释问题原因，并选择向市场主流优化或进行受控差异化：

- 分析美国站 KT 板灯牌 TOP 竞品及有销量依据的样本，归纳视觉模式和用户熟悉的购买信号；证据不足时明确标记限制。
- 区分必须保持的产品事实与规则、优先保持的市场共识，以及可建立记忆点的突破空间。
- 遵循 **80% 符合市场主流审美，20% 形成差异化优势**；这是策略原则，不是固定画面比例，不为创新而创新。
- 输出原因链、共识 / 突破矩阵、路线决策，并将策略写入制作方案与 AI Prompt。

新增领域模块：

| 模块 | 职责 |
| --- | --- |
| `market-intelligence` | 市场趋势、视觉模式和购买信号 |
| `differentiation-strategy` | 主流修复或差异化选择，以及保留 / 突破策略 |
| `conversion-feedback` | 未来接入 CTR、CVR、广告表现和 A/B 测试结果 |
| `experience-database` | 沉淀历史优化结果、证据、适用条件和经验检索 |

长期规则见 [AGENTS.md](AGENTS.md)，详细接口、数据模型和交付计划见 [市场洞察架构](docs/architecture.md#15-核心能力增强市场洞察与合理差异化策略)。目前完成的是架构与规则定义，四个模块尚未实现，经营数据尚未接入。
