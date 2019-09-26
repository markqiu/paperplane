FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /beehive3

COPY ./app app
COPY pyproject.toml Makefile ./
RUN \
    # 安装beehive3环境
    pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    make install

CMD ["poetry", "run", "gunicorn","-k", "uvicorn.workers.UvicornWorker", "-c", "/gunicorn_conf.py", "app.main:app"]
