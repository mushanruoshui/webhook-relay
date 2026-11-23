from sqlalchemy import create_engine, inspect, text

from app.database import DATABASE_URL

from sqlalchemy import create_engine, inspect, text

from app.database import DATABASE_URL

INDEX_NAME = "ix_deliveries_status_next_attempt"
TABLE = "deliveries"
COLUMNS = ("status", "next_attempt_at")


def main():
    engine = create_engine(DATABASE_URL)
    dialect = engine.dialect.name
    print(f"目标库: {DATABASE_URL}  (dialect={dialect})")

    inspector = inspect(engine)
    if TABLE not in inspector.get_table_names():
        print(f"表 {TABLE} 不存在，无需处理（首次启动会自动建表并带上索引）")
        return

    existing = {idx["name"] for idx in inspector.get_indexes(TABLE)}
    if INDEX_NAME in existing:
        print(f"索引 {INDEX_NAME} 已存在，跳过")
        return

    if dialect == "sqlite":
        ddl = f'CREATE INDEX IF NOT EXISTS {INDEX_NAME} ON {TABLE} ({", ".join(COLUMNS)})'
    else:
        # MySQL 不支持 CREATE INDEX IF NOT EXISTS
        ddl = f'CREATE INDEX {INDEX_NAME} ON {TABLE} ({", ".join(COLUMNS)})'

    with engine.begin() as conn:
        conn.execute(text(ddl))
    print(f"已创建索引 {INDEX_NAME} ({', '.join(COLUMNS)})")

    if dialect == "sqlite":
        with engine.connect() as conn:
            plan = conn.execute(text(
                f"EXPLAIN QUERY PLAN SELECT * FROM {TABLE} "
                f"WHERE status = 'retrying' AND next_attempt_at <= '2030-01-01'"
            )).fetchall()
        print("EXPLAIN QUERY PLAN:")
        for row in plan:
            print("   ", row[-1])


if __name__ == "__main__":
    main()
