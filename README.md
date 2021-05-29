# httplog - http log processor

**httplog** is a CLI for processing http log files and providing metrics and alerts.

## Requirements:

- Python 3.8

## Running

To run locally in development:

```bash
python3 -m venv my_env
source myenv/bin/activate

make test
make dev

httplog -h
```

To run in a docker environment:

```bash
make build

docker run --rm -v <path_to_file_locally>:<path_to_file_in_container> httplog:latest httplog --input-file=<path_to_file_in_container>
```

To install as a package:

```bash
make test
make install

httplog -h
```


## Design

**httplog** is designed as an extendable pipeline.

The `Pipeline` class is a wrapper class that expects a list of callables to process. These callables extend the `Stage` class and must implement it's methods.

The expectation for the pipeline are that:

        - First stage must consume string
        - Last stage is a sink and not a stage
        - Stages publish types that can be consumed by next stage

This allows for composition of the sort:

```python
Pipeline([
        lambda sink: HttpParser(sink),
        lambda sink: Metrics(sink),
        lambda sink: Alert(threshold, timedelta(minutes=2), sink),
        print
])
```

## Implementation

Three separate stages were implemented.

        - Stage 1 (HttpParser): This stage takes a line as input and parses it in accordance with the expected http log format and forwards it to the next stage.
        - Stage 2 (Metrics): This stage updates the current snapshot view of the metrics with the new information and forwards a copy to the next stage.
        - Stage 3 (Alerts): This stage keeps a view of the latest alert window and returns a string on threshold trigger or recovery.
        - Stage 4 (Sink): This final stage is just a sink, which in this case prints the alerts.

Finally, the `Pipeline` class also launches a thread to periodically log the state of the metrics. The `Metrics` stage stores a new snapshot in a "mocked" in-memory database, so it can be fetched by this thread.

In order to facilitate usage and as requested, a module named `httplogcli` was also implemented, to provide a CLI for interacting with the pipeline.
The implementation of the actual pipeline logic is in a separate module, so it can be re-used.

## Improvements

- The alerts only keep track of the latest two minutes, meaning we would have to replay the whole log in order to access that data again.
If this was a requirement, then some sort of persistence for the metrics data would be required.

- Logging is done using `print` as a sink. A better solution is to create a proper logging configuration with different levels.

- Error handling is basic, and could stand to be improved.

- Packaging. Currently this will only work on linux (depends on tail, etc...) so that could also be improved.

- Performance. Python isn't the fastest language (in fact it's pretty slow). I'd prefer a Golang for this, but I'm more comfortable in Python to build something to show you.

- Configuration. Configuration is basic, and could stand to allow more things to be defined. (alert window size, metrics lifetime, what metrics to show, etc...)
