# 专利数据与文献方法注册表（2026-11-19）

方法的成熟度高于文件数和脚本行数：每项工具必须有输入和输出契约、真实或合成测试、反证与历史研究问题关联。状态区分 design / executable / synthetic-tested / real-sample-tested / independently-validated。

| ID | 方法/工具 | 当前状态 | 实测证据 | 下一道门槛 |
| --- | --- | --- | --- | --- |
| PD-001 | 多批次专利数据导入与检索分页对账 | real-sample-tested | 39页、1917条、2个已完整检索窗口 | 另一个数据库API/原始合法导出格式 |
| PD-002 | 公报、申请、provider family ID独立计数 | real-sample-tested | 1917 / 1465 / 836，跨窗口重复56家族 | EPO DOCDB和INPADOC各自可核的标识 |
| PD-003 | 年份、优先权、现时申请人名称风险审计 | real-sample-tested | 422条非目标名称关联、1366条priority早于filing | 原始优先权链与申请当日主体校准 |
| PD-004 | IPHouse双家族接口一致性对照 | real-sample-tested | 10样本中2组返回数量差异、10组都排除锚点 | 提供方解释50成员上限/接口定义并与EPO核对 |
| PD-005 | 动态权属与企业来源重建 | design | Silverbrook/DoubleClick的少数真实反证 | 原始转让、有效日期与所有权类型可执行计算器 |
| PD-006 | 专利文献拆分、权利要求、引用与法律状态解析 | design | 既有论文与专利个案 | 取得合法完整文本数据并设计人工复核 |
| PD-007 | 技术主题及发明人网络长期演化 | design | Google Maps候选主题变化 | 在剔除后取得权利后复算主题与网络 |
| PD-008 | 五体证据与Claim Lifecycle互联 | design | 初步五体一库框架 | 从母集信号到可校订历史命题的可追溯链 |

工具总体接口： [v0.1说明](PATENT_EVIDENCE_TOOLKIT_V0_1.md)；方法记录模板：[PATENT_METHOD_RESULT_CARD](../templates/PATENT_METHOD_RESULT_CARD.md)。不自动将尚未通过独立核验的工具归为成熟研究基础设施。

## v0.2新增方法（2026-11-19）

| ID | 方法/工具 | 当前状态 | 实测证据 | 下一步缺口 |
| --- | --- | --- | --- | --- |
| PD-009 | 优先权申请标识比较及关联候选 | synthetic-tested + real-source-fixture | 4件地图专利、6对比较：两件不同provider family_id共享两项临时申请；另两件同日优先权但申请号不同 | 官方EPO DOCDB/INPADOC具体身份、完整原始优先权数据 |
| PD-010 | 权属事件的历史日期与登记知识截止双时间查询 | synthetic-tested + real-source-fixture | US20050270311A1在2005-02-08与2005-12-31不同登记快照；US20050182770A1登记晚于所载生效日一天 | USPTO原始转让文件、合同法律效力、第三方独立验证 |
| PD-011 | 收购、专利转让、产品上线分离的企业史机制检验 | historical-research-candidate | Where2收购2004年、Google Maps2005-02-08上线、相关专利公开和后续权益事件并列对读 | 专利是否由Where2直接原始持有、具体权利要求是否实际部署 |

上述PD-009/010工具均已运行并通过18项单元测试，**不等于EPO官方族或司法权属结果已核实**。详见[方法v0.2](PATENT_EVIDENCE_TOOLKIT_V0_2.md)和[第16号历史研究](../research/16-google-maps-ownership-timeline-and-family-audit.md)。

## 2026-11-20｜v0.3专利文献与跨企业复用新增

| ID | 能力 | 当前状态 | 已实际验证 | 未完成 |
| --- | --- | --- | --- | --- |
| PD-012 | 专利索引全文可用性审计 | real-sample-tested | 3件Tencent/Huawei专利，claims/description均missing_in_index；公开华为原文有10项权利要求 | 合法原文多源段落核对、真正权利要求拆解 |
| PD-013 | 中国分案申请号/原案时间异常分类 | synthetic-tested + real-source-fixture | CN200710165788号、2002-06-11日期、parent division；从错误告警降为历史日期口径待核 | 正式CNIPA原案、分案提交及法律日期影像 |
| PD-014 | 真实第二企业的同一数据处理流水线 | real-sample-tested | Tencent CN 2002一页4/4、2应用/2族；Huawei CN 2002只有8/2039被强制完整性规则拒绝 | 全量Huawei/别名与法域覆盖，第三方跨数据商复核 |
| PD-015 | 官方概念与官方个案证据等级分离 | documented + access-tested | EPO官方DOCDB/INPADOC定义已核；具体EP官方详情403，USPTO官方查询UI可达但未取原始deed | EPO正式具体族标识、USPTO登记原文件取得 |

方法说明：[v0.3](PATENT_EVIDENCE_TOOLKIT_V0_3.md)；研究记录：[17](../research/17-epo-tencent-huawei-quality-audit.md)。

## 2026-11-20｜v0.4新增：真实专利文献结构及多版本轨迹

| ID | 方法/能力 | 状态 | 实际验证 | 不足与下一道验收 |
| --- | --- | --- | --- | --- |
| PD-016 | 公开号/申请号/文种和HTML段落源定位 | real-sample-tested on provider HTML | 华为、腾讯和Google Maps共6个A/B/C文献，588个有URL锚点的说明书段落 | 专利局正式XML和原始PDF独立核对 |
| PD-017 | 逐项权利要求及显式claim-ref引用图 | real-sample-tested on provider HTML | 6文献173项权项；页面编号与解析编号一致，保留明示从属关系的候选图 | 法律完整依赖、组合/范围引用、不同文本格式测试 |
| PD-018 | 公开版对授权版的计数与文本哈希对照 | real-sample-tested, legal inference pending | 华为10→7、腾讯4→4、Google Maps 74→74；按位置HASH差异6/4/74 | 原始审查文件、修改记录与实质权利范围人工认定 |
| PD-019 | AI可引用的证据原子及原文使用隔离 | real-sample-tested | evidence_id、来源URL段落锚点、HTML校验摘要、单段HASH；6份原始HTML仅在私有研究区 | 更多正式XML适配器、来源级许可、自动版次追踪 |

此版本只称Google Patents HTML的适配器，**不是WIPO ST.96/XML、ST.97/JSON、EPO ST.36、USPTO Red Book合规实现**。文件级SOP见[工具v0.4](PATENT_EVIDENCE_TOOLKIT_V0_4.md)。


## 2026-11-21｜v0.5官方原生XML与授权后权利史

| ID | 方法/能力 | 当前状态 | 已实际验证 | 下一步核验 |
| --- | --- | --- | --- | --- |
| PD-020 | EPO真实EP Patent Document XML解析与三语权项去重 | real-official-source-sample-tested | EP1004359B1：en/de/fr各7项；EP0729353B2：各4项，保留原始DTD和段落锚点 | 不同历史EPO DTD、完整法律依存、DTD校验 |
| PD-021 | WIPO ST.96官方示例映射与schema来源校验 | official-synthetic-sample-tested | Annex VII V6_0/V8_0两份TEST；各10权项、70段；v10目录实际文件声明V8_0 | 真实ST.96数据交换与XSD校验 |
| PD-022 | EPO A1只含著录时的缺全文处理 | real-official-source-sample-tested | EP0729353A1可取XML不含权项，工具明确区分“这份XML未提供”和“历史原件不存在” | 官方A1影像及其他同年代完整性对照 |
| PD-023 | 同一EP申请的B1/B2异议后文本历史比较 | real-official-source-sample-tested; legal-analysis-pending | EP0729353 B1 6英文权项、2012 B2 4项；三语节点18→12，按相同编号4个位置HASH变化 | 异议原始决定书、修改理由、逐项法律范围人工复核 |
| PD-024 | EPO公开申请人/权利人标签的时点保留 | real-official-source-sample-tested; chain-pending | A1/B1中Alkermes Controlled Therapeutics, Inc.，B2中Alkermes, Inc. | EPO正式登记、法人关联/交易与有效日期 |
| PD-025 | USPTO Red Book v4.7 DTD | source-definition-obtained, parser-NOT-implemented | 官方DTD文件62,376字节，已确认格式规范 | 取得实际授权XML并做版本相关解析测试 |

交付材料：[v0.5 SOP](PATENT_EVIDENCE_TOOLKIT_V0_5.md)、[第十九轮历史记录](../research/19-alkermes-ep-postgrant-and-official-xml.md)、[来源审计数据](../data/examples/official-xml-four-source-derived-2026-11-20.json)。不要把WIPO TEST与真实发明混同，不把DTD文件当授权专利文本。


## 2026-11-21｜v0.6程序事件与知识时间

| 方法ID | 能力 | 当前状态 | 实际证据 | 仍需核验 |
| --- | --- | --- | --- | --- |
| PD-026 | 专利程序事件类型与来源等级审计 | real-source-fixture + synthetic-tested | EP0729353和两件官方上诉案12条记录，防止撤销通知被当成最终无效 | 官方异议文件、上诉全文及法律效力 |
| PD-027 | 历史事件日与当时可知日双时间视图 | real-source-fixture + synthetic-tested | 2005-07-20事后5条事件，仅2条有已核原始公开出版日期 | 各索引事件最早可知/公告日期 |
| PD-028 | 跨案主体角色网络候选而非自动身份归并 | official EPO page + indexed event | 两件EPO官方T案件、EP0729353聚合索引中的相反异议方向候选 | 法人实体关系、独立经营史和技术竞争关联 |
| PD-029 | Claim Lifecycle ID与证据来源双向约束 | real-source-fixture + synthetic-tested | 4项affected_claim、impact_type、verification_next，引用未找到的事件即拒绝 | 与编辑OS和更广企业专利母集接合 |

第20轮研究：[research/20](../research/20-alkermes-sri-opposition-network.md)；[v0.6规范](PATENT_EVIDENCE_TOOLKIT_V0_6.md)。它是可测试的方法积累，而不是完整企业本纪已写成的证据。

## 2026-11-22｜v0.7 多窗口覆盖与公报日期快照

| 方法ID | 能力 | 实证 | 待核 |
| --- | --- | --- | --- |
| PD-030 | 逐查询完页、按公开号合并、名称交集和分年统计 | 七窗口 77 页，3,642 条查询返回去重为 3,297 份，重取旧公开号集合的哈希一致 | 历史法人及别名扩展、多源独立族对账 |
| PD-031 | 依据公报出版日期回溯版本可见性 | 1999 年底申请日命中 64 份、当时已出版 22 份；两组 EPO 原生 A/B XML 复核著录角色 | 逐件公报对照和历史法律事件的独立公开证据 |

[工具入口](../patent_evidence/README.md#v07-longitudinal-query-coverage-and-publication-dates) · [第21轮研究](../research/21-google-1996-2006-patent-coverage.md)

## 2026-11-22｜2007—2009 实证接续

- PD-030/031 复用于新增 91 页，保留前一轮 77 页的文件哈希。跨段去重合成 7,449 份公报，并核验 201 个数据库族标识跨段重复。
- PD-032 把交易公告、交割、登记封面、底层合同和专利申请号绑定。9 案 11 份 USPTO 原始登记影像、2 份 EPO 公报具有可复验来源和哈希。保留登记封面与附件角色冲突、续案的后续登记及收购未交割等情形。[第22轮研究](../research/22-google-2007-2009-acquisitions-and-patent-title.md) · [可复跑校验](../scripts/validate_google_2007_2009_coverage.py)

## 2026-11-22｜2010 母集与同一资产的多次登记

- PD-030/031 增加 46 页，与前段合计 214 页。两个交割日各自重放申请日和公报出版日。
- PD-032 增加法人名、逐申请号、登记卷页三步复核，查得七条路径的 96 份登记，补回一条名称漏查的让与，并以官方公报验证实际续案和临时申请优先权。 [第23轮研究](../research/23-google-2010-on2-admob-patent-assets.md) · [可复跑校验](../scripts/validate_google_2010_acquisition_assets.py)

## 2026-11-22｜2011 母集和大批权属登记

- PD-030/031 增加 99 页、4,792 份公报和实际交割日出版快照，合计取齐 313 页。
- PD-032 用转让双方组合、执行日复核、卷页全量分页，校验 IBM 的 2,394 条清单行与授权日期口径。Motorola 两个大卷页的 12,500 条记录核对总数和卷内序号，按三个申请号复核具体路径。 [第24轮研究](../research/24-google-2011-ibm-motorola-patent-transfers.md) · [复跑校验](../scripts/validate_google_2011_patent_transfers.py)
