# 北京 AI 产品实习机会雷达

在线网站：https://a853255726-liu.github.io/ai-product-intern-radar/

## 目标与筛选

**仅北京的 AI 产品及相邻产品方向，日常实习优先，但不排除普通、留用和专项实习。**
只有明确仅面向应届毕业生的实习/正式校招、社招全职，以及纯算法/工程岗位会被排除。
如果职位仅写“2027届”“2027届及以后”或者届次不明，不擅自认定满足条件，保留资格备注。
工作地点优先使用 JD 明确的职位地点，遇到标题“厦门”但列表泛称北京的冲突，暂不纳入北京看板。

官网职位有记录 **不等于目前仍有招聘名额**。应当区分官网详情、官方 API/职位列表、第三方线索和最后验证日期。

## 数据源状态（2026-10-14，按北京时间）

目前 GitHub Actions 每天北京时间约 09:17 对下列 **17 个已配置的公开查询源**进行刷新与核验。2026-10-14 最新一轮 **16 个成功、1 个失败（美团重复ID）**；失败时保留上次成功结果，并不等于该企业停止招聘。
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
| 阿里巴巴 | `campus-talent.alibaba.com/campus/position?batchId=100000760001` 混合校招批次 | 470 | 官方匿名会话 API 成功，5页ID核验；实习类别筛选诊断中 |

以上数字是首次修复和测试时的证据快照。往后请以 `jobs.json.source_audits`、`jobs.json.source_attempts` 和 `data/last_errors.json` 的最近结果为准。页面不展示所有原始记录；只有“北京+产品相关+实习”筛查后留下的候选才入库。

### 尚未每日自动核验

- **小米**：官网公开 API 已核对北京实习334条、27条AI产品相关候选，并存为 `data/xiaomi_official_20261013.json`。GitHub Actions 请求会返回403，因此该来源是带日期的官网人工快照，**没有每日自动更新**。
- **腾讯其他通道**：另核查了北京应届实习51、青云计划实习134条。应届实习不属于本版优先渠道；青云计划主要为科研课题，没有明确AI产品经理岗，所以未并入每日主采集。
- **字节跳动、B站、阿里及其他企业**：仍存在接口和公司覆盖缺口；不因空列表推断企业没有在招。字节新增四类范围限定查询尝试（见下方），不代表公司全部团队与招聘项目。

### 新增官方来源接入（2026-10-14）

- **爱奇艺日常实习**：新增官方飞书目录 `https://iq.jobs.feishu.cn/intern/m/`，以 `feishu-iqiyi` 开启完整分页、唯一职位 ID 对账、北京/实习/AI 产品职责筛选及官方职位详情 URL。新增接口的真实成功状态，以工作流执行后的 `source_audits.爱奇艺` 和 `source_attempts.爱奇艺` 为准，**配置完成不等于已抓取成功**。
- **发现规则**：`candidate_scope.py` 在常规产品岗位外，允许标题不是“产品”但 JD 具有明确 AI 产品工作职责的相邻岗位；排除纯研发、标注、行政等工作。保留原始官方职位总数与最终候选数的区别。
- **后续官方接入**：Kimi 已核验并自动接入。阿里当前校招批次已完成470条完整分页，但日常实习类型的字段识别与筛选范围仍在核查；字节日常实习的当前公开 API 在 GitHub Actions 返回 HTTP 405，因此尚未成功接入，不能推断没有岗位。
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
- 已在 GitHub Actions 核验当前批次 470 条职位、5页且无重复 ID。**混合校招不等于日常实习**，当前严格的岗位类型筛选尚无新增公开候选，需依据新的筛选诊断进一步核查字段。

### 新增小型 AI 公司官方源验证（2026-10-14）

- 生数科技：官网 `https://shengshu.jobs.feishu.cn/index/position/list`；官方最近一次核验为 108 条原始记录，招聘类型混合，**仅筛北京实习与 AI 产品相邻职位**。选择器 `feishu-shengshu`。
- 面壁智能：官网 `https://modelbest.jobs.feishu.cn/campus/m/position/list`；公开校园招聘目录观察到约 60 条原始记录，**不将校招正式岗算作实习**。选择器 `feishu-modelbest`。
- 两个新源均复用飞书公开 HTML/普通浏览器分页核验、唯一职位 ID 对账、失败保留快照机制。配置完成不代表实时采集成功，以 `source_attempts` 和 `source_audits` 为准。

### 阿里巴巴校园招聘公开会话 API 验证（2026-10-14）

- 新增 `alibaba_sources.py`、命令 `alibaba-public`，已核验官方 `https://campus-talent.alibaba.com/campus/position?batchId=100000760001`。中文地区网页初步观察到约470条原始职位，不代表北京日常 AI 产品实习数。
- 采用官网公开、匿名会话提供的标准页面 token，并调用同域职位列表 JSON；**不会绕过登录、验证码或风控验证**。2026-10-14 GitHub Actions 已成功抓取 470 条唯一 ID、5页；后续批次或接口行为可能改变，继续以实际审计结果为准。
- 先核对总数与所有唯一职位ID，再根据职位/招聘项目**明确的“实习”证据**、北京地点和 JD 中 AI 产品工作职责筛选。不能因为校招目录中出现“产品经理”就把正式应届岗位收为实习。
- 入口范围仅是当前 campus batchId，其他集团或独立招聘渠道不在成功声称范围。若实际 HTTP 拒绝、token 未提供或数据不完整则失败保留既有记录。

### 阶跃星辰来源发现（2026-10-14）

- 已确认阶跃星辰校招/实习的官方 Moka 入口 `https://app.mokahr.com/campus-recruitment/step/94905#/jobs`，并在企业覆盖页中改为直接打开这一招聘目录。
- 官网另有 StepStar 专项人才招聘入口，与一般校园实习的筛选范围不同。当前两个目录尚未完成独立分页/岗位性质验收，因此**只是来源入口，不算每日自动采集成功**。

### 阿里巴巴筛选诊断（2026-10-14）

- 完整抓取 470 条职位，只证明当前校招混合目录 API 可访问，不证明日常实习分类准确。本轮新增 `source_audits.阿里巴巴.screening_diagnostics`，记录真实字段名称、北京/实习判定数量与有限岗位样例，以找出候选为零的具体原因。
- 实习筛选不会依据业务描述中顺便出现“实习”就把正式校招岗归入实习，后续要先定位和验证正式的招聘项目/岗位性质字段。
