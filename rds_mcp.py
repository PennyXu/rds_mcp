from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import os

load_dotenv()
# ========== 数据库连接 ==========
def get_db_connection():
    return psycopg2.connect(
         host=os.getenv("RDS_HOST"),
         port=int(os.getenv("RDS_PORT", 5432)),
         user=os.getenv("RDS_USER"),
         password=os.getenv("RDS_PASSWORD"),
         dbname=os.getenv("RDS_DATABASE"),
         cursor_factory=psycopg2.extras.RealDictCursor
     )


# ========== 安全检查 ==========
def is_safe_sql(sql, action):
    sql_upper = sql.upper().strip()
    forbidden = ['DROP', 'CREATE DATABASE', 'GRANT', 'REVOKE', 'ALTER USER', 'FLUSH', 'SHUTDOWN']
    for kw in forbidden:
        if kw in sql_upper:
            return False, f"禁止关键字: {kw}"
    if action == "select" and not sql_upper.startswith("SELECT"):
        return False, "只允许 SELECT"
    return True, "OK"

# ========== 初始化 MCP ==========
mcp = FastMCP("PostgreSQL Tool")

@mcp.tool()
def execute_sql(action: str, sql: str) -> dict:
    """执行数据库操作，操作类型有select、insert、delete、update_table、create_table、alter_table、truncate_table"""
    allowed = ["select", "insert", "delete", "update_table", "create_table", "alter_table", "truncate_table"]
    if action not in allowed:
        return {"error": f"不支持操作: {action}", "status": "failed"}

    safe, msg = is_safe_sql(sql, action)
    if not safe:
        return {"error": msg, "status": "failed"}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)

        if action == "select":
            results = cursor.fetchall()
            resp = {"result": results, "row_count": len(results), "status": "success"}
        else:
            conn.commit()
            resp = {"affected_rows": cursor.rowcount, "status": "success"}


        cursor.close()
        conn.close()
        return resp
    except Exception as e:
        return {"error": str(e), "status": "failed"}

# ========== 函数计算入口 ==========
def handler(event, context):
    return mcp.handle_http(event, context)

if __name__ == '__main__':
    mcp.settings.host = "0.0.0.0"
    mcp.run(transport = 'sse')
