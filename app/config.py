from environs import Env

env = Env()
env.read_env()

DATABASE_URL = env.str("DATABASE_URL")

SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = env.str("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES")

MINIO_SERVER_URL = env.str("MINIO_SERVER_URL")
MINIO_ACCESS_KEY = env.str("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env.str("MINIO_SECRET_KEY")
