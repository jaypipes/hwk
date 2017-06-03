#!/usr/bin/env python

import platform

from hwk import cpu
from hwk import memory
from hwk import block
from hwk import net

if __name__ == '__main__':
    print("== Inspecting host =============================================")
    print("")
    print("  platform.system(): %s" % platform.system())

    i = cpu.info()

    print("")
    print("== CPU information =============================================")
    print("")
    print("  # cores:   %d" % i.total_cores)
    print("  # threads: %d" % i.total_threads)
    print("  processors:")
    for p in i.cpus:
        print("    %s" % p)

    i = memory.info()

    print("")
    print("== Memory information ==========================================")
    print("")
    print("  physical size bytes: %d" % i.total_physical_bytes)
    print("  usable size bytes:   %d" % i.total_usable_bytes)
    print("  supported page sizes:")
    for ps in i.supported_page_sizes:
        print("    %s bytes" % ps)

    i = block.info()

    print("")
    print("== Block information ===========================================")
    print("")
    print("  size bytes: %d" % i.total_size_bytes)
    if i.disks:
        print("  disks:")
    for d in i.disks:
        print("    %s" % d)
        if d.partitions:
            print("    partitions:")
        for p in d.partitions:
            print("      %s" % p)

    i = net.info()

    print("")
    print("== Network information =========================================")
    print("")
    if i.nics:
        print("  nics:")
    for n in i.nics:
        print("    %s" % n)
