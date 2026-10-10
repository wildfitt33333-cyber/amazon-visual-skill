# KT 板发光灯牌 AI 修改 / 制作 Prompt 模板

每个任务复制一份；字段不适用时明确标记，未确认事实不能进入可执行 Prompt。

- Prompt ID / 任务 ID / 策略 ID：
- 模式：editing / generation / compositing。
- 状态：ready / draft / blocked；缺失项：
- 模型及可用能力：未指定时输出通用指令，不伪造参数。
- 源图 ID / 产品素材 ID：
- 参考图 ID 与用途：仅参考构图、光影或信息组织，不迁移竞品功能。
- 中文目标摘要：
- 修改区域 / 保留区域 / 蒙版需求与可用性：
- 已确认产品描述与事实来源：
- 构图、尺度、场景、人物、光影、材质：
- 必须保持的市场信号 / 允许突破的表达：
- 禁止改动：产品形状、颜色、Logo、结构、接口、数量及包装事实。
- 英文文案 / 事实来源 / 后期文字图层位置：
- 输出画幅与尺寸：未指定时写建议与依据，不伪称平台要求。

## 灯牌身份锁定

- 类型 / SKU、准确字符、顺序、方向、售卖数量：
- KT 板表面、边缘、厚度、接缝、底座及支撑来源：
- 真实尺寸与人物 / 家具尺度依据：
- 灯点数量与位置、已确认灯色、曝光 / 光晕约束：
- 活动用途、具体数字 / 词组 / 年份及来源：
- 布景中不随附的装饰与组合标识：
- 供电和装配展示依据、不得新增的未知功能：

不能靠改字符、镜像字形、改材质、增加灯点、夸大尺寸或亮度实现差异化。关键字段未知时仅引用原图保留，不补造。

## English Prompt

```text
Task: {{specific_edit_or_generation_goal}}.
Use {{source_asset_ids}} as the product identity reference.
Preserve {{verified_product_identity_and_unchanged_regions}}.
Change only {{explicit_changes_and_regions}}.
Composition and scale: {{composition_and_verified_scale_constraints}}.
Scene and human interaction: {{scene_or_not_applicable}}.
Lighting and material: {{realistic_light_contact_shadows_and_material}}.
Keep the familiar purchase signals: {{preserve_elements}}.
Differentiate through: {{allowed_breakthrough_or_no_breakthrough}}.
Marquee identity: preserve {{exact_characters_order_orientation_and_sold_quantity}}.
Preserve the actual KT-board surface, edges, bulb layout and support structure from {{verified_assets}}.
Light appearance: {{verified_light_color_exposure_and_restrained_glow}}; keep character contours and board detail visible.
Event context: {{verified_event_number_word_or_year}}. Do not imply that {{non_included_decor_or_extra_characters}} are included.
Do not {{task_specific_prohibited_changes}}.
Leave {{text_safe_area_or_not_applicable}} for separate typography.
```

删除不适用指令并补齐具体内容后交付；不能原样输出占位段落。模型不支持的负向提示或蒙版参数不输出为可用功能。

## 验收与限制

- 关联验收 ID、产品保真检查、修改范围检查：
- 待补素材或事实、模型能力限制、是否实际执行 / 检查：
