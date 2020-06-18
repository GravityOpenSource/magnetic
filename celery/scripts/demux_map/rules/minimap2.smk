rule minimap2:
    input:
         fastq=input_fastq,
         ref=reference_file
    output:
          temp(minimap2_paf)
    shell:
         """
         minimap2 -x map-ont \
         --secondary=no \
         --paf-no-hit \
         --cs \
         {input.ref:q} \
         {input.fastq:q} > {output:q}
         """
