# Benchmark Case Importer

入口：`scripts/benchmark_importer.py`。扫描 `case-library/visual-benchmark-library/images/`，支持子目录。保持原图文件名与内容，ID写入 metadata.json，不要求用户预先重命名。导入记录默认 pending，不因“优秀图片”目录自动获得老师分或发布资格。

## 使用

在仓库根目录安装现有 requirements 后运行一次扫描：

```bash
python scripts/benchmark_importer.py
```

持续新增只需在监听进程运行时放入图片：

```bash
python scripts/benchmark_importer.py --watch --interval 5
```

Ctrl+C停止；监听是前台轮询进程，不是已安装的后台服务，机器 / 会话重启后需重新启动。建议先复制到非图片扩展名临时文件，完成后改成真实扩展名，避免扫描到复制中的文件。损坏图片报错，其他有效图片仍导入，下一次扫描重试。

支持 JPEG、PNG、WebP、BMP、TIFF；AVIF 取决于 Pillow 支持。HEIC 未接入，请先自行转换并保留原件。新文件按相对路径稳定排序分配 CR001、CR002……，持久化 next_image_number，编号不复用。

## 自动生成内容

- 真实文件路径、SHA-256、图片像素宽高、文件完整性检查。
- image_id、逐图 `case-library/benchmark-cases/_pending/<ID>/metadata.json`、数据库 image_records 与 cases 摘要。
- visual_tags：实际图像横 / 竖 / 方形标签，文件名分类线索标签。
- 色彩量化与平均像素亮度：是可计算像素特征，不等同灯光真实性、环境色或产品面积判断。
- category / product_type：只有单一明确文件名或子目录线索时生成候选；未知或歧义为 null。导入不确认 KT 板材质。
- teacher_score.value、score_level：默认 null；老师评分必须来自评分资料，不能从图像、文件名含92或模型评价推断。
- 构图、产品位置 / 占比、人物作用、情绪、用途、为什么优秀与可复用规则：本地模式保留待分析；不会凭像素颜色编造语义。

名字可包含 birthday、proposal、graduation、marry-me、number、letter 等线索；中文生日、求婚、毕业、数字、字母也支持。文件名线索不是实际看图结论。

## 可选图片内容分析

配置环境变量 OPENAI_API_KEY 与 BENCHMARK_VISION_MODEL（支持图片输入和 JSON 输出的模型名称）后：

```bash
python scripts/benchmark_importer.py --analyze
python scripts/benchmark_importer.py --watch --analyze
```

也可传 `--vision-model <model>`。密钥只从环境读取，不写入元数据、不输出；仅显式 --analyze 会把图片发送给 OpenAI API并产生相应调用费用。当前仓库未配置 / 验证远程凭据和真实模型能力，不默认发起外部请求。该模式支持 JPEG、PNG、WebP。

接口返回 category、product_type、scene_type、usage、target_customer、visual_analysis、visual_tags、why_good、reusable_rules、avoid，要求解释“画面证据 → 感知机制假设 → 可迁移约束”，不只描述物件。返回字段严格校验；老师分、素材授权、产品事实及首图合规不允许模型补写。

模型分析仍为 unverified，不自动转 active；已有基本 pending 记录可在后续 --analyze 扫描补充分析，已模型分析的记录不重复请求。若存在人工填写的优秀点、可迁移规则、风险或语义分析，则跳过并输出 analysis_skipped，保留原内容。接口失败时保存基本记录、报告错误，下一次扫描重试；不覆盖人工分析。

## 连续导入与可靠性

- 哈希相同只登记一次；重复扫描不产生新ID或改写人工元数据。
- pending 原图改名且原路径消失时更新路径，保留 ID 和分析；已 active 素材变更需先人工处理以保护已复核记录。
- 同名文件内容改变报错，不将新图静默挂到旧案例；使用新文件名导入新版。
- 文件锁序列化并发分配；metadata 和数据库采用临时文件原子替换。
- 数据库提交中断后，下一次扫描恢复本 importer 创建的未登记 pending 记录，防止编号重复。
- 可检索前按原流程补评分来源、素材权限、真实产品事实和视觉复核，完成 active 状态；待审记录仍可在数据库查看，但正式检索不推荐。

输出 imported、duplicates、relocated、recovered、errors、registered_images；可选 analyzed。单次扫描存在错误时退出码为1，即使部分图片已成功导入；监听模式继续扫描，错误信息保留在输出。
