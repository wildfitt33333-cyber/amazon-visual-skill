# KT 板灯牌 Case Library

用于沉淀 Amazon 美国站 KT 板数字 / 字母发光灯牌差转优项目。当前仅有目录与模板，没有具体案例，也没有已验证的成功或失败结论。

## 分类结构

```text
case-library/
├── successful-cases/
│   ├── birthday/
│   ├── wedding/
│   ├── proposal/
│   ├── graduation/
│   └── holiday/
├── product-categories/
│   ├── number-light/
│   └── letter-light/
├── age-segments/
│   ├── kids/
│   ├── teen/
│   ├── adult/
│   └── senior/
├── failed-patterns/
│   ├── product-too-small/
│   ├── background-overpower/
│   ├── wrong-scale/
│   ├── unrealistic-human/
│   └── wrong-lighting/
├── evaluation/
│   ├── visual-quality-score.md
│   ├── amazon-ctr-factor.md
│   └── conversion-factor.md
└── templates/
    └── case-analysis-template.md
```

空目录用 `.gitkeep` 保留，不表示其中已有案例。

## Visual Benchmark Library v0.1 入口

[视觉图片数据库](visual-benchmark-library/README.md)提供逐图元数据、评分溯源、分类目录、六维评价和标签检索。它与现有 Benchmark 和 Creative Reference Group 通过稳定 ID 关联；不把已有创意等级换算为老师分，不迁移或覆盖原记录。当前首批评分图片尚未导入。

## Creative Reference Group 创意参考组

新增目录 `creative-reference-group/`，使用[创意参考组模板](creative-reference-group/creative-reference-template.md)记录视觉方法、构图策略与情绪表达。Benchmark 按具体产品和场景匹配；创意参考组用于抽取方法并独立设计人物、装饰、文案及场地，不能直接复制内容或产品比例。

本模块当前仅含模板，未录入新案例或图片，不移动现有 Benchmark。多图按一个共同主题记录，同时保留各图证据、差异、适用范围与未验证状态；高级感和购买吸引力假设不等于实际经营效果。

## 未来记录方式

- 使用 [案例记录模板](templates/case-analysis-template.md)，一个案例一个稳定 ID，保留原图、改图与方案版本引用。
- 成功案例按活动保存主记录；产品与受众目录保存指向主记录的分类索引，避免多份内容不同步。
- 失败或无明确结果的项目可在对应产品目录保存主记录；失败模式目录仅索引有证据的诊断与结果，无适用模式时不强行分类。
- 受众标签来自项目输入，不能从图片推断年龄。活动分类不是新增产品类别。
- 未执行改图、无可比数据或结果未复核的项目，不进入 `successful-cases/`。记录成功是视觉验收还是业务指标改善，并说明证据与判定标准。
- 失败模式是待积累的诊断标签，不代表已证实的转化下降原因；原图缺陷不等于优化项目失败。
- 保留改善、恶化、无明确差异和无效实验。单项 CTR 增长不能自动宣布整体成功。
- 来源、授权、适用条件、时效与局限必须记录；未经授权不得跨用户共享经营数据或图片。

## 失败模式标签

| 目录 | 后续记录对象 |
| --- | --- |
| `product-too-small` | 主体在展示画面中难以识别；与产品实际尺寸小分开判断 |
| `background-overpower` | 布景、人物或装饰抢夺字符与灯牌注意力 |
| `wrong-scale` | 产品、人物、环境比例或尺寸标注与事实不符 |
| `unrealistic-human` | 人物姿态、肢体、持握或接触关系不真实 |
| `wrong-lighting` | 灯点、灯色、光晕、曝光或环境受光不合理 |

此库是文档框架，不是已部署的经验数据库；未来引用须说明案例上下文、证据等级和适用差异。

## 统一评价体系

- [视觉质量评分](evaluation/visual-quality-score.md)：单项 0–4 分、角色权重、证据覆盖、硬约束与前后比较。
- [点击率视觉因素](evaluation/amazon-ctr-factor.md)：入口主图判断、CTR 口径、实验与护栏。
- [购买转化因素](evaluation/conversion-factor.md)：灯牌购买顾虑、图片组解释、CVR 口径与反馈验证。

录入时分别填写视觉评价、点击反馈与转化反馈，保留量表版本和检查条件；缺失数据不能用视觉分代替。当前标准是评价框架，尚无案例结果或已校准的业务预测权重。
