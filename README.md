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

### Well-documented code and inline help

The code itself should be well-documented, of course, but the objects that the
library exposes should themselves be self-describing. See below for the
`describe()` methods that the Info objects all implement.

### Interfaces should be consistent across modules

Each module in the library is structured in a consistent fashion, and the
objects returned by various module functions should have consistent attribute
and method names.

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

#### CPU

```
>>> import pprint
>>> from hwk import cpu
>>> i = cpu.info()
>>> i
cpu (1 physical packages, 6 cores, 12 hardware threads)
>>> for c in i.cpus:
...     print c
... 
CPU 0 (6 cores, 12 threads)[Intel(R) Core(TM) i7 CPU         980  @ 3.33GHz]
>>> pmap = i.cpus[0].processor_map
>>> pprint.pprint(pmap)
{0: set([0, 6]),
 1: set([1, 7]),
 2: set([2, 8]),
 3: set([3, 9]),
 4: set([4, 10]),
 5: set([5, 11])}
>>> features = i.cpus[0].features
>>> pprint.pprint(features)
set(['acpi',
     'aes',
     'aperfmperf',
     'apic',
     'arat',
     < ... >
     'vme',
     'vmx',
     'vnmi',
     'vpid',
     'xtopology',
     'xtpr'])
```

#### Network

```
>>> from hwk import net
>>> i = net.info()
>>> i
net (2 NICs)
>>> for nic in i.nics:
...     print "%8s %12s %s" % (nic.name, nic.mac, nic.vendor)
... 
 enp0s25 e06995034837 Intel Corporation
    wls1 1c7ee5299a06 Qualcomm Atheros
>>>
>>> for nic in i.nics:
...     print "%8s %12s %12s" % (nic.name, nic.bus_type, nic.driver)
...
    wls1          pci        ath9k
 enp0s25          pci       e1000e
>>>
>>> for nic in i.nics:
...     print "NIC: " + str(nic.name)
...     print "Enabled features: "
...     pprint.pprint(nic.enabled_features)
... 
NIC: wls1
Enabled features:
set(['generic-receive-offload', 'netns-local'])
NIC: enp0s25
Enabled features:
set(['generic-receive-offload',
     'generic-segmentation-offload',
     'highdma',
     'receive-hashing',
     'rx-checksumming',
     'rx-vlan-offload',
     'scatter-gather',
     'tcp-segmentation-offload',
     'tx-checksum-ip-generic',
     'tx-checksumming',
     'tx-scatter-gather',
     'tx-tcp-segmentation',
     'tx-tcp6-segmentation',
     'tx-vlan-offload'])
>>>
>>> # The net.nic_features() function returns two sets, one of all features the
>>> # NIC supports and the other containing only the features that are
>>> # currently enabled on the NIC.
>>>
>>> pprint.pprint(net.nic_features('enp0s25'))
(set(['busy-poll',
     'fcoe-mtu',
     'generic-receive-offload',
     'generic-segmentation-offload',
     'highdma',
     'hw-tc-offload',
     'l2-fwd-offload',
     'large-receive-offload',
     'loopback',
     'netns-local',
     'ntuple-filters',
     'receive-hashing',
     'rx-all',
     'rx-checksumming',
     'rx-fcs',
     'rx-vlan-filter',
     'rx-vlan-offload',
     'rx-vlan-stag-filter',
     'rx-vlan-stag-hw-parse',
     'scatter-gather',
     'tcp-segmentation-offload',
     'tx-checksum-fcoe-crc',
     'tx-checksum-ip-generic',
     'tx-checksum-ipv4',
     'tx-checksum-ipv6',
     'tx-checksum-sctp',
     'tx-checksumming',
     'tx-fcoe-segmentation',
     'tx-gre-csum-segmentation',
     'tx-gre-segmentation',
     'tx-gso-partial',
     'tx-gso-robust',
     'tx-ipxip4-segmentation',
     'tx-ipxip6-segmentation',
     'tx-lockless',
     'tx-nocache-copy',
     'tx-scatter-gather',
     'tx-scatter-gather-fraglist',
     'tx-sctp-segmentation',
     'tx-tcp-ecn-segmentation',
     'tx-tcp-mangleid-segmentation',
     'tx-tcp-segmentation',
     'tx-tcp6-segmentation',
     'tx-udp_tnl-csum-segmentation',
     'tx-udp_tnl-segmentation',
     'tx-vlan-offload',
     'tx-vlan-stag-hw-insert',
     'udp-fragmentation-offload',
     'vlan-challenged']),
set(['generic-receive-offload',
     'generic-segmentation-offload',
     'highdma',
     'receive-hashing',
     'rx-checksumming',
     'rx-vlan-offload',
     'scatter-gather',
     'tcp-segmentation-offload',
     'tx-checksum-ip-generic',
     'tx-checksumming',
     'tx-scatter-gather',
     'tx-tcp-segmentation',
     'tx-tcp6-segmentation',
     'tx-vlan-offload']))
```

#### GPU

```
>>> from hwk import gpu
>>> i = gpu.info()
>>> i
gpu (1 physical GPUs)
>>> i.gpus[0]
GPU @pci:0000:03:00.0 [NVIDIA Corporation] (GF114 [GeForce GTX 560 Ti])
>>> print "kernel driver: " + i.gpus[0].driver
kernel driver: nouveau
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
