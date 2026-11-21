# Patent Evidence Workbench v0.5｜官方XML适配与历史版本证据

**研究记录日期：2026-11-21；样本取得与首次验证：2026-11-20。** 这是《企业史记》双轨成果之一：既依据专利重建企业技术及权利历史，也把真实研究中用到的专利数据处理工艺固化为可复用代码。当前版本是受限样本验证的研究原型，不是通用专利局生产数据服务。

## 一、原始数据已经实际取得，而非仅仅研究标准

- EPO欧洲专利出版服务器的真实原文：EP1004359B1、EP0729353A1、EP0729353B1、EP0729353B2；来源均为data.epo.org的Publication Server REST v1.2。
- WIPO ST.96 Annex VII的官方XML测试样本：v6-0目录下和v10-0目录下的PatentPublication_Example.xml。两份的documentStatusText为TEST，不能作为真实历史发明。
- USPTO官方2022-02-17的us-patent-grant-v47 DTD已经取得（62,376字节），但本轮**没有下载、解析任何真实USPTO Red Book授权公报XML**。取得DTD≠美国专利原始文献已解析。

上述官方原始文件仅保存于研究私有目录。仓库公开：
[4份官方XML来源派生审计](../data/examples/official-xml-four-source-derived-2026-11-20.json)；
[EP0729353三次公报及B1/B2变化派生审计](../data/examples/alkermes-ep0729353-1996-2012-derived.json)。
公开内容仅含文献标识、原文哈希、日期、结构数量、少量XML锚点和证据状态，不复制原始全文。

来源：
- EPO真实出版原文：https://data.epo.org/publication-server/rest/v1.2/patents/EP1004359NWB1/document.xml
- EPO历史样本A1：https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWA1/document.xml
- EPO历史样本B1：https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB1/document.xml
- EPO历史样本B2：https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB2/document.xml
- WIPO官方示例：https://www.wipo.int/standards/en/st96/v10-0/annex-vii/PatentPublication_Example.xml
- USPTO DTD：https://data.uspto.gov/documents/documents/xml-resources/us-patent-grant-v47-2022-02-17.dtd

## 二、两个已运行的适配器

**patent_evidence/official_xml.py**（Python标准库，无外部网络访问）：

1. EPO EP文献：从根节点的country、doc-number、kind取公报身份，不能直接把root.id认作文献公开号；保存真正声明的DTD版本、公告日、语言、claim编号、说明书段落、引证节点、B711申请人及B731权利人公开标签。输出每项证据的source URI、XML id或结构位置、UTF-8规范化文本SHA-256，不传出完整文本。
2. 对EPO英文、德文、法文权项分组，不能把三组翻译计为三倍的法律权利要求。EP1004359B1的en/de/fr各7项，XML共21个节点；EP0729353B2的en/de/fr各4项，XML共12个节点。
3. A1样本：EP0729353A1的此次官方XML文件不含权利要求和说明书内容。默认报错；只有显式允许“文献结构只有书目资料”时才输出claims_present_in_this_XML=false。**绝不**将其解释为1996年专利申请实际不存在权利要求。
4. WIPO ST.96样例：按真实命名空间解析ClaimNumber、ClaimTypeCategory、ClaimReference、说明书P段落、书目引用、documentStatusText以及根节点实际com:st96Version。两份TEST示例均含10个权项，3 Independent和7 Dependent、70个P段落；不能当成真实专利统计。
5. v10-0路径下的样例**实际自述V8_0**，因此软件使用XML根节点自身声明版本，不以下载目录名决定schema。
6. 只做安全受控XML解析：拒绝自定义ENTITY，限制单次输入10MB，不主动获取外部DTD或实体，不执行代码；尚未做DTD/XSD严格校验。

**patent_evidence/official_version_diff.py**：只比较同一EP号不同公报kind的文本结构，输出日期、声明DTD、第一语言权项数、相同编号位置哈希变化、翻译节点数、说明书数量和B711/B731名称差异；不做法律保护范围或真实转让的因果推断。

## 三、可执行调用

从仓库根目录执行（下列/private路径是示意，需要合法取得的本地原始XML）：

    python3 -m unittest discover -s tests -p 'test_patent_*.py' -v

    python3 -m patent_evidence.cli official-xml --format epo \
      --input /private/EP0729353NWB1.xml \
      --source-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB1/document.xml \
      --expected-publication EP0729353B1 \
      --output /private/ep-b1-derived.json

    python3 -m patent_evidence.cli official-xml --format epo \
      --input /private/EP0729353NWA1.xml \
      --source-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWA1/document.xml \
      --expected-publication EP0729353A1 --allow-no-claims \
      --output /private/ep-a1-bibliography-only.json

    python3 -m patent_evidence.cli compare-epo \
      --first-input /private/EP0729353NWB1.xml \
      --second-input /private/EP0729353NWB2.xml \
      --first-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB1/document.xml \
      --second-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB2/document.xml \
      --first-publication EP0729353B1 \
      --second-publication EP0729353B2 \
      --output /private/ep-b1-b2-diff.json

    python3 scripts/validate_official_xml_2026_11_20.py

## 四、历史样本形成的具体判断

EP0729353的官方XML：1996-09-04 A1、2002-02-06 B1、2012-09-12 B2；B1有6项英文权利要求和18个三语节点，B2有4项英文权利要求和12个三语节点。B1声明DTD v1-1，B2为v1-4。EPO B2文种表示异议程序后修改的专利说明书。根据相同编号位置的文本SHA，4个可比较位置均有变化，但**不能据此判定专利保护范围缩小三分之一，也不能推断异议裁决的具体法律理由**。

B711/B731文献字段记载：A1申请人Alkermes Controlled Therapeutics, Inc.；B1权利人同名；B2权利人Alkermes, Inc.。仅凭公开文献名称差异不能证明并购或转让，必须取得登记事件、法律有效日期与企业档案。

WIPO示例只用于检验工具结构：不能用于企业历史事实。USPTO DTD只能说明已取得格式定义，不能宣称已完成真实美国专利XML处理。

## 五、方法成熟度与未来任务

**已实际验证**：EPO公开B1/B2的v1.4、B1的v1.1，以及一个不含全文结构的A1；WIPO ST.96 Annex VII的V6_0、V8_0 TEST样本；共44项研究工具合成测试（截至本次恢复前的工具提交）。若最终自动回归统计变化，按CI记录更新。

**仍然待证**：EP0729353的原始异议决定和具体修改理由、官方登记/Alkermes集团法人关系、专利权利要求的法律范围、USPTO真实Red Book XML解析、完整ST.96 XSD校验和其他年代EPO DTD覆盖。

**下一阶段**优先从EP0729353的异议决定书及专利原始权项中核对实际修改；在合规许可下取得真实USPTO Red Book XML，增加第二个真实专利局的原生XML适配；然后将结构化证据反向用于跨企业长时间专利母集和《企业史记》五体互见，不陷入单件专利法证的无限深化。
