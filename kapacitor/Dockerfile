FROM kapacitor:1.5
LABEL maintainer="zhuy@grandomics.com"

RUN sed -i "s@http://ftp.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list