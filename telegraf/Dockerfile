FROM telegraf:1.14
LABEL maintainer="zhuy@grandomics.com"

RUN sed -i "s@http://ftp.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list


RUN apt update
RUN apt install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm requirements.txt