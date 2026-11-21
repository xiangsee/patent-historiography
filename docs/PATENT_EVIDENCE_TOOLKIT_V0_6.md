# Patent Evidence Workbench v0.6｜专利程序、时态与跨企业当事人证据图

2026-11-21。输入为研究者已核实或带明确来源等级的合法结构化记录，不联网；输出为研究假说服务的程序时间线与元数据。不是自动专利法律状态判断或法律意见。

## 完成的工具能力

核心模块：patent_evidence/procedural_ledger.py。

1. verify_events：检查event_id、case_id、event_kind、ISO事件日期、来源等级、来源URL、role实体类型和来源可知日期。不得把revocation_communication标记为最终不可撤销的法律失效；单份opposition withdrawal不能代表所有异议已撤回。
2. procedural_view：显式区分历史事件发生日as_of、研究资料知识截止knowledge_as_of；当前可以事后检索到的法律事件，不自动取得“历史当时已公开”的证据等级。返回包括retrospectively_observed和contemporaneously_dated_evidence两个列表。
3. compare_roles_across_cases：可搜索跨案主体角色及相反方向的异议关系，但名称substring仅构成候选，法律实体/集团隶属及商业竞争未核。
4. review_claim_lifecycle：对齐《详见》的affected_claim / impact_type / verification_next / evidence ID，拒绝不存在的来源和重复Claim ID；不自动将判断提升为已证事实。
5. source_quality_ledger_complete永远不由“读到了当前输入的所有事件”得出TRUE；官方案卷的完整性必须单独审计。
6. Python标准库，无需网络或第三方依赖，不发送或写入凭据。

## 真实数据验证

取三组不同EPO案件：
- EP0729353，A1/B1/B2真实EPO官方XML，加公开第三方索引中的异议、撤销通知、上诉、修改维持等7项事件；
- T0003/98，EPO官网公布的上诉委员会决定摘要；
- T0507/98，另一件不同专利的EPO官网上诉决定摘要。

共12条事件，4个Claim Lifecycle。对2005-07-20：有5条今天能事后发现的EP0729353历史事件，其中两条是已核实当年公开日期的A1/B1；撤销通知的当时可知时间仍未证明。两个另一案件具有有确定日期的2002年上诉决定/网页上线日期；研究者不能在正式上线前就把决定网页当成可获得的公开文献。

来源和输出：
- data/examples/epo-cross-case-procedural-events-2026-11-21.json
- data/examples/epo-procedure-evidence-audit-v0-6.json
- scripts/validate_ep_procedural_ledger_v06.py
- tests/test_patent_procedural_ledger.py
- research/20-alkermes-sri-opposition-network.md

## 可运行命令

从公开仓库根目录：

    python3 -m unittest discover -s tests -p 'test_patent_*.py' -v
    python3 scripts/validate_ep_procedural_ledger_v06.py

    python3 -m patent_evidence.cli procedure-check \
      --input data/examples/epo-cross-case-procedural-events-2026-11-21.json \
      --case-id EP0729353 --as-of 2005-07-20 \
      --output /tmp/EP0729353-2005-procedure.json

    python3 -m patent_evidence.cli procedure-check \
      --input data/examples/epo-cross-case-procedural-events-2026-11-21.json \
      --as-of 2012-09-12 \
      --party-a Alkermes --party-b "Southern Research" \
      --output /tmp/ep-cross-case-party-network.json

输出只包含可公开的事件元数据与来源URL，不包含EPO完整案卷或受版权限制的批量XML。实验的EPO个案原始全文仍按此前政策保存在非公开研究区。

## 研究史与法律解释的严格边界

- “2005年撤销通知”不是“已最终撤销”；“2012年B2公布”不说明2005年所有司法救济细节。
- 一方在别案是异议人、在另一案其关联主体可能是申请人/权利人，是跨案网络线索，不等于商业战略和主观动机。
- 法律实体名称的相似与企业集团关系必须由原始公司材料和有日期的变更记录确认。
- 第三方法律事件索引没有历史公开日期时，不能自动用事件发生日期充作公开可知日期。
- EPO官方决定网页可核实案件编号、当事人角色和裁判命令；并不意味着已逐页审阅完整上诉案卷、异议全部附件。
- USPTO现行开放数据API要求适当账户/API key；不能把未授权访问障碍写成官方专利数据缺失。
- 此工具可帮助五体编纂、历史时间线和Claim Lifecycle，却不能自动输出完整企业史或证成其产业因果。

## 下一轮v0.7的优先级

1. 把程序事件的来源等级、历史时态和当事人关系图用于**真实企业跨年专利母集**（Google/华为/腾讯），输出事件覆盖率及标注缺失，不在单件EPO专利上继续无限扩深。
2. 对企业实体进行有时间的原始申请人与现权利人关联核查，不把Alkermes等相似法人或Google Inc/LLC名字自动合并。
3. 在合法授权情况下取得实际USPTO Red Book单件真实XML，将官方v4.7 DTD与样本一致性进行测试；如账户/API限制尚在，继续保持PENDING，不声称已经解决。
4. 历史研究同步推进《史记》原典与中外专利企业史理论合成，为第一部五体整书大纲设立实证门槛。
