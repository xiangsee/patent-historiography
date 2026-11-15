# 第八轮：US7110993 计算机程序光盘的档案存续与访问审计
研究日期：2026-11-15；状态 **REFERENCE VERIFIED / ARTIFACT NOT OBTAINED**。承接 research/11 与 Issue #14；不是 GoTo 生产源代码研究完成报告。

## 1. 文献可以证明什么？
同一申请 09/915,801 的授权文献 US7110993B2 在“REFERENCE TO COMPUTER PROGRAM LISTINGS SUBMITTED ON COMPACT DISK”中记载附带一张光盘，包含 **22,808个文件、101,776,919字节**，并称目录文件 **dir_s** 包含文件名称、创建时间和大小。2003 A1与2005 A9亦记载这项声明。
- https://patents.google.com/patent/US7110993B2/en
- https://patents.google.com/patent/US20030208474A1/en
- https://patents.google.com/patent/US20050289120A9/en

这仅证明专利公开文本声称存在附件；尚未获得官方接收单、实物所在位置、目录或任何字节。不要把 22,808 件解释为22,808项GoTo自主研发的源代码文件。

## 2. 正确使用历史制度，不让现行规定覆盖2001年

申请日 **2001-07-26**。当时USPTO已经开始使用CD承载大型计算机程序清单。2001-02-20官方公告制定了**可选择的临时检测程序**：提交 Compact Disc Transmittal Letter、逐文件目录，抽查ASCII可读性，产生Acknowledgement of Receipt、文件列表及确认材料并放入申请档案。只有在本案实际采用该程序并取得相应文件后，才能推断存在这些记录；不能把“可选择程序”说成“本案必经且已经完成”。
- https://www.uspto.gov/news/og/2001/week08/patsubm.htm

MPEP §608.05(a)现行解释计算机程序清单可以是单独不印出的电子附件，公开材料可通过Patent Center或依37 CFR 1.19请求。
- https://www.uspto.gov/web/offices/pac/mpep/s608.html

MPEP §103说明2003-06-30前纸质申请的电子案卷覆盖存在时间差；本案2001年申请，电子案卷缺少某项不等于原来没有材料或今天一定已经遗失。
- https://www.uspto.gov/web/offices/pac/mpep/s103.html

## 3. 实际访问尝试（2026-11-15）

| 目标 | 通路与观测 | 结论边界 |
| --- | --- | --- |
| https://patentcenter.uspto.gov/applications/09915801 | 未登录macOS Python请求HTTP 403；网页文本工具无法获取动态页 | 没有读到Documents and Transactions，不等于附件不存在 |
| https://api.uspto.gov/api/v1/patent/applications/09915801/documents | 未附API key的HTTP请求403 | 没有得到案卷目录；ODP API官方要求密钥，不能据403归因于特定文件缺失 |
| https://data.uspto.gov/patent-file-wrapper/application/09915801 | HTTP 200但返回网页应用HTML壳而非案卷数据 | 不算成功取得公开案卷 |
| Google Patents授权说明书 | HTTP 200，附录声明可见 | 已核对公开文本，未取得附录 |

ODP官方认证政策见 https://data.uspto.gov/apis/patent-file-wrapper/documents 及 https://catalog.data.gov/dataset/open-data-portal-odp-api-version-2-3 。

## 4. 法定公开与研究者实际取得之间的差别

**D0 引用确认**：公开文本记载有CD、文件数及字节数——已完成。  
**D1 官方受理与保管证明**：USPTO的Transmittal Letter、Receipt或artifact sheet——未取得。  
**D2 媒体文件可访问**：实物或数字副本与其目录——未取得。  
**D3 完整性核验**：SHA-256、目录哈希、文件数/总字节/时间戳验证——未做。  
**D4 史学解释**：特定模块与专利、真实产品、开发者或组织关联——未做。  
**D5 可公开使用**：版权、隐私及安全审核——未做。

各状态应单独记录；低层成立不等于高层自动成立。我们将其称为 **史料存续与可访问性偏差（archival survival/access bias）**。

## 5. 可行的官方获取路线

先使用USPTO Patent Center按申请号 09/915,801 或专利号 7110993 查 Documents and Transactions，检索 Compact Disc、Program Listing、Artifact Sheet、Transmittal Letter、dir_s。没有材料时不要自行填“没有提交”。

官方 Patent and Trademark Copy Fulfillment Branch：dsd@uspto.gov，+1-571-272-3150，官网 https://www.uspto.gov/learning-and-resources/support-centers/patent-and-trademark-copy-fulfillment-branch 。Certified Copy Center https://certifiedcopycenter.uspto.gov/ 。官网允许在能取得的情况下免费下载电子非认证案卷文书，不能取得时可订副本：https://www.uspto.gov/patents/apply/checking-application-status/order-certified-copies 。

2026-11-01更新的官方收费表列出：申请原文件副本 **38美元**、电子整套案卷副本 **65美元**、单项文书副本 **27美元**。这些是产品**类别**费用，不能未经USPTO确认便宣称包括这张CD、能取到全部22,808文件，也不能擅自代用户支付。https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule

准备了询问模板：../templates/USPTO_CD_INQUIRY.md 。**没有发送任何邮件、注册账号或下单**。

## 6. 取得媒体后的研究纪律
只读复制，先做SHA-256和目录清单，不运行任何源程序或安装依赖；先核定是否为完整申请披露、混入第三方库或秘密、目录元数据来源与复写历史。文件数、创建时间和署名不能直接推论实际产品部署或工程个人贡献。不能批量将原始代码上传公开库。

## 7. 本轮实质发现
除了寻找CD，还在三个公开版本中发现“交叉引用前案文字”差异——说明技术世家需分别追踪**当时公开版本**和**今日标准化申请族**，见 research/13。此项差异不能在未获原始案卷前解释为有效优先权被改动。

下一步：查官方接收/转交材料是否保存；取得至少一个同案原始接收或目录文件，再升级D1，继续追查媒体与内容。
