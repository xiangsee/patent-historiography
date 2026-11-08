# 史料、命题与 Claim Lifecycle

## 证据分层
- **Primary**：专利/转让登记原文、官方监管披露、法院/行政文书、当时产品文件和可追溯的一手档案。
- **Secondary**：同行评议论文、可靠商业史与学术著作、媒体深度调查。
- **Context**：采访、回忆录、公司公关材料和网络内容；用于寻找线索，须注意事后选择性叙述。
主张动机、团队内部决策和因果关系时，必须有足够独立证据，不以单件专利标题推定。

## 历史命题状态
- **HYPOTHESIS**：待验证命题，不能作为正文事实。
- **OBSERVED**：一手史料直接支持的可定位事实。
- **INFERRED**：按公开、可复核方法从数据推出。
- **INTERPRETED**：在多组史料基础上形成的可争辩历史解释。
- **CONTESTED**：存在重大反证或不同解释。
- **REJECTED**：经复核不成立，保留审计轨迹。

命题变化不覆盖旧记录，应写日期、影响类型、原因和复核人/方法。

## 对接《详见》 Claim Lifecycle
每条高价值外部信号至少记录：
- affected_claim：影响了哪个已有命题。
- impact_type：support / extend / revise / contradict / new / pending。
- verification_next：下一项实际可验证动作。
另外为历史研究增加 **knowledge_as_of_date**，使研究者不将事后结果伪装成当时人的知识。

## 发布门槛
1. 文中可核事实均有source_id或明确出处。
2. 每条重大结论至少有一项非专利的独立交叉证据；否则明确降级为假设。
3. 已检查最强替代解释、时间线冲突和归属变化。
4. 若使用“首次”“全部”“主要”“领先”必须注明覆盖范围与判断方法。
5. 第三方隐私、商业秘密、著作权及数据库授权必须过审。

## 模板
templates/CLAIM_CARD.md、templates/SOURCE_CARD.md。JSON格式见 schemas/historical-claim.schema.json。
