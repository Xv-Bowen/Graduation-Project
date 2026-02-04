# 毕业设计 - 老年心理健康支持网站（银龄心语）

本项目为本地演示用途，面向老年人心理健康科普与咨询辅助。

**快速启动**
0. 一键启动（推荐；会自动创建 `.venv`、安装依赖、生成 `.env`、迁移数据库并启动服务）：
   ```bash
   python3 scripts/dev.py
   ```
   - 首次运行会生成 `.env`，请打开 `.env` 填写 `DEEPSEEK_API_KEY`（否则 AI 对话不可用）。
   - 可选：如需补全量表/机构/热线/放松方法等演示数据，可加 `--seed`：
     ```bash
     python3 scripts/dev.py --seed
     ```
1. 创建并激活虚拟环境（建议使用 `.venv`；若不存在可自行创建）。  
   示例：`python3 -m venv .venv`
2. 安装依赖：
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```
3. 配置环境变量：
   ```bash
   cp .env.example .env
   ```
   然后编辑 `.env`：将 `DEEPSEEK_API_KEY` 替换为你自己的 Key（不使用 AI 可留空）。
4. 执行数据库迁移：
   ```bash
   .venv/bin/python manage.py migrate
   ```
5. 可选：初始化示例数据（文章、量表、机构/热线、放松方法）：
   ```bash
   .venv/bin/python manage.py seed_data
   ```
6. 可选：创建管理员账号：
   ```bash
   .venv/bin/python manage.py createsuperuser
   ```
7. 启动服务：
   ```bash
   .venv/bin/python manage.py runserver 127.0.0.1:8000
   ```
8. 访问：`http://127.0.0.1:8000/`

**功能概览**
1. 知识库：文章分类、关键词搜索、适老化字体调节、朗读；列表支持分页。
2. AI 陪伴：登录后可使用 DeepSeek 对话，含基础风险关键词提示。
3. 人工咨询：提交咨询申请与后台管理。
4. 心理工具：
   1. 心理自测（PHQ-9/GAD-7/ISI 等示例量表）
   2. 机构与热线（本地/本省/全国）
   3. 放松疗法提醒与练习记录

**交互说明（无整页刷新）**
- 页面主内容区使用 HTMX 做局部切换（点击导航/列表/分页通常不会整页刷新）。
- 登录、注册、提交咨询、提交量表、后台更新等 POST 表单仍保持整页提交（更稳定、便于消息提示与跳转）。
- 若网络环境无法加载 HTMX CDN，页面会自动退化为普通跳转（仍可用）。

**AI 配置**
- 使用 DeepSeek 的 OpenAI 兼容接口。
- 在 `.env` 中设置 `DEEPSEEK_API_KEY` 后，登录用户可使用 AI 对话。
- 未配置 Key 时，AI 会提示服务未配置或不可用（演示可不填）。

**常用配置项（.env）**
- `DJANGO_SECRET_KEY`：生产必须替换。
- `DJANGO_DEBUG`：`1/0`。
- `DJANGO_ALLOWED_HOSTS`：逗号分隔，如 `localhost,127.0.0.1`。
- `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` / `DEEPSEEK_MODEL_R`：AI 服务配置。
- `AI_MAX_TOKENS`：AI 回复最大 token（默认 1024）。
- `AI_TIMEOUT`：AI 请求超时（秒）。
- `AI_MAX_INPUT_CHARS`：单条消息长度上限（字符数）。
- `PAGINATION_PAGE_SIZE`：列表分页大小（默认 10）。
- `LOCAL_PROVINCE` / `LOCAL_CITY`：机构/热线页面默认地区显示。

**管理后台**
- 地址：`http://127.0.0.1:8000/admin/`
- 可管理文章、咨询记录、AI 记录、量表、机构与放松数据。

**迁移与索引**
- 项目包含用于演示性能的索引迁移（文章、咨询、AI 记录、量表等常用查询字段）。
- 仅在你修改 `core/models.py` 后才需要再运行：
  ```bash
  .venv/bin/python manage.py makemigrations
  .venv/bin/python manage.py migrate
  ```

**测试**
```bash
.venv/bin/python manage.py test
```

**日志清理**
- 已提供每日 0:00 自动清理方案（macOS LaunchAgent）。
- 清理脚本：`scripts/clear_chatlog.sh`
- LaunchAgent：`scripts/launchd/com.gradproject.chatlog.cleanup.plist`
- 注意：`com.gradproject.chatlog.cleanup.plist` 里的路径需要替换为你本机项目的绝对路径（`/ABSOLUTE/PATH/TO/GRADUATION_PROJECT`）。
- 安装（只需一次）：
  ```bash
  cp scripts/launchd/com.gradproject.chatlog.cleanup.plist ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.gradproject.chatlog.cleanup.plist
  ```
- 手动清理：
  ```bash
  .venv/bin/python manage.py clear_chatlog
  ```

**说明**
- 数据库为 SQLite：仓库包含已脱敏的演示数据库 `db.sqlite3`，包含文章/分类/量表/机构与热线/放松方法等**非敏感演示材料**（已移除用户/会话/AI 聊天/咨询等隐私数据）。
  - 如需从零开始：删除 `db.sqlite3` 后执行 `migrate`，再运行 `seed_data` 生成示例内容。
- 本系统提供心理健康科普与咨询参考，不替代医学诊断或紧急援助。
