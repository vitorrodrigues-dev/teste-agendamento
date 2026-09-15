import oracledb

import config


def get_connection():
    if not all([config.ORACLE_USER, config.ORACLE_PASSWORD, config.ORACLE_DSN]):
        raise RuntimeError(
            "Configuracao Oracle incompleta. Verifique se o arquivo .env existe "
            "(copie .env.example) e contem ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN."
        )

    return oracledb.connect(
        user=config.ORACLE_USER,
        password=config.ORACLE_PASSWORD,
        dsn=config.ORACLE_DSN,
    )
