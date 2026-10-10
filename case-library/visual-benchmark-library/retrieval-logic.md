# Visual Benchmark Retrieval v0.1

当前提供基于人工视觉标签的文件检索，不是从图片自动提取特征、向量相似度或模型训练。使用 database.json 的已登记记录；正式推荐需 active、素材存在、哈希有效、评分与来源可追溯、授权允许内部引用。

## 输入与优先级

输入产品类型、活动 / 主分类、年龄角色、usage、实际灯色和高度、视觉目标。字段未知不猜测，关键缺失在结果列出。消费者心理依据实际需求，不用年龄强制审美。

硬过滤：产品范围、active、有效素材与授权；产品类型与主活动匹配。category_tags 可提供交叉活动标签。amazon-main-image 请求必须 policy_review.status=verified_for_main，否则排除，不能把场景主视觉别名当首图许可。审核日期、来源和适用类别仍需人工确认时效。

排序按任务相关性，老师分数只作最后同等条件下排序，不让92分覆盖错误场景。可解释匹配权重：产品30、主活动25、图片角色15、明确年龄标签10、灯色10、尺寸5、视觉目标5；每项返回原因。非精确条件允许方法迁移，但必须列为 conditional / technique_only，尺寸不同重新校准，不用参考图改当前规格。分值是检索排序权重，不是视觉分或概率。

无明确年龄标签、不同灯色 / 尺寸 / usage 或视觉目标没有匹配时标记差异，缺失输入标记 incomplete_query。主场景不匹配不强行推荐；结果可为 no_match。同等匹配度按有依据的 teacher_score 降序、image_id 稳定排序。

## 输出解释与 Agent 复核

每个候选输出 image_id、metadata / asset 路径、score_level、teacher_score、匹配分、匹配状态、选择理由、不同与未知项、why_good、avoid、redesign_required。Agent 必须实际读取 / 查看候选原图，然后用 Benchmark Matching Rules 和 Visual Quality Rules 复核。标签检索不能证明具体画面优秀，不直接将第一条结果复制到 Prompt。

允许迁移构图、层级、产品人物关系、色彩方向及光影逻辑；禁止复制人物、装饰、文案、具体场地及产品比例。已有 BM / Creative Reference Group 通过 related_records、reference_group_id 保持关系，不重新编号。每次记录查询参数、版本与排除原因。

## 未来扩展

批量导入保留 image_id、SHA-256 去重、复核状态及元数据版本。向量检索以后可返回候选，但仍先做事实与用途过滤，再进行视觉检查。外部 embedding、数据库服务、自动打标和图片生成尚未接入；权限、来源与删除状态必须同步到衍生索引。
