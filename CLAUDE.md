# Webhook Relay 项目说明

## 项目定位
Webhook 事件转发服务 —— 接收事件，异步投递给所有匹配的订阅者，支持失败重试和签名验证。

## 技术栈
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Mapped 声明式)
- **数据库**: SQLite (webhook_1.db，测试用 test.db)
- **HTTP 客户端**: httpx
- **定时任务**: APScheduler (BackgroundScheduler)
- **签名算法**: HMAC-SHA256

## 架构概览

```
Event(事件) ──POST /api/events──> BackgroundTasks ──> deliver_event()
                                                         │
                                          匹配 Subscription.event_types
                                                         │
                                              创建 Delivery 记录
                                                         │
                                          httpx.post → 订阅者 URL
                                                         │
                                              失败? → 指数退避重试
                                              APScheduler 每10秒扫描
```

## 核心数据模型 (app/models.py)
- **Subscription**: id, url, secret, event_types(JSON), is_active, description
- **Event**: id, event_type, payload(JSON)
- **Delivery**: id, event_id(FK), subscription_id(FK), status, attempt_count, response_code, error_message, max_attempts(默认5), next_attempt_at

## API 端点
| 模块 | 路径 | 说明 |
|------|------|------|
| subscriptions | `/api/subscriptions` | CRUD 订阅管理 |
| events | `/api/events` | 创建事件、查询事件列表/详情(含关联 deliveries) |
| deliveries | `/api/deliveries` | 查询投递记录(支持 status 过滤、分页)、手动触发重试 |

## 认证
- 所有 `/api/*` 端点需要 `X-API-Key` header
- API_KEY 从 `.env` 读取，缺失时服务拒绝启动
- 使用 `hmac.compare_digest` 防时序攻击

## 签名机制
投递 webhook 时，header 携带 `X-Relay-Signature: t={timestamp},v1={signature}`
- signing_payload = `"{timestamp}.{payload_json}"`
- signature = HMAC-SHA256(subscription.secret, signing_payload)

## 关键文件
| 文件 | 职责 |
|------|------|
| `app/main.py` | FastAPI 入口，lifespan 管理调度器启停 |
| `app/models.py` | SQLAlchemy 模型定义 |
| `app/schemas.py` | Pydantic 请求/响应 schema |
| `app/auth.py` | API Key 认证 |
| `app/database.py` | 数据库引擎、会话工厂 |
| `app/routers/subscriptions.py` | 订阅 CRUD |
| `app/routers/events.py` | 事件创建 + 详情查询 |
| `app/routers/deliveries.py` | 投递查询 + 手动重试 |
| `app/services/delivery.py` | 投递核心逻辑 + 签名计算 |
| `app/services/retry.py` | 扫描到期的 retrying 投递并重试 |
| `app/scheduler.py` | APScheduler 定时任务配置 |
| `test_receiver.py` | 本地测试用 webhook 接收方 (端口 9000) |
| `tests/` | pytest 测试，conftest.py 提供隔离数据库和认证 header |

## 运行方式
```bash
# 启动服务
uvicorn app.main:app --reload

# 运行测试
pytest tests/ -v

# 启动测试接收方
python test_receiver.py
```

## 环境变量 (.env)
- `API_KEY` — 必填，接口认证密钥
- `DATABASE_URL` — 可选，默认 sqlite:///./webhook_1.db

## 用户偏好
- 中文交流
- 求职项目，注重代码质量和工程规范
- 初次部署，需要详细讲解每步操作的含义

## 部署状态（2026-09-01）

### 已完成
- [x] 代码推送到 GitHub: `https://github.com/mushanruoshui/webhook-relay`
- [x] 阿里云 ECS 购买，Ubuntu 22.04，公网 IP: `47.109.128.96`
- [x] SSH 密钥登录（deploy 用户，禁用 root 登录和密码登录）
- [x] 防火墙 ufw 开放 22/80/443 端口
- [x] 服务器拉取代码到 `/opt/webhook-relay/`
- [x] Python 3.10 虚拟环境 + pip 依赖安装（补充了 python-dotenv）
- [x] `.env` 文件已创建在服务器（API_KEY 随机生成，已告知用户）
- [x] systemd 服务 `webhook-relay.service` 后台常驻运行
- [x] Nginx 反向代理 80端口 → localhost:8000
- [x] 验证通过：`curl http://47.109.128.96/` 返回 `{"message":"Webhook Relay is running"}`

### 未完成
- [ ] HTTPS（需要域名 + certbot，可选）
- [ ] 本地代码的 `.env` 需同步 `python-dotenv` 到 `requirements.txt`（服务器已改，本地未改）
- [ ] 服务器端代码更新流程（git pull + systemctl restart）还未实际使用过

### 服务器运维常用命令
```bash
# SSH 连接
ssh deploy@47.109.128.96

# 查看服务状态
sudo systemctl status webhook-relay

# 重启服务
sudo systemctl restart webhook-relay

# 查看实时日志
sudo journalctl -u webhook-relay -f

# 代码更新部署
cd /opt/webhook-relay
git pull
sudo systemctl restart webhook-relay
```

### 服务器关键路径
| 路径 | 说明 |
|------|------|
| `/opt/webhook-relay/` | 项目代码 |
| `/opt/webhook-relay/.venv/` | Python 虚拟环境 |
| `/opt/webhook-relay/.env` | 服务器环境变量（API_KEY） |
| `/etc/systemd/system/webhook-relay.service` | systemd 服务配置 |
| `/etc/nginx/sites-available/webhook-relay` | Nginx 配置 |
