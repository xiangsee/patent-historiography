# 专利处理方法卡｜Patent Method Result Card

- method_id / semver：
- applicable_research_question：解决了哪类真实企业历史问题？
- source_provider / query_snapshot / license：原始数据从何而来、何时抓取、是否允许导出？
- input_schema / original_ids_preserved：原始公报、申请、族、主体、事件字段与外部来源定位。
- normalization_rules：何种变换？如何避免不同单位混同？
- algorithm_or_processing_steps：可运行命令/模块/参数/版本。
- quality_checks：分页、重复、时间口径、主体归属、族定义、缺失及反例。
- sample_or_fixture：合成测试与真实研究验证数据（公开只保留可许可统计）。
- output_artifacts：汇总JSON、审计日志、错误清单、review queue。
- observed_claims / updated_claims：这一方法改变了哪个历史判断？
- limitations_and_strongest_counterexample：目前在哪些情形会失效？
- next_verification：下一项最需要的独立来源或对照实验。
- reuse_conditions：从Google复用到华为/腾讯等需改哪些输入配置？
- publication_and_rights：哪些数据能发表，哪些只可内部留存？
- status：design / executable / validated_on_synthetic / validated_on_real_sample / independently_validated。

**不得**仅因为某个脚本能运行，就把历史命题状态设为CONFIRMED；需另有独立历史材料交叉证明。
