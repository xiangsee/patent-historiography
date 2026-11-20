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
