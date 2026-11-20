# Patent Evidence Workbench v0.4｜专利正文结构化与多文献版本对读

2026-11-20。《企业史记》研究成果与可复用专利数据工具的并行迭代。

## 1. 本轮真正解决的能力

上一轮IPHouse全文索引中缺少部分claims和description。现在通过**三件不同企业技术主题的公开专利申请及对应授权版本（共六份文献）**，建立了一个针对Google Patents公开HTML页面的保守结构化适配器。

真实数据：
- Huawei CN101166059A（10项权利要求）/B（7项）；分别有111个编号说明书段落。
- Tencent CN1482771A（4项）/CN1315292C（4项）；分别有46和47段。
- Google Maps US20050270311A1（74项）/US7158878B2（74项）；分别有136和137段。

累计173项编号权利要求、588段结构化说明书；每一项均保留来源页面URL、HTML元素锚点、编号、UTF-8标准化文本SHA-256、字符长度及来源类型。源HTML与全文只在私有研究区保存；GitHub公开派生索引与少量证据示例，不复制整批专利正文。

研究输出：[真实六文献结构和版本差异](../data/examples/six-patent-publication-version-structures-2026-11-20.json)；[历史研究报告](../research/18-six-publications-structure-and-version-history.md)。

## 2. 目前可运行的模块

- **patent_evidence/structured_docs.py**：支持直接解析**单份**Google Patents网页HTML，按itemprop等结构定位书目信息、摘要、权利要求、说明书编号段落和页面可观察的向后引证。
- **patent_evidence/version_diff.py**：对不同公开文献版本进行**编号位置**、文本哈希、引用边以及段落计数比较。
- **patent_evidence/cli.py**：增加parse-html和compare-html；旧audit、family-check、history-check、text-check命令继续可用。
- **requirements-document-parser.txt**：仅HTML适配器需要beautifulsoup4；旧版其他处理工具继续以标准库运作。
- **tests/test_patent_structured_docs.py**：合成原始测试HTML，检验文献身份、逐项引用、页锚点、哈希、授权版元数据、缺失与误配、私有全文显式开关、版本差异。真实外部网页HTML不上传公开库。

示例（从仓库根目录）：

    python3 -m pip install -r requirements-document-parser.txt
    python3 -m unittest discover -s tests -p 'test_patent_*.py' -v

    python3 -m patent_evidence.cli parse-html \
      --input /private/CN101166059A_zh.html \
      --source-url https://patents.google.com/patent/CN101166059A/zh \
      --expected-publication CN101166059A \
      --output /private/CN101166059A_derived.json

    python3 -m patent_evidence.cli compare-html \
      --first-input /private/CN101166059A_zh.html \
      --second-input /private/CN101166059B_zh.html \
      --first-url https://patents.google.com/patent/CN101166059A/zh \
      --second-url https://patents.google.com/patent/CN101166059B/zh \
      --first-publication CN101166059A \
      --second-publication CN101166059B \
      --relationship-source 'Google Patents Other versions links' \
      --output /private/CN101166059_ab_textual_delta.json

    python3 scripts/validate_document_versions_2026_11_20.py

默认**不输出任何完整专利权利要求或说明书文本**，只有结构/锚点/文本哈希。只有在明确添加--private-text后，才会输出原文片段；此时工具拒绝把结果写在公开仓库的目录下。使用者仍需自行确认资料获取和再发布权利。

## 3. 证据数据契约

每条最小证据包含publication_number、kind_code_as_provider_meta、application_number_as_provider_meta、evidence_id、source_locator、sha256_utf8_normalized_text、normalized_text_char_count、source_html_sha256、adapter_version和原始来源状态。

Claim额外包含：
- claim_number及展示编号；
- 由页面claim-ref给出的被引用权利要求编号与DOM锚点；
- independent_candidate_no_explicit_references 或 dependent_candidate_explicit_links 等**候选**分类；
- 页面索引项数与实际解析项数一致性、缺编号或引用不完整的告警。

以上不是法院或官方确认的独立权利要求分类：有些权利要求通过范围/组合进行引用，HTML链接可只呈现部分依赖意义；保留dependent_claim_reference_exhaustiveness_verified=false。

## 4. 版本差异不是法律范围结论

华为公开版10→授权版7；腾讯4→4；Google Maps 74→74。位置对齐后文本SHA差异分别6/4/74。这里的比较仅按**相同编号位置**计算：同编号可能是完全不同的改写、合并和重编号；哈希变化也可能来自网页转换/标点/排版差异。**不可据此称‘华为保护范围缩小三项’或‘Google 74项均经过实质修改’。**

下一步需合法取得各自官方原始A/B/C版本及审查文件、人工逐权项语义对照，再决定实质修改、收窄或法定范围。

## 5. 绝不能冒充国际标准合规

当前v0.4是**Google Patents HTML展示层的适配器**，而不是ST.96/XML、ST.97/JSON、USPTO Red Book、EPO ST.36或CNIPA官方数据适配器。对照这些成熟标准的**字段边界**，优先复用而非重造法律定义：

- WIPO ST.9著录和ST.16文种，ST.27法律状态，ST.96 XML和ST.97 JSON：
  https://www.wipo.int/en/web/standards/part_03_standards
  https://www.wipo.int/standards/en/st97/v2-0/annex-ii/index.html
- USPTO XML原始公报DTD及不同历史版本：
  https://www.uspto.gov/learning-and-resources/xml-resources
- EPO EP full-text bulk data为ST.36 XML，并有单篇官方欧洲文献下载服务：
  https://www.epo.org/en/searching-for-patents/data/bulk-data-sets/data
  https://www.epo.org/en/searching-for-patents/technical/publication-server

EPO正式出版物及其数据的自动提取另有许可条件与使用规范：
https://www.epo.org/en/service-support/ordering/fair-use

## 6. 未来与五体、AI原生系统怎样接合

本轮优先产出可复核的**证据原子**，不让语言模型在缺失来源时补造正文。AI以后可以基于evidence_id和source_locator展开文本/权利要求，形成技术问题、方案和背景对照，并将历史判断关联到affected_claim、impact_type和verification_next。

- 本纪：基于技术方案演化与独立外部证据提出历史转折。
- 表：申请、公开、授权、修改、跨版本关系严格分时。
- 书：专利权利要求形成、制度选择、技术公开和权属变动。
- 世家：技术方案的继承与分叉，以引证/家族/特征共现形成待证网络。
- 列传：署名只证明被列为发明人，实际研发分工要另外取证。

下一轮工具v0.5优先：使用USPTO Red Book和EPO ST.36的合法**机器可读官方原始样本**实现第二适配器；对多版本权利要求做语义与人工双重审查，不用HASH差异替代法律判断。
