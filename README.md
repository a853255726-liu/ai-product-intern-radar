# 北京 AI 产品实习机会雷达 V3.1

**快照日期：2026-10-13（北京时间）。** 已入库 58 条候选岗位，涉及 18 家企业；追踪名单共有 53 家，**不代表 53 家已采集完成**。默认队列为官网详情已核验且方向相关的岗位；以网页实时统计为准。

## 一、先体验网页

双击 `index.html`。它是内嵌岗位数据的单文件网页，使用浏览器即可筛选、收藏、标记投递、阅读岗位摘要和跳转企业官方职位链接。收藏/备注/已投递仅在浏览器本地保存，不会公开上传到 GitHub。

**重要：** 公司官网显示“投递”按钮不等于已确认 HC；“官网详情已核验”不等于 HR 已确认职位仍有空缺；第三方岗位必须再次向官网核实。发布日期、更新时间和首次发现时间不混用。2027 届正式校招不能当作实习。

## 二、GitHub Pages 发布状态（需要仓库所有者完成一次设置）

代码已上传到 [a853255726-liu/ai-product-intern-radar](https://github.com/a853255726-liu/ai-product-intern-radar)，而且首次 GitHub Actions 中的 Python 单元测试、数据重建和网页检查已成功。

**目前网站尚未上线。** 初次自动部署在 `Configure Pages` 时报错 `Get Pages site failed`，因为 GitHub Pages 尚未为本仓库启用。

当前仓库是 **Private**。按照 GitHub 官方政策，GitHub Free 账户需要将 Pages 所在仓库设成 Public；GitHub Pro/Team 等支持从 Private 仓库发布 Pages。不要为了公开网站把任何私人记录或密钥写入仓库，网页仅存放公开招聘数据。

请打开仓库设置，完成：

1. 如果使用 GitHub Free：`Settings → General → Danger Zone → Change repository visibility → Make public`。此操作会公开仓库全部内容，请先确认。
2. `Settings → Pages → Build and deployment → Source`，选择 **GitHub Actions**。
3. `Actions → Beijing AI Product Internship Radar → Run workflow`，重新运行。进入该执行记录确认 **Deploy Pages** 步骤成功。
4. 只有部署成功后，网站才可能出现在 `https://a853255726-liu.github.io/ai-product-intern-radar/`；具体请以 Pages 设置里的 **Visit site** 为准。

更新日程：`.github/workflows/site.yml` 每天 UTC 01:17（北京时间约 09:17）检查指定招聘接口。首次 `push` 只构建和部署，不重新采集；定时或手动执行会调用采集脚本。GitHub Actions 运行可能延迟，目标官网也可能限制 GitHub 云 IP，因此无法保证每次自动更新都成功。

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