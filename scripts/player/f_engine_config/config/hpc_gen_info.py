
info = {'flag0':
            {'10GbE_interfaces':
                 [{'10.17.16.200': 0x7CFE90B92DF0},
                  {'10.17.16.201': 0x7CFE90B1EBC1},
                  {'10.17.16.202': 0x7CFE90B1EEC0},
                  {'10.17.16.203': 0x7CFE90B1EEC1}],
            'infiniband_interface': '10.40.1.1'},
        'flag1':
            {'10GbE_interfaces':
                 [{'10.17.16.204': 0xAADEADBEEFAA},
                  {'10.17.16.205': 0xAADEADBEEFAA},
                  {'10.17.16.206': 0x7CFE90B1F030},
                  {'10.17.16.207': 0x7CFE90B1F031}],
            'infiniband_interface': '10.40.2.1'},
        'flag2':
            {'10GbE_interfaces':
                 [{'10.17.16.208': 0x7CFE90B92DF0},
                  {'10.17.16.209': 0x7CFE90B92BD0},
                  {'10.17.16.210': 0x7CFE90B92BD1},
                  {'10.17.16.211': 0x7CFE90B92DF1}],
            'infiniband_interface': '10.40.3.1'},
        'flag3':
            {'10GbE_interfaces':
                 [{'10.17.16.212': 0x7CFE90B1EEB0},
                  {'10.17.16.213': 0x7CFE90B1EEB1},
                  {'10.17.16.214': 0x7CFE90B1EEE0},
                  {'10.17.16.215': 0x7CFE90B1EEE1}],
            'infiniband_interface': '10.40.4.1'},
        'flag4':
            {'10GbE_interfaces':
                 [{'10.17.16.216': 0x7CFE90B1EE90},
                  {'10.17.16.217': 0x7CFE90B1EBA1},
                  {'10.17.16.218': 0x7CFE90B1EBA0},
                  {'10.17.16.219': 0x7CFE90B1EE91}],
            'infiniband_interface': '10.40.5.1'}
       }

master_info = {}

lastDigit = 200
numHPC = 5

hpc_base_name = 'flag'
baseIP = '10.17.16.'
#baseIP_decimal =  10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8)


for i in range(0, numHPC, 1):
    hpc_info = {}
    ip_addrs = []
    #ip_addrs_dec = []


    for j in range(0,4,1):
        ip = 200 + i*(numHPC-1) + j
        ip_addr = baseIP + str(ip)
        #ip_addr_dec = baseIP_decimal + ip

        ip_addrs.append(ip_addr)
        #ip_addrs_dec.append(ip_addr_dec)

    hpc_info['ip_addrs']     = ip_addrs
    #hpc_info['dec_ip_addrs'] = ip_addrs_dec

    hpc_name = hpc_base_name + str(i)
    master_info[hpc_name] = hpc_info






"""
paf0 = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 39
flag3_0 = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 208
flag3_1 = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 209
flag3_2 = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 210
flag3_3 = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 211
# west        = 10*(2**24)+17*(2**16)+0*(2**8)+35 # west ip address , need to direct the unwanted packets somewhere
# tofu        = 10*(2**24)+17*(2**16)+0*(2**8)+36 # ip address of tofu for the correct mac address
# south       = 10*(2**24)+17*(2**16)+0*(2**8)+33
blackhole = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 200


macs = {
    '10.17.16.39': 0x000F5308458C,  # paf0
    '10.17.16.208': 0x7CFE90B92DF0,  # flag3_0
    '10.17.16.209': 0x7CFE90B92BD0,  # flag3_1
    '10.17.16.210': 0x7CFE90B92BD1,  # flag3_2
    '10.17.16.211': 0x7CFE90B92DF1,  # flag3_3
    #    '10.17.0.35': 0x000F530C668C, # west
    #    '10.17.0.33': 0x0002C952FDCB, # south
    #    '10.17.0.36': 0x000F530CFDB8, # tofu
    '10.17.16.200': 0x0202b1ac401e,
# blackhole mac address and fake ip; Note the switch is configured to drop packets sent to this mac
}

hpc_macs = {}
hpc_macs_list = [0xffffffffffff] * 256

"""