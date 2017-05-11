
import struct, time
import numpy as np
from numpy import genfromtxt

from helper_functions import *

config_debug = True
lo = 1450
hpc_macs_list = [0xffffffffffff] * 256
source_port = 60000
dest_port = 60000

numHPC = 5

blackhole   = 10*(2**24)+17*(2**16)+16*(2**8)+200
backend = 'flag'

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

def configure_roach(fpga, fid, hpc_name, roach_name):

    # resets the GbE cores
    if config_debug:
        print "ConfigFE: Resetting the GbE cores for: %s" % (roach_name)
    fpga.write_int('part2_gbe_rst_core', 0)
    time.sleep(1)
    fpga.write_int('part2_gbe_rst_core', 1)
    time.sleep(1)
    fpga.write_int('part2_gbe_rst_core', 0)
    time.sleep(1)

    # Configure 10 GbE cores
    if config_debug:
        print "ConfigFE: Configuring 10 GbE interfaces for: %s" % (roach_name)
    # give each physical port a unique id
    baseMac   = (2 << 40) + (2 << 32) + (10 << 24) + (17 << 16) + (16 << 8)
    mac_base0 = baseMac + (4 * fid + 230)
    mac_base1 = baseMac + (4 * fid + 231)
    mac_base2 = baseMac + (4 * fid + 232)
    mac_base3 = baseMac + (4 * fid + 233)

    baseIp     = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + 230
    source_ip0 = baseIp + 230 + (4 * fid)
    source_ip1 = baseIp + 231 + (4 * fid)
    source_ip2 = baseIp + 232 + (4 * fid)
    source_ip3 = baseIp + 233 + (4 * fid)

    fpga.config_10gbe_core('part2_gbe0', mac_base0, source_ip0, source_port, hpc_macs_list)
    fpga.config_10gbe_core('part2_gbe1', mac_base1, source_ip1, source_port, hpc_macs_list)
    fpga.config_10gbe_core('part2_gbe2', mac_base2, source_ip2, source_port, hpc_macs_list)
    fpga.config_10gbe_core('part2_gbe3', mac_base3, source_ip3, source_port, hpc_macs_list)

    # set fid
    if config_debug:
        print 'ConfigFE: Writing fid...'
    fpga.write_int('part2_f_id', fid)
    time.sleep(0.5)

    # set xid
    if config_debug:
        print 'ConfigFE: Writing xid...'

    for i in range(20):
        fpga.write_int('part2_x_id' + str(i), i)
    time.sleep(0.5)

    # set dest port
    if config_debug:
        print "ConfigFE: Writing destination port as: %d" % dest_port
    fpga.write_int('part2_x_port', dest_port)
    time.sleep(0.5)

    #set dest IP addrs
    if config_debug:
        print "ConfigFE: Writing destination IP addrs..."

    # set all to blackhole first
    for i in range(20):
        fpga.write_int('part2_x_ip'+str(i), blackhole)

    # fill in for hpc's present
    xid_range = range(fid*numHPC, fid*numHPC+4, 1)
    #ip_addrs = info[backend+str(fid)]['10GbE_interfaces']
    ip_addrs = info[hpc_name]['10GbE_interfaces']

    for i in length(xid_range):
        register = 'part2_x_ip' + str(xid)
        split_addr = ip_addrs[i].split('.')
        dest_addr = 10 * (2 ** 24) + 17 * (2 ** 16) + 16 * (2 ** 8) + split_addr[-1:]
        fpga.write_int(register, dest_addr)


def set_coeff(fpga, fid, bankPrefix):

    if config_debug:
        print "ConfigFE: setting coefficients..."

    basePath = './coefficietns/'
    
    lsbre01 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbre01_' + lo + '.csv', delimiter='/n')
    lsbre23 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbre23_' + lo + '.csv', delimiter='/n')
    lsbre45 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbre45_' + lo + '.csv', delimiter='/n')
    lsbre67 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbre67_' + lo + '.csv', delimiter='/n')

    lsbim01 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbim01_' + lo + '.csv', delimiter='/n')
    lsbim23 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbim23_' + lo + '.csv', delimiter='/n')
    lsbim45 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbim45_' + lo + '.csv', delimiter='/n')
    lsbim67 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_lsbim67_' + lo + '.csv', delimiter='/n')

    usbre01 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbre01_' + lo + '.csv', delimiter='/n')
    usbre23 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbre23_' + lo + '.csv', delimiter='/n')
    usbre45 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbre45_' + lo + '.csv', delimiter='/n')
    usbre67 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbre67_' + lo + '.csv', delimiter='/n')

    usbim01 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbim01_' + lo + '.csv', delimiter='/n')
    usbim23 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbim23_' + lo + '.csv', delimiter='/n')
    usbim45 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbim45_' + lo + '.csv', delimiter='/n')
    usbim67 = genfromtxt(basePath + lo + '/' + bankPrefix + '_512_usbim67_' + lo + '.csv', delimiter='/n')

    # 000000 111111 #
    lsbre01_to_pack = np.round(lsbre01 * 2 ** 29)
    lsbre01_packed = struct.pack('>512l',
                                 *lsbre01_to_pack)  # the star is there so that it actually reads lsbre01_topack[0] lsbre01_topack[1] lsbre01_topack[2] .... lsbre01_topack[512]
    fpga.write('lsbre01', lsbre01_packed, 0)

    lsbim01_to_pack = np.round(lsbim01 * 2 ** 29)
    lsbim01_packed = struct.pack('>512l', *lsbim01_to_pack)
    fpga.write('lsbim01', lsbim01_packed, 0)

    usbre01_to_pack = np.round(usbre01 * 2 ** 29)
    usbre01_packed = struct.pack('>512l', *usbre01_to_pack)
    fpga.write('usbre01', usbre01_packed, 0)

    usbim01_to_pack = np.round(usbim01 * 2 ** 29)
    usbim01_packed = struct.pack('>512l', *usbim01_to_pack)
    fpga.write('usbim01', usbim01_packed, 0)

    # 222222 333333 #
    lsbre23_to_pack = np.round(lsbre23 * 2 ** 29)
    lsbre23_packed = struct.pack('>512l', *lsbre23_to_pack)
    fpga.write('lsbre23', lsbre23_packed, 0)

    lsbim23_to_pack = np.round(lsbim23 * 2 ** 29)
    lsbim23_packed = struct.pack('>512l', *lsbim23_to_pack)
    fpga.write('lsbim23', lsbim23_packed, 0)

    usbre23_to_pack = np.round(usbre23 * 2 ** 29)
    usbre23_packed = struct.pack('>512l', *usbre23_to_pack)
    fpga.write('usbre23', usbre23_packed, 0)

    usbim23_to_pack = np.round(usbim23 * 2 ** 29)
    usbim23_packed = struct.pack('>512l', *usbim23_to_pack)
    fpga.write('usbim23', usbim23_packed, 0)

    # 444444 555555 #
    lsbre45_to_pack = np.round(lsbre45 * 2 ** 29)
    lsbre45_packed = struct.pack('>512l', *lsbre45_to_pack)
    fpga.write('lsbre45', lsbre45_packed, 0)

    lsbim45_to_pack = np.round(lsbim45 * 2 ** 29)
    lsbim45_packed = struct.pack('>512l', *lsbim45_to_pack)
    fpga.write('lsbim45', lsbim45_packed, 0)

    usbre45_to_pack = np.round(usbre45 * 2 ** 29)
    usbre45_packed = struct.pack('>512l', *usbre45_to_pack)
    fpga.write('usbre45', usbre45_packed, 0)

    usbim45_to_pack = np.round(usbim45 * 2 ** 29)
    usbim45_packed = struct.pack('>512l', *usbim45_to_pack)
    fpga.write('usbim45', usbim45_packed, 0)

    # 666666 777777 #
    lsbre67_to_pack = np.round(lsbre67 * 2 ** 29)
    lsbre67_packed = struct.pack('>512l', *lsbre67_to_pack)
    fpga.write('lsbre67', lsbre67_packed, 0)

    lsbim67_to_pack = np.round(lsbim67 * 2 ** 29)
    lsbim67_packed = struct.pack('>512l', *lsbim67_to_pack)
    fpga.write('lsbim67', lsbim67_packed, 0)

    usbre67_to_pack = np.round(usbre67 * 2 ** 29)
    usbre67_packed = struct.pack('>512l', *usbre67_to_pack)
    fpga.write('usbre67', usbre67_packed, 0)

    usbim67_to_pack = np.round(usbim67 * 2 ** 29)
    usbim67_packed = struct.pack('>512l', *usbim67_to_pack)
    fpga.write('usbim67', usbim67_packed, 0)

    if config_debug:
        print "ConfigFE: Finished!"

def write_quantization_gain(fpga, gain=0x0000000a):
    if config_debug:
        print "ConfigFE: Writing quantization gain..."
    fpga.write_int('quant_gain', gain)

def write_fft_shift(fpga, shift):
    if config_debug:
        print "ConfigFE: Writing fft_shift..."
    fpga.write_int('fft_shift', shift)

def bit_lock(fpga):
    if config_debug:
        print "ConfigFE: Aligning bits..."

    fpga.write_int('msb_realign', 1)
    time.sleep(0.5)

    fpga.write_int('msb_realign', 0)
    time.sleep(0.5)

    if (fpga.read_int('bit_locked') != 255):
        print "ConfigFE: bit locked failed."

    if config_debug:
        print "ConfigFE: Done Aligning bits!"

def byte_lock(fpga, check):
    if config_debug:
        print "ConfigFE: Aligning IQ..."

    # The Black Box that byte locks...
    if check:
        time.sleep(0.3)
        ####################################
        ####################################
        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 0)
        usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0, 0)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb0_mag = usb0_mag1
        lsb0_mag = lsb0_mag1
        usb1_mag = usb1_mag1
        lsb1_mag = lsb1_mag1
        usb2_mag = usb2_mag1
        lsb2_mag = lsb2_mag1
        usb3_mag = usb3_mag1
        lsb3_mag = lsb3_mag1
        usb4_mag = usb4_mag1
        lsb4_mag = lsb4_mag1
        usb5_mag = usb5_mag1
        lsb5_mag = lsb5_mag1
        usb6_mag = usb6_mag1
        lsb6_mag = lsb6_mag1
        usb7_mag = usb7_mag1
        lsb7_mag = lsb7_mag1

        ii = 1
        # while ii<257:
        ########luke
        while ii < 256:
            usb0_mag[ii] = usb0_mag1[ii] + usb0_mag2[ii] + usb0_mag3[ii] + usb0_mag4[ii] + usb0_mag5[ii] + usb0_mag6[
                ii] + usb0_mag7[ii] + usb0_mag8[ii] + usb0_mag9[ii] + usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii] + lsb0_mag2[ii] + lsb0_mag3[ii] + lsb0_mag5[ii] + lsb0_mag5[ii] + lsb0_mag6[
                ii] + lsb0_mag7[ii] + lsb0_mag8[ii] + lsb0_mag9[ii] + lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii] + usb1_mag2[ii] + usb1_mag3[ii] + usb1_mag4[ii] + usb1_mag5[ii] + usb1_mag6[
                ii] + usb1_mag7[ii] + usb1_mag8[ii] + usb1_mag9[ii] + usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii] + lsb1_mag2[ii] + lsb1_mag3[ii] + lsb1_mag5[ii] + lsb1_mag5[ii] + lsb1_mag6[
                ii] + lsb1_mag7[ii] + lsb1_mag8[ii] + lsb1_mag9[ii] + lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii] + usb2_mag2[ii] + usb2_mag3[ii] + usb2_mag4[ii] + usb2_mag5[ii] + usb2_mag6[
                ii] + usb2_mag7[ii] + usb2_mag8[ii] + usb2_mag9[ii] + usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii] + lsb2_mag2[ii] + lsb2_mag3[ii] + lsb2_mag5[ii] + lsb2_mag5[ii] + lsb2_mag6[
                ii] + lsb2_mag7[ii] + lsb2_mag8[ii] + lsb2_mag9[ii] + lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii] + usb3_mag2[ii] + usb3_mag3[ii] + usb3_mag4[ii] + usb3_mag5[ii] + usb3_mag6[
                ii] + usb3_mag7[ii] + usb3_mag8[ii] + usb3_mag9[ii] + usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii] + lsb3_mag2[ii] + lsb3_mag3[ii] + lsb3_mag5[ii] + lsb3_mag5[ii] + lsb3_mag6[
                ii] + lsb3_mag7[ii] + lsb3_mag8[ii] + lsb3_mag9[ii] + lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii] + usb4_mag2[ii] + usb4_mag3[ii] + usb4_mag4[ii] + usb4_mag5[ii] + usb4_mag6[
                ii] + usb4_mag7[ii] + usb4_mag8[ii] + usb4_mag9[ii] + usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii] + lsb4_mag2[ii] + lsb4_mag3[ii] + lsb4_mag5[ii] + lsb4_mag5[ii] + lsb4_mag6[
                ii] + lsb4_mag7[ii] + lsb4_mag8[ii] + lsb4_mag9[ii] + lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii] + usb5_mag2[ii] + usb5_mag3[ii] + usb5_mag4[ii] + usb5_mag5[ii] + usb5_mag6[
                ii] + usb5_mag7[ii] + usb5_mag8[ii] + usb5_mag9[ii] + usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii] + lsb5_mag2[ii] + lsb5_mag3[ii] + lsb5_mag5[ii] + lsb5_mag5[ii] + lsb5_mag6[
                ii] + lsb5_mag7[ii] + lsb5_mag8[ii] + lsb5_mag9[ii] + lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii] + usb6_mag2[ii] + usb6_mag3[ii] + usb6_mag4[ii] + usb6_mag5[ii] + usb6_mag6[
                ii] + usb6_mag7[ii] + usb6_mag8[ii] + usb6_mag9[ii] + usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii] + lsb6_mag2[ii] + lsb6_mag3[ii] + lsb6_mag5[ii] + lsb6_mag5[ii] + lsb6_mag6[
                ii] + lsb6_mag7[ii] + lsb6_mag8[ii] + lsb6_mag9[ii] + lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii] + usb7_mag2[ii] + usb7_mag3[ii] + usb7_mag4[ii] + usb7_mag5[ii] + usb7_mag6[
                ii] + usb7_mag7[ii] + usb7_mag8[ii] + usb7_mag9[ii] + usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii] + lsb7_mag2[ii] + lsb7_mag3[ii] + lsb7_mag5[ii] + lsb7_mag5[ii] + lsb7_mag6[
                ii] + lsb7_mag7[ii] + lsb7_mag8[ii] + lsb7_mag9[ii] + lsb7_mag10[ii]
            ii = ii + 1

        mag0_rat_a = usb0_mag[166] / lsb0_mag[166]
        mag1_rat_a = usb1_mag[166] / lsb1_mag[166]
        mag2_rat_a = usb2_mag[166] / lsb2_mag[166]
        mag3_rat_a = usb3_mag[166] / lsb3_mag[166]
        mag4_rat_a = usb4_mag[166] / lsb4_mag[166]
        mag5_rat_a = usb5_mag[166] / lsb5_mag[166]
        mag6_rat_a = usb6_mag[166] / lsb6_mag[166]
        mag7_rat_a = usb7_mag[166] / lsb7_mag[166]
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)
        time.sleep(0.1)
        fpga.write_int('rxslide', 255)
        time.sleep(0.1)
        fpga.write_int('rxslide', 0)

        time.sleep(1)
        ####################################
        ####################################
        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 0)
        usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0, 0)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb0_mag = usb0_mag1
        lsb0_mag = lsb0_mag1
        usb1_mag = usb1_mag1
        lsb1_mag = lsb1_mag1
        usb2_mag = usb2_mag1
        lsb2_mag = lsb2_mag1
        usb3_mag = usb3_mag1
        lsb3_mag = lsb3_mag1
        usb4_mag = usb4_mag1
        lsb4_mag = lsb4_mag1
        usb5_mag = usb5_mag1
        lsb5_mag = lsb5_mag1
        usb6_mag = usb6_mag1
        lsb6_mag = lsb6_mag1
        usb7_mag = usb7_mag1
        lsb7_mag = lsb7_mag1

        ii = 1
        # while ii<257:
        ########luke
        while ii < 256:
            usb0_mag[ii] = usb0_mag1[ii] + usb0_mag2[ii] + usb0_mag3[ii] + usb0_mag4[ii] + usb0_mag5[ii] + usb0_mag6[
                ii] + usb0_mag7[ii] + usb0_mag8[ii] + usb0_mag9[ii] + usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii] + lsb0_mag2[ii] + lsb0_mag3[ii] + lsb0_mag5[ii] + lsb0_mag5[ii] + lsb0_mag6[
                ii] + lsb0_mag7[ii] + lsb0_mag8[ii] + lsb0_mag9[ii] + lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii] + usb1_mag2[ii] + usb1_mag3[ii] + usb1_mag4[ii] + usb1_mag5[ii] + usb1_mag6[
                ii] + usb1_mag7[ii] + usb1_mag8[ii] + usb1_mag9[ii] + usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii] + lsb1_mag2[ii] + lsb1_mag3[ii] + lsb1_mag5[ii] + lsb1_mag5[ii] + lsb1_mag6[
                ii] + lsb1_mag7[ii] + lsb1_mag8[ii] + lsb1_mag9[ii] + lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii] + usb2_mag2[ii] + usb2_mag3[ii] + usb2_mag4[ii] + usb2_mag5[ii] + usb2_mag6[
                ii] + usb2_mag7[ii] + usb2_mag8[ii] + usb2_mag9[ii] + usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii] + lsb2_mag2[ii] + lsb2_mag3[ii] + lsb2_mag5[ii] + lsb2_mag5[ii] + lsb2_mag6[
                ii] + lsb2_mag7[ii] + lsb2_mag8[ii] + lsb2_mag9[ii] + lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii] + usb3_mag2[ii] + usb3_mag3[ii] + usb3_mag4[ii] + usb3_mag5[ii] + usb3_mag6[
                ii] + usb3_mag7[ii] + usb3_mag8[ii] + usb3_mag9[ii] + usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii] + lsb3_mag2[ii] + lsb3_mag3[ii] + lsb3_mag5[ii] + lsb3_mag5[ii] + lsb3_mag6[
                ii] + lsb3_mag7[ii] + lsb3_mag8[ii] + lsb3_mag9[ii] + lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii] + usb4_mag2[ii] + usb4_mag3[ii] + usb4_mag4[ii] + usb4_mag5[ii] + usb4_mag6[
                ii] + usb4_mag7[ii] + usb4_mag8[ii] + usb4_mag9[ii] + usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii] + lsb4_mag2[ii] + lsb4_mag3[ii] + lsb4_mag5[ii] + lsb4_mag5[ii] + lsb4_mag6[
                ii] + lsb4_mag7[ii] + lsb4_mag8[ii] + lsb4_mag9[ii] + lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii] + usb5_mag2[ii] + usb5_mag3[ii] + usb5_mag4[ii] + usb5_mag5[ii] + usb5_mag6[
                ii] + usb5_mag7[ii] + usb5_mag8[ii] + usb5_mag9[ii] + usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii] + lsb5_mag2[ii] + lsb5_mag3[ii] + lsb5_mag5[ii] + lsb5_mag5[ii] + lsb5_mag6[
                ii] + lsb5_mag7[ii] + lsb5_mag8[ii] + lsb5_mag9[ii] + lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii] + usb6_mag2[ii] + usb6_mag3[ii] + usb6_mag4[ii] + usb6_mag5[ii] + usb6_mag6[
                ii] + usb6_mag7[ii] + usb6_mag8[ii] + usb6_mag9[ii] + usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii] + lsb6_mag2[ii] + lsb6_mag3[ii] + lsb6_mag5[ii] + lsb6_mag5[ii] + lsb6_mag6[
                ii] + lsb6_mag7[ii] + lsb6_mag8[ii] + lsb6_mag9[ii] + lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii] + usb7_mag2[ii] + usb7_mag3[ii] + usb7_mag4[ii] + usb7_mag5[ii] + usb7_mag6[
                ii] + usb7_mag7[ii] + usb7_mag8[ii] + usb7_mag9[ii] + usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii] + lsb7_mag2[ii] + lsb7_mag3[ii] + lsb7_mag5[ii] + lsb7_mag5[ii] + lsb7_mag6[
                ii] + lsb7_mag7[ii] + lsb7_mag8[ii] + lsb7_mag9[ii] + lsb7_mag10[ii]
            ii = ii + 1

        mag0_rat_b = usb0_mag[166] / lsb0_mag[166]
        mag1_rat_b = usb1_mag[166] / lsb1_mag[166]
        mag2_rat_b = usb2_mag[166] / lsb2_mag[166]
        mag3_rat_b = usb3_mag[166] / lsb3_mag[166]
        mag4_rat_b = usb4_mag[166] / lsb4_mag[166]
        mag5_rat_b = usb5_mag[166] / lsb5_mag[166]
        mag6_rat_b = usb6_mag[166] / lsb6_mag[166]
        mag7_rat_b = usb7_mag[166] / lsb7_mag[166]

        if config_debug:
            print ('mag0_rat_a')
            print mag0_rat_a
            print ('mag0_rat_b')
            print mag0_rat_b

            print ('mag1_rat_a')
            print mag1_rat_a
            print ('mag1_rat_b')
            print mag1_rat_b

            print ('mag2_rat_a')
            print mag2_rat_a
            print ('mag2_rat_b')
            print mag2_rat_b

            print ('mag3_rat_a')
            print mag3_rat_a
            print ('mag3_rat_b')
            print mag3_rat_b

            print ('mag4_rat_a')
            print mag4_rat_a
            print ('mag4_rat_b')
            print mag4_rat_b

            print ('mag5_rat_a')
            print mag5_rat_a
            print ('mag5_rat_b')
            print mag5_rat_b

            print ('mag6_rat_a')
            print mag6_rat_a
            print ('mag6_rat_b')
            print mag6_rat_b

            print ('mag7_rat_a')
            print mag7_rat_a
            print ('mag7_rat_b')
            print mag7_rat_b

        if (mag0_rat_a > mag0_rat_b):
            ##flyp dem bites on A0!!!
            if config_debug:
                print 're-aligning 0 \n'
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 1)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag1_rat_a > mag1_rat_b):
            ##flyp dem bites on A1!!!
            if config_debug:
                print 're-aligning 1 \n'
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 2)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag2_rat_a > mag2_rat_b):
            ##flyp dem bites on A2!!!
            if config_debug:
                print 're-aligning 2 \n'
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 4)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag3_rat_a > mag3_rat_b):
            ##flyp dem bites on A3!!!
            if config_debug:
                print 're-aligning 3 \n'
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 8)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag4_rat_a > mag4_rat_b):
            ##flyp dem bites on A4!!!
            if config_debug:
                print 're-aligning 4 \n'
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 16)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag5_rat_a > mag5_rat_b):
            ##flyp dem bites on A5!!!
            if config_debug:
                print 're-aligning 5 \n'
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 32)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag6_rat_a > mag6_rat_b):
            ##flyp dem bites on A6!!!
            if config_debug:
                print 're-aligning 6 \n'
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 64)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if (mag7_rat_a > mag7_rat_b):
            ##flyp dem bites on A7!!!
            if config_debug:
                print 're-aligning 7 \n'
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)
            time.sleep(0.1)
            fpga.write_int('rxslide', 128)
            time.sleep(0.1)
            fpga.write_int('rxslide', 0)

        if config_debug:
            print "ConfigFE: Finished aligning bytes!"

    else:
        if config_debug:
            print "ConfigFE: Checking IQ Alignment..."

        time.sleep(0.3)
        ####################################
        ####################################
        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 0)
        usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0, 0)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(0, 1)
        usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(2, 1)
        usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(4, 1)
        usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4, 1)

        usb_r, usb_i, lsb_r, lsb_i = get_data_sbs(6, 1)
        usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6, 1)

        time.sleep(0.1)

        usb0_mag = usb0_mag1
        lsb0_mag = lsb0_mag1
        usb1_mag = usb1_mag1
        lsb1_mag = lsb1_mag1
        usb2_mag = usb2_mag1
        lsb2_mag = lsb2_mag1
        usb3_mag = usb3_mag1
        lsb3_mag = lsb3_mag1
        usb4_mag = usb4_mag1
        lsb4_mag = lsb4_mag1
        usb5_mag = usb5_mag1
        lsb5_mag = lsb5_mag1
        usb6_mag = usb6_mag1
        lsb6_mag = lsb6_mag1
        usb7_mag = usb7_mag1
        lsb7_mag = lsb7_mag1

        ii = 1
        # while ii<257:
        ########luke
        while ii < 256:
            usb0_mag[ii] = usb0_mag1[ii] + usb0_mag2[ii] + usb0_mag3[ii] + usb0_mag4[ii] + usb0_mag5[ii] + \
                           usb0_mag6[ii] + usb0_mag7[ii] + usb0_mag8[ii] + usb0_mag9[ii] + usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii] + lsb0_mag2[ii] + lsb0_mag3[ii] + lsb0_mag5[ii] + lsb0_mag5[ii] + \
                           lsb0_mag6[ii] + lsb0_mag7[ii] + lsb0_mag8[ii] + lsb0_mag9[ii] + lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii] + usb1_mag2[ii] + usb1_mag3[ii] + usb1_mag4[ii] + usb1_mag5[ii] + \
                           usb1_mag6[ii] + usb1_mag7[ii] + usb1_mag8[ii] + usb1_mag9[ii] + usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii] + lsb1_mag2[ii] + lsb1_mag3[ii] + lsb1_mag5[ii] + lsb1_mag5[ii] + \
                           lsb1_mag6[ii] + lsb1_mag7[ii] + lsb1_mag8[ii] + lsb1_mag9[ii] + lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii] + usb2_mag2[ii] + usb2_mag3[ii] + usb2_mag4[ii] + usb2_mag5[ii] + \
                           usb2_mag6[ii] + usb2_mag7[ii] + usb2_mag8[ii] + usb2_mag9[ii] + usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii] + lsb2_mag2[ii] + lsb2_mag3[ii] + lsb2_mag5[ii] + lsb2_mag5[ii] + \
                           lsb2_mag6[ii] + lsb2_mag7[ii] + lsb2_mag8[ii] + lsb2_mag9[ii] + lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii] + usb3_mag2[ii] + usb3_mag3[ii] + usb3_mag4[ii] + usb3_mag5[ii] + \
                           usb3_mag6[ii] + usb3_mag7[ii] + usb3_mag8[ii] + usb3_mag9[ii] + usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii] + lsb3_mag2[ii] + lsb3_mag3[ii] + lsb3_mag5[ii] + lsb3_mag5[ii] + \
                           lsb3_mag6[ii] + lsb3_mag7[ii] + lsb3_mag8[ii] + lsb3_mag9[ii] + lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii] + usb4_mag2[ii] + usb4_mag3[ii] + usb4_mag4[ii] + usb4_mag5[ii] + \
                           usb4_mag6[ii] + usb4_mag7[ii] + usb4_mag8[ii] + usb4_mag9[ii] + usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii] + lsb4_mag2[ii] + lsb4_mag3[ii] + lsb4_mag5[ii] + lsb4_mag5[ii] + \
                           lsb4_mag6[ii] + lsb4_mag7[ii] + lsb4_mag8[ii] + lsb4_mag9[ii] + lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii] + usb5_mag2[ii] + usb5_mag3[ii] + usb5_mag4[ii] + usb5_mag5[ii] + \
                           usb5_mag6[ii] + usb5_mag7[ii] + usb5_mag8[ii] + usb5_mag9[ii] + usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii] + lsb5_mag2[ii] + lsb5_mag3[ii] + lsb5_mag5[ii] + lsb5_mag5[ii] + \
                           lsb5_mag6[ii] + lsb5_mag7[ii] + lsb5_mag8[ii] + lsb5_mag9[ii] + lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii] + usb6_mag2[ii] + usb6_mag3[ii] + usb6_mag4[ii] + usb6_mag5[ii] + \
                           usb6_mag6[ii] + usb6_mag7[ii] + usb6_mag8[ii] + usb6_mag9[ii] + usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii] + lsb6_mag2[ii] + lsb6_mag3[ii] + lsb6_mag5[ii] + lsb6_mag5[ii] + \
                           lsb6_mag6[ii] + lsb6_mag7[ii] + lsb6_mag8[ii] + lsb6_mag9[ii] + lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii] + usb7_mag2[ii] + usb7_mag3[ii] + usb7_mag4[ii] + usb7_mag5[ii] + \
                           usb7_mag6[ii] + usb7_mag7[ii] + usb7_mag8[ii] + usb7_mag9[ii] + usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii] + lsb7_mag2[ii] + lsb7_mag3[ii] + lsb7_mag5[ii] + lsb7_mag5[ii] + \
                           lsb7_mag6[ii] + lsb7_mag7[ii] + lsb7_mag8[ii] + lsb7_mag9[ii] + lsb7_mag10[ii]
            ii = ii + 1

        if config_debug:
            print ('usb0_mag_sum')
            print usb0_mag[166]
            print ('lsb0_mag_sum')
            print lsb0_mag[166]

            print ('usb1_mag_sum')
            print usb1_mag[166]
            print ('lsb1_mag_sum')
            print lsb1_mag[166]

            print ('usb2_mag_sum')
            print usb2_mag[166]
            print ('lsb2_mag_sum')
            print lsb2_mag[166]

            print ('usb3_mag_sum')
            print usb3_mag[166]
            print ('lsb3_mag_sum')
            print lsb3_mag[166]

            print ('usb4_mag_sum')
            print usb4_mag[166]
            print ('lsb4_mag_sum')
            print lsb4_mag[166]

            print ('usb5_mag_sum')
            print usb5_mag[166]
            print ('lsb5_mag_sum')
            print lsb5_mag[166]

            print ('usb6_mag_sum')
            print usb6_mag[166]
            print ('lsb6_mag_sum')
            print lsb6_mag[166]

            print ('usb7_mag_sum')
            print usb7_mag[166]
            print ('lsb7_mag_sum')
            print lsb7_mag[166]

        if (usb0_mag[166] < (lsb0_mag[166] * 10)):
            ##flyp dem bites on A0!!!
            if config_debug:
                print 'Channel 0 not aligned\n'
            if (usb0_mag[166] < (lsb0_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 1)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb1_mag[166] < (lsb1_mag[166] * 10)):
            ##flyp dem bites on A1!!!
            if config_debug:
                print 'Channel 1 not aligned\n'
            if (usb1_mag[166] < (lsb1_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 2)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb2_mag[166] < (lsb2_mag[166] * 10)):
            ##flyp dem bites on A2!!!
            if config_debug:
                print 'Channel 2 not aligned\n'
            if (usb2_mag[166] < (lsb2_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 4)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb3_mag[166] < (lsb3_mag[166] * 10)):
            ##flyp dem bites on A3!!!
            if config_debug:
                print 'Channel 3 not aligned\n'
            if (usb3_mag[166] < (lsb3_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 8)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb4_mag[166] < (lsb4_mag[166] * 10)):
            ##flyp dem bites on A4!!!
            if config_debug:
                print 'Channel 4 not aligned\n'
            if (usb4_mag[166] < (lsb4_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 16)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb5_mag[166] < (lsb5_mag[166] * 10)):
            ##flyp dem bites on A5!!!
            if config_debug:
                print 'Channel 5 not aligned\n'
            if (usb5_mag[166] < (lsb5_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 32)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb6_mag[166] < (lsb6_mag[166] * 10)):
            ##flyp dem bites on A6!!!
            if config_debug:
                print 'Channel 6 not aligned\n'
            if (usb6_mag[166] < (lsb6_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 64)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if (usb7_mag[166] < (lsb7_mag[166] * 10)):
            ##flyp dem bites on A7!!!
            if config_debug:
                print 'Channel 7 not aligned\n'
            if (usb7_mag[166] < (lsb7_mag[166] * 3)):
                if config_debug:
                    print 'setting threshold lower \n'
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)
                time.sleep(0.1)
                fpga.write_int('rxslide', 164)
                time.sleep(0.1)
                fpga.write_int('rxslide', 0)

        if config_debug:
            print 'done checking byte alignment \n'
