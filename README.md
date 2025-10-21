# PostgreSQL MCP 工具

一个基于 FastMCP 的 PostgreSQL 数据库操作工具，为 AI 助手提供安全的数据库访问能力。

## 功能特性

- 🤖 **AI 友好** - 专为 AI 助手设计的数据库工具接口
- 🔐 **安全执行** - 内置 SQL 安全检查，防止危险操作
- 📊 **多操作支持** - 支持查询、插入、删除、更新等多种数据库操作
- 🛡️ **权限控制** - 限制危险关键字和操作类型，保护数据库安全
- 🔌 **MCP 协议** - 基于 Model Context Protocol，可与 Claude、GPTs 等 AI 系统无缝集成

## 技术架构

```
AI 助手 (Claude/GPTS等)
    ↓ MCP 协议
PostgreSQL MCP 工具
    ↓ 安全检查
PostgreSQL 数据库
```

## 安装运行

### 前置要求
- Python 3.8+
- PostgreSQL 数据库
- 支持 MCP 协议的 AI 助手（如 Claude Desktop）

### 启动服务

```bash
# 进入项目目录
cd examples/snippets/clients

# 使用 SSE 传输启动服务（适用于 Claude Desktop）
uv run server fastmcp_quickstart stdio
```

## 环境配置

在项目根目录创建 `.env` 文件，配置数据库连接信息：

```env
RDS_HOST=your_database_host
RDS_PORT=5432
RDS_USER=your_username
RDS_PASSWORD=your_password
RDS_DATABASE=your_database_name
```

## AI 集成示例

### MCP服务配置文件

```json
{
"mcpServers":{
"rds_interact": {
    "url":"http://101.37.26.74:8000/sse",
    "type":"sse/streamableHttp" 
}
}
}
```

### 在 Cherry Studio Client 中配置方法

```json
{
  "mcpServers": {
    "mcp-OGZjNzFjMjJmZjFk": {
      "type": "sse",
      "isActive": true,
      "name": "阿里云百炼_rds_interact",
      "baseUrl": "https://dashscope.aliyuncs.com/api/v1/mcps/mcp-OGZjNzFjMjJmZjFk/sse",
      "headers": {
        "Authorization": "Bearer ${DASHSCOPE_API_KEY}"
      }
    }
  }
}
```

### AI 使用场景

AI 助手可以通过自然语言操作数据库：

```
用户: "帮我查询所有年龄大于18岁的用户"
AI: 使用 execute_sql 工具执行: SELECT * FROM users WHERE age > 18

用户: "在products表中添加一个新商品"
AI: 使用 execute_sql 工具执行: INSERT INTO products (name, price) VALUES ('新商品', 99.9)
```

## 工具功能

### execute_sql 工具

AI 助手通过此工具执行安全的数据库操作。

**支持的操作类型：**
- `select` - 数据查询（只读）
- `insert` - 插入新数据
- `delete` - 删除数据
- `update_table` - 更新现有数据
- `create_table` - 创建新表
- `alter_table` - 修改表结构
- `truncate_table` - 清空表数据

**安全特性：**
- 自动拦截危险操作（DROP、GRANT 等）
- 查询操作限制为 SELECT 语句
- 完整的错误处理和日志记录

## 安全机制

### 禁止的关键字
```python
['DROP', 'CREATE DATABASE', 'GRANT', 'REVOKE', 'ALTER USER', 'FLUSH', 'SHUTDOWN']
```

### 操作限制
- SELECT 操作必须以 `SELECT` 开头
- 所有操作都经过关键字过滤
- 数据库连接使用只读权限用户（推荐）

## 部署选项

### 1. SSE 传输（推荐用于 AI 集成）
```python
mcp.run(transport='sse')
```

### 2. HTTP 传输（Web 应用）
```python
def handler(event, context):
    return mcp.handle_http(event, context)
```

### 3. Stdio 传输（命令行工具）
```bash
uv run server fastmcp_quickstart stdio
```

## 响应格式

### 成功响应
```json
{
  "result": [...],
  "row_count": 5,
  "status": "success"
}
```

### 错误响应
```json
{
  "error": "SQL 语法错误",
  "status": "failed"
}
```

## 最佳实践

### 对于 AI 开发者
1. **清晰的提示词**：在系统提示中说明可用的数据库操作
2. **错误处理**：教导 AI 如何解析和处理数据库错误
3. **查询优化**：鼓励 AI 使用限制条件避免大数据量查询

### 对于数据库管理员
1. **权限分离**：为 AI 工具创建专用数据库用户
2. **备份策略**：定期备份重要数据
3. **监控日志**：审查 AI 执行的 SQL 语句

## 故障排除

### 常见问题
1. **连接失败**：检查 .env 文件配置和网络连接
2. **权限错误**：验证数据库用户权限
3. **SQL 被拦截**：检查是否包含禁止的关键字

### 日志调试
启用详细日志来跟踪 AI 的数据库操作：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展开发

您可以基于此模板扩展更多数据库工具：

```python
@mcp.tool()
def get_table_schema(table_name: str) -> dict:
    """获取表结构信息 - 为 AI 提供数据库元数据"""
    # 实现代码...
```
