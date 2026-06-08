import os
import re
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import BranchPythonOperator

WORKDIR = os.path.expanduser("~/hw3")
SAMPLE = "SRR39036158"
THRESHOLD = 90.0

def check_mapping_quality(**context):
    """
    Разбирает файл *.flagstat.txt, достаёт процент картированных ридов
    и решает, по какой ветке идти дальше.
    Возвращает task_id следующей задачи.
    """
    flagstat_path = os.path.join(WORKDIR, f"{SAMPLE}.flagstat.txt")
    pct = None

    with open(flagstat_path) as f:
        for line in f:
            if " mapped (" in line and "primary" not in line and "properly" not in line:
                m = re.search(r"([0-9]+\.[0-9]+)%", line)
                if m:
                    pct = float(m.group(1))
                break

    print(f"Картировано: {pct}%")

    if pct is not None and pct > THRESHOLD:
        return "write_ok"
    return "write_not_ok"


with DAG(
    dag_id="quality_check_variant_calling",
    description="Оценка качества картирования + коллинг вариантов",
    start_date=datetime(2026, 6, 8),
    schedule=None,
    catchup=False,
) as dag:
    fastqc = BashOperator(
        task_id="fastqc",
        bash_command=(
            f"cd {WORKDIR} && "
            f"./FastQC/fastqc {SAMPLE}_1.fastq.gz {SAMPLE}_2.fastq.gz && "
            f"mv {SAMPLE}_1_fastqc.html {SAMPLE}_1.html && "
            f"mv {SAMPLE}_2_fastqc.html {SAMPLE}_2.html && "
            f"rm -f {SAMPLE}_1_fastqc.zip {SAMPLE}_2_fastqc.zip"
        ),
    )

    minimap2 = BashOperator(
        task_id="minimap2",
        bash_command=(
            f"cd {WORKDIR} && "
            f"minimap2 -ax sr ref.mmi {SAMPLE}_1.fastq.gz {SAMPLE}_2.fastq.gz "
            f"> {SAMPLE}.sam"
        ),
    )

    sam_to_bam = BashOperator(
        task_id="samtools_view",
        bash_command=f"cd {WORKDIR} && samtools view -bS {SAMPLE}.sam > {SAMPLE}.bam",
    )

    flagstat = BashOperator(
        task_id="samtools_flagstat",
        bash_command=f"cd {WORKDIR} && samtools flagstat {SAMPLE}.bam > {SAMPLE}.flagstat.txt",
    )

    check = BranchPythonOperator(
        task_id="check_mapping",
        python_callable=check_mapping_quality,
    )

    write_ok = BashOperator(
        task_id="write_ok",
        bash_command='echo "OK"',
    )

    write_not_ok = BashOperator(
        task_id="write_not_ok",
        bash_command='echo "not OK"',
    )

    samtools_sort = BashOperator(
        task_id="samtools_sort",
        bash_command=f"cd {WORKDIR} && samtools sort {SAMPLE}.bam -o {SAMPLE}.sorted.bam",
    )

    freebayes = BashOperator(
        task_id="freebayes",
        bash_command=f"cd {WORKDIR} && freebayes -f ref.fna {SAMPLE}.sorted.bam > {SAMPLE}.vcf",
    )

    finished = BashOperator(
        task_id="finished",
        bash_command='echo "Finished"',
    )

    fastqc >> minimap2 >> sam_to_bam >> flagstat >> check
    check >> write_ok >> samtools_sort >> freebayes >> finished
    check >> write_not_ok
