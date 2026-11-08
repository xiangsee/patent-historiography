# 数据空间说明

本仓库尚未包含Google、华为或腾讯的全量专利母集。公开数据目录未来只保留经过许可审查的提取规则、清洗代码、聚合结果、史料索引及非敏感示例。

当前数据边界：
- private/raw/、data/raw/、data/restricted/：禁止加入Git，参见 .gitignore。
- 专利全文与商业数据库批量导出：不得因研究用途而直接再公开。
- 统计文件应附元数据：source、snapshot_version、retrieved_at、query、scope、family_definition、dedupe、coverage、license。
- 一条事件必须有证据来源；不允许从自动聚类直接生成历史事实。
- Google试验卷中的空CSV仅提供字段模板，不是调查结果。

数据版本与质量检查规范见 docs/CORPUS_PROTOCOL.md。
