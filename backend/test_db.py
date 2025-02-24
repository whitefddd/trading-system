import psycopg2

try:
    conn = psycopg2.connect(
        dbname="trading_db",
        user="postgres",
        password="123456",
        host="localhost",
        port="5432"
    )
    print("数据库连接成功!")
    conn.close()
except Exception as e:
    print(f"连接错误: {e}") 