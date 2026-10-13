# 北京 AI 产品实习机会雷达 V3.1

**快照日期：2026-10-13（北京时间）。** 已入库 58 条候选岗位，涉及 18 家企业；追踪名单共有 53 家，**不代表 53 家已采集完成**。默认队列为官网详情已核验且方向相关的岗位；以网页实时统计为准。

## 一、先体验网页

双击 `index.html`。它是内嵌岗位数据的单文件网页，使用浏览器即可筛选、收藏、标记投递、阅读岗位摘要和跳转企业官方职位链接。收藏/备注/已投递仅在浏览器本地保存，不会公开上传到 GitHub。

**重要：** 公司官网显示“投递”按钮不等于已确认 HC；“官网详情已核验”不等于 HR 已确认职位仍有空缺；第三方岗位必须再次向官网核实。发布日期、更新时间和首次发现时间不混用。2027 届正式校招不能当作实习。

## 二、部署到 GitHub Pages（需在 GitHub 网页做一次设置）

当前账号已连接 GitHub，但可用的 GitHub 集成**不能创建新仓库或修改 Pages 设置**，因此没有擅自使用其他已有项目的仓库，也没有声称已上线。

1. 登录 GitHub，访问 <https://github.com/new>，创建一个 **Public** 的独立**空仓库**，推荐名称 `ai-product-intern-radar`。不要勾选 Initialize with README / .gitignore / license，因为这些文件已随压缩包提供。
2. 将本压缩包解压，在 Windows 双击 `发布到GitHub.cmd`，按提示输入新仓库 URL，例如 `https://github.com/<your-username>/ai-product-intern-radar.git`。需要已安装 Git for Windows，并能使用你的 GitHub 凭据登录。程序不会 `--force` 覆盖远端。
3. 在新仓库的 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。打开 Actions → `北京 AI 产品实习雷达 · 更新与发布` → `Run workflow`。首次 `main` 推送也会触发发布。完成后，**真实网址以 Actions 部署输出的 page_url 为准**。

默认工作流 `.github/workflows/site.yml`：

- 每天 **北京时间约 09:17** 请求美团、小红书、腾讯和京东的指定公开职位接口。GitHub 定时调度可能延迟甚至失败，不能保证精确时间。
- 单个公司接口失败只保留它上次成功快照，记录错误，不会据此删除岗位；全部接口失败则本轮失败，网页保持原样。
- 严格核对分页报告总数和唯一 ID；避免把采集不完整当成无新岗位。
- 成功构建后，自动部署 `index.html`、`jobs.csv` 与 `company_coverage.csv`。包含 `push` 触发和同一工作流内完成部署，因此不依赖 GitHub Actions 机器人提交后再次触发其他工作流。
- 若 GitHub 平台 IP 被招聘官网拦截，自动刷新可能失败；**本地离线单元测试不能代替一次 GitHub 线上端到端验收。**

如果不想每日运行，删除 `site.yml` 里的 `schedule:` 与 `cron:` 两行，仅保留手动 `workflow_dispatch`。如需早晚多次刷新，可调整 `cron`，但应遵守各招聘站点访问规则。

## 三、手动运行采集

```bash
python -m pip install -r requirements.txt
python refresh_sources.py --sources meituan xhs tencent jd
python expand_companies.py
python rebuild.py
```

只检测不入库：`python refresh_sources.py --sources meituan xhs --audit-only`。

公司来源范围及注意事项：

| 企业 | 已实现 | 局限 |
|---|---|---|
| 美团 | 校招 API 中 `jobType=2` 的实习，逐页核对 | 非其他岗位入口/团队直招；返回的更新时间不等于首次发布 |
| 小红书 | 校园岗位 API 分页，区分项目类型 | 包含正式校招、实习专项和其他项目；需要按 JD 判断 |
| 腾讯 | `join.qq.com` 三类实习项目、北京筛选 | 是职位级入口，岗位可能对应多个招聘方向；不含其他招聘渠道 |
| 京东 | 官网 `type=intern` 分类 | 返回 0 **不能**证明京东没有任何实习，需要研究其他入口 |
| 爱奇艺、美图 | 这版新发现并人工核实的 3 条北京职位详情 | **尚未完成自动全量采集** |
| 字节、阿里、快手、百度、智谱、MiniMax 等 | 有部分线索/人工记录 | **还没有可靠的全量自动接口** |

不要尝试绕过登录、签名、验证码或访问限制。`source_audits` 保存上次成功核查，`source_attempts` 保存最新尝试状态；`data/last_errors.json` 记录最新错误。多家公司显示“待查”不等于没有招聘。

## 四、测试和源码

```bash
python -m unittest discover -s tests -p 'test_refresh.py' -v
python -m unittest discover -s tests -p 'test_deploy.py' -v
```

离线单元测试共 9 项，浏览器回归测试在制作阶段执行通过（需要本地额外安装 Playwright/Chromium）：`python tests/test_ui.py`。后者不是 GitHub Action 的必需依赖。

主要文件：`template.html` + `rebuild.py` 生成独立网页；`jobs.json` 为主数据库；`refresh_sources.py` 为公开接口适配与完整性校验；`expand_companies.py` 更新公司池和 CSV；`AUDIT.md` 记录当前已知风险。

## 五、关于持续扩大企业覆盖

**首先解决可重复性，再扩展覆盖率**。每家新增企业都要有明确的官网来源、项目/城市过滤、唯一 ID、完整分页核对、时效字段定义和失败处理。没有核验过的职位只能进入“待复核”，不能因为标题包含 AI 就标为适合投递，更不能把旧岗位当作最近 24 小时新发布。