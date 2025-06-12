import jaydebeapi
from config import db_config


def get_db_connection():
    conn = jaydebeapi.connect(
        "org.h2.Driver",
        db_config.JDBC_URL,
        [db_config.DB_USER, db_config.DB_PASSWORD],
        db_config.H2_JAR_PATH
    )
    return conn
