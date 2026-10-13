# 北京 AI 产品日常实习雷达

线上网页：https://a853255726-liu.github.io/ai-product-intern-radar/

**本版范围：仅北京、AI 产品及相邻产品方向的日常实习。** 不收录留用实习、应届实习、暑期实习、2028届专项和正式校招，也不将没有日常项目证据的普通实习混入公开页面。

## 数据规则

- 主数据库 jobs.json 保留旧候选，包括非日常与实习项目类型未核实的历史条目，用于审计和复核。
- daily_scope.py 定义 daily / non_daily / unverified；rebuild.py **只发布 daily**，expand_companies.py 输出的 jobs.csv 也采用同样口径。
- 依据：企业官网明确的日常项目或经过审查的具体日常实习岗位。毕业届次限制不等于岗位项目类别。第三方写明日常实习但未核实官网的线索仍标第三方待复核。
- 网站前端展示的是已确定检索范围的候选，不代表总市场岗位数或确认可投的 HC；页面自动分官网详情与待复核线索。

## 招聘来源及限制

| 来源 | 已核验范围与边界 |
|---|---|
| 腾讯 | 只监控北京“日常实习”（项目ID 104）；不再纳入应届、青云项目 |
| 美团 | 官方实习类别（日常实习）；岗位按产品方向筛查 |
| 小红书 | 校招混合职位完整分页核查，但未经日常项目确认的记录不进入新网页 |
| 京东 | intern 接口尝试；未证实日常类别者不入库 |
| 快手 | 校招接口实习类别包含“留用实习”；非日常留用岗已排除 |
| 米哈游 | 校招混合接口已全量核对，暂未找到符合条件的北京 AI PM 日常岗位 |
| 百度 | 官网页面人工核验日常实习岗位；列表全量 API 尚未完成 |
| 爱奇艺 | 官方日常实习入口，有北京 AI 产品岗位，列表未全面自动化 |
| 字节跳动 | 官网区分日常实习与 ByteIntern；目前 1 条第三方提供的日常实习岗位线索，官网详情未独立确认 |
| B站 | 官网职位动态请求依赖会话，现有静态采集不可靠 |
| 智谱、MiniMax | 招聘门户已查看，暂无已核实、符合北京 AI PM 日常实习的新增职位 |

未在已访问接口中发现符合要求岗位 ≠ 该公司没有岗位。岗位发布日期、更新时间和第三方首次收录时间分别处理。

## 自动更新与验证

GitHub Actions：.github/workflows/site.yml。每天北京时间约 09:17 自动检查，GitHub 定时任务可能延迟。无完整分页对账时不将结果写作成功，也不会误判下架。

本地运行：

    python -m pip install -r requirements.txt
    python refresh_sources.py --sources meituan xhs tencent jd kuaishou mihoyo
    python -m unittest discover -s tests -p 'test_*.py' -v
    python expand_companies.py
    python rebuild.py

更新页面前先看 data/last_errors.json 及 jobs.json 中的 source_audits。尊重招聘官网访问规则，不绕过登录、验证码或动态签名。
