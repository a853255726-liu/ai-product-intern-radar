# 北京 AI 产品实习机会雷达

在线网站：https://a853255726-liu.github.io/ai-product-intern-radar/

## 目标与筛选

**仅北京的 AI 产品及相邻产品方向，日常实习优先，但不排除普通、留用和专项实习。**
只有明确仅面向应届毕业生的实习/正式校招、社招全职，以及纯算法/工程岗位会被排除。
如果职位仅写“2027届”“2027届及以后”或者届次不明，不擅自认定满足条件，保留资格备注。
工作地点优先使用 JD 明确的职位地点，遇到标题“厦门”但列表泛称北京的冲突，暂不纳入北京看板。

官网职位有记录 **不等于目前仍有招聘名额**。应当区分官网详情、官方 API/职位列表、第三方线索和最后验证日期。

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
