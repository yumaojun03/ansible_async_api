# 简介
---

基于Ansible2.0 开发一个异步高效的API系统， 供其他系统调用。

# 组件
---

+ Ansible 注意版本2.0
+ Tornado 异步就靠他了
+ MongoDB 数据存储

# 布局
---

+ handlers

tornado handlers 目录, 当import envronment　模块时，
这个目录下面的所有文件都将加入到PYTHONPATH环境变量.


+ libs

存储Python包的目录，那些不是Tornado request handlers的模块文件都放在这里
这个目录下面的所有文件都将加入到PYTHONPATH环境变量.

+ logconfig

python logging的配置文件存放目录,　具体可以参考python logging官方说明，
这个包主要包含一个initalize_logging的方法，用此方法可以实例华一个真正的logger实例
在settings.py　文件用此来配置日志

注意root logger在settings.py中就已经设置好了, app中仅需要调用他的子logger即可使用
具体方法如下：
```
#!python
import logging
logger = logging.getLogger('five.' + __name__)
```

+ requirements

pip 的requirements文件存放目录，总共分成3类, 

1. common.txt 开发和生产环境都需要的包
2. devolop.txt 开发环境依赖的包
3. production.txt 生产环境依赖的包

+ environment.py

修改Python运行时的PYTHONPATH环境变量，这个模块会在settings.py的顶层被导入，以确保handlers和libs下的模块能被python找到。

+ app.py

Tornado app　入口模块，　用于启动 Tornado Server.

+ settints.py

app 配置模块

+ urls.py

app 路由模块







