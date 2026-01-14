import psycopg2

conn = psycopg2.connect(
    host='ep-nameless-mountain-acjk6c0r-pooler.sa-east-1.aws.neon.tech',
    dbname='neondb',
    user='neondb_owner',
    password='npg_UEote2LiQbD9',
    sslmode='require'
)

cur = conn.cursor()
cur.execute('SELECT 1;')
print(cur.fetchone())

conn.close()