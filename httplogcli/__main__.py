import argparse
import subprocess
import sys
import logging
from datetime import timedelta

from httplog.Pipeline import Pipeline
from httplog.HttpParser import HttpParser
from httplog.Alerts import Alert
from httplog.Metrics import Metrics


def main():
    parser = argparse.ArgumentParser(
        prog='httplog',
        description='httplog - HTTP log processor')
    parser.add_argument('--input-file', type=str, required=True,
                        help='input file')
    parser.add_argument('--threshold', type=float, default=10,
                        help='threshold for alerts')

    args = parser.parse_args()

    pipeline = http_log_pipeline(args.threshold)
    init(args.input_file, pipeline)


def http_log_pipeline(threshold: float):
    return Pipeline([
        lambda sink: HttpParser(sink),
        lambda sink: Metrics(sink),
        lambda sink: Alert(threshold, timedelta(minutes=2), sink),
        print
    ])


def init(input_file: str, pipeline: Pipeline):
    pipeline.start()
    f = subprocess.Popen(['tail', '-F', '-n', '+1', input_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        try:
            line = f.stdout.readline()
            line = line.decode("utf-8").strip()
            pipeline.receive(line)
        except:
            pipeline.end()
            sys.exit(0)


if __name__ == '__main__':
    main()
