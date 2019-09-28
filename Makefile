HOST="127.0.0.1"
PORT=8000
TEST_PATH=./

.PHONY: server debug default test flake8

default:
	@echo "帮助:"
	@echo "\tmake server [host] [port] 启动服务器"
	@echo "\tmake debug  [host] [port] 启动调试服务器"
	@echo "\tmake test                 运行单元测试"
	@echo "\tmake coverage             运行coverage检查"
	@echo "\tmake install              用poetry安装环境（注意是安装到虚拟python环境下）"
	@echo "\tmake init_db              初始化数据库"
	@echo "\tmake doc                  启动mkdocs文档服务器"
	@echo "\tmake build_doc            编译mkdocs文档"
	@echo "\tmake build_image          编译docker image"
	@echo "\tmake format_code          用black美化代码"

server:
	poetry run uvicorn paperplane.main:app --host=$(HOST) --port=$(PORT) --log-level=info

debug:
	poetry run uvicorn paperplane.main:app --host=$(HOST) --port=$(PORT) --reload --debug --log-level=debug

test:
	PYTHONPATH=. poetry run pytest tests

coverage:
	poetry run pytest --cov=app tests/

install:
	curl http://cxan.chong.so:88/packages/ta-lib-0.4.0-src.tar.gz -o ta-lib-0.4.0-src.tar.gz
	tar -xzvf ta-lib-0.4.0-src.tar.gz
	cd ta-lib && ./configure --prefix=/usr/local && make && make install && cd .. && rm -rf ta-lib
	poetry update
	poetry install

update:
	poetry update

init_db:
	poetry run sh -c "PYTHONPATH=. python ./scripts/init_db.py"

doc:
	poetry run mkdocs serve

build_doc:
	poetry run mkdocs build

build_image:
	poetry run docker build -t beehive3 .

format_code:
	poetry run black .

