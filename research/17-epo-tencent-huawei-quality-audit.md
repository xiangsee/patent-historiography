# 第十七轮｜官方家族口径、第二企业验证与专利全文可见性

日期：2026-11-20。目标：同时服务《企业史记》的历史解释与Patent Evidence Workbench工具迭代。不把局部检索结果或外部网页视为已经完成企业专利全集。

## 1. 官方规则已核；Google Maps具体家族和原始转让仍待查

EPO官方明确区分DOCDB simple与INPADOC extended：
- 简单家族侧重同样的优先权及同等技术内容；继续申请、分案及部分继续申请在自动归集上有特别规则。
- 扩展家族可通过直接/间接共享优先权连接相近却不完全相同的技术。
- 一家数据商的family_id不必然与任一官方口径相同。
来源：https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/docdb 和 https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/inpadoc

实际个案访问尝试：EPO Register以EP04812220、EP05729642查询以及EPO OPS以EP1738329A2查询，未认证直接请求均返回HTTP403，未获得正式个案家族结果。这是访问/权限障碍，不能据此称无记录，也**不能**把提供方的申请号列表升级成已核实EPO官方家族。

USPTO的Assignment Search主页HTTP200可读，但未能从该查询渠道取得具体Google Maps专利原始转让文书；未认证的ODP assignment API请求HTTP403。USPTO官方强调登记是administrative/ministerial，不核查合同或转让行为的法律效力。2026年7月官方公告将部分专利转让导出功能迁至Open Data Portal。
来源：
https://www.uspto.gov/patents/maintain/patents-assignments-change-search-ownership
https://www.uspto.gov/system-status/20260707-assignment-center-patent-search-service-alert
https://assignmentcenter.uspto.gov/search/patent

这一轮的准确结论是：**官方方法规则可证，官方个案结论未取得。**

## 2. 第二公司：腾讯2002年的中国公开专利（一个完整查询窗口）

实际使用IPHouse Research search_patents：
- 条件：assignee包含“腾讯科技”、country_code=CN、申请日2002-01-01至2002-12-31；
- 后端返回total=4，一页取得全部4条；
- Workbench v0.2已实际执行--require-complete，通过并核得4个公报号、2个申请号、2个provider家族ID（34145908、34145917）。
- 两项主题：一个号码标识网络用户群组；即时通信与手机间多媒体短信互通。
- 每项都有A公开公报和C授权公报，不能将4份文献写成4件独立发明。

公开对照：
https://patents.google.com/patent/CN1482771A/zh
https://patents.google.com/patent/CN1482787A/zh

**边界**：这是特定申请人检索词、国别和一年窗口的完整数据库返回，不意味着已经覆盖腾讯集团所有研发主体、未公开技术或所有国际同族。

## 3. 华为样本：工具正确拒绝把局部数据冒充全集

同一IPHouse数据源查询：assignee“华为技术有限公司”、CN、2002全年，提供方total=2039，而本轮只取回第一页8条。
- Workbench普通audit明确报告8/2039、状态INCOMPLETE；
- 启用--require-complete时CLI返回错误，**拒绝声称取齐**。
- 不能用8条样本推断当年华为专利技术结构、数量及研发投入。

## 4. 中国分案的历史时间口径

在华为CN101166059B中，IPHouse应用号为CN-200710165788-A，但filing_date/priority_date均为2002-06-11，并另有parent.type=division，父案CN-02112025-A。
公开说明书明确表示这是2002-06-11原案CN02112025.0的分案，属于**延续的法律申请关系**。不能把编号中的2007与2002不同直接认定为检索错误，也不能用原案日期代替尚未核验的真实分案提交日期。
https://patents.google.com/patent/CN101166059A/zh

本轮新工具识别现代CN编号年份、父案division标识，输出“later number with divisional parent, review”而不自行改写时间。

## 5. 全文API有摘要，却缺权利要求和说明书

实际通过IPHouse get_patent_detail(include_full_text=true)查询：
CN1315292C、CN1299492C（腾讯），CN101166059B（华为）。
3件都返回标题和长度为500字符的摘要片段，却都把claims、description记为missing_in_index，source_chars=0。它只证明**连接的数据索引中没有这些部分**，不证明真实专利没有权利要求或说明书，也不能确认摘要的原始完整性。

公开CN101166059A页面展示10项权利要求及说明书，可直接与“索引缺失”做反证。
https://patents.google.com/patent/CN101166059A/zh

v0.3工具将missing_in_index、truncated、not_requested、indexed_but_not_returned分开记录；不复制原始受版权限制的大段文本，仅发布可追溯的可用性统计。

## 6. 对五体和工具的具体修订

本纪：跨企业检索的匹配数不等于创新强弱。表：应用编号、继承原案日、正式申请/授权/公开各自独立。书：法律转让、分案规则及资料公开的制度条件。世家：同族与分案是文献上的技术谱系候选，不自动证明工程实现。列传：著录人名不能直接作为实际贡献的完整证明。

**下阶段**：正式EP DOCDB/INPADOC家族映射、USPTO原始转让、可许可专利全文段落与权利要求提取，并检验Google Maps的同一历史转折。不是再无限扩充Google成功故事。

数据审计见data/examples/cross-company-document-qa-2026-11-20.json、cn2002-text-quality-result-v0-3.json。
