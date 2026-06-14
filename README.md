# CROWN-seq-lite mapping pipeline

## Background

It is very difficult in mapping CROWN-seq reads to snRNA and snoRNA. It is because there are many copies of snRNA and snoRNA in the genome. Many of the copies are identical, or only differ to each other of a few nucleotides. In CROWN-seq, it is more challenging, because, A nucleotides are converted into G nucleotides. As a result, if the standard CROWN-seq mapping pipeline [https://github.com/jhfoxliu/CROWN-Seq] was applied, those reads mapped to the snRNA and snoRNAs were removed in the final alignment results due to multiple alignment.

To handle this problem, while analyzing CROWN-seq-lite reads, we use a alternative strategy: we first map the reads to transriptome, which contain all possible snRNA and snoRNA sequences. We then keep the reads mapping to isoforms of the **same** type of snRNA/snoRNA, assigning them to one type of snRNA or snoRNA. Notably, we manually generated a transcript id to snRNA/snoRNA type database to perform this mapping.

## Workflow

0. Prepare metadata

(1) Download the `.genelist` and `.database.txt` files.

(2) Make a bowtie2 index of the A-to-G converted transcriptome.

`python fasta_a2g.py {fasta_in} > {fasta_A2G_out}` # Here we used the one from gencode M35.

`bowtie2-build {fasta_A2G_out} {fasta_A2G_out_index_prefix}`

1. Run regular read QC according to the standard GLORI/CROWN-seq mapping pipeline [https://github.com/jhfoxliu/CROWN-Seq].

2. In silico convert the reads

`python fastq_a2g.py {read1} > {read1.A2G}`

`python fastq_t2c.py {read2} > {read2.A2G}`

3. Mapping

`bowtie2 -x {fasta_A2G_out_index_prefix} -1 {read1.A2G} -2 {read2.A2G} -p {threads} --no-unal --norc --no-mixed --no-discordant -k 20 --end-to-end -S {SAM_out}`

4. Recover the nucleotides 

`python Bam_recovery_A2G_PE.py -i {BAM_out} -o {BAM_recovered} -o {BAM_out} -f {read1} -r {read2}` 

`samtools sort -o {BAM_recovered_sorted} {BAM_recovered}`

`samtools index {BAM_recovered_sorted}`

5. Generate the conversion rate table

`python filter_snRNA_mapping_output.py -i {BAM_recovered_sorted} -o {snRNA_snoRNA_m6Am_csv} --db {database} --genelist {genelist}`

## Contact

Please email Jianheng Liu (Fox) if you have any question:

[jil4026@med.cornell.edu] or [jhfoxliu@gmail.com]

## License

MIT.