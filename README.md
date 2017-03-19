# os-hardware

`os-hardware` is a small Python library containing hardware utilities.

## Usage

### Discovery

You can use the functions in `os_hardware` to determine various
hardware-related information about the host computer.

#### Memory

```bash
>>> from os_hardware import memory
>>> 
>>> memory.info()
memory (24565.0 MB physical, 24099.0 MB usable)
>>> memory.supported_page_sizes()
set([2048, 1048576])
```

## Developers

For information on how to contribute to `os-hardware`, please see the contents of
the `CONTRIBUTING.rst`.

Any new code must follow the development guidelines detailed in the `HACKING.rst`
file, and pass all unit tests.

### Running tests

You can run unit tests easily using the `tox -epy27` command, like so:

```bash
$ tox -epy27
```
