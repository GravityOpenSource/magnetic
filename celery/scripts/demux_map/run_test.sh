snakemake \
--snakefile /opt/scripts/demux_map/Snakefile \
--configfile /opt/scripts/demux_map/config.yaml \
--cores 2 \
--config \
input_fastq=/data/basecalled/20200313-COV0028-P5-PAE38849-NCP/PAE38849/fastq_pass/PAE38849_pass_c7324bab_1111.fastq \
output_path=/data/rampart_annotations/20200313-COV0028-P5-PAE38849-NCP-2 \
reference_file=/data/ncov2019/references.fasta \
guppy_barcoding_threads=2
