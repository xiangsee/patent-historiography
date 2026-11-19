# 《企业史记》专利族、技术来源与动态权属协议 v1.0

**适用**：将长期专利记录用于企业史时，必须把四种层次分开。

## 公报 publication
公开号、文种、公开国/局、公开日期、版本。A1/B1/B2/C/E等不等于多次发明。研究时可以衡量文件量与权利布局，但不能直接计为研发数量。

## 申请 application / priority
申请号、申请日、每一项优先权、继续案/分案关系、母案引用、最早可核技术时间。申请日与真实发明完成日期不同；优先权不是研究者已知道的公开日期。

## 家族网络 family
必须写明来源体系：
- provider family_id：保持原值及抽取日期；不能根据字段名字推定含义。
- DOCDB simple：按EPO规则的相同/对应技术内容、优先权组合；
- INPADOC extended：优先权直接或间接关联的更大网络，可能包含不同发明主题。

一个provider family_id可以有多家族成员、多个申请人、跨年和跨国。不同窗口的distinct计数不能相加：2000—2004观察522个、2005观察370个，合并仅836个，重叠56个。优先权网络与技术相似性不能证明工程实际继承。

## 历史来源与权属 origin & ownership as-of
- originated：以当时研发组织和原始申请为主要佐证；需要证据。
- transferred/acquired：在有日期的转让、合并或购买后取得的权利/资产；个别家族成员可能不同。
- licensed：独立于所有权，合同在规定期间内赋予使用权；不得混为owned。
- owned_at(date)：某特定日期实际拥有的权利。
- unknown：现有来源不足，不得自动归到Google原创。

专利转让登记的recorded_at与合同effective_at分开，法律事件聚合数据需抽样以USPTO原始档案复核。案例：family3814761中Silverbrook原始申请、后分别出现Zamtec/Google记录；family24968825早期DoubleClick、2008合并进入Google。

## 必须保留的反证
1. 后买入的专利被当作20年前公司自行研发？
2. 同族多份跨国公报被当成多项发明？
3. 一个覆盖许多技术主题的大家族当成一项单一发明？
4. 当前标准化申请人名称被倒填到历史时间？
5. 某公司收购的团队与专利是否自动推断实际产品实施？
6. 删去独立非专利材料，技术贡献与商业获利命题还能成立吗？

该协议是对方法的修正，不代表已验证所有EPO和IPHouse家族匹配。

## v0.1可执行检查入口
在根目录通过 python3 -m patent_evidence.cli audit 读取私有IPHouse批次，区分公报/申请/provider family并审查跨查询窗口家族重复；其输出不是发明归属计算器。另以 family-check 比较两个家族API返回值。工具实现见 ../patent_evidence/core.py，实测报告见 ../research/14-patent-methods-first-real-experiment.md。未接入真实USPTO转让事件之前，历史original_assignee一律不得从current assignee推断。
