# Database config for H2 and Oracle connection

# Toggle this flag to switch between H2 and Oracle
USE_ORACLE = True  # Set to False to use H2, True to use Oracle

# Oracle connection details
ORACLE_USER = "system"
ORACLE_PASSWORD = "pwd"
ORACLE_HOST = "127.0.0.1"
ORACLE_PORT = 1521
ORACLE_SERVICE_NAME = "XE"
ORACLE_DSN = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE_NAME}"

# Path to your downloaded H2 JAR file
H2_JAR_PATH = r"C:\Users\rohit\OneDrive\Desktop\workspace\global_search\code\h2-2.3.232.jar"
JDBC_URL = "jdbc:h2:tcp://localhost:9092/~/test;MODE=Oracle"

# DB credentials (H2 default)
DB_USER = "sa"
DB_PASSWORD = ""
