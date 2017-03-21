# hwk - The HardWare toolKit library

`hwk` is a small Python library containing hardware discovery and configuration
tools.

## Design Principles

### No root privileges needed

`hwk` goes the extra mile to be useful without root priveleges. We query for
host hardware information as directly as possible without relying on shellouts
to programs like `dmidecode` that require root privileges to execute.

## Usage

### Discovery

You can use the functions in `hwk` to determine various
hardware-related information about the host computer.

Each module in `hwk` contains a single `info()` function that returns an object
containing information about a particular subsystem or component. For example,
to get information about the memory subsystem, you would use the
`hwk.memory.info()` function. The `hwk.disk.info()` method likewise returns an
object that describes the disk subsystem of the host.

The objects returned by the `info()` functions all have a `describe()` method
that prints out helpful descriptions of the attributes of the object.

#### Memory

```bash
>>> from hwk import memory
>>> 
>>> memory.info()
memory (24565.0 MB physical, 24099.0 MB usable)
>>> memory.supported_page_sizes()
set([2048, 1048576])
```

## Developers

Contributions to `hwk` are welcomed! Fork the repo on GitHub and submit a pull
request with your proposed changes. Or, feel free to log an issue for a feature
request or bug report.

### Running tests

You can run unit tests easily using the `tox -epy27` command, like so:

```bash
$ tox -epy27
```
