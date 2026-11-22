# 《企业史记》第22轮｜Google 2007—2009：收购何时完成，专利何时易手

**2026-11-22 · Google 长时段专利研究 · 方法试验稿**

沿用第 21 轮口径，Google Inc. 与 Google LLC 在 2007—2009 年的六个全球查询窗口全部取齐，共 **91 页、4,152 份去重公报**。与上一轮合并，1996—2009 年两个名称累计命中 **7,449 份公报、5,343 个申请号、2,774 个数据库族标识**。另以美国众议院调查报告附表中的 26 个具名候选逐案追查交易与专利，其中九案取得 11 份 USPTO 原始登记影像。**公司交割、接收专利的法人、单件权利的登记日经常不同**，可以在 DoubleClick、Postini、On2 和 AdMob 的原件里逐项定位。 [本轮派生数据](../pilots/google-longitudinal/derived/google-2007-2009-name-coverage-2026-11-22.json) · [合并观察范围](../pilots/google-longitudinal/derived/google-1996-2009-combined-audit-2026-11-22.json) · [26 案台账](../pilots/google-longitudinal/derived/google-2007-2009-acquisition-roster.csv) · [专利权属原件索引](../pilots/google-longitudinal/derived/google-2007-2009-patent-rights-2026-11-22.json)

## 一、沿用两名称和公开号口径

来源为 IPHouse Research `search_patents`，使用 `assignee` 匹配、数据库所载申请日、不限公报局，每页 50 条。三个年度分别查询历史名称 Google Inc. 和现用名称 Google LLC，按公开号去重。各窗口的逐页总数和独立公开号数均通过完整性检查。

| 申请年 | Inc. 命中 | LLC 命中 | 名称交集 | 公报并集 | 申请号 | 数据库族标识 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2007 | 1,104 | 112 | 45 | 1,171 | 827 | 585 |
| 2008 | 1,203 | 131 | 45 | 1,289 | 947 | 620 |
| 2009 | 1,533 | 252 | 93 | 1,692 | 1,192 | 739 |
| **2007—2009** | **3,840** | **495** | **183** | **4,152** | **2,966** | **1,745** |

三年合并后按族标识重新去重，年度 585、620、739 相加会重复计入 199 个族标识。与 1996—2006 合并时另有 **201 个**族标识跨越分段边界。数据库族的归集类型仍待查。2009 年的 1,692 份公报中，1,141 份所载优先权年份早于申请年份，因此公报曲线同时反映早期申请的延续和当年的新增活动，技术来源还须逐件核定。 [查询与分年统计](../pilots/google-longitudinal/derived/google-2007-2009-name-coverage-2026-11-22.json) · [第21轮口径](21-google-1996-2006-patent-coverage.md)

在新三年窗口里，截至 2007、2008、2009 年底，申请日已到的公报分别为 1,171、2,460、4,152 份，其中公报日期已经到达的分别为 **112、589、1,149 份**。将第 21 轮向前积累的文献也纳入，2009 年底的可见版本为 3,084 份。可见性按当前数据库记录的各版本出版日回溯，历史主体及权属仍由当时的公报和有日期的登记判断。 [合并快照](../pilots/google-longitudinal/derived/google-1996-2009-combined-audit-2026-11-22.json)

## 二、逐案核对交易范围与权属时间

用众议院调查报告附表中标作 2007、2008、2009 年的 **26 个名称**作为有界名单，逐个核对交易来源，并以目标名称做专利检索。共保存 35 个名称探针，含 Green Border Technologies、SIPphone 等变体。外部附表把公告、交易和资产获取混列为年份，SEC 年报还披露了若干未逐项具名交易。例如，2007 年报在 Postini 之外列出 17 笔收购，2009 年报披露当年完成 10 笔。下表列出取得足以改变历史判断的个案，其余日期和权属状态在逐案台账中。 [众议院调查报告附表，第 354—355 页](https://www.govinfo.gov/content/pkg/CPRT-117HPRT47832/pdf/CPRT-117HPRT47832.pdf) · [2007 年 10-K 注 7](https://www.sec.gov/Archives/edgar/data/1288776/000119312508032690/d10k.htm) · [2009 年 10-K 注 7](https://www.sec.gov/Archives/edgar/data/1288776/000119312510030774/d10k.htm) · [全名单](../pilots/google-longitudinal/derived/google-2007-2009-acquisition-roster.csv)

| 个案 | 企业交易事实 | 样本专利的归属证据 |
| --- | --- | --- |
| Adscape | 2007-03-16 Delaware 合并证书记载 Neverwinter 并入 Adscape，Adscape 存续 | 2007-07-26 登记封面列 Google 为接收方，包含 US11/397,733。证书与封面所说的主体角色不同，直接转给母公司的中间文书待补。 [019614/0940](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/19614/940) |
| Green Border | 2007-04-27 签约，2007-05-11 Tapas 并入 Green Border，后者存续 | US10/971,645 等列于 2007-10-23 登记。封面记 Google 为接收方，附证书只列 Green Border 存续，直接移转链待核。以 `Green Border Technologies` 查询补足 `GreenBorder` 零命中。 [019995/0713](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/19995/713) |
| DoubleClick | 2007-04-13 签约，2008-03-11 交割，Click Holding 当时存续 | US11/250,575 的卷宗附 2008-05-01 后续法人合并文件，2008-09-24 登记。该卷页只列一项申请。 [SEC 交割 8-K](https://www.sec.gov/Archives/edgar/data/1288776/000119312508057423/d8k.htm) · [021579/0040](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/21579/40) |
| Postini | 2007-07-09 公告，SEC 季报确认 2007 年 9 月完成 | US11/689,634 列于 27 个 property numbers 的清单。Postini→Google 让与于 2009-03-25 签署、2009-04-30 登记。 [公告](https://cloud.googleblog.com/2007/07/secure-innovation-postini-joins-google.html) · [SEC 季报](https://www.sec.gov/Archives/edgar/data/1288776/000119312507238468/d10q.htm) · [022620/0513](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/22620/513) |
| Jaiku | Google 于 2007-10-09 公告已收购 | 2008 年公开的样本 US12/028,066 对应 US20080201289A1。Jaiku Oy→Google 让与于 2009-04-07 签署、2009-04-21 登记。 [Google 公告](https://googleblog.blogspot.com/2007/10/reach-out-and-message-someone.html) · [022576/0570](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/22576/570) |
| On2 | 2009-08-04 签约，翌日公告，2010-02-19 完成两步合并 | US10/713,807 先随第二步合并进入 On2 Technologies, LLC，后由 LLC 于 2010-04-16 另行让与 Google。两项在该日登记。 [签约公告](https://www.sec.gov/Archives/edgar/data/1045280/000118811209001738/ex99-1.htm) · [SEC 合并披露](https://www.sec.gov/Archives/edgar/data/1045280/000119312510039052/ds8pos.htm) · [024248/0343](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/24248/343) · [024248/0432](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/24248/432) |
| AdMob | 证书引述 2009-11-07 的协议，11-09 公告，2010-05-27 交割 | 样本 US11/702,893 随存续法人更名为 AdMob Google Inc.。更名于 2010-12-02 登记。该法人于 12-10 另签向 Google Inc. 的让与，12-16 登记。 [SEC 季报](https://www.sec.gov/Archives/edgar/data/1288776/000119312510172387/d10q.htm) · [025440/0161](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/25440/161) · [025512/0448](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/25512/448) |
| Teracent | 2009 年 11 月公告已签协议，12-11 更新确认已完成交易 | 2021-01-27 的登记封面列 US16/102,470，所附 2010-07-09 签署的确认让与书的清单列 US11/624,618 等早期申请。末页有较早登记戳叠印，独立的早期卷页待核。 [Google 公告和更新](https://googleblog.blogspot.com/2009/11/displaying-best-display-ad-with.html) · [055047/0905](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/55047/905) |
| ImageAmerica | Google 于 2007-07-20 公告已收购 | US08/738,713 的原件显示三位发明人在 1996 年签署给 Omni，2007-05-07 才登记。该记录与企业收购各有日期，历史优先顺位和 Google 后续取得该样本权利的证据仍需查。 [Google 公告](https://maps.googleblog.com/2007/07/imaging-america.html?amp=1) · [019254/0217](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/19254/217) |
| Marratech | Google 2007-04-19 明示收购软件，Marratech 企业本身未被收购 | EPO 原生 XML 显示 EP03733760.7 的申请公报记载 Marratech AB，2008-04-02 授权公报记载 Google Sweden Technique AB。瑞士公报另可见相关主体变更。 [Google 澄清](https://googleblog.blogspot.com/2007/04/collaborating-with-marratech.html) · [EPO A1 原件](https://data.epo.org/publication-server/rest/v1.2/patents/EP1527567NWA1/document.xml) · [EPO B1 原件](https://data.epo.org/publication-server/rest/v1.2/patents/EP1527567NWB1/document.xml) · [瑞士公报](https://www.ige.ch/fileadmin/user_upload/Services_Links/pmmbl/2007/P_2007_22_II.pdf) |
| reCAPTCHA | Google 与 Carnegie Mellon 于 2009-09-16 公布已收购衍生公司 | US9600648B2 的公报首页仍记载大学。可确认公司交易与大学名下的研发史料同时存在，具体许可和转让范围待查。 [大学公告](https://www.cs.cmu.edu/news/2009/google-inc-acquires-carnegie-mellon-spin-recaptcha-inc) · [美国授权公报首页](https://patentimages.storage.googleapis.com/f4/b7/86/3fa8ab520bd1c8/US9600648.pdf#page=1) |

另一个需要改记为拟议交易的条目是 **Begun**。Rambler 的 2008 年度结果显示，2008 年 10 月俄罗斯反垄断机关拒绝批准交易，协议随后取消。 [Rambler 年度结果](https://adindex.ru/files/17364/090421_Rambler_FY08_results_final.pdf) · [26 案台账](../pilots/google-longitudinal/derived/google-2007-2009-acquisition-roster.csv)

## 三、母集的缺口可以由原件直接反证

至少四份进得了交易或权属证据链、申请日也落在 2007—2009 年的公开文献，逐号对照后都没有进入 4,152 份两名称公报并集。它们分别属于 Postini、Jaiku、AdMob 和 Teracent。AdMob 与 On2 的交割落在 2010 年，但其此前的研发和申请可作为前史保留。反过来，已公告收购的目标即使本次名字检索返回零，也无法排除专利由旧法人、发明人或大学登记。需要增设目标法人、原申请号、续案和登记资产清单的检索入口。 [四项逐号对照及原件哈希](../pilots/google-longitudinal/derived/google-2007-2009-patent-rights-2026-11-22.json)

## 四、对五体编纂的具体影响

**本纪**把 2007 签约、2008 交割和后续法人归并按实际发生时间记叙，On2、AdMob 移至 2010 年交割节点。**表**并列公司事件、历史专利申请、登记所载执行日和登记日，资料可知日期另据来源核验。**书**区分股权收购、软件资产收购、合并、更名及独立专利让与。**世家**把搜索广告之外的展示、游戏、移动与视频编码能力作为有证据的研究线索，产业化成效待产品史复查。**列传**保留发明人、受让主体和当事企业管理层的不同角色，贡献和实际实施须另证。

本轮验证了 2007—2009 两名称数据库范围和指定样本的登记文件。未具名交易、境外权属链、各交易全部专利及更早权利负担仍有空缺。USPTO 登记证明有关文件进入行政记录，其权利范围还受具体文书、法域和资产清单约束。下一段优先追踪 2010 年 On2 和 AdMob 交割后的申请群，并将早期申请人、签署、登记与产品时间继续对账。 [USPTO Assignment Center](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) · [研究路线](../docs/ROADMAP.md)
