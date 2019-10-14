# paper_trading
creat your own paper trading server


## 安装环境

### 安装Python

至少Python3.7以上

### 安装mongodb

1. 安装mongodb 4.2以上版本，且需要打开replica set（因为需要使用最新的session和transaction功能）。
2. 安装好mongo数据库后，建立在配置文件中配置的的数据库和数据用户，并给与dbOwner的权限
3. 之后将mongodb服务开启

### 安装依赖包
```bash
make install
```

## 配置

将.env.sample重命名为.env，修改其中的参数。参数说明见(settings.md)[settings.md]


## 使用
启动服务器
```bash
make server
```
开始模拟交易吧

## 感谢

[https://github.com/cao6237699/paper_trading.git]
