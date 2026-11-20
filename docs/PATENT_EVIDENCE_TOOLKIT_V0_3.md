# Patent Evidence Workbench v0.3｜跨企业验证与专利全文完整性闸门

**2026-11-20，Python标准库。** 在v0.2申请族/双时间权益之上增加专利文献结构可用性审计，源于腾讯及华为真实专利查询。工具仍是可复用研究原型，而非官方家族与权属裁决系统。

## 已实现的实用能力

1. text_quality.py：检查provider返回的说明书description及权利要求claims字段，独立标记missing_in_index、truncated、not_requested、indexed_but_not_returned、returned-but-original-completeness-unknown。
2. CN应用号年份与filing_date不同：如有parent.type=division则发出“历史分案口径待核”提示；**不**把2007编号直接覆盖2002原案法律日期。
3. CLI新增text-check命令，输出无全文的字段覆盖状态JSON；不自动复制受限原始专利全文。
4. 跨企业数据核对：腾讯2002 CN匹配4条取齐、2申请/2族；华为2002 CN仅第一页8/2039，启用--require-complete正确拒绝。
5. 实际三件授权公报均显示description/claims缺失在当前IPHouse索引中；另公开华为CN101166059A网页显示10项权利要求，证明缺索引不等于原文不存在。

## 执行

在仓库根目录：

~~~bash
python3 -m unittest discover -s tests -p 'test_patent_*.py' -v

python3 -m patent_evidence.cli text-check \
  --input data/examples/cn2002-text-availability-v0-3.json \
  --output /tmp/cn-text-audit.json

python3 scripts/validate_cross_company_2026_11_20.py
~~~

以前的audit、family-check、history-check保持可用。

## 证据纪律

- family_id口径仍未与EPO正式DOCDB/INPADOC逐案核实；已核官方规则不等于已核个案。
- USPTO登记摘要不等于原始deed，也不等于官方认定法律交易有效。
- 摘要恰好为500字符不能自动推论为完整或已经截断；保留original_completeness=not_verified。
- 数据源字段缺失、网页403或未取得权限不构成缺少发明的历史判断。
- 私有原始数据库响应不进公开仓库，公开只放派生统计、状态和必要著录引用。

## v0.4候选

以可以依法取得的原始文献为基础，结构化题名/摘要/说明书/权利要求/引证及版本，带段落定位与原文来源等级；并把申请和转让原始文件通过证据生命周期连入五体一库。不预设AI抽取输出即为真实权属。
