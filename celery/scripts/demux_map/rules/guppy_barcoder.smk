rule guppy_barcoder:
    input:
         input_fastq
    params:
          barcoding_input_path=expand("{guppy_barcoding_path}/input", guppy_barcoding_path=guppy_barcoding_path),
          barcoding_output_path=expand("{guppy_barcoding_path}/output", guppy_barcoding_path=guppy_barcoding_path),
    threads:
           guppy_barcoding_threads
    output:
          temp(guppy_barcoding_summary)
    shell:
         """
         mkdir -p {params.barcoding_input_path} && \
         cp {input:q} {params.barcoding_input_path} && \
         guppy_barcoder -i {params.barcoding_input_path} -s {params.barcoding_output_path} -t {threads} -z && \
         cp {params.barcoding_output_path}/barcoding_summary.txt {output:q} && \
         rm -r {guppy_barcoding_path}
         """
