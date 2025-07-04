import jaydebeapi
import oracledb
from config import db_config


def get_db_connection():
    if getattr(db_config, 'USE_ORACLE', False):
        # Oracle connection
        return oracledb.connect(
            user=db_config.ORACLE_USER,
            password=db_config.ORACLE_PASSWORD,
            dsn=db_config.ORACLE_DSN
        )
    else:
        # H2 connection
        return jaydebeapi.connect(
            "org.h2.Driver",
            db_config.JDBC_URL,
            [db_config.DB_USER, db_config.DB_PASSWORD],
            db_config.H2_JAR_PATH
        )
