# 专利证据工作台 v0.1｜Patent Evidence Workbench

2026-11-19｜《企业史记》研究的第二条产出主线：在重建企业与产业历史的同时，逐步沉淀可以跨企业复用的专利文献、专利数据处理方法和工具。核心是为**历史研究**服务，而不是只做更多技术脚本。

## 两条并行、相互校正的产品线

**历史研究线**：历史问题 → 企业与技术长期史料 → 本纪/表/书/世家/列传互见 → 历史判断与可读作品。

**方法与工具线**：数据来源契约 → 原始数据私有留存 → 公报/申请规范化 → 专利族和时间核对 → 版本/权属处理 → 文献/引证/技术特征提取 → 可追溯历史证据卡 → 质量验收与可复用工具。

每轮至少产生一项可测试的工具增量，或一份方法卡（问题、输入、变换、反证、误差、输出、复用条件）。故事写作发现的问题应回流为工具测试，工具发现的异常则必须改变历史研究的判断。

## v0.1 已实现、已在真实数据上运行的工具

| 功能 | 已做什么 | 不能宣称什么 |
| --- | --- | --- |
| IPHouse输入适配 | 本地JSON的pages[].records/items、列表JSON、JSONL；保留原始行，仅导出派生统计 | 不是已经取得所有专利局完整数据库 |
| 标识标准化 | 对公报/申请号生成可比对的键，原始号保留，前导0不丢失 | 不是全球各局格式的完整ST.9/ST.16实现 |
| 分页完整性核验 | 按查询参数分组，检查缺页、重复页、返回量与提供方total一致 | 不能证明数据库自身覆盖率完整 |
| 三种计数单位 | 公报、申请、provider family_id分开统计；-1等哨兵不聚成一个家族 | family_id不自动等于DOCDB简单族或一项发明 |
| 时间与主体风险 | 申请/优先权先后、家族跨年、跨公报局、名称混杂预警 | 不从当前assignee推断原始研发主体 |
| 家族核验队列 | 根据跨年、跨国、标题与当前申请人变化，生成少量有定位的待核样本 | 不自动证明同一族包含多件发明或权利已转让 |
| IPHouse接口对照 | 单独按family_id搜索对比get_patent_family的返回成员及规模 | 不等于EPO官方家族验证、原始案卷或接口上限已查明 |
| 8项synthetic unittest | 校验多文种/同申请、-1、跨年、分页缺失、接口不一致等 | 不等于生产环境全输入模型均受测 |
| Google真实数据回归 | 39页、1,917公报/1,465申请/836 provider family_id、56家族跨窗口重复 | 不等于Google六年自主发明全集 |

## 可复用的命令（仓库根目录）

只需要Python标准库，没有外部依赖或网络权限。建议用户把有数据许可限制的原始批次保存在私有区域。

~~~bash
python3 -m unittest discover -s tests -p 'test_patent_evidence.py' -v

python3 -m patent_evidence.cli audit \
  --inputs '/private/google/batch*.json' '/private/google/2005/batch*.json' \
  --focus-name Google --require-complete --review-limit 10 \
  --output '/private/google-audit.json'

python3 -m patent_evidence.cli family-check \
  --input data/examples/iphouse-family-api-10-sample-2026-11-19.json \
  --output '/private/iphouse-interface-audit.json'
~~~

- 第一条命令只跑单元测试；第二条从本地读取JSON并返回质量报告；第三条比较两个family接口的统计。
- --require-complete让“只抓了第一页”显式失败，不允许把部分结果当成全集。
- --review-limit默认10，只在输出中给出少量可公开查验的公报/家族标识，不能将批量原始数据库响应直接上传公共仓库。
- 系统不会代替研究者调用IPHouse授权接口、下载外部资料、支付或执行光盘文件。输入的合法取得和数据使用许可需要单独管理。

## 真实测试中发现的接口差异

2026-11-19抽样10个代表性family_id，分别调用IPHouse的search_patents(family_id)和get_patent_family(publication_number)。

- **8个样本**的两接口计数一致；
- **2个不一致**：3814761为358与51；34381362为63与51；
- 所有10个样本的family_detail成员列表均不含作为查询起点的公报；其family_size=成员列表长度+1；
- 两处差异恰好都列出50个其他成员，**可能是50成员返回限制，也可能是接口范围/家族聚合口径差异，不能据此正式判定原因**。

这项问题已经成为工具的接口质量检查，而不是某个Google故事的临时例外。

真实派生输出：[Google 2000–2005工具运行审计](../data/examples/google-2000-2005-patent-workbench-v0-1.json)；[10族接口交叉测试](../data/examples/iphouse-family-api-audit-result-v0-1.json)。

## 国标、国际数据标准的边界

目前对国际标准只进行映射设计，**未宣称ST.96或ST.97格式完全兼容**：
- EPO DOCDB simple family / INPADOC extended family需分别对待。https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families
- WIPO ST.9专利著录、ST.16专利文献种类、ST.27法律状态事件与ST.96结构化XML。https://www.wipo.int/en/web/standards/part_03_standards
- WIPO ST.97于2026年发布v2.0 JSON相关规范，可作为未来统一数据交换接口的参照。https://www.wipo.int/standards/en/st97/v2-0/annex-ii/index.html

## 下一阶段按重要性推进

**P0 数据工具v0.2**：专利原始申请人+优先权集合+EPO官方两种家族标识，建立申请/公报/族/权属随时间变化的独立表；包含来源、时间和证据强度。优先补充可直接用于Google Maps与收购历史问题的能力。

**P1 文献工具v0.3**：抽取标题/摘要/权利要求/说明书/引证/审查案卷，保留原文段落与版本，区分技术陈述、法律主张与历史解释。必要时AI辅助抽取，但不允许无来源编造申请日、权利人或人物贡献。

**P2 知识分析v0.4**：实体消歧、技术主题演变、专利和非专利知识图谱、同一主题的不同竞争公司比较，生成可以人工校订的五体证据包。

只有在至少两个不同企业或场景成功复用后，才考虑抽成独立工具仓库或产品。现阶段直接沉淀于 patent-historiography 项目，避免工具与历史研究脱节。
