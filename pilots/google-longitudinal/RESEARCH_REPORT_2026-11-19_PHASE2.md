# 《企业史记》数据研究02：同族不等于同一发明，更不等于同一企业的技术

研究日期：2026-11-19。阶段：v1.0校准期。方法路线：先建立来源与权属规则，再逐步扩展完整Google历史专利母集，正式《谷歌本纪》尚不启动。

## 研究问题
上一阶段完成Google Inc.申请日2000—2004、不设公开国家限制22页/1,067文献。现在要验证三个基本假设：
- family_id是否可以用作“一项发明”的直接计数单位？
- 当前Google名下的早年申请，是否确属当年由Google创造？
- 数据中是否可以发现一个不同于传统企业产品年表的技术起源线索？

## A. 数据范围及实际取数记录

继续连接IPHouse Research的patents_bulk，用完全相同的assignee匹配Google Inc.、不设公报局过滤，但将申请日期限定为2005-01-01至2005-12-31；每页50条，共17页、850条，全部成功。此前2000—2004年22页/1,067条同样从私有研究区重新核对。合并后本研究仅包含两个清楚限定的窗口，不代表Google全部时期、全部名称或所有法域完整覆盖。

| 单位 | 2000—2004 | 2005 | 合并按ID去重 |
| --- | ---: | ---: | ---: |
| 公报文献 | 1,067 | 850 | **1,917** |
| 申请号 | 843 | 622 | **1,465** |
| 数据库family_id | 522 | 370 | **836** |

窗口内不同family_id的简单相加是892，而两个窗口合并去重只有836，重复56个跨窗口家族ID。家族标识不属于天然的年度独立发明指标。2005年850条中有589条的优先权年份早于申请年；196条的assignee数组同时出现至少一个非Google名称，只能标为“历史归属有待核查”，不是已确认的收购或共同研发数。2005年公报局以US 284、EP 164、WO 142、CA 139、AU 59为主。

[完整聚合数据](derived/google-inc-2000-2005-joint-audit.json)，[首轮2000—2004完整分页](derived/google-inc-2000-2004-global-audit.json)。原始全量响应只存在非公开研究区，不推送到此公开GitHub。

## B. EPO的家族定义说明：不能想当然定义IPHouse family_id

EPO官方定义：
- DOCDB simple family：具有相同优先权基础，通常技术内容相同或高度对应（也包括其编目规则对继续申请/分案的处理）。
- INPADOC extended family：申请之间直接或间接具有优先权/技术联系，技术内容可能相近但并不相同。

EPO原始定义：
https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/docdb
https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/inpadoc

目前无法仅凭family_id字段名证明IPHouse提供的是DOCDB还是INPADOC型，必须抽样对照优先权图及EPO家族标识。更不能把某个标识直接称为一件自主发明。

## C. 代表性反例一：同一family_id可以包含不同技术及权利人

IPHouse对family_id 3814761单独查询返回358条记录；当前2000—2005小切片中观察到14条公报、7个申请号、6种题名，涉及相机模块、便携打印、存储模块与图像处理。Google Patents相关家族展示101个申请（与358篇公报不是同一统计单位）。

相关公开专利：
- https://patents.google.com/patent/US6712452B1/en ：2000年5月由Silverbrook Research申请，后在2012年登记转至Zamtec。
- https://patents.google.com/patent/US7557828B2/en ：2004年10月由Silverbrook Research申请，2013年登记转至Google。

**研究结论**：同一关联家族内的不同具体申请，可能拥有不同的权利归属。不能因为同族某一成员后来进入Google，就把全家族作为Google在2000年自主发明，更不能把358篇公报当成358项研发成果。具体美国转让记录来自专利聚合页，尚未复核USPTO登记影像，需保留证据等级。

## D. 代表性反例二：一项进入Google组合的早期广告技术，其源头可追溯至DoubleClick

数据库family_id 24968825在2000—2004切片中出现5个申请号，但其前身US5948061A由DoubleClick在1996年10月申请，早于Google成立。公开专利权属事件记载，2008年9月将与DoubleClick合并相关的权利变动登记至Google（生效日标为2008年5月1日）。
https://patents.google.com/patent/US5948061A/en

2000—2004若只按今天Google名下的同族成员统计，就容易把DoubleClick技术的后续文献放到Google当年的研发史。它应先归于DoubleClick的技术起源史，再研究Google何时通过企业交易纳入该权利组合。合并事件记录证明权利流转，不自动证明原有工程人员或实际代码全部转入Google。

## E. 由专利数据主动提示的Google Maps候选转折

将IPC前缀G01C21作为与路径/导航有关的**粗筛**（可能有误分及交叉）：
- 2000—2004五年：16篇匹配公报、3个不同provider family_id。
- 2005一年：53篇匹配公报、12个不同provider family_id。

两段长度不同，不可直接作为统计增长率。但2005年记录题名集中出现A digital mapping system、Generating and serving tiles in a digital mapping system等，值得追查。

实例：[US20050270311A1](https://patents.google.com/patent/US20050270311A1/en)主张2004-03-23优先权、2005-02-05申请，著录Lars/Jens Rasmussen等人，2005-08-12发生向Google的发明人权益转让登记。Google当年2005-02-08宣布Google Maps上线：
https://googleblog.blogspot.com/2005/02/

学术史研究[Exploration, exploitation, and mode of market entry: acquisition versus internal development by Amazon and Alphabet](https://doi.org/10.1093/icc/dtad015)论述Google于2004年10月收购Where 2 Technologies，相关开发团队包括Lars/Jens Rasmussen、Stephen Ma、Noel Gordon。时间交集强烈提示“被收购研发能力与后续产品及专利布局的关系”，但尚未找到直接档案证明该专利在收购前属于Where2，或权利要求实际逐项实施于Google Maps。

这就不是选择了某个著名产品再到处找一件专利作装饰；而是先从技术分类出现候选，再用产品史和组织并购史寻找可核验解释。它可以成为未来《企业史记》世家/列传/书共同校验的候选。

## F. 方法论修订

以后每条技术史证据分四张互相关联的表：
1. publication：公报号、文种、公开局、公开日期；
2. application / priority：申请、不同优先权、母案或继续申请、技术范围；
3. family_network：DOCDB/INPADOC/provider三种不同口径、关系图与跨时段映射；
4. ownership_event and origin：最初申请人、实际完成研发的组织（需要独立证据）、历史转让/许可、并购控制权起讫，不得由当前assignee倒推。

年度图可以分别展示公开文献、申请、EPO简单同族、扩展同族、历史自主发明（仅经证实）以及当期拥有资产，但**不能把这些曲线合并成一个“企业创新数量”**。

## G. 下一阶段检验

- 与EPO可取得的家族ID及原始优先权图对照至少10个有代表性的provider family_id，尤其是3814761和24968825。
- 核原始USPTO转让卷宗与主体历史；对DoubleClick、Silverbrook、Where2三种技术来源分别评估自研、收购、受让或合作关系。
- 再按同一规范扩展2006—2009或其他区间，而不是只把匹配量相加。
- 将“Google Maps技术来源”作为来自母集的第一项重点候选史实，待研究后再判断能否改变企业历史编年与世家/列传立篇。
- 《史记》原典与企业专利史理论融合仍需补齐，正式《谷歌本纪》继续HOLD。

**阶段验收：2000—2005限定检索集合全部分页、家族去重的跨年重复检验和两个外部权属反例已完成；Google全历史原始自主研发组合尚未完成。**
