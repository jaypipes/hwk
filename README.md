# hwk - The HardWare toolKit library

`hwk` is a small Python library containing hardware discovery and configuration
tools.

## Design Principles

### No root privileges needed for discovery

`hwk` goes the extra mile to be useful without root priveleges. We query for
host hardware information as directly as possible without relying on shellouts
to programs like `dmidecode` that require root privileges to execute.

Of course, manipulating hardware often requires elevated privileges, and that
is fine. However, when querying for device and host hardware information, we
will not use any method that requires elevating to root/superuser.

## Usage

### Discovery

You can use the functions in `hwk` to determine various
hardware-related information about the host computer.

Each module in `hwk` contains a single `info()` function that returns an object
containing information about a particular subsystem or component. For example,
to get information about the memory subsystem, you would use the
`hwk.memory.info()` function. The `hwk.block.info()` method likewise returns an
object that describes the block devices of the host.

The objects returned by the `info()` functions all have a `describe()` method
that prints out helpful descriptions of the attributes of the object. For
example, from the `hwk.memory` module:

```
>>> from hwk import memory
>>> i = memory.info()
>>> print i.describe()
Memory subsystem
===============================================================================
`hwk.memory.Info` attributes:

total_physical_bytes (int)

  Number of bytes of physical RAM available to the system

total_usable_bytes (int)

  Number of bytes usable by the system (physical bytes minus a few bits
  reserved for system and the resident kernel size)

supported_page_sizes (set of int)

  A set of ints indicating memory page sizes the system can utilize, in bytes
```

#### Memory

```
>>> from hwk import memory
>>> 
>>> memory.info()
memory (24565.0 MB physical, 24099.0 MB usable)
>>> memory.supported_page_sizes()
set([2048, 1048576])
```

#### Block devices

```
>>> from hwk import block
>>> i = block.info()
>>> i
block (1 disk block devices, 1905440.0 MB total size)
>>> for d in i.disks:
...     print "disk: " + str(d)
...     for p in d.partitions:
...             print "  partition: " + str(p)
... 
disk: /dev/sda (1905440 MB) [SCSI] LSI - SN #3600508e000000000f8253aac9a1abd0c
  partition: /dev/sda6 (1699533 MB) [ext4] mounted@/ - f29a0c43-749b-4fea-b2bb-d120e896e702
  partition: /dev/sda1 (100 MB) [ntfs] - E0A237E1A237BABC
  partition: /dev/sda3 (449 MB) [ntfs] - 7026ADB926AD8128
  partition: /dev/sda2 (190881 MB) [ntfs] - B00C39910C395416
  partition: /dev/sda5 (14473 MB) [swap] - 7710167e-924b-4773-b1e6-906540d15b6d
  partition: /dev/sda4 (0 MB) [None]
```

#### Disks



## Developers

Contributions to `hwk` are welcomed! Fork the repo on GitHub and submit a pull
request with your proposed changes. Or, feel free to log an issue for a feature
request or bug report.

### Running tests

You can run unit tests easily using the `tox -epy27` command, like so:

```bash
$ tox -epy27
```
