from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

PASSWORD_BD = os.getenv('PASSWORD_BD')

bd_pool = pool.SimpleConnectionPool(
    minconn=1,  
    maxconn=15, 
    dbname="railway", 
    user="postgres", 
    password= PASSWORD_BD, 
    host="autorack.proxy.rlwy.net", 
    port="36947"
)
