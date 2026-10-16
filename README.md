# 北京 AI 产品实习机会雷达

在线网站：https://a853255726-liu.github.io/ai-product-intern-radar/

## 最新云端验收结果（2026-10-16，北京时间）

本次不再仅以代码提交判断接入是否完成。来自 [GitHub Actions 定向采集](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38914100175) 和当次写回的 `jobs.json.source_attempts`：

| 官网公开来源 | 本次真实全量对账 | 北京 AI 产品初筛候选 | 详情 |
| --- | ---: | ---: | --- |
| **好未来新版官网「日常实习」项目** | **6/6 唯一职位 UUID，成功** | 0 | `job.tal.com/campus/positions`；逐条对照官网详情的岗位性质，禁止把「全职」当日常实习 |
| **OPPO 日常实习** | **10/10 唯一职位 ID，成功** | 0 | 正常等待官网异步加载；此前页面初始显示的 0 属于加载态 |
| **腾讯北京日常实习** | **25/25 唯一职位 ID，成功** | 3 | 官网 mapping=104 指定项目；只覆盖该官方查询范围 |

上述候选数量是按北京和 AI 产品职责等条件初筛的结果，不代表招聘名额、HR 确认在招或企业所有岗位。**好未来 / OPPO 两个来源已通过云端采集验收，但本次均未筛出符合要求的北京 AI 产品实习。**

## 目标与筛选

**仅北京的 AI 产品及相邻产品方向，日常实习优先，但不排除普通、留用和专项实习。**
只有明确仅面向应届毕业生的实习/正式校招、社招全职，以及纯算法/工程岗位会被排除。
如果职位仅写“2027届”“2027届及以后”或者届次不明，不擅自认定满足条件，保留资格备注。
工作地点优先使用 JD 明确的职位地点，遇到标题“厦门”但列表泛称北京的冲突，暂不纳入北京看板。

官网职位有记录 **不等于目前仍有招聘名额**。应当区分官网详情、官方 API/职位列表、第三方线索和最后验证日期。

## 当前来源配置（2026-10-16）

截至2026-10-16主工作流现**配置了26个公开招聘查询源**：原有20个、商汤科技、智平方、无问芯穹、星动纪元，以及好未来、OPPO两个首批新增来源。来源已配置 ≠ 本次云端执行成功 ≠ 有符合北京 AI 产品日常实习的职位。须逐个以 `jobs.json.source_attempts`、`jobs.json.source_audits` 的最近实测结果判断。清程极智仅进入官方来源核查池，**不包含在上述24个自动采集源内**。

以下2026-10-14章节保留历史成功快照与早期修复记录，不应解释为2026-10-16所有来源的实时状态。

## 数据源状态（2026-10-14，按北京时间）

目前 GitHub Actions 每天北京时间约 09:17 对 **20 个已配置的公开查询源**运行定时全量刷新（另有定向调试模式）。以下表格给出已确认的接口与近期审计参考值，**不是一次统一运行中20个来源全部成功的声明**。最近 B站定向运行成功核验322个唯一职位ID；其他来源各自成功与失败状态，应分别查看 `jobs.json.source_attempts` 与 `source_audits`。失败不删除历史数据，也不等于企业停止招聘。
数量为公开入口返回的**原始职位记录**，不是最终 AI 产品岗位数量，不可跨公司简单相加。

| 公司 | 最近确认的入口查询范围 | 原始记录 | 自动化 |
| --- | --- | ---: | --- |
| 腾讯 | `join.qq.com` 北京日常实习 `projectMappingIdList=104` | 25 | 成功 |
| 美团 | `zhaopin.meituan.com` 校招实习类别，所有城市 | 当前查询约363 | 本轮重复 ID 导致完整性校验失败，保留历史结果 |
| 小红书 | `job.xiaohongshu.com` 校招混合目录 | 约492 | 成功 |
| 京东 | `campus.jd.com/api/wx/position/page?type=internship` 全部城市 | 102 | 成功，已修正错误的 `intern` 参数 |
| 百度 | `talent.baidu.com/httservice/getPostListNew` 北京/产品/实习 | 184 | 成功，已用 form-encoded 和 `curPage` 修复分页 |
| 快手 | `campus.kuaishou.cn` 实习项目 | 228 | 成功 |
| 米哈游 | `ats.openout.mihoyo.com` 校招混合入口 | 269 | 成功 |
| 零一万物 | `01ai.jobs.feishu.cn/index/position/list` 全类别 | 51 | 公开浏览器页面，成功 |
| MiniMax | `vrfi1sk8a0.jobs.feishu.cn/index/position/list` 全类别 | 197 | 公开浏览器页面，成功 |
| 智谱 | `zhipu-ai.jobs.feishu.cn/index/position/list` 全类别 | 222 | 公开浏览器页面，成功 |
| RealAI | `realai.jobs.feishu.cn/272867/` 全类别 | 11 | 公开浏览器页面，成功 |
| 百川智能 | `cq6qe6bvfr6.jobs.feishu.cn/646926/` 的日常实习项目 | 6 | 公开浏览器页面，成功；此项目目前无 AI PM |
| 爱奇艺 | `iq.jobs.feishu.cn/intern/m/` 日常实习公开目录 | 95 | 公开浏览器页面，成功；10页唯一ID完整对账 |
| 月之暗面 Kimi | `app.mokahr.com/campus-recruitment/moonshot/148507` 校招公开目录 | 94～95 | 公开浏览器页面成功，按最近成功快照为准 |
| 生数科技 | `shengshu.jobs.feishu.cn/index/position/list` 全招聘类型 | 108 | 公开页面成功，11页独立 ID 对账 |
| 面壁智能 | `modelbest.jobs.feishu.cn/campus/m/position/list` 校园招聘 | 60 | 公开浏览器页面成功，6页独立 ID 对账 |
| 阿里巴巴 | `campus-talent.alibaba.com/campus/position?batchId=100000560002&lang=zh` 日常实习项目 | 368 | 官方匿名 API 已通过4页唯一ID对账，142条地点含北京，20条AI产品相关候选已入库 |
| 阶跃星辰 | `app.mokahr.com/campus-recruitment/step/94905` 校招混合职位目录 | 129 | 官方Moka全量5页唯一ID核验，严格筛实习与北京 |
| 深势科技 | `dptechnology.jobs.feishu.cn/index/position/list` 招聘混合目录 | 239 | 官网飞书24页唯一ID核验；6条北京AI产品相邻候选已入库 |
| B站 | `jobs.bilibili.com/campus/positions?type=0&page=1` 实习招聘 | 322 | 匿名官网API4页322个唯一ID，均标实习；当前无明确北京AI产品候选 |

以上数字是首次修复和测试时的证据快照。往后请以 `jobs.json.source_audits`、`jobs.json.source_attempts` 和 `data/last_errors.json` 的最近结果为准。页面不展示所有原始记录；只有“北京+产品相关+实习”筛查后留下的候选才入库。

### 尚未每日自动核验

- **小米**：官网公开 API 已核对北京实习334条、27条AI产品相关候选，并存为 `data/xiaomi_official_20261013.json`。GitHub Actions 请求会返回403，因此该来源是带日期的官网人工快照，**没有每日自动更新**。
- **腾讯其他通道**：另核查了北京应届实习51、青云计划实习134条。应届实习不属于本版优先渠道；青云计划主要为科研课题，没有明确AI产品经理岗，所以未并入每日主采集。
- **字节跳动及其他未完全核验的企业**：仍存在接口和公司覆盖缺口；不因空列表推断企业没有在招。字节新增四类范围限定查询尝试（见下方），不代表公司全部团队与招聘项目。

### 新增官方来源接入（2026-10-14）

- **爱奇艺日常实习**：新增官方飞书目录 `https://iq.jobs.feishu.cn/intern/m/`，以 `feishu-iqiyi` 开启完整分页、唯一职位 ID 对账、北京/实习/AI 产品职责筛选及官方职位详情 URL。新增接口的真实成功状态，以工作流执行后的 `source_audits.爱奇艺` 和 `source_attempts.爱奇艺` 为准；当前已获成功审计，仍不能将原始职位总数直接视为北京AI产品数。
- **发现规则**：`candidate_scope.py` 在常规产品岗位外，允许标题不是“产品”但 JD 具有明确 AI 产品工作职责的相邻岗位；排除纯研发、标注、行政等工作。保留原始官方职位总数与最终候选数的区别。
- **后续官方接入**：Kimi 已核验并自动接入。阿里已确认日常实习入口 `batchId=100000560002`，完成368条全量核验；之前 `batchId=100000760001` 完整抓取的470条是2027届应届生岗位，不得混作实习。字节日常实习公开 API 在 GitHub Actions 返回 HTTP 405，尚未成功接入，不能推断没有岗位。
- **重复记录**：新捕获的爱奇艺职位会优先按职位专属 ID、招聘职位代码（如 A15887）与已收录记录去重，并在证据足够时把原来的列表链接升级为官方详情。

### 月之暗面 Kimi 官方 MokaHR 来源（2026-10-14）

- 官方校园招聘职位目录：https://app.mokahr.com/campus-recruitment/moonshot/148507#/jobs/?page=1 。网页核查时显示95条原始职位，分布4页；不等于北京AI产品候选数量。
- kimi_sources.py 使用公开浏览器正常渲染，核验总数与唯一UUID，需到职位详情确认北京（部分职位列表省略城市）。不模仿非公开API，也不绕过登录限制。
- 新增 kimi-moka 命令及官方 Moka `/job/<UUID>` 详情链接识别。若职位列表缺页、总数不一致或职位详情无法渲染，保留上一版成功的数据。
- 职位发布状态不能证明仍有招聘名额；以 jobs.json.source_attempts.月之暗面 判断真实采集状态。



## 工程实现

- `refresh_sources.py`：多个招聘站点 API，京东/百度修复，主数据更新、失败保留和去重。
- `extra_sources.py`：快手、米哈游、小米来源的适配代码。
- `feishu_sources.py`：可复用的飞书招聘适配器，**先尝试公开 HTML/SSR，再用普通 Chromium 正常渲染网站职位列表**；不绕过登录、验证码或签名限制。检查总数、分页、唯一职位ID，再筛北京实习和产品方向。
- `daily_scope.py`：日常实习优先、应届资格筛查。
- `rebuild.py`、`expand_companies.py`：生成独立 `index.html`、岗位/企业 CSV。
- `tests/`：离线测试 JD/Baidu 请求契约、飞书列表、城市冲突、校验失败等。
- `SOURCE_REPAIR_FEISHU_AUDIT.md`：问题复现、接口参数和查询边界。

本地运行：

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m unittest discover -s tests -p 'test_*.py' -v
python refresh_sources.py --sources meituan xhs tencent jd baidu kuaishou mihoyo feishu-zeroone feishu-minimax feishu-zhipu feishu-realai feishu-baichuan feishu-iqiyi feishu-shengshu feishu-modelbest kimi-moka alibaba-public
python expand_companies.py
python rebuild.py
```

GitHub Actions 配置：`.github/workflows/site.yml`；每日自动更新和网页部署按一条工作流执行。任一数据源失败时不删除历史岗位，只保留上一次核验数据并标记源失败。


## 官网职位直达规则（2026-10-14）

默认显示“仅官网职位直达”候选。点击岗位名称会在新标签页打开企业官方具体职位详情页，“职位摘要”按钮则保留本地整理的完整岗位信息和收藏功能。

- 源于官网 API 但仍是官网列表地址的职位，不得冒充具体职位详情。
- 尚无专属官方职位 ID 的第三方线索继续保留在“全部候选”，提供“查看原始来源”，绝不构造虚假的官网职位 URL。
- 京东原有六条候选的错误 \`#/job/detail?publishId=...\` 详情路由已修正为实际可用的 \`#/details?id=...\`，未来自动采集也采用新路由。
- 腾讯历史占位 \`postId=-3\` 无法对应真实职位，因此不再显示于公开候选。
- 每条记录分别保存官网专属详情地址、原始来源、链接类别与是否仍待核实的信息。职位的专属 URL 符合页面路由规范并不等于当前仍有 HC，不能作为实时开放证明。

详细规则、边界和待补链接详见 [LINK_POLICY.md](LINK_POLICY.md)，由 [official_links.py](official_links.py) 统一执行。导出 CSV 同时保留官网直达与原始来源两个字段。

### 字节跳动北京日常实习来源试接入（2026-10-14）

- 新增 `bytedance_sources.py`，按实习、日常实习、北京，以及产品/产品运营/用户研究/策略四类查询公开职位 API `/api/v1/search/job/posts`。2026-10-14 GitHub Actions 实测 HTTP 405，**已暂停其每日自动调用**，保留代码供接口恢复和手动诊断；不得将该查询标为成功。
- 本来源必须在真实云端返回成功、总数一致和唯一职位 ID 对账后才能标记自动成功。`source_audits.字节跳动` 只指这一子查询，不能称为字节全量招聘源。
- 若 API 拒绝访问、类别标识发生变化或分页异常，保留已核实的现有岗位而不是假装岗位为零。
- JD 的 AI 业务关联度和岗位性质仍需筛选；ByteIntern 与算法等其他项目不属于此采集范围。

### 阿里巴巴官方招聘链接范围（2026-10-14）

- 已确认校园招聘的独立职位详情 URL 格式：`https://campus-talent.alibaba.com/campus/position/<职位ID>`；`official_links.py` 对符合格式的专属职位链接归为 `official_detail`，普通目录页面仍为 `official_list`。
- 曾核验应届校招批次 `100000760001` 的470条职位、5页，但不属于日常实习。2026-10-14 已改为真正的日常实习批次 `100000560002`；请查看最新 `source_attempts.阿里巴巴` 和 `source_audits.阿里巴巴` 判断是否成功。

### 新增小型 AI 公司官方源验证（2026-10-14）

- 生数科技：官网 `https://shengshu.jobs.feishu.cn/index/position/list`；官方最近一次核验为 108 条原始记录，招聘类型混合，**仅筛北京实习与 AI 产品相邻职位**。选择器 `feishu-shengshu`。
- 面壁智能：官网 `https://modelbest.jobs.feishu.cn/campus/m/position/list`；公开校园招聘目录观察到约 60 条原始记录，**不将校招正式岗算作实习**。选择器 `feishu-modelbest`。
- 两个新源均复用飞书公开 HTML/普通浏览器分页核验、唯一职位 ID 对账、失败保留快照机制。配置完成不代表实时采集成功，以 `source_attempts` 和 `source_audits` 为准。

### 阿里巴巴校园招聘公开会话 API 验证（2026-10-14）

- `alibaba_sources.py`、命令 `alibaba-public` 现指向官网首页“日常实习生 → 去投递”真实目的地 `https://campus-talent.alibaba.com/campus/position?batchId=100000560002&lang=zh`。官网中文页面显示约368条原始职位，仍需按实习、北京、AI产品职责过滤。
- 采用官网公开匿名会话提供的标准页面 token，并调用同域职位列表 JSON；**不会绕过登录、验证码或风控验证**。之前成功的470条记录属于应届校招，不能证明新日常实习入口已经完成全量验证；请以新一轮 Actions 审计为准。
- 先核对总数与所有唯一职位ID，再根据职位/招聘项目**明确的“实习”证据**、北京地点和 JD 中 AI 产品工作职责筛选。不能因为校招目录中出现“产品经理”就把正式应届岗位收为实习。
- 入口范围仅是当前 campus batchId，其他集团或独立招聘渠道不在成功声称范围。若实际 HTTP 拒绝、token 未提供或数据不完整则失败保留既有记录。

### 阶跃星辰来源发现（2026-10-14）

- 已确认阶跃星辰校招/实习的官方 Moka 入口 `https://app.mokahr.com/campus-recruitment/step/94905#/jobs`，并在企业覆盖页中改为直接打开这一招聘目录。
- 官网另有 StepStar 专项人才招聘入口，与一般校园实习的筛选范围不同。当前普通校园目录已完成全量分页及岗位性质筛选，而StepStar专项尚未纳入，所以**已经完成129个唯一ID的正式自动核验**；历史待验证描述不再适用。

### 阿里巴巴筛选诊断（2026-10-14）

- 完整抓取 470 条职位，只证明当前校招混合目录 API 可访问，不证明日常实习分类准确。本轮新增 `source_audits.阿里巴巴.screening_diagnostics`，记录真实字段名称、北京/实习判定数量与有限岗位样例，以找出候选为零的具体原因。
- 实习筛选不会依据业务描述中顺便出现“实习”就把正式校招岗归入实习，后续要先定位和验证正式的招聘项目/岗位性质字段。

### 阶跃星辰 Moka 官网校园招聘采集试接入（2026-10-14）

- 新增 `step_sources.py` 和 `step-moka` 来源，目标为官方 `https://app.mokahr.com/campus-recruitment/step/94905#/jobs`，此前公开页面观察到约129个校园职位；仅在成功全量分页及唯一ID核验后计入已核验来源。
- 校园招聘列表包含标题写有“实习生”、但职位性质明确为“全职”的记录，**优先以职位性质判定**，避免误收录正式岗；还要求北京和AI产品相关职责。
- StepStar人才专项为独立招聘项目，此版本不包含。若浏览器抓取不完整则保留历史数据，不将空页面判为无岗位。

### 阿里日常实习正确入口定位（2026-10-14）

- 已通过官网首页“研究型/日常实习生”下的**日常实习生**独立投递按钮验证目标 URL `batchId=100000560002`，不再误用应届校招 `batchId=100000760001`。
- 中文页面按 `lang=zh` 展示约368个职位；英文界面的职位数量不同，不可不带语言参数把两者混为完整招聘清单。新采集仍要求同一查询范围内总数、分页、稳定ID一致。
- 首次采集必须经 GitHub Actions 成功并生成 `source_attempts.阿里巴巴` 才能称已上线；严格依据实习项目、北京地点和职责筛选。

### 阿里日常实习公开候选的匹配度与时间字段（2026-10-14）

- 已验证官方日常实习批次 368 条原始职位，142 条工作地点包含北京，25 条通过初层“产品相邻”判定，其中满足 AI 业务筛选的 20 条已收录（以最新 source_audits 和 jobs.json 为准）。这些是本次发现的职位，不代表过去24小时新发布。
- 产品经理、产品实习等职责优先；纯内容运营、交互设计、模型评测研究岗位不会一律归入“优先关注”。其中强制生物背景、世界模型等明显专业不匹配的研究岗位标为“匹配较弱”，保留在候选池供用户选择。
- 从原始 JD 里明确出现的每周 3/4/5 天与至少实习月数提取条件。没写的不猜测；后续重新刷新时只更新本采集器生成的岗位优先级和时间信息，不覆盖已人工核验的岗位。

### 美团完整分页修复与 B站官方入口（2026-10-14）

- 本次代码验收已通过；以下美团真实接口效果以重新运行的 `source_attempts.美团` 为准。
- 美团公开实习 API 最近连续出现“官方 total = 检索行数，但唯一职位 ID 少 1”的错误。严格拒绝重复 ID 保留不变；新增仅在该特定错误下以更小分页（100→50）重新完整抓取与唯一 ID 对账。重试仍失败则不入库、不标记成功。
- B站现已完成官网 `type=0` 实习频道的匿名API全量322条核验，详见文末来源说明；不带类型的目录默认应届招聘，不能混用。

### 招聘接口重复职位 ID 的溯源（2026-10-14）

- 美团最近报告366条但365个唯一ID，小红书报告495条但494个唯一ID。不能凭差一个就推断“只是页面重复”，因此继续执行严格ID校验，失败保留上次成功数据。
- 新增重复记录位置诊断：仅输出公开职位ID、首次出现页、重复出现页、同页或跨页，以及两次记录内容是否完全一致，以区分原始数据重复、排序不稳定和抓取过程中结果变动。不会隐藏或自动删除重复职位。
- 小红书ID重复时，按100→50→20条/页依次重新全量抓取，每次严格对账。美团继续100→50条/页重抓，并在失败审计中记录两次诊断。全部失败时，保留历史确认的岗位。
- B站历史排障：曾误用 `type=1/2` 查询发现0条；正确实习参数为 `type=0`，现已完成官网匿名API分页和稳定ID核验，见 `source_audits.B站`。

### 深势科技（DP Technology）官方 AI for Science 实习源（2026-10-14）

- 新增飞书招聘源 https://dptechnology.jobs.feishu.cn/index/position/list，命令 feishu-dptechnology。官网招募页面的原始职位数量在核查时约237～239条，属于混合全职/实习目录；这个数量并不是北京 AI 产品岗位数量。
- 官网可直接核验产品实习生详情 https://dptechnology.jobs.feishu.cn/index/position/7611105993640741170/detail，岗位涉及 AI for Science 科研/教育平台需求、用户调研、PRD、产品迭代，每周4天及以上、连续3个月及以上。
- 接入自动化后需要按官网完整分页与唯一职位ID校验，北京实习与AI产品职责再次筛选；若第一页未渲染可尝试公开普通浏览器，不绕过登录或反爬；未成功前不计入已成功每日来源。

### 定向数据源验收（2026-10-14）

- 日常定时任务与手动运行仍抓取全部配置来源。只对带指定标记的 GitHub push 支持定向刷新，避免每次修一个来源都等待全部飞书和 Moka 分页。
- commit 标记 [refresh:focus]：仅刷新美团、小红书、深势科技；[refresh:diagnostics]：仅刷新美团与小红书；[refresh:dptechnology]：仅刷新深势科技；原 [refresh] 仍为全源刷新。
- 定向运行仅更新被选数据源的审计与岗位，其余来源保留上次成功状态与历史数据。不要将定向运行的 last_errors.json 误读为全部来源当日无错误。

### 已验证的分页恢复策略与深势科技专用职位排除（2026-10-14）

- 美团2026-10-14首次每页100条时，职位ID 4346490662在第2、3页出现同内容重复；每页50条重新完整抓取后，对账366条/366唯一ID成功。
- 小红书首次每页100条时，职位ID 20028在第2、3页出现同内容重复；改每页50条后，对账495条/495唯一ID成功。
- 此后默认采用已验证的每页50条，美团如果再发生ID重叠用每页25条重新全量重抓，小红书用每页20条。仍无法对账则保持严格失败标记，不静默删除重复记录。
- 深势科技官方校园目录包含带“比赛专用”的岗位，这类岗位不等同普遍开放的日常实习，新增自动排除和回归测试，原始招聘目录数量照实审计。

### B站官方日常/暑期实习招聘项目（2026-10-14）

- 之前只确认了 B站官网 `https://jobs.bilibili.com/campus/positions`，这个不带类型的入口默认是应届生招聘（type=3），因此不能把其中的正式岗当作实习。现已确认 `https://jobs.bilibili.com/campus/positions?type=0&page=1` 是官方实习生招聘。
- 前端程序公开使用匿名会话的 `/api/auth/v1/csrf/token` 和 `/api/campus/position/positionList`，明确参数 `workTypeList=["0"]`、`positionTypeList=["0"]`。在官网浏览器环境实测该频道返回322条原始记录（100、100、100、22，共322唯一职位ID），其中有6条地点含北京；职位类型还需逐条确认，不能直接将322条全部视为合格实习。目前未发现明确符合北京AI产品经理/相邻产品职责的岗位。
- 新增 `bilibili_sources.py` 与 `bilibili-public` 来源及官方专属详情路由 `/campus/positions/<id>?type=0`，只采公开访客接口，不登录或绕过验证。是否能在GitHub Actions持续使用以真实自动化 `source_attempts.B站` 为准，接口失败时不删除历史记录。
- B站官网有实习职位 ≠ 北京AI PM岗位；全国322条并不意味着北京存在322条有效机会。每条候选需同时通过实习类型、北京地点、AI业务及产品职责筛查。

### 硅基流动来源状态（2026-10-14）

- 牛客企业HR的北京AIGC产品体验实习 `https://www.nowcoder.com/jobs/detail/456133` 仍是可核查的第三方招聘线索，条件每周4天、至少3个月；不等同公司独立官方职位ID。没有找到能够核实为硅基流动且稳定分页的官方招聘目录，因此不标记为官方自动采集成功。

- 首次 GitHub Actions 发现 type=0 招聘频道存在非标准的职位性质字段，采集器已改为原始记录全量审计且保存 `position_type_counts`、`explicit_internships`、`non_internship_rows`；仅职位性质明确含“实习”的记录才可发布。未知或正式职位不进入实习看板。

**文档维护说明：** 上述较早的“首次发现/试接入”小节保留历史测试过程，判定当前状态时请优先看本节来源表以及 `jobs.json.source_attempts`、`source_audits`。B站本次定向运行成功，但不代表其他19个来源在同一时刻均成功。


## 2026-10-15｜受限招聘源修复与安全验收

- **字节跳动**：`bytedance_sources.py` 首先请求原有官方公开校园 API。仅在 HTTP 403/405 时尝试 `bytedance_browser.py`：用正常 Chromium 打开招聘官网的北京、日常实习、产品相关类别筛选页，观察网页自身返回的职位 API 响应。必须核对网页实际发出的招聘类型 202、日常项目 ID、北京城市、四个指定类别以及分页 offset/limit，再检查返回总数、每页记录、全部职位 ID 唯一性。不登录、不模拟受保护签名、不解决验证码。**新逻辑尚未通过 GitHub Actions 的云端全量验证，因此仍未加入每日正式源。**
- **小米**：`extra_sources.py` 在原有公开 `searchJobPage` API 遇到 HTTP 403/405 时，调用 `xiaomi_browser.py` 从官方职位页面中使用其公开同源接口读取北京、实习类型=3的数据。只有完整分页和全部职位 ID 对账成功才接受更新；否则保留带日期的官方快照。**暂未恢复每日自动更新。**
- **蚂蚁集团**：`https://talent.antgroup.com/campus/home` 官方首页明确列出「日常实习」面向全体在校生、毕业时间不限。现作为单独已确认的招聘入口列入 `company_coverage`，**未验证全量职位分页与职位 ID，不纳入自动岗位记录**。不要和仅面向特定毕业届次的转正实习混用。
- **诊断工作流**：`.github/workflows/diagnose-blocked-sources.yml` 可在 Actions 中手动运行，分别检查字节和小米。已安装 Chromium，失败会显示为失败检查，而不再是误导性的绿色成功状态。
- **只读审计**：`refresh_sources.py --audit-only --sources bytedance-daily xiaomi` 仅在运行进程内检查、打印结果，不写回 `jobs.json`、`data/last_errors.json` 或 `data/raw`。离线测试见 `tests/test_bytedance_browser.py`、`tests/test_xiaomi_browser.py`、`tests/test_audit_read_only.py`。

请先手动运行上述诊断工作流，查看两家公司实际云端请求结果和唯一职位 ID。**只有某一来源当次真实对账成功，且岗位性质、城市、JD 资格校验可靠后**，才将它加入正式定时刷新列表。HTTP 403/405、验证码、部分分页或详情失效均不构成“零在招岗位”的证据。

 
## 2026-10-16｜商汤与地平线渠道增补

- **商汤科技**：确认官网校园招聘 `https://hr.sensetime.com/campus/?c=1` 将实习生招聘单列，公开的 `https://hr-jobs.sensetime.com/edu/m/` 可见实习、城市、职能类别。新增 `feishu-sensetime`，复用公开 HTML/浏览器分页、报告总数和唯一职位ID完整性校验，筛选仅北京实习及AI产品职责，并产生官方专属职位链接。不采纳仅有“27届校招”的正式岗位。
- **地平线机器人**：官方校园招聘入口 `https://horizon-campus.hotjob.cn/` 已列入公司来源核查，日常实习是独立关注渠道。招聘入口发现不等于已采集到可投递的北京AI产品岗位；没有完整稳定分页/职位ID之前，保持 `partial` 且不写入岗位候选。
- **验收**：添加 `tests/test_sensetime_source.py` 核对商汤官网域名、职位链接、北京与实习筛选。定时任务已添加商汤作为待验收来源，首次完整抓取成功与否以 `jobs.json.source_attempts.商汤科技` 为准。可用 GitHub commit 标记 `[refresh:sensetime]` 定向刷新商汤和腾讯，不修改其他来源。**本节不宣称商汤已完成云端自动化验收。**


## 2026-10-16｜中小型 AI 公司招聘来源扩充

这一批优先纳入招聘页已经存在公开职位列表、且能复用普通飞书 HTML/浏览器采集策略的 AI 公司：

| 公司 | 官网入口 | 纳入范围与现状 |
| --- | --- | --- |
| 智平方 | https://ai2robotics.jobs.feishu.cn/ | 北京具身智能软件平台产品日常实习（官网明确每周4–5天、3个月以上）；接入 `feishu-ai2robotics`，待云端首次全量审计 |
| 无问芯穹 | https://infinigence.jobs.feishu.cn/ | 北京 AI Infra / 算力产品；目前可见产品岗位多为全职，接入 `feishu-infinigence` 但正式岗绝不进入实习看板 |
| 星动纪元 | https://k0fqxcszc9.jobs.feishu.cn/ | 北京具身智能/机器人产品；可见技术产品岗主要为全职，接入 `feishu-robotera` 并仅在确认实习时入库 |
| 清程极智 | https://chitu-ai.jobs.feishu.cn/ | 北京 AI 推理平台招聘主页已核实；职位专属全量分页与北京产品实习尚未核实，先进入来源核查池，不启动自动采集 |

`feishu_sources.py` 继续要求本来源总数、全量分页和全部唯一职位 ID 一致，筛选北京实习与真实 AI 产品职责后才会入库。官网存在全职产品岗不等于当前存在实习机会。链接优先官网职位详情而非招聘目录，未取得职位 ID 时不伪造详情页。

首次诊断可通过 `python refresh_sources.py --audit-only --sources feishu-ai2robotics feishu-infinigence feishu-robotera`（只读，不更新数据）。每日定时刷新已经配置这些来源；每一家真实运行成功与否须查看 `jobs.json.source_attempts` 和 `source_audits`。定向 CI 验证使用 `[refresh:expand-ai]` 提交标记（额外运行已知可用的腾讯来源保障流程）；测试见 `tests/test_ai_employer_expansion.py`。**完成代码接入不等于已经完成云端采集验收。**


## 2026-10-16｜第一批大厂/中厂接入（华为、OPPO、汽车之家、好未来、搜狐）

| 公司 | 官方入口 | 当前实现与不确定性 |
| --- | --- | --- |
| 华为 | https://career.huawei.com/reccampportal/portal5/campus-recruitment.html | 「勇敢星」实习生官网入口已确认；客户端职位接口、完整分页和稳定ID尚未验收，仅监测官方页面可访问性 |
| OPPO | https://career.oppo.com/official/oppo/recruitment/post?recruitType=OFFEN-RECRUITMENT | 已接入 `oppo-daily`，独立于2027届寻梦/正式校园招聘；核验页面公布岗位数量与全部职位ID，筛北京AI产品。若有未抓取分页则失败；未取得对应数字详情ID时只保留官网列表 |
| 汽车之家 | https://talent.autohome.com.cn/campus_index.html | 2027届正式校招之外，另有面向在校生的日常实习。实习专属可分页职位接口待定位；仅监测官方入口可达性 |
| 好未来 | https://app.mokahr.com/campus-recruitment/tal/95443#/jobs | 已接入 `tal-moka`，使用现有Moka解析器核对列表总数/唯一UUID，读取产品实习完整JD并严筛北京AI产品岗位；2027暑期实习有届次限制风险，显式仅限应届者不在公开看板展示 |
| 搜狐 | https://campus.sohu.com/ | 2027秋招官网也列有面向在校生的实习项目；秋招2026/27届条件不自动适用于日常实习，专属职位接口待确认；仅监测官网入口可达性 |

### 运行与验收
专项手动诊断：[GitHub Actions - Diagnose first-batch internship sources](https://github.com/a853255726-liu/ai-product-intern-radar/actions/workflows/diagnose-first-batch.yml)，分别运行 `tal-moka` 与 `oppo-daily`。诊断使用 `--audit-only`，失败有红色状态及7天日志工件；不更新招聘数据。华为、汽车之家、搜狐的入口可访问性每天由 `directory_monitor.py` 单独记录在 `jobs.json.directory_attempts`，与完整岗位源的 `source_attempts` 完全分离。


- 新代码：`tal_sources.py`、`oppo_sources.py`；只读官网入口健康检查：`directory_monitor.py`。入口监测只记录「官网可访问」，绝不产生岗位或把 403 判成零职位。
- 检查：`python -m unittest discover -s tests -p 'test_*.py' -v`；`python refresh_sources.py --audit-only --sources tal-moka oppo-daily`（只读，检查完整性）；`python directory_monitor.py`（记录华为/汽车之家/搜狐页面可达性，不抓岗位）。
- 定向云端验证：在 `main` 上提交包含 `[refresh:batch1]` 的消息触发只采集好未来、OPPO、腾讯，运行所有离线测试、入口监测并重新生成页面。定时运行现在尝试 26 个来源。
- **发布门槛**：`source_attempts.好未来` 和 `source_attempts.OPPO` 有当日成功记录，并且职位ID数与全部分页校验通过，才可说自动采集已验收。当前完成的是代码和来源入口接入；不能把「已配置」说成「成功更新」或「目前有北京AI产品HC」。


### 2026-10-16｜第一批验收加固

- **好未来资格校验**：`tal_sources.explicit_grad_only` 对完整公开 JD 检查毕业届次限制，不受面向看板的 `summary/requirements` 摘录长度影响；对明确仅招2027届等条件保留原始限制证据，使 `daily_scope.eligible_jobs` 能排除。增加超长 JD 的回归测试。
- **来源计数**：已核验来源的 `source_attempts` 增加 `candidate_count` 和 `new_candidate_count`；这是北京 AI 产品初筛候选，不是已确认可投职位、剩余 HC 或日报新增数量。网页仅展示经过筛选和去重后的记录。
- **工作流顺序**：依赖安装后立即运行离线测试，再下载 Chromium、执行多来源网络采集。若采集失败，GitHub Actions 保留 `source-errors-<run id>` 诊断工件 14 天。
- **官方入口监测**：公开页面 HTTP 200 但静态 HTML 没出现「实习」时，`directory_attempts` 标记「入口可达，待浏览器复核」，而非「网站不可访问」或「零岗位」。
- **未通过的验收不能提前宣传**：截至这一轮仓库检查，`jobs.json` 仍为2026-10-15快照，`source_attempts.好未来` 与 `source_attempts.OPPO` 尚无成功记录。请以最新 GitHub Actions 运行日志为准。



### 2026-10-16｜岗位有效性与独立诊断加固

- `source-tests.yml`：Python 源代码或回归测试变更时，独立执行 Python 编译及全部离线测试，并保存 14 天测试日志；与 Pages 部署解耦。
- `diagnose-first-batch.yml`：北京时间每天约 11:47 分别只读审计好未来、OPPO；测试/抓取日志分别保留，单源失败显示失败，不发布岗位数据。GitHub Actions 的定时启动可能延迟。
- **毕业届次**：好未来、OPPO 都从公开 JD 保留明确的「仅招某届」限制证据；同一官网自动收录职位后续改变资格时，刷新其资格信息，避免旧资格继续流入看板。
- **完整性与下架**：只有好未来或 OPPO 的公开职位列表真正通过数量和唯一 ID 的全量校验，才对该来源的自动导入记录进行存在性核对。未再出现的岗位保留历史原文，但标为 `listing_inactive=true` 并在公开列表暂停展示；重新出现会恢复。采集失败时不进行下架判断，手动研究的岗位也不受此规则影响。
- **验收严格区分**：代码提交、GitHub 测试通过、官网全量采集成功、发现符合北京 AI 产品实习资格的职位，是四个不同状态。截至该段更新时，GitHub 仓库的 `jobs.json` 仍是 2026-10-15 的快照，尚无好未来、OPPO 真实成功审计结果。

### 2026-10-16｜第一批上线前的一致性修复

- **明确届次限制优先**：好未来、OPPO 从完整官方 JD 生成 `graduation_restriction_confirmed`，发布筛选优先执行，防止一份冗长 JD 中其他「某届及以后」表述覆盖真正的仅限某届要求；刷新已有自动记录时也会更新这个标记。
- **官网消失与不再匹配分开**：对完整验收成功的 TAL/OPPO 列表，优先以公开原始职位 ID 判断是否还在官网，再用北京/实习/AI产品条件决定候选资格。`listing_missing_reason` 分别记录「官网当前完整列表未检出」或「不再满足北京AI产品实习初筛」。历史原文保留、暂停公开展示，失败请求绝不触发失效判定。
- **三个来源数量概念**：`reported` 为官网原始职位数，`candidate_count` 为来源北京AI产品初筛，`eligible_candidate_count` 为进一步排除明确毕业限制后的候选数。三者都不是目前已确认可投递的HC数量。
- **来源表时效透明**：`company_coverage.csv` 追加「最近自动采集状态」「最近自动采集日期」。过往曾成功完成分页的企业，若最近检查失败，也会单独显示失败；只定位到官网入口的公司不冒充已成功采集。
- **测试**：增加届次限制优先级、OPPO 在官网仍有记录但不符筛选条件、官网列表缺失、来源导出状态列的离线回归测试。CI 测试工作流已配置，但截止此次仓库检查，仍没有可靠的 GitHub Actions 成功结果或好未来、OPPO 的最新抓取回写，不能据此宣称两家已稳定上线。

### 2026-10-16｜首次确认离线测试通过，启动官网定向采集

- 已从 GitHub Actions 真实日志复现并修复 2 个历史阻塞：好未来 `AI产品` 紧挨中文时的 AI 关键词漏筛，以及美团 50/25/10 分页重试与旧断言不一致。
- 独立离线测试运行 `38910933244` 已报告成功，主站构建亦已有成功运行，说明原有代码测试阻塞已清除。
- 本条带 `[refresh:batch1]` 标记的提交触发好未来、OPPO、腾讯官方来源定向完整性核验。成功与失败以该运行日志及新写入 `jobs.json.source_attempts` 为准；发起采集不等于已有可投职位。

### 2026-10-16｜真实采集与页面诊断

- 主采集恢复执行，`jobs.json.snapshot` 已更新为 2026-10-16。腾讯本轮核验25个唯一职位ID并筛出3个北京相关产品候选。
- 2026-10-16 首次云端定向采集显示好未来 `TAL campus job list did not render`，OPPO `OPPO count zero or beyond auditable bound`。这不是「公司没有岗位」，而是公开浏览器解析尚未通过。
- 采集器已增加有界公开页面诊断：好未来记录页面标题、URL、实际岗位链接数、前650字可见文本；OPPO记录实际职位数和前600字可见文本。严格完整性标准保持不变，未验证成功的两个来源继续保留失败状态。
- 本提交携带 `[refresh:batch1]`，用于复验好未来、OPPO、腾讯的公开采集接口。必须根据新的 source_attempts 结果决定是否继续修改网页解析。

### 2026-10-16｜好未来新版招聘页二次验收

已修正日常实习项目筛选后页面异步更新造成的全站 132 条误读：只有确认职位总数从全站基线变为日常项目独立数量、且可见卡片数与该数量完全一致时，才打开每条官网 UUID 详情，核对岗位性质、北京地点和唯一职位 ID。明确标注「全职」的职位即使处于日常实习项目也不会入库。保留失败保护，不因单次未渲染清空历史候选。

### 2026-10-16｜主工作流不更新的诊断入口

主工作流最近的岗位快照在检查时仍为2026-10-15，不能根据代码提交记录判断 GitHub Actions 的实际运行成败。新增 [Diagnose radar publication](https://github.com/a853255726-liu/ai-product-intern-radar/actions/workflows/diagnose-publication.yml) 定时与手动工作流，**只读取 GitHub Actions 最近8次主工作流运行、最近4次运行的 job/step 结果，并读取仓库 jobs.json 快照日期**。会生成 report.md、recent_runs.json 和 jobs-*.json 的诊断工件（保留14天），清楚区分根本未执行、代码测试失败、采集失败、构建/发布失败以及快照滞后。

此诊断无需额外招聘 API 或浏览器，不会发布职位，也不会修改 jobs.json。**只有在这个诊断显示实际失败步骤后，才能有根据地修复导致网站不更新的根因。** 如果该诊断本身无法执行，应先检查仓库的 Actions 启用状态、工作流文件有效性和 GitHub Pages 环境权限。最新工作流执行情况仍必须以 GitHub Actions 运行页面为准。

## 2026-10-16｜首次云端验收与下一批入口勘察

- **已确认的故障与恢复**：2026-10-16 北京时间约13:53的主定时任务在离线测试环节失败，未进入采集阶段。失败来自美团重试提示语的旧测试期望以及好未来长JD测试的筛选问题，详见 [Actions 38858115098](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38858115098)。后续2026-10-16的 [主工作流成功运行 38914100175](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38914100175) 已通过测试、定向刷新和Pages部署，岗位快照已经恢复到2026-10-16。
- **第一批采集实测**：好未来新版官网 `https://job.tal.com/campus/positions` 日常实习项目当天完整对账 6/6 个职位UUID，符合北京AI产品实习初筛 0；OPPO官网独立日常实习列表完整对账 10/10 个职位代码，符合初筛 0。两家来源成功并不意味着存在可投北京AI产品职位，也不代表企业所有招聘渠道已全覆盖。
- **汽车之家精确入口**：已定位官方职位列表 `https://talent.autohome.com.cn/campus-recruit-list.html`，页面提供实习生、北京、产品等选择，且展示分页和不同招聘类型。仅查询列表，不声称完成自动全量采集；职位是否属于AI产品方向需实际JD确认。
- **其他三家公开页面排查**：`probe_remaining_batch.py` 和 [独立DOM勘察工作流](https://github.com/a853255726-liu/ai-product-intern-radar/actions/workflows/probe-remaining-batch.yml) 对华为、汽车之家、搜狐的雇主官网进行只读浏览器检查，最多采样公开可见文字、岗位列表锚点和分页提示，不登录、不模拟投递、不写入正式岗位。只有确认分页、职位ID、招聘性质和北京筛选以后才能做真正采集器。

 
## 2026-10-16｜剩余三家公开筛选实测结果

[GitHub Actions 实际公开浏览器勘察](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38916827517) 已完成三家页面加载；这不是完整职位采集成功的标记。

- **汽车之家**：公开职位列表 `https://talent.autohome.com.cn/campus-recruit-list.html` 在按「实习生→北京→产品」依次筛选后，页面显示 3 个标题：`C1产品实习生`、`出口业务产品运营实习生`、`产品运营实习生（代查）`。原始混合列表第一页显示的是多项 `2027届校招`，已确认必须先区分招聘性质。**这些实习职位尚未逐条核对完整JD、AI相关性和官方唯一ID，不自动入库。**
- **华为**：旧校园职位搜索入口导航至新版 `https://career.huawei.com/cn/campus-recruitment-job-list`。公开页面存在「实习生」筛选，默认列表显示共102条、10条/页，但初次点按一个同名「实习生」标签后仍显示102条与应届岗位，**不能证明筛选生效**。应在确认控件状态确实发生变化、页数与职位类别对得上之后开发采集器。
- **搜狐**：`https://campus.sohu.com/` 确认面向在校生的实习生招聘项目；页面首页本身无可枚举的职位卡片或分页链接，当前尚不能宣称官网岗位全量采集。
- **质量界限**：本轮仅验证用户可见的公开搜索/筛选页面，不点击正式「申请该职位」按钮、不登陆账号、不调用需鉴权接口、不凭旧校招标题推断日常实习资格。AutoHome 3 项实习不等于 3 条 AI PM。

## 2026-10-16｜华为与搜狐专项来源攻坚

- **搜狐独立实习项目已定位并试抓**：`https://campus.sohu.com/` 官网的「立即投递」跳转到 Moka 企业 `sohu/5682`，其中「实习生职位」独立跳转 `sohu/28313`。官网公开浏览器已验证实习目录 **59 条结果，30 条/页，职位卡片具备唯一 UUID**；`parse_list_html` 与现有Moka解析器兼容。对应独立来源 `sohu-moka`，不混入 `sohu/5682` 2027校招。
- **搜狐候选详情**：官方职位详情含“AI 产品实习生（评测方向）”（评测集、AIGC 内容质量、自动评估），“数据分析/数据产品实习生”（模型方案设计、prompt评测优化），“数据产品实习生”（DMP平台、结合大模型设计方案），“产品运营实习生”（AIGC内容策略、prompt）。只有官网实习项目及直接工作地证据都充分时，才进入北京AI产品公开名单；工作地点不能仅靠「北京高校优先」推断。
- **新增采集器与校验**：`sohu_sources.py` 对独立实习项目核验全部页、唯一 UUID，并读取产品相关 JD；城市以搜狐公开实习首页可见的「职位标题+城市」映射或详情明确工作地点为准。页面分页数不符、职位ID重复、JD加载失败都失败保留旧数据。专属官网 UUID 路由在 `official_links.py` 登记；已增加 `tests/test_sohu_source.py`，`site.yml` 每日刷新新增此来源。
- **华为还在调查**：官方新职位系统 `https://career.huawei.com/cn/campus-recruitment-job-list` 的浏览器真实请求使用公开列表响应 `getJobPage`；页面初始102条主要是应届生。即使精确点击「招聘类别/实习生」控件，本轮云端界面仍返回102条且控件未显示选中，**不能宣称已筛出实习职位**。只完成源发现与诊断，不自动发布应届生岗位。
- **定向验收**：在 main 提交消息包含 `[refresh:sohu]` 时，主工作流对 `sohu-moka` 和 `tencent` 执行完整官方源抓取、对账、页面重建与Pages部署，结果以 `jobs.json.source_attempts.搜狐`、`source_audits.搜狐` 和 Actions 日志为准。尚无成功结果之前不宣称实际上线。


### 2026-10-16｜搜狐初次完整采集结果和额外城市佐证

- `sohu-moka` 首次云端完成 **59/59** 个唯一职位 UUID 对账，公开分页为 **30 + 29**，审核了产品相关官方 JD，成功运行见 [GitHub Actions](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38919510659)。首次正式入库 2 个北京 AI 产品相关实习岗位，均为搜狐官方独立实习项目的岗位，不是2027届应届校招。
- **官网已确认城市的职位**：数据分析/数据产品实习生、数据产品实习生；产品职责均在搜狐官方 Moka 详情中涉及模型/Prompt方案及评测。严禁把官网JD写的「北京高校优先」单独当作实际办公城市。
- **AI 产品实习生（评测方向）**：官方 UUID 为 `7e078123-8764-4b6c-8a21-905680360bd5`，官方职位介绍含评测集、AIGC质量评测、自动评估；官网详情未显示城市。另一份与标题及JD吻合的近期 LinkedIn 职位页面明确标「搜狐网·海淀区」，所以使用限定此 UUID、完整标题和关键JD片段的交叉城市佐证；`location_evidence` 与 `location_evidence_url` 明确记录其**非官网**性质，绝不套用到其他职位。后续仍应向招聘方确认办公地址和剩余 HC。
- 代码变更均已配套回归测试。另对华为公开官网返回的 `getJobPage` 职位数据继续核查字段结构、页码与实习类别，不跳过筛选证据直接发布应届生岗位。

### 2026-10-16｜华为默认校园职位目录完成云端验收

- [华为专属只读核验](https://github.com/a853255726-liu/ai-product-intern-radar/actions/runs/38921066343) 已在GitHub真实浏览器通过，按官网分页取得102条、102个唯一职位ID，核验全部11页。北京 AI 产品实习初筛候选0；这不意味着华为整体没有相关实习。
- 第11页使用不同的 pager-item-active DOM 标签，已修复，与普通 pager-item-pager 并行识别；总数、页码、唯一职位ID均做完整性校验。
- 覆盖状态维持 partial：华为官网实习生筛选控件尚未产生过滤效果，102条是默认校园目录，大多为应届生；不能称为华为全部实习职位。筛选要求标题明确实习、jobType 非已验证的应届类别0、北京工作地及真实AI产品工作。未验证专属详情链接时只给官网职位列表。
- 每日主工作流已加入 huawei-browser；本次提交含 [refresh:huawei] 以只刷新该来源和腾讯。是否成功回写，以 jobs.json 的 source_attempts.华为 为准。
