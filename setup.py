from setuptools import setup

setup(
    name="fastapi-upload-app",
    version="0.0.1",
    author="Alexander Kosove",
    author_email="alexander.kosove@gmail.com",
    description="FastAPI Upload tool with MinIO storage for storing images.",
    install_requires=[
        "fastapi[all]==0.78.0",
        "pydantic==1.9.1",
        "uvicorn==0.17.6",
        "sqlalchemy==1.4.39",
        "minio==7.1.9",
        "pytest==7.1.2",
        "environs==9.5.0",
        "passlib[bcrypt]==1.7.4",
        "python-jose[cryptography]==3.3.0",
    ],
    scripts=["app/main.py"]
)
