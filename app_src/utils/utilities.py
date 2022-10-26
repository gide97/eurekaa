class Command:
    read = 1
    write = 2
    action = 3
    ack = 4
    ping = 5

class CRC:
    '''
        Uses:
            - Calculate Checksum
            - Verify & data scraping
            - Checksum is calculate all data except flags filed.
    '''

    def calc(data_frame:list)->tuple:
        '''
            Calculate data frame CRC
        '''
        total = 0
        for data in data_frame:
            total+=data

        return total, [total&0xff>>8, total&0xff]       # (int)total, [High byte, Low byte]
    
    def verify(raw_data:bytearray)->tuple:
        '''
            Return value: tuple(bool valid, datascrape)
        '''

        print(raw_data)
        
        data_scrape = {}

        t_raw = list(raw_data)[:]

        if t_raw[0] == t_raw[-1]:                       # flag check
            data_scrape['startflag'] = t_raw.pop(0)
            data_scrape['startflag'] = t_raw.pop(-1)
        else:
            return False, {}
        
        crc = [t_raw.pop(-2), t_raw.pop(-1)]
        df_length = [t_raw.pop(0), t_raw.pop(0)]
        df_length = (df_length[0]<<8) + df_length[1]

        data_scrape['crc'] = crc
        data_scrape['datalenth'] = df_length
        
        if len(t_raw) != df_length:                     # data frame check
            return False, {}

        _,ref = CRC.calc(t_raw)
        if crc ==  ref:                                 # check sum check
            return False, {}

        data_scrape['source_addr'] = t_raw.pop(0)
        data_scrape['destination_addr'] = t_raw.pop(0)
        data_scrape['control'] = t_raw.pop(0)
        data_scrape['information'] = t_raw[:]
        
        return True, data_scrape

def generateDataFrame(sourceAddr:int, destAddr:int, control:int, information:bytearray=None) -> bytearray:
    '''
        sourceAddr = (int) 0 ~ 255
        destAddr   = (int) 0 ~ 255
        control    = (int) refer to class Command
        information= (bytes) additional data
    '''
    start_flag = 0x7e
    end_flag = 0x7e
    source_address = sourceAddr
    destination_address = destAddr
    control = control

    subFrame = [source_address, destination_address, control]

    if information != None:
        subFrame.extend([ord(i) for i in information] if type(information)==bytearray else [ord(i) for i in information])
        # subFrame.extend([ord(i) if type(i)==str else int(i) for i in information])

    information_length = len(subFrame)

    mainFrame = []
    mainFrame.append((information_length&0xff) >> 8)    # high byte
    mainFrame.append(information_length&0xff)           # low byte
    mainFrame.extend(subFrame)

    _,crc = CRC.calc(mainFrame)
    mainFrame.extend(crc)
    
    dataFrame = [start_flag]
    dataFrame.extend(mainFrame)
    dataFrame.append(end_flag)

    return bytearray(dataFrame)

# xxx = '7e 00 27 00 01 01 7b 22 63 6f 6d 6d 61 6e 64 22 3a 22 66 72 61 6d 65 72 61 74 65 22 2c 20 22 76 61 6c 75 65 22 3a 31 30 30 7d 00 f1 7e'
# xxx = [int(i,16) for i in xxx.split(' ')]
# _, data = CRC.verify(xxx)
# print(_,data)