FROM python:3.8

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH
COPY ./.condarc /root/.condarc
RUN conda install -y -c bioconda -c conda-forge snakemake
RUN conda install -y -c bioconda biopython minimap2 git
COPY ./porechop /root/porechop
RUN apt update
RUN apt install -y g++ make supervisor
RUN cd /root/porechop && python3 setup.py install

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm requirements.txt
RUN mkdir /var/log/celery
COPY conf.d /etc/supervisor/conf.d/

CMD ["supervisord","-n"]