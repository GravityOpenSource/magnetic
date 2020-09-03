FROM kapacitor:1.5
LABEL maintainer="zhuy@grandomics.com"

RUN sed -i "s@http://ftp.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@http://repo.huaweicloud.com@g" /etc/apt/sources.list

#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
#RUN /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda
#ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
#ENV PATH /opt/conda/bin:$PATH
#COPY ./.condarc /root/.condarc
#RUN conda install -y -c bioconda -c conda-forge snakemake
#RUN conda install -y -c bioconda biopython minimap2 git
#COPY ./porechop /root/porechop
#RUN apt update
#RUN apt install -y g++ make
#RUN cd /root/porechop && python3 setup.py install
