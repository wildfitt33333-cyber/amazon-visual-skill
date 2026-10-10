# Amazon Visual Benchmark Library v0.1

本模块集成现有 Amazon Marquee Visual Director，不创建独立项目。采用文件式图片数据库：原图、逐图元数据、版本化 Schema、标签检索和独立视觉评价；当前尚未收到本批老师评分图片，数据库为空。

## 数据入口与分类

数据库目录：[database.json](database.json)。`image_records` 保存从仓库根目录出发的 metadata.json 路径，作为正式入库清单；扫描发现但未登记的文件不能自动成为可检索图片。每张图片用稳定 image_id，一个主分类保存唯一记录，其他场景通过 category_tags 交叉检索，不复制多份原图。

第一批导入按最新要求使用 `images/CR001.<实际格式>`、`images/CR002.<实际格式>` 等保存原图。编号只在收到实际图片后分配，查重后继续递增，删除编号不复用；现阶段未分配任何 CR 编号。分类目录保存逐图 metadata.json，asset.path 指向此集中图片目录，既有路径仍兼容。

database.json 新增 cases 作为逐图分析摘要，当前为空；未来导入时与 image_records 按 image_id 同步更新，metadata.json 为主记录，摘要不得另行手改而产生不同版本。摘要包含 image_id、teacher_score、category、product_type、scene_type、usage、target_customer、visual_analysis、why_good、reusable_rules、avoid；保留老师评分来源与状态。新增字段已纳入模板及 Schema，旧字段保留以兼容当前检索。

visual_analysis 对应用户要求的八项分析，包含 product_position；visual_features 保持既有检索契约。同名特征由同一观察同步填写，未知不补造。reusable_rules 须写出“观察依据 → 为什么有效的假设 → 适用条件 → 生成约束 → 验收方式”，why_good 解释主体突出、空间质感、自然人物和真实光影，不只列图中物件。不从老师总分反推其具体评分理由，未取得原始评语时标记为 Agent 的视觉解释。

```text
case-library/benchmark-cases/
├── birthday/
│   ├── outdoor-premium/
│   ├── kid-birthday/
│   ├── teen-birthday/
│   ├── adult-birthday/
│   └── senior-birthday/
├── proposal/
│   ├── beach/
│   ├── indoor/
│   └── emotional-pov/
├── school-event/
├── family-emotion/
└── luxury-celebration/
```

逐图存储：`<分类>/<子分类，如有>/<image_id>/original.<真实格式>`、`metadata.json`；可选预览与独立 evaluation.json。原图不覆盖，改版另存。空目录用 .gitkeep 保留；当前目录不代表已有图片。

## 数据契约

- [图片 Schema](schemas/image-metadata.schema.json)：统一 image_id、评分、产品、用途、七类视觉特征、来源、素材、规则与迁移边界。
- [metadata.json 空白模板](templates/metadata.json)：待录入状态，不是具体案例，不进入正式入库清单。
- [评价输入模板](templates/evaluation-input.json)：评审人查看实际图片后填写，不以空白模板计算成图分数。
- [视觉评价规则](visual-evaluation-rules.md)：六维 0–100 评分、缺失项、硬约束与旧量表区别。
- [检索逻辑](retrieval-logic.md)：事实过滤、场景与心理需求、可解释排序和无匹配分支。

老师原始评分独立记录在 teacher_score，S 为 90–92，A 为 86–89。边界外、来源缺失或分数未提供不强行定级；先保留 pending 状态。已有 BM-001 至 BM-004 的创意A级标签不等于老师86–89分，不自动迁移评分。

产品保持 Amazon US KT 板灯牌范围：marquee-number、marquee-letter、marry-me；按本次产品标签需求加入 heart-light，仅限资料确认的 KT 板心形灯牌，不扩展到霓虹、金属或其他灯具。学校活动、家庭情绪等是使用 / 视觉主题，不是新产品类别。

usage 为用途意图，不是发布认证；amazon-main-image 仍需 policy_review。引用 Benchmark 或 Creative Reference Group 时保留各自原记录 ID，图片数据库通过 related_records 关联，不改变原编号、不把多图参考组拆散。

字段统一使用 image_id、teacher_score.value（数值）和 score_level；导入样例中的 id、score 等别名需先转换，hero-main-image 须先确认实际图片角色再映射为 amazon-main-image 或其他用途，不能自动取得首图资格。visual_features 是可观察特征，visual_rules 是方法摘要，why_good 是有证据的优秀点解释；avoid 与 redesign_required 分别记录风险和迁移时必须重设计的内容。

## 导入与持续扩展

1. 收到实际可访问图片与老师评分资料后分配 image_id，登记来源、授权与真实得分；核实是否符合 KT 板产品范围。
2. 保存原图，记录尺寸、真实相对路径、SHA-256；校验工具检查真实图片格式、文件完整性、尺寸与哈希。重复文件通过哈希检测，不重复入库。多图主题共享 reference_group_id，但每图有独立 ID 和评分。
3. 实际查看图片，标注视觉特征及 why_good / avoid / redesign_required；产品占比须说明测量口径，未知填 null。
4. 复核评分等级、事实、用途和授权，将 status 改为 active，登记 database.json 的 image_records，再执行校验。
5. 需要评价时保存独立评价输入及计算结果；不以新量表覆盖老师原分。
6. 修改元数据递增 metadata_version，保存变更说明；评分、授权或素材失效时改为 retired / pending 并停止推荐。

未来可增加缩略图、向量嵌入或 SQL / 向量数据库适配器，仍以 image_id 为主键，保留元数据、证据和检索解释。v0.1 不调用外部嵌入服务、不训练模型，不声称已完成图像相似度检索。

## Benchmark Case Importer

新增[持续导入工具](importer.md)：运行 `python scripts/benchmark_importer.py` 扫描 images/，或添加 `--watch` 持续监听。自动生成稳定 CR ID、尺寸 / 哈希、metadata.json、候选标签及 database.json；未复核记录保留 pending，老师分为 null。配置视觉模型后可显式 `--analyze` 根据图片生成语义分析；未配置时仅像素测量与文件名线索，不冒充实际视觉判断。详细字段、重试与调用说明见 importer.md。

## 可运行工具

在仓库根目录安装工具依赖并执行：

```bash
python -m pip install -r case-library/visual-benchmark-library/requirements.txt
python scripts/visual_benchmark.py validate
python scripts/visual_benchmark.py retrieve --product-type marquee-number --category birthday --age senior --usage secondary-image --lighting warm-yellow --size-cm 122 --goal family-celebration
python scripts/visual_benchmark.py evaluate --input /path/to/evaluation-input.json
python -m unittest discover -s tests -p 'test_visual_benchmark.py'
```

visual_benchmark.py 工具只读数据库和输入，输出 JSON，不自动入库、改图或发布；benchmark_importer.py 则明确写入元数据与数据库，不改动原图。evaluate 不看图、不由图片自动评分：评审人实际检查后提供六维分数，工具计算总分及完整性。空库检索返回 no_match；空库校验通过不代表真实图片已入库或匹配效果已验证。
