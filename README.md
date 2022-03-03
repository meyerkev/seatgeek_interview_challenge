# Meyerkev's Seatgeek interview 

Following the spec provided based on a previous repo that I'd used for a similar use case a few months back,
I updated my repository for some Mac -> Ubuntu 20.04 changes, tested the server locally

(And then spent 4 hours debugging network failures that were caused by PID 1)

To run the test suite on the Docker image:

```
make docker-build && make test
```

General commands: 

```
# Build
make docker-build

# Run
make up

# Test
# Currently, this is not multi-OS, so it needs to run on linux/amd64
make test

# Unit tests
make unit-test

# Get a Docker shell
make sh

# Reset the server to the beginning state
# Lit. make down && make up
make reset  
```
