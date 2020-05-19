define flash
file build/arcin.elf
load
end

define flash_bootloader
file build/bootloader.elf
load
end

define restart
run
end

define attach_swd
mon swdp_scan
attach 1
end

define attach_jtag
mon jtag_scan
attach 1
end

file build/arcin.elf

set mem inaccessible-by-default off
