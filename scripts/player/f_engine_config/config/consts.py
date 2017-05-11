from helper_functions import _ip_string_to_int, _hostname_to_ip

paf0        = 10*(2**24)+17*(2**16)+16*(2**8)+39
flag3_0     = 10*(2**24)+17*(2**16)+16*(2**8)+208
flag3_1     = 10*(2**24)+17*(2**16)+16*(2**8)+209
flag3_2     = 10*(2**24)+17*(2**16)+16*(2**8)+210
flag3_3     = 10*(2**24)+17*(2**16)+16*(2**8)+211
#west        = 10*(2**24)+17*(2**16)+0*(2**8)+35 # west ip address , need to direct the unwanted packets somewhere
#tofu        = 10*(2**24)+17*(2**16)+0*(2**8)+36 # ip address of tofu for the correct mac address
#south       = 10*(2**24)+17*(2**16)+0*(2**8)+33
blackhole   = 10*(2**24)+17*(2**16)+16*(2**8)+200

macs = {
    '10.17.16.39' : 0x000F5308458C, # paf0
    '10.17.16.208': 0x7CFE90B92DF0, # flag3_0
    '10.17.16.209': 0x7CFE90B92BD0, # flag3_1
    '10.17.16.210': 0x7CFE90B92BD1, # flag3_2
    '10.17.16.211': 0x7CFE90B92DF1, # flag3_3
#    '10.17.0.35': 0x000F530C668C, # west
#    '10.17.0.33': 0x0002C952FDCB, # south
#    '10.17.0.36': 0x000F530CFDB8, # tofu
    '10.17.16.200': 0x0202b1ac401e, # blackhole mac address and fake ip; Note the switch is configured to drop packets sent to this mac
}

hpc_macs = {}
hpc_macs_list = [0xffffffffffff] * 256

for hostname, mac in macs.iteritems():
    key = _ip_string_to_int(_hostname_to_ip(hostname)) & 0xFF
    hpc_macs[key] = mac
    hpc_macs_list[key] = mac