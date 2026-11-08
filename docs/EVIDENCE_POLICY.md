# 史料、命题与 Claim Lifecycle（v0.3）

## 原则：证据作用相对于命题

不宜把某份文献永久标为Primary/Secondary就视作其所有叙述均是真实一手。文件可能是“某天申请了某项专利”的一手证据，却是“企业自主开发并推出产品”的间接甚至不足证据；《史记》是研究司马迁写法的直接文本，却是记述秦楚事件的后出史书。

**每一项claim_id均需明确其source_id的evidence_role_for_claim**：direct_attestation / reported_testimony / contextual / interpretation / contradicts / unknown。

参见 [史记原典与现代专利证据的对应规范](SHIJI_SOURCE_CRITICISM.md)。

## 来源层次（无论古典或专利史）

- documentary_object：原始文本及具体版本，确实发生何种披露。
- embedded_statement：当事人自述、公司披露或原文记述（不自动等于真实动机）。
- narrator_interpretation：作者/编者对原因、意义和人物的判断。
- later_commentary：后代注释、现代论文与校勘。
- modern_inference：本项目通过数据与跨源证据形成的推断。

每一引用明确谁在何时何地说、何种版本和目的；网络版《史记》的“索隐述赞”不得当成司马迁本人论赞。专利不同阶段申请/公开/授权文本不得当成同一不变文本。

## 历史命题状态

- **HYPOTHESIS**：待验证，不能写为事实。
- **OBSERVED**：来源支持“某文档记载/某项记录存在”；注意文档记载与事件真实性不同。
- **INFERRED**：按有审计轨迹的方法从观察推出。
- **INTERPRETED**：在多组史料基础上产生的可争辩历史解释。
- **CONTESTED**：重大反证、原文异文或不同解释仍存在。
- **REJECTED**：经复核不成立，保留审计轨迹。

## 《详见》 Claim Lifecycle

affected_claim、impact_type（support/extend/revise/contradict/new/pending）、verification_next继续有效。历史研究额外记录 knowledge_as_of_date，防止事后时间倒灌；原始历法、范围差异与来源立场不许被统一数据库静默覆盖。

## 发布门槛

1. 重大事实有定位到版本/段落的source_id及相对于命题的证据角色。
2. 用“已经研发成功”“决定公司命运”“首次”等必须有独立佐证，且能说明覆盖范围、反证和时间先后。
3. 明确历史权属、技术发明、实际实施、产品利润的不同事实类型。
4. 重要时间变换记录原文、换算方法、观察窗口和争议。
5. 人物贡献、动机与关系不由专利署名、群传或广告宣传自动推出。
6. 公开权利检查、版权、隐私、安全与数据库授权通过。

## 模板

[证据卡](../templates/SOURCE_CARD.md)、[历史命题卡](../templates/CLAIM_CARD.md)，JSON见 schemas 目录。
