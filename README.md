# get.py 描述

自用脚本，centos7.3下测试通过。

python通过shell命令获取cpu 内存 磁盘io 网络使用量 网络连接数，其中io数据通过线程后台持续获取。

整个脚本每隔1秒提交一次。

数据格式为json

post提交
