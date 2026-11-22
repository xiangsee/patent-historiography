# 《企业史记》｜Patent Historiography

**v1.7.0 · Google 1996—2006 专利覆盖与历史归属 · 2026-11-22**

以专利记录及其他史料为基础，用《史记》完整的**本纪、表、书、世家、列传**五体体系研究企业与产业发展史。不是古文化写作，也不是专利排行榜。**全量专利不是全部创新，五体不是五个彼此独立的栏目。**

《企业史记》为项目暂定总名；《企业本纪》降为五体之一。保留仓库名称 patent-historiography；研究与出版均不代表被研究企业。







## 2026-11-22｜第21轮：Google 创立前后与 2006 年专利覆盖（工具 v0.7）

- 取齐 Google Inc. 与 Google LLC 的七个查询窗口共 77 页，旧 2000—2005 公开号集合与存档哈希一致。1996—2006 按公开号去重得 **3,297 份公报、2,377 个申请号、1,230 个数据库族标识**。[第21轮研究](research/21-google-1996-2006-patent-coverage.md) · [派生统计](pilots/google-longitudinal/derived/google-1996-2006-name-coverage-2026-11-22.json)
- 早于 Google 设立月份的申请日命中 32 份。斯坦福名下的 PageRank 公报另由 USPTO 公报和 SEC 公开许可合同接入。Xerox、Microoptical 两个 EP 申请的 A/B 版次明确记载不同主体角色。[EPO 角色证据](pilots/google-longitudinal/derived/google-early-epo-party-evidence-2026-11-22.json)
- 新增 `coverage-check`，按名称查询去重并重建公报出版日期快照。完整集团历史归属、同族核验和五体首篇写作仍有证据门槛。[使用与复核命令](patent_evidence/README.md#v07-longitudinal-query-coverage-and-publication-dates)

## 2026-11-21｜第20轮：EPO程序事件和跨案主体网络（工具v0.6）

- [第20轮研究：授权后的异议、撤销通知、上诉与跨案企业角色](research/20-alkermes-sri-opposition-network.md)：Alkermes相关EP0729353从2002年B1到2012年B2，不能把2005年第三方索引的“撤销通知”认作不可上诉的终局撤销。
- [可运行的程序证据工作台v0.6](docs/PATENT_EVIDENCE_TOOLKIT_V0_6.md)与[Python核心](patent_evidence/procedural_ledger.py)：严格保留事件发生时间、已核当时可知时间、来源等级、实体角色与Claim Lifecycle。
- [三案12条来源事件及4项判断](data/examples/epo-cross-case-procedural-events-2026-11-21.json)、[公开派生审计](data/examples/epo-procedure-evidence-audit-v0-6.json)、[13项新增单元测试](tests/test_patent_procedural_ledger.py)及[运行校验](scripts/validate_ep_procedural_ledger_v06.py)。累计57项测试通过。
- EPO官方T0003/98、T0507/98分别显示Southern Research作为申请人、Alkermes相关主体作为异议方；EP0729353第三方法律事件索引则记载Southern Research对Alkermes相关专利提出异议。**这是不同法律程序的角色候选，不证明同一法人、市场竞争战略或因果关系。**
- **主线下一步回到企业长时段专利母集**：用程序事件和来源质量对Google/华为/腾讯等企业的历史专利组合做覆盖与不确定性审计，不继续无限深入单案。

## 2026-11-21｜官方XML双源验证与专利权利史（v0.5）

**从HTML展示层推进到真实专利局原生XML。** 工具已处理两件EPO真实专利的B类公开文献与两份WIPO ST.96 TEST XML，并追踪EP0729353的1996 A1、2002 B1、2012 B2三个历史公开版本。

- [第十九轮历史研究：Alkermes相关欧洲专利授权后的文本变化](research/19-alkermes-ep-postgrant-and-official-xml.md)。
- [Patent Evidence Workbench v0.5说明与命令](docs/PATENT_EVIDENCE_TOOLKIT_V0_5.md)：[EPO/WIPO官方XML解析器](patent_evidence/official_xml.py)、[B1/B2结构差异对照](patent_evidence/official_version_diff.py)、[合成回归测试](tests/test_patent_official_xml.py)。
- [EPO真实专利/WIPO标准TEST样例的派生结构审计](data/examples/official-xml-four-source-derived-2026-11-20.json)、[EP0729353 A1→B1→B2历史证据](data/examples/alkermes-ep0729353-1996-2012-derived.json)。
- [公开派生数据校验脚本](scripts/validate_official_xml_2026_11_20.py)。两件EPO真实专利主语言权利要求分别为7和4项，三语节点合计21和12；不能误算为21或12项独立权利要求。
- **来源边界**：WIPO样例是TEST非真实专利；v10目录下XML实际声明schema V8_0；已取得USPTO 2022年Red Book DTD但尚未解析真实USPTO授权XML。EPO原始XML与完整正文留在私有研究区，公开只保留派生统计、来源与哈希。
- **史学边界**：EP0729353的B1英文6项→B2英文4项，不能据此认为法律范围缩小三分之一；B1/B2的Alkermes公司名称不同，也不能据此推断实际转让。

## 2026-11-20｜文献工作台v0.4：解析真实权利要求、段落与版本差异

**首次将三家企业、六份专利公开/授权文献转换为可追溯的结构化证据索引：173项编号权利要求、588个有锚点的说明书段落、三组版本对读。** 公开索引不含原始全文；无法仅凭HTML哈希差异认定法律保护范围变化。

- [第18轮史料研究：同一技术的申请公开和授权历史](research/18-six-publications-structure-and-version-history.md)；[工具v0.4方法说明](docs/PATENT_EVIDENCE_TOOLKIT_V0_4.md)。
- [六份文献的来源、原文校验摘要、权利要求与说明书定位、三个版本差异JSON](data/examples/six-patent-publication-version-structures-2026-11-20.json)。
- [HTML原文结构解析适配器](patent_evidence/structured_docs.py)、[不同版本差异对照模块](patent_evidence/version_diff.py)、[CLI parse-html/compare-html](patent_evidence/cli.py)、[验证脚本](scripts/validate_document_versions_2026_11_20.py)及[合成测试](tests/test_patent_structured_docs.py)。
- **权利边界**：Google Patents的单篇HTML只作为可核对的公开聚合页面；尚未获得对应官方专利局原始XML/PDF和审查全过程，不宣称符合WIPO ST.96/ST.97、EPO ST.36或USPTO Red Book标准。新适配器需要可选beautifulsoup4，其他核心工具仍以标准库运行。

## 2026-11-20｜双主线第3轮：跨企业方法与专利全文覆盖质量

- [第17号研究：EPO规则与个案访问、腾讯/华为第二企业实证](research/17-epo-tencent-huawei-quality-audit.md)
- [Patent Evidence Workbench v0.3说明](docs/PATENT_EVIDENCE_TOOLKIT_V0_3.md)：新增[专利全文字段覆盖与分案日期规则](patent_evidence/text_quality.py)、[CLI命令](patent_evidence/cli.py)、[6项新增单元测试](tests/test_patent_text_quality.py)。
- [跨企业派生审计](data/examples/cross-company-document-qa-2026-11-20.json)：腾讯2002年CN查询4件文献完整取数→2申请、2provider族；华为同窗口仅取8/2039且完整性强制检查正确失败。
- [3份真实专利全文索引字段状态](data/examples/cn2002-text-availability-v0-3.json)与[工具派生输出](data/examples/cn2002-text-quality-result-v0-3.json)：claims/description三件均索引缺失，不等于原文不存在；1件2007号CN分案沿用2002原案日的历史时间需区分。
- [公开校验脚本](scripts/validate_cross_company_2026_11_20.py)。当前工具24项单元测试通过，原有历史证据/长期数据验收仍保留。
- **没有取得EPO官网具体Google Maps案件家族资料或USPTO原始转让影像**；官方规则已核≠案件已核。数据访问状态在第17号报告中逐项公开。

## 2026-11-19｜双主线第2轮：工具v0.2与Google Maps技术史互证

- [研究第16号：Google Maps外部研发来源、专利优先权及不同时间的转让登记](research/16-google-maps-ownership-timeline-and-family-audit.md)
- [可执行方法v0.2说明](docs/PATENT_EVIDENCE_TOOLKIT_V0_2.md)；[lineage.py](patent_evidence/lineage.py)实现优先权申请号关系与双时间权益登记证据查询
- [4件地图专利与权益事件的真实小样本](data/examples/maps-priority-rights-v0-2.json)；[实际运行输出](data/examples/maps-lineage-v0-2-derived.json)
- [历史证据新增10项测试](tests/test_patent_lineage.py)，连同v0.1共18项单元测试通过；命令行history-check已在三个历史时点真实执行。
- 数据边界：IPHouse优先权列表和Google Patents法律事件是可定位**来源线索**，尚未审USPTO原始登记影像与EPO正式DOCDB/INPADOC家族号，不宣称法律权属裁决、Where2原始持有特定专利或2005年产品实现专利全部权利要求。

## 2026-11-19｜新增成果主线：专利证据工作台（通用工具）

《企业史记》不只是写企业专利历史；每次研究也要逐渐留下可移植的专利数据处理**方法、工具、测试与可审计证据**。与五体史学主线并行，研究问题指导工具，工具的质量结果反过来修正历史判断。

- [工具箱v0.1总体说明](docs/PATENT_EVIDENCE_TOOLKIT_V0_1.md) · [通用Python核心](patent_evidence/core.py) · [CLI](patent_evidence/cli.py) · [使用入口](patent_evidence/README.md)。
- [真实样本验证结果](data/examples/google-2000-2005-patent-workbench-v0-1.json)：39页、1917公报、1465申请、836个provider家族ID和56个跨窗口重复族；7项单元测试通过。
- [10个专利族接口对照](data/examples/iphouse-family-api-audit-result-v0-1.json)：两接口8组计数一致、2组不一致，均排除了锚定公报；不将疑似50成员截断当成已核实的后台规定。
- [方法卡模板](templates/PATENT_METHOD_RESULT_CARD.md) · [方法注册表](docs/PATENT_METHOD_REGISTRY.md) · [方法论研究纪要](research/14-patent-methods-first-real-experiment.md)。

**现阶段能力边界**：已实现输入、标准化、分页与族质量审计；EPO官方DOCDB/INPADOC核对、申请时点权属重建、全文/权利要求和知识图谱仍在下一阶段。工具不接入私有原始数据向公网分发。

## 2026-11-19｜完成第一个全球检索片段的全部分页（请先阅读）

首次实际从知产宝IPHouse检索、分页取得 Google Inc. 2000—2004年申请日期、不限公开国家/地区的一整个数据库查询集合：**22页、1,067篇文献、843个申请号、522个未核实类型的provider family_id**。美国公报子集合452件。此结果不是Google全史或其自主发明总量。

- [正式取数与方法审计报告](pilots/google-longitudinal/RESEARCH_REPORT_2026-11-19.md)
- [22页分页、国别/年度数据及去重派生统计](pilots/google-longitudinal/derived/google-inc-2000-2004-global-audit.json)
- [历史名称与中国/美国/EP/WO等21项查询探针](pilots/google-longitudinal/derived/alias-region-count-probes-2026-11-19.json)
- [纯派生数据校验脚本](scripts/validate_google_inc_2000_2004_global.py)

原始整批响应仅保留于非公开研究区。**522是数据库不同族ID数，并非已经验证的DOCDB简单专利族数；Google Inc/LLC及中英文名称命中有重叠，不能累加。**下一轮优先历史申请人关系与同族口径交叉核验，然后扩张到更长时间窗口；正式五体企业史仍按原定门槛暂缓。

## 2026-11-16｜项目重新聚焦（请先阅读）
**总体方向未错，但研究资源明显向Google—Overture单一案例与程序光盘倾斜；企业整体长期专利母集尚未建成。**
- [阶段总审计](docs/PROJECT_REVIEW_2026-11-16.md)：逐项对照原始目标，保留哪些成果、哪些支线降级
- [方法核心v1.0候选](docs/METHOD_CORE_V1.md)：历史问题→专利母集→历史发现→五体互见→作品
- [Google长时段专利母集可行性设计](pilots/google-longitudinal/CORPUS_FEASIBILITY.md)及[主体候选表](pilots/google-longitudinal/ENTITY_CANDIDATES.csv)：**设计已启动，真实全球母集尚未取得**
- 优先：#9/#10理论合成与#2/#3整体数据可行性；然后#11五体整体试验。#14程序CD与#15单案版本问题降为不阻塞的资料支线；正式文章#7仍保持HOLD。

## 第八轮｜从专利正文进入原始档案存续研究

- [US7110993光盘档案获取审计](research/12-uspto-cd-archive-audit.md)：确认22,808文件、101,776,919字节及dir_s为公开文本的声明；2001历史提交制度、现行USPTO提供副本与2026账号/API限制已核；**未取得光盘或真实目录**。
- [同申请三版交叉引用对读](research/13-us7110993-publication-versions.md)：2003 A1和2005 A9的申请族文字，与2006 B2所述2001中间案存在差异，待原始审查案卷解释。
- [档案存续证据门槛](docs/ARCHIVAL_SURVIVAL_PROTOCOL.md)：区分文献提及、接收证明、官方保管、实际复制、完整性验证与法律公开。
- [案卷访问状态数据](data/examples/us7110993-cd-access.json)、[JSON Schema](schemas/external-archive-artifact.schema.json)、[核验脚本](scripts/verify_archival_access.py)。
- [USPTO官方询问函模板（未发送）](templates/USPTO_CD_INQUIRY.md)。没有登录USPTO账号、付费下单、获得代码或向公开仓库上传任何程序附录。
- **G1仍部分通过，G2/G3/G4仍未达到正式方法验收，G5未开始**。本轮新增的实质进展是史料存续与不同公开版本的证据治理，**不是“原始代码已下载”**。

## 第七轮｜世家与列传实证补强

- [Google—Overture技术谱系、工程师和商业分销史](research/10-search-advertising-lineage-and-people.md)：Google/Overture 2000—2002年的公司级营收对照；Overture的渠道成本；GoTo主案及后续申请族；Google的GSP→暂缓VCG→2012年内容广告重启的技术分叉；Veach等工程师的可证贡献与限制。
- [收入与渠道成本数据](data/examples/search-ads-company-financials.json) · [专利族及聚合转让事件](data/examples/search-ads-patent-lineage.json) · [技术路线、人物贡献证据](data/examples/search-ads-tech-forks-and-people.json)。
- [世家与列传分级证据规则](docs/SHIJIA_LIEZHUAN_PROOF_RULES.md) · [独立检查脚本](scripts/validate_round7.py)，已在远端克隆后执行通过。
- **事实边界**：Google Patents记录不是USPTO转让原始影像；2014年Google内部学者论文是重要参与者回顾，不是客观代码鉴定；Overture整体收入领先不等于广告市场份额领先或解释Google最终胜出的原因。
- **门槛**：G3继续PARTIAL，但已有真实技术分叉与署名以外人物贡献证据；G1/G2部分完成，G4部分压力测试，G5尚未通过。第一篇正式企业史继续暂缓。

## 第六轮｜从AdWords公告走进真正的专利与竞争者历史

**重要进展**：不再只依据Google自述其2000年产品发布，而是将GoTo/Overture早期付费搜索专利、Google 2001优先权的广告排序专利、2002年AdWords Select、2002–2004年诉讼及综合和解纳入同一事件和命题库。

- [真实企业五体互见及制度史压力测试](research/09-google-overture-patent-commercial-history-test.md)：修订“Google 2000年即采用后来的CPC排序”和“2004年270万股全是专利许可费用”等错误历史表述。
- [10条来源索引](data/examples/adwords-overture-source-index.json) · [14项事件](data/examples/adwords-overture-events.json) · [8条Claim Lifecycle示例](data/examples/adwords-overture-claims.json)。
- [Python核验脚本](scripts/verify_adwords_case.py)：JSON Schema和跨源ID检查已通过。属于**小样本史料工程**，不等于企业完整专利族。
- [五体整书／节点级立篇裁量](templates/FIVE_FORMS_ASSEMBLY_DECISION.md)：整部书保留五体，单一转折不机械写成五篇；表需经“撤表会失去什么信息”检查。
- **门槛**：G3由PENDING升为PARTIAL（表与书出现可追溯的反向修订）；G1/G2仍不完整，G4部分反证已覆盖，G5未通过。正式《谷歌本纪》仍不启动。

## 原典精读进度（第二轮）

- [《史记》11个原典入口的五体结构对读](research/04-shiji-original-reading-round1.md)：关键段落及史料校勘问题，非全文精校完成。
- [秦亡汉兴：五体互见结构样板](research/05-classical-five-forms-cross-reading.md)：用于验证体例如何互见，不是企业史实证。
- [史记/专利共通的史料批判](docs/SHIJI_SOURCE_CRITICISM.md)：文献层、事实层、作者评判和后人注释必须区分。
- **学术验收**：G1 partial；G2/G4/G5 pending；G3古典结构演练partial。首篇仍未启动。

## 第四轮｜方法论的新发展

- [阮芝生两篇论文与“五体的两层创造”](research/06-ruan-and-two-layer-book-architecture.md)：1979/1980官方摘要已核，PDF全文尚未逐页阅读。
- [《史记》时间起点与多时制研究](research/07-three-chronologies-and-time-origin.md)：原典关键段落、2025徐建委官方摘要和网络转载文字对读，正式脚注待查。
- [整书编纂架构](docs/BOOK_ARCHITECTURE.md)：**两层编纂、五体互见、一库证据**。
- [阅读状态登记](docs/READING_LEDGER.md)：区分书目、摘要、网络转载、原典关键段落及正式全文。
- [历史观察窗口样例](data/examples/shiji-chronology-scopes.json)与[测试脚本](scripts/check_chronology_examples.py)：五年和八年的不同叙事范围并存；示例算术和Schema验证已通过。
- [整书蓝图模板](templates/BOOK_BLUEPRINT.md)、[book-plan Schema](schemas/book-plan.schema.json)。
- **验收：G1仍为PARTIAL，其余门槛未通过；第一篇企业史正文继续暂缓。**

## 三项必须先完成的方法研究

1. [《史记》的五体、互见、史料批判与叙事方法](research/01-shiji-historiography.md)
2. [企业专利史研究：六组学术进路及其解释边界](research/02-patent-history-schools.md)
3. [五体一库：纪传体企业专利史的融合框架](research/03-five-forms-synthesis.md)

## 五体的历史任务

| 体例 | 要回答什么 | 不能误写成 |
|---|---|---|
| 本纪 | 企业的历史转折和产业地位 | CEO年表、成就清单 |
| 表 | 多主体、多时点、多条历史线的交错与核验 | 装饰性的专利数折线图 |
| 书 | 研发、产权、标准、组织、许可、商业化制度的演变 | 专利法知识普及 |
| 世家 | 能力共同体、技术或组织谱系如何延续、分支与断裂 | 子公司目录 |
| 列传 | 人、团队、竞争者的具体行动与制度处境 | 发明人排名或英雄传 |

另外可设有证据边界的“**研究者按**”，承担史家论断功能，但不是第六个并列体例。

## 方法的三个约束

- **两层编纂、五体互见、一库证据**：第一层是各体独立研究，第二层是总问题、篇次、竞争解释与跨篇修订；共享史料、主体、事件、专利与命题。
- **专利是史料，不是全部历史**：同时研究商业秘密、产品、商业化、组织、政策、制度与竞争者。
- **先方法后文章**：本阶段**不开始《谷歌本纪》或其他第一篇正文**。通过[方法论验收门槛](docs/METHODOLOGY_GATE.md)，才进入具体企业的五体完整目录和初篇设计。

## 工作入口

[五体编纂协议](docs/FIVE_FORMS.md) · [史学架构](docs/HISTORIOGRAPHY.md) · [学术来源与阅读状态](docs/REFERENCES.md) · [研究路线](docs/ROADMAP.md) · [决策日志](docs/DECISIONS.md) · [数据规范](docs/CORPUS_PROTOCOL.md) · [史料与命题治理](docs/EVIDENCE_POLICY.md)

[五体模板](templates/) · [历史叙事单位Schema](schemas/narrative-unit.schema.json) · [Google 1996—2004预备史料](pilots/google-1996-2004/README.md)

公开仓库仅发布原创研究方法、参考索引、可分享成果；**不批量公开授权受限的原始专利数据库、他人版权文献全文或私人数据**。参见[RIGHTS.md](RIGHTS.md)。文献目前多已核实题录与摘要，重点专著的全文深读仍是下一阶段任务。
