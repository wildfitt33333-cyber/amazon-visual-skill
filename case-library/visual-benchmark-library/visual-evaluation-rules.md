# Visual Evaluation Rule v0.1

量表 ID：`visual-benchmark-v0.1`。用于实际查看后的单张图片评价，不将 Brief / Prompt 当作成图，不代替 Amazon 官方规则或 CTR / CVR 实验。

## 六维权重与锚点

每维 0–100，0 为任务严重失败，50 为基本可理解但有明显缺陷，100 为记录检查条件下无明显缺陷；中间值需说明具体证据。100 不表示绝对完美。

| dimension key | 维度 | 权重 | 0 / 50 / 100 观察锚点 |
| --- | --- | ---: | --- |
| product_prominence | Product prominence | 30% | 商品难辨 / 可辨但被抢视觉 / 数字词组完整、产品第一视觉且售卖内容清楚 |
| composition | Composition | 20% | 严重遮挡裁切或透视错误 / 层级基本成立但拥挤 / 轮廓、留白、人物关系与空间有序 |
| lighting_realism | Lighting realism | 15% | 错灯色、漂浮光或严重光影冲突 / 局部光晕与接触欠佳 / 保留真实灯色、材质、阴影和合理环境反馈 |
| human_realism | Human realism | 15% | 人体、接触明显异常 / 基本自然但姿态或手部有缺陷 / 皮肤、动作、视线、接触与角色自然 |
| lifestyle_authenticity | Lifestyle authenticity | 10% | 空间、尺度或事件矛盾 / 活动可理解但环境关系欠佳 / 真实比例、布置和行为支持明确事件 |
| color_harmony | Color harmony | 10% | 材质失色或配色压过商品 / 大体协调但干扰主体 / 环境色支持产品且真实板体灯色保持 |

先检查硬约束：实际字符、SKU 数量、尺寸、KT 板结构、灯泡排列与灯色、使用条件和已核实的平台规则。错误为 fail；资料缺失为 pending；核实范围满足才为 pass。高分不能抵消 fail 或 pending。

## 计算与缺失

全部六项适用且已评分时：

```text
visual_quality_score = 0.30×product_prominence + 0.20×composition
                     + 0.15×lighting_realism + 0.15×human_realism
                     + 0.10×lifestyle_authenticity + 0.10×color_harmony
```

四舍五入一位小数。无人物图 human_realism 可在评审前声明 not_applicable；纯白产品图 lifestyle_authenticity 可不适用。不为凑分加人物 / 场景，也不因表现差而事后排除维度。

适用权重 A 排除真正不适用项；已评分权重 R 仅含 scored 项。证据覆盖率 R/A×100%。归一化分为 Σ(weight×score)/R。只有 R=A 且 A>0 才输出 visual_quality_score；R<A 输出 null 和 partial_visual_quality_score，列出缺失项，不能拿部分分排名。R=0 不算分。不同适用配置不能直接比较。

## 输入与输出

evaluate 输入含 image_id、reviewer、reviewed_at、image_observed:true、检查条件、hard_constraints 状态、六维与证据。各维格式为 `{ "status": "scored", "score": 90, "evidence": "实际观察依据" }`；未检查用 pending，证据不足用 unknown，不适用用 not_applicable，后三者 score 为 null 并说明理由。

```json
{
  "image_id": null,
  "reviewer": null,
  "reviewed_at": null,
  "image_observed": false,
  "check_conditions": null,
  "hard_constraints": "pending",
  "dimensions": {}
}
```

这是未填写结构，不是可评分记录；工具拒绝未观察图片或缺少必要评审信息的输入。输出含量表版本、分项、适用权重、覆盖率、完整总分或部分分、硬约束和 needs_review / blocked / eligible_for_review 状态。eligible_for_review 仅表示计算与记录门槛具备，不等于可发布或正式验收通过。

## 与已有评分的关系

本次六维权重作为明确新增的单图量表，保留原有 marquee-visual-v1 的 Q1–Q8、角色权重与图片组评价，不覆盖、不混合、不互相换算。两种量表都受同一产品事实和验收门槛约束。

teacher_score 与 score_level 是老师原始评分与本库导入等级；visual_quality_score 是此新量表结果，两者独立。模型 / 新量表评分不自动授予公司老师 S / A 等级；>92 或 <86 的老师分数不擅自扩展等级范围。评分阈值不证明销量或转化。
