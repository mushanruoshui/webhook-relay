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
