#!/usr/bin/env bash
# Runs the job on a real Hadoop installation (HDFS + Hadoop Streaming).
# Adjust STREAMING_JAR if your Hadoop version differs.
set -euo pipefail
cd "$(dirname "$0")"

STREAMING_JAR="${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-streaming-*.jar"

hdfs dfs -mkdir -p /bank_project/input
hdfs dfs -put -f input/bank_transactions_hadoop.csv /bank_project/input/
hdfs dfs -rm -r -f /bank_project/output

hadoop jar $STREAMING_JAR \
  -files mapper.py,reducer.py \
  -mapper "python3 mapper.py" \
  -combiner "python3 reducer.py" \
  -reducer "python3 reducer.py" \
  -input /bank_project/input/bank_transactions_hadoop.csv \
  -output /bank_project/output

mkdir -p results
hdfs dfs -cat /bank_project/output/part-* > results/mapreduce_output.txt
echo "Output records: $(wc -l < results/mapreduce_output.txt)"
