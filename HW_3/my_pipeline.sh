#!/bin/bash

# Использование:
# ./my_pipeline.sh SRR39036158

set -uo pipefail

SAMPLE="$1"
REF="ref.fna"
INDEX="ref.mmi"
THRESHOLD=90

echo "Образец: $SAMPLE"

echo "[1/8] FastQC..."
./FastQC/fastqc ${SAMPLE}_1.fastq.gz ${SAMPLE}_2.fastq.gz
mv ${SAMPLE}_1_fastqc.html ${SAMPLE}_1.html
mv ${SAMPLE}_2_fastqc.html ${SAMPLE}_2.html
rm -f ${SAMPLE}_1_fastqc.zip ${SAMPLE}_2_fastqc.zip

echo "[2/8] Картирование minimap2..."
minimap2 -ax sr "$INDEX" ${SAMPLE}_1.fastq.gz ${SAMPLE}_2.fastq.gz > ${SAMPLE}.sam

echo "[3/8] SAM -> BAM..."
samtools view -bS ${SAMPLE}.sam > ${SAMPLE}.bam

echo "[4/8] samtools flagstat..."
samtools flagstat ${SAMPLE}.bam > ${SAMPLE}.flagstat.txt

echo "[5/8] Разбор %mapped..."
PCT=$(./parse_flagstat.sh ${SAMPLE}.flagstat.txt)
echo "    Картировано: ${PCT}%"

OK=$(awk -v p="$PCT" -v t="$THRESHOLD" 'BEGIN { print (p > t) ? 1 : 0 }')

if [ "$OK" -ne 1 ]; then
    echo "not OK (картировано <= ${THRESHOLD}%)"
    exit 1
fi
echo "OK (картировано > ${THRESHOLD}%)"

echo "[7/8] samtools sort..."
samtools sort ${SAMPLE}.bam -o ${SAMPLE}.sorted.bam

echo "[8/8] freebayes..."
freebayes -f "$REF" ${SAMPLE}.sorted.bam > ${SAMPLE}.vcf

echo "Finished"
