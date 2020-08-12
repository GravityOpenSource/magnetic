rule parse_mapping:
    input:
         fastq=input_fastq,
         mapped=minimap2_paf,
         summary=guppy_barcoding_summary
    params:
          path_to_script=workflow.current_basedir,
          min_identity=minimum_identity
    output:
          report_csv
    shell:
         """
         python {params.path_to_script}/parse_paf.py \
         --paf {input.mapped:q} \
         --report {output:q} \
         --fastq {input.fastq:q} \
         --summary {input.summary:q} \
         {params.min_identity} 
         """
         #produces a csv report
