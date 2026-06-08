1. Ссылка на загруженные прочтения E.coli из NCBI SRA: https://www.ncbi.nlm.nih.gov/sra/SRX33787154
2. Скрипт на bash с реализованным алгоритмом в файле `my_pipeline.sh`
3. Результат команды samtools flagstat:
```txt
50919639 + 0 in total (QC-passed reads + QC-failed reads)
49617536 + 0 primary
0 + 0 secondary
1302103 + 0 supplementary
0 + 0 duplicates
0 + 0 primary duplicates
43682078 + 0 mapped (85.79% : N/A)
42379975 + 0 primary mapped (85.41% : N/A)
49617536 + 0 paired in sequencing
24808768 + 0 read1
24808768 + 0 read2
35728512 + 0 properly paired (72.01% : N/A)
41284414 + 0 with itself and mate mapped
1095561 + 0 singletons (2.21% : N/A)
0 + 0 with mate mapped to a different chr
0 + 0 with mate mapped to a different chr (mapQ>=5)
```

4. Скрипт разбора файлов с этими результатами в файле `parse_flagstat.sh`
5. Инструкция по развертыванию и установке фреймворка Apache AirFlow:
   - Установка:

   ```python
   python3 -m venv airflow-venv
   source airflow-venv/bin/activate
   
   export AIRFLOW_HOME=~/airflow
   
   AIRFLOW_VERSION=3.2.2
   PYTHON_VERSION="$(python --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)"
   CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
   
   pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
   ```

   - Создать DAG-файл и положить в папку airflow/dags.
   
   - Запуск фреймворка: `airflow standalone`
   
   - В терминале появится логин admin и сгенерированный пароль - запишите его.
   
   - Открыть в браузере веб-интерфейс фреймворка: `http://localhost:8080`.

6. Код тестового пайплайна в файле `hello_world_dag.py`.

7. Результаты работы тестового пайплайна и лог-файлы в папке `/test_pipeline`.

8. Код пайплайна "оценки качества картирования" на фреймворке в файле: `pipeline_dag.py`.

9. Результаты работы пайплайна, лог-файлы, визуализация в папке `/pipeline`.

10. Описание использованного способа визуализации и отличия полученной визуализации от
    блок-схемы алгоритма:

    Визуализация пайплайна получена автоматически средствами самого фреймворка
    Apache Airflow. Граф не рисовался вручную: Airflow строит его из объявленных
    в коде DAG зависимостей между задачами (оператор `>>`). Готовый граф доступен в веб-интерфейсе Airflow.

    Таким образом, исходная блок-схема алгоритма это схема потока управления. Она показывает,
    в каком порядке выполняются действия, и читается сверху вниз как
    последовательность шагов с возможными ветвлениями и циклами.
    А DAG - это направленный ацикличный граф зависимостей между
    задачами. Когда именно и в каком порядке физически запускать задачи,
    решает планировщик Airflow, а не сам граф.

   - Также граф Airflow динамичен: он несёт информацию о ходе выполнения. Цвет каждой задачи показывает её статус (успех / выполняется / ошибка / пропущена), доступны логи, время выполнения и история запусков. Блок-схема ничего о реальном прогоне не знает.
