snakemake \
--snakefile Snakefile \
--configfile config.yaml \
--config \
input_fastq=/project/zhuying/data/basecalled/20200212-COV0003-P5-PAE36018/fastq_pass/PAE36018_pass_96513dd9_1468.fastq \
output_path=/data/personal/zhuying/github/tigk/output \
references_file=/data/ncov2019/references.fasta \
guppy_barcoding_threads=2