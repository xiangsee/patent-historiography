# 第十六号研究笔记｜Google Maps的技术来源、优先权与权益登记时间

日期：2026-11-19。定位：《企业史记》史学研究与专利证据工作台v0.2共同验证项目。**不是正式本纪。**

## 最初的历史问题
Google在2004年收购Where 2 Technologies的团队及地图技术，2005年2月8日推出Google Maps。前者的技术和研发组织与后者产品形成的关系有学术研究支持；但企业收购、具体专利申请、发明人权益登记、产品实际实施并不是同一法律或工程事实。

学术来源：https://doi.org/10.1093/icc/dtad015
Google当年产品公告：https://googleblog.blogspot.com/2005/02/mapping-your-way.html
英国2016年地图市场司法判决也论及2005年Google Maps的交互地图功能：https://www.bailii.org/ew/cases/EWHC/Ch/2016/253.html

## 四件专利产生两组相反的家族研究问题

| 公报 | 技术主题 | 主张最早优先权日 | IPHouse family_id |
|---|---|---|---|
| US20050270311A1 | 数字地图系统 | 2004-03-23 | 35064376 |
| US7599790B2 | 地图瓦片生成和展示 | 2004-03-23 | 46304193 |
| US20050182770A1 | 网页地理标识 | 2003-11-25 | 36693532 |
| US7730389B2 | 数字地图系统自动集成 | 2003-11-25 | 34623223 |

第一组：前两件专利数据中共同出现两项临时申请标识US-55550104-P和US-56794604-P，但是provider family_id不同。这是一个需要继续核实的申请族/技术关联，不能因为两个family_id不同就断言彼此无关。

第二组：后两件专利同为2003-11-25优先权日，但是分别指向US-52540003-P和US-52542003-P两个不同申请号。**日期相同不等于优先权基础相同。** 无直接共享号不证明绝对没有间接技术联系。

具体标识来自实际IPHouse get_patent_family查询和公开专利书目，尚未取得EPO官方DOCDB/INPADOC ID与完整优先权案卷。EPO分别说明简单和扩展同族的优先权规则：
https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/docdb
https://www.epo.org/en/searching-for-patents/helpful-resources/first-time-here/patent-families/inpadoc

## 公开可知时间与事后重建时间必须分开

- 2004-03-23：US20050270311A1主张优先权。
- 2005-02-05：美国申请日。聚合数据的原始申请人栏目显示Individual；需要核对原始卷宗。
- 2005-02-08：Google Maps正式发布。当时这件专利尚未公开，本研究也没有找到截至该日的发明人权益转让登记；**不能据此断言Google拥有或不拥有该具体权利**。
- 2005-08-12：聚合专利法律事件记载发明人权益转让Google Inc.；没有核到其合同确切生效日。
- 2005-12-08：专利公开。不能在写2005年2月历史时，让当时的公众预知12月说明书。
- 2017-12-05：Google Inc.到Google LLC的名称变更登记；不能记为获得新的研发发明。

另一件网页地理标识专利US20050182770A1有更适合工具核验的双日期：法律事件载2005-04-26权益转让生效、2005-04-27才登记，Reel/Frame为016498/0162；2017-09-29的名称变更于2017-10-06登记，044142/0357。必须分开记录生效日与登记日。公开资料仅来自Google Patents聚合，原始USPTO转让文件仍待获取。

主要专利来源：
https://patents.google.com/patent/US20050270311A1/en
https://patents.google.com/patent/US20050182770A1/en
https://patents.google.com/patent/US7599790B2/en
https://patents.google.com/patent/US7730389B2/en

USPTO声明权属登记是一项行政性记录，不对登记文件和交易效力作出实质性确认：
https://assignmentcenter.uspto.gov/search/advanced

## 本轮方法与工具产出
增加Patent Evidence Workbench v0.2的两个核心模块：
1. 对指定公报涉及的优先权/母子案标识进行标准化后比对，识别共享、相同、只有日期相同、来源不足，不越权称为官方EPO家族。
2. 对同一专利的assignment、name_change、license建立历史时点as_of及资料可知截止knowledge_as_of两个坐标；输出的是最后观察到的权益登记指向，不是司法确认的完整所有权。

真实fixture及实际运行派生JSON：
data/examples/maps-priority-rights-v0-2.json
data/examples/maps-lineage-v0-2-derived.json

实际运行：
- US20050270311A1，历史时点2005-02-08：没有本研究已取得的Google权益登记证据，不能推断正反结论。
- 同案历史时点2005-12-31：已知8月12日向Google Inc.登记的权益事件，但未复核正式转让合同。
- US20050182770A1，历史时点2005-04-26，允许研究者知道2005-04-27资料：后出登记显示此前一天生效。这是双时间技术上可观察的差异。

## 五体与反证
本纪：Google Maps能力形成是收购、团队与研发和产品整合的候选转折。表：区分优先权、申请、产品、转让登记、专利公开五条时钟。书：公司收购不自动代表全部相关专利权益转移。世家：共享优先权标识指向可追踪的技术谱系候选，且同日的不同申请不能机械合并。列传：Rasmussen兄弟、Bret Taylor等人物有专利著录和同期发表资料，具体工程分工仍需独立原始证据。

反证缺口：没有原始美国转让合同和EPO官方家族映射，没有证明该专利由Where2公司原始持有，也没有证明任何权利要求在2005年Google Maps实际部署；2004年收购的准确月份不同来源记载有差异，不能自动消歧。

**本轮结论**：一个真实企业史问题反向推动了可复用的数据工具；这比先写一个成功故事再补专利号更符合《企业史记》的方法目标。
