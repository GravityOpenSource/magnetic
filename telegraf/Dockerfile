FROM telegraf:1.14
LABEL maintainer="zhuy@grandomics.com"

RUN sed -i "s@http://ftp.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apt update
RUN apt install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm requirements.txt
COPY minknow /opt/minknow
RUN mkdir /opt/grpc
RUN mkdir /opt/grpc/minknow
RUN cd /opt && python3 -m grpc_tools.protoc \
    --python_out=/opt/grpc \
    --grpc_python_out=/opt/grpc \
    -I . \
    minknow/rpc/*.proto
RUN rm -rf /opt/minknow