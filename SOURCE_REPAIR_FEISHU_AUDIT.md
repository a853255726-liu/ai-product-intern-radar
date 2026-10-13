# 2026-10-13 官方职位接口修复与飞书招聘适配器

此文档记录已验证范围、分页对账、访问限制。**不能把接口存在当作所有岗位都能投递**。

## 第一步：修复百度 / 京东 / 腾讯的覆盖

| 来源 | 正确方法 | 公开查询范围 | 验证结果 |
| --- | --- | --- | --- |
| 京东 | POST `campus.jd.com/api/wx/position/page?type=internship`，`pageIndex` 从 0 开始 | 京东校园招聘中的实习类型，所有城市 | 102 条，三页 50/50/2，102 唯一 `publishId`，91 条的岗位需求地址包含北京；原 `type=intern` 返回0是**错误参数** |
| 百度 | POST `talent.baidu.com/httservice/getPostListNew`，使用 `application/x-www-form-urlencoded`，字段 `recruitType=INTERN&workPlace=1100&postType=2&curPage=N&pageSize=10` | 北京实习、产品类别（不含其它类别） | 184 条，19 页（10×18 +4），184 唯一 `postId`；此前只读到首页是编码及分页方式不匹配 |
| 腾讯 | `POST join.qq.com/api/v1/position/searchPosition`，不同 `projectMappingIdList` | 北京日常实习104 / 应届实习2 / 青云计划20 | 分别25 / 51 / 134 条（对应各自接口），104保持每天自动采集；2属于应届项目，本版不默认并入；青云计划20的134条主要是模型/算法科研课题，没有明确产品经理实习，不并入产品候选 |

> 腾讯数字是通道范围内职位计数，不能简单相加视为岗位或HC数量。京东长期存在泛招聘岗位，一个 `publishId` 可能包含大量部门地点与需求实例，需保留唯一主岗位ID，不能按每个需求实例虚增岗位数。

代码：`refresh_sources.py`，离线回归测试：`tests/test_official_sources_v4.py`。自动采集失败时保持旧候选，不推断职位下架。

## 第二步：飞书招聘通用适配器

复用配置：`feishu_sources.py` 支持零一万物、MiniMax、智谱、RealAI 的 `*.jobs.feishu.cn` 官方门户。只采公开展示页面，无需账号、签名和企业系统权限。检查页面广告总数、逐页唯一 ID、北京与实习类型以及职位职责，才允许纳入候选。

- `requests` 公开 HTML/SSR 优先；页面只返回客户端空框架时，尝试标准 Chromium 渲染公开职位列表。
- 浏览器不调用受保护的内部 API、不破解签名、不绕过验证码或登录。不满足完整性校验就中止该来源。
- 首轮 GitHub Actions 中仅用直接 HTML 时，零一万物、MiniMax、智谱、RealAI 都因缺少服务器渲染职位数而失败，保留原有经人工核查数据。
- 浏览器回退的 CI 可用性需要单独以 GitHub Actions 最新运行记录确认，不能只凭离线通过声明成功。
- 零一万物在浏览器场景下已经人工核对 51 个官方职位（6页）；MiniMax 与智谱的官网门户还存在不同招聘项目/渠道，不应把门户的全量岗位当作实习。RealAI 官网招聘目录有11条的人工记录。

**更新口径**：优先北京日常实习、兼顾其他实习，排除明确仅面向应届毕业生的招聘；只纳入真正与AI产品、Agent、平台、策略和用研相关的职位。发布日期、岗位首次发现日和接口最后核验日严格区分。
