# 《企业史记》第26轮｜Google 2013：Motorola Home 的交割、专利归属与许可

**2026-11-22 · Google 长时段专利研究 · 方法试验稿**

Motorola Home 于 **2013-04-17** 实际交割。ARRIS 向 SEC 披露，签约时 Home 有 **3,164 项专利或待审申请**，其中 **991 项随交易取得，2,173 项由 Google 经 Motorola Mobility 保留并向 Home 许可**。本轮从公开美国登记中逐号核到 **18 个进入随股出售公司的双段权属链**，以及 **1,036 个留在 Google 一侧的双段权属链**。2013 年 Google 两名称母集取齐 **161 页、7,873 份去重公报**。 [ARRIS 交割 8-K](https://www.sec.gov/Archives/edgar/data/1141107/000119312513160131/d522646d8k.htm) · [ARRIS 向 SEC 的组合与许可说明](https://www.sec.gov/Archives/edgar/data/1141107/000119312513456280/filename1.htm) · [逐申请号权属清单](../pilots/google-longitudinal/derived/google-2013-arris-home-title-evidence.csv)

## 一、2013 年母集沿用两名称与申请日口径

IPHouse Research `search_patents` 按 `assignee` 匹配 Google Inc. 与 Google LLC，限制数据库所载申请日在 2013 年，不限公报局，每页 50 条。Inc. 取齐 **142 页、7,088 份**，LLC 取齐 **19 页、913 份**，两名称共同命中 **128 份**。去重并集含 **5,641 个申请号、4,306 个数据库族标识**。4,680 份的优先权年早于 2013 年。与前段合并，有 1,307 个族标识跨段重合。1996—2013 年累计 **617 页、29,208 份公报、21,485 个申请号和 11,565 个数据库族标识**。 [第25轮口径](25-google-2012-motorola-assets-and-published-parties.md) · [2013 年审计](../pilots/google-longitudinal/derived/google-2013-name-coverage-2026-11-22.json) · [跨年合并](../pilots/google-longitudinal/derived/google-1996-2013-combined-audit-2026-11-22.json)

| 截至日期 | 2013 窗口中申请日已到 | 其中公报已出版 | 1996—2013 合并窗口中公报已出版 |
| --- | ---: | ---: | ---: |
| 2013-04-17，实际交割 | 2,392 | 10 | 10,283 |
| 2013-05-28，保留侧大批让与所载执行日 | 3,070 | 25 | 10,848 |
| 2013-07-09，两份 995 项卷页登记 | 4,065 | 47 | 11,309 |
| 2013-12-31 | 7,873 | 724 | 13,581 |

快照按本次索引的申请日和出版日重放。它反映当前命中公报在相应时间的出版情况，历史权属按交易文件、当期公报和登记另核。 [可复跑的覆盖审计](../scripts/validate_google_2013_arris_home.py)

## 二、交割取得的产权与双方向许可

2012-12-19 签署收购协议。2013-04-17，卖方 **General Instrument Holdings, Inc.**（GIH）把持有的 **General Instrument Corporation**（GIC）全部流通股份交给 ARRIS。交割 8-K 披露约 22.4 亿美元现金及 1,060 万股 ARRIS 普通股。GIC 是承载 Home 的运营公司。其在交割时已持有的产权随公司控制权进入 ARRIS，另行内部划转则看每份专利文书。被出售的 GIC 与卖方 GIH 是两个法人。 [收购协议](https://www.sec.gov/Archives/edgar/data/1141107/000119312512510580/d457255dex21.htm) · [交割 8-K](https://www.sec.gov/Archives/edgar/data/1141107/000119312513160131/d522646d8k.htm)

| ARRIS 对 SEC 披露的范围 | 产权及许可安排 |
| --- | --- |
| **991 项** Home 专利或待审申请 | ARRIS 随 Home 取得产权。Home 同时向 Motorola Mobility 和 Google 提供非排他、全球、不可撤销的许可回授，许可延续至适用专利保护届满。 |
| **2,173 项** Home 保留资产 | Google 经 Motorola Mobility 保有产权。Home 在约定业务范围内获非排他、全球、不可撤销、延续至适用专利保护届满的使用许可，覆盖符合条款的现有和未来 Home 产品。 |
| **约 17,000 项**其他 Motorola Mobility 资产 | 权利继续由 Mobility 一侧持有或依法许可。Home 的使用许可限于当时已有的产品、服务及业务范围内的延伸。 |

ARRIS 确认另有交割后申请、优先权日期早于 **2014-04-17** 的范围约定，各类资产仍受相关产品和权利要求条件约束。收购协议第 4.18(b) 条把已登记的 GIC 知识产权指向卖方披露表。其 **Section F** 所附许可协议格式在第 1.1(l) 条把具体保留许可权利要求指向 **Schedule 1.1(l)**，第 2.1、3.1 条分别给出向 Home 和向 Mobility／Google 回授的安排。公开文本和 SEC 回复足以核实总量、方向和业务范围，本轮未取得两份完整逐项附表。 [许可协议格式及第 4.18(b) 条](https://www.sec.gov/Archives/edgar/data/1141107/000119312512510580/d457255dex21.htm) · [ARRIS 的逐类许可说明](https://www.sec.gov/Archives/edgar/data/1141107/000119312513456280/filename1.htm) · [ARRIS 年报确认 991 项为 outright acquisition](https://www.sec.gov/Archives/edgar/data/1141107/000119312514079303/d630179d10k.htm)

## 三、公开卷页逐号核对到的两侧资产

本轮按转让双方组合检索 USPTO Assignment Center，对 **105 个卷页**核清资产页，其中 2 份担保登记作旁证。103 个产权卷页给出 **2,988 条资产行**。另按申请号核对交易时点与继受证据，形成 **1,657 个不同美国申请号**的权属表。以下件数以美国申请号计，SEC 披露则按跨法域的专利和申请资产口径。 [逐卷资产表](../pilots/google-longitudinal/derived/google-2013-arris-home-us-asset-register.csv) · [逐号权属表](../pilots/google-longitudinal/derived/google-2013-arris-home-title-evidence.csv)

**进入随股出售的 Home 公司。** 在 2013-04-16、04-17 所载执行日下，Motorola Mobility LLC → GIH、GIH → GIC 两段各有 6 个卷页，每段 20 条资产行，去重后是同一批 **18 个不同美国申请号**。原件均按所附 Schedule A 描述权利及相关申请，第二份文书明确列 Delaware 的 General Instrument Corporation 为受让方。例如 **US13/277,254** 经 **030420/0602、030420/0659** 进入 GIC。2013 年 3 月申请的 **US29/448,217／USD732558** 在 **035595/0346、035589/0479** 所载两段执行日均为交割日，2015 年才登记。 [两段原件 030420/0602](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/30420/602#page=3) · [030420/0659](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/30420/659#page=3) · [18 个申请号及卷页](../pilots/google-longitudinal/derived/google-2013-arris-home-title-evidence.csv)

**经 GIC 延续至 ARRIS。** 另从 GIC → ARRIS 相关继受卷页查得 615 个美国申请号，其中 542 个的申请日已在交割日或此前。逐申请号反查，**479 个**有交割日前后可衔接的 GIC 收受和 ARRIS 继受证据，其中 458 个的 GIC 收受已在交割日或此前入卷。这 479 个与上段 18 个重合 16 个。**US11/613,295／US8433368B2** 在 GIC 名下可追至 2006 年，2013-04-17 列入 ARRIS 一侧的共同担保卷，2015 年又列入 GIC 继受及改名为 ARRIS Technology, Inc. 的卷页。共同担保的其他申请也有不同保证人，在表中保留为担保旁证。 [2006 年让与](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/18658/709) · [2013 年担保](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/30498/23) · [2015 年继受及 Delaware 证明，第 18 页](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/35176/620#page=18)

**留在 Google 一侧。** 两个最大卷页 **030764/0575、030866/0113** 各列 **995 项**，所附让与书援引 2012-12-19 的收购协议。前一段由 GIC 于 2013-04-15 划给 GIH，后一段由 GIH 于 05-28 划给 Motorola Mobility LLC，两卷均于 **07-09** 登记。将同日的补登记全部合并，两段分别覆盖 **1,035、1,038** 个美国申请号，交集 **1,033** 个。再逐申请号调查 7 个分歧项，补回两份同日第一段记录及一份封面执行日为 **05-18** 的第二段记录，最终 **1,036 个**两段均有权属证据，**4 个**仍有单段缺口。**US11/562,214** 和 **US13/087,847** 位于两个 995 项卷页内。 [第一段原件](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/30764/575#page=28) · [第二段原件](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/30866/113#page=28) · [复查补回的 05-18 卷页](https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/34582/99) · [保留侧逐号列表](../pilots/google-longitudinal/derived/google-2013-arris-home-title-evidence.csv)

权属表中另有 **136 个**仅见后续 ARRIS 继受记录，未达到本轮交割时点的证据阈值。欧洲对照 **EP2089803** 的 2009 年 A2 列 Motorola, Inc.，2018 年 B1 列 ARRIS Enterprises LLC。该案证实具体版次的名称变化，欧洲权属事件与 2013 年交易附表的联系仍待确认。 [欧洲 A2](https://data.epo.org/publication-server/rest/v1.2/patents/EP2089803NWA2/document.xml) · [欧洲 B1](https://data.epo.org/publication-server/rest/v1.2/patents/EP2089803NWB1/document.xml)

在五体中，**本纪**记签约及实际交割，**表**分别列股权完成、专利文书执行与入卷，**书**记录 991 项产权、2,173 项保留许可及 Mobility 业务领域许可。**世家**和**列传**沿已知申请、原运营公司和发明人继续查产品及人员贡献。逐号许可的最后一层仍依赖签署版附表，现有登记链先解决专利资产留在哪一侧。 [证据索引及缺项](../pilots/google-longitudinal/derived/google-2013-arris-home-rights-2026-11-22.json)
