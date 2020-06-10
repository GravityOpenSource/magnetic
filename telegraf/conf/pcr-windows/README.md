### PCR 文件监控

#### 环境依赖
* windows (7、8、10)
* python3.6+

#### 安装方式
1. 下载telegraf windows平台程序包
2. 将`telegraf.exe`文件复制到`C:/ProgramData/Telegraf/`目录下
3. 将本目录下的配置文件复制到`C:/ProgramData/Telegraf/`目录下
4. 将`scripts/pcr-windows/`目录下的脚本文件复制到`C:/ProgramData/Telegraf/scripts/`目录下
5. 修改配置文件`telegraf.env`
6. 执行```telegraf.exe --service install --config C:\ProgramData\Telegraf\telegraf.conf --config-directory C:\ProgramData\Telegraf\telegraf.d\```安装telegraf服务
7. 执行```python reg.py```将环境变量注册到服务中
8. 执行```telegraf.exe --service start```启动服务