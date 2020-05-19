import os

env = Environment(
	ENV = os.environ,
)

SConscript('laks/build_rules')

env.SelectMCU('stm32f303rc')

env.Firmware('build/arcin.elf', Glob('arcin/*.cpp'), LINK_SCRIPT = 'arcin/arcin.ld')

env.Firmware('build/bootloader.elf', Glob('bootloader/*.cpp'), LINK_SCRIPT = 'bootloader/bootloader.ld')

env.Firmware('build/test.elf', Glob('test/*.cpp'))
