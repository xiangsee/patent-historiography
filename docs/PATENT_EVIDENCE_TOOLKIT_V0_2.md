# 专利证据工作台v0.2：优先权候选关系与双时间权益登记

本版不接触用户未授权账户、没有自动网络请求，仅使用Python标准库对本地可许可的文献元数据进行可追溯运算。

## 新增函数
**priority_link_audit(documents)**：比较规范化的优先权/关联申请号，不把同一天自动当同一个申请；返回相同观察集合、共享申请号、仅同日、无直接共享以及来源不足。即便同一集合也不能冒充EPO正式DOCDB简单家族，因为继续案、分案与数据完整性要受EPO特殊规则调整。

**registry_snapshot(events, patent_id, as_of, knowledge_as_of)**：分别提供待还原的历史日期和证据允许的可知截止日期。可区别一个权利事件的实际生效日期和之后的登记日期。将assignment与merger视为可观察的权益变动，将name_change视为名称变化，license视为非所有权许可。输出last_recorded_interest_entity，而不是独立司法确认的真实权利人。

## 使用命令
在仓库根目录运行，Python无需第三方依赖。

~~~bash
python3 -m unittest discover -s tests -p 'test_patent_*.py' -v

python3 -m patent_evidence.cli history-check \
  --input data/examples/maps-priority-rights-v0-2.json \
  --patent-id US20050270311A1 \
  --as-of 2005-02-08 \
  --output /tmp/google-maps-launch-evidence.json

python3 -m patent_evidence.cli history-check \
  --input data/examples/maps-priority-rights-v0-2.json \
  --patent-id US20050182770A1 \
  --as-of 2005-04-26 \
  --knowledge-as-of 2005-04-27 \
  --output /tmp/geo-patent-retrospective.json
~~~

## 实际核验
已有v0.1八项数据质量测试，本轮新增10项优先权/双时间权益测试，共18项全部通过。基于4件真实专利输入产生6组优先权对照，并对3个不同历史时点生成实际证据快照；结果见data/examples/maps-lineage-v0-2-derived.json。

主要发现：共享申请号的两件地图专利可有不同provider family_id；同为2003-11-25的两件专利不具有相同的已观察申请号。2005年2月Google Maps发布时的公开可知资料与2005年末事后重建的转让情况不同。

## 使用边界
- 已验证的是**公开/聚合资料的可观察关系**和代码逻辑；尚无EPO官方家族号、USPTO原始权益文件、源代码或授权合同。
- 来源仅为部分列表时，缺失关联关系只能标为未观察到，不能宣布不存在。
- 任何登记只能说记录了相关事项，不能自动证明权属绝对有效。
- 2004年Where2并购属于公司组织事件，与单项专利转让独立建表。
- 原始商业或付费数据库批量记录仍留在私有研究区，公开仓库仅保留小型可许可历史案例与派生结果。

**下一版v0.3**：EPO或原始申请案卷核对4件专利具体优先权声明；USPTO原始权益转让影像的来源级校验；对至少一家非Google企业进行同样的双时间权益测试；再考虑说明书和权利要求结构化。
