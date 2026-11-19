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
