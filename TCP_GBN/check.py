def do_checksum(source_string):
    """  Verify the packet integritity """
    sum = 0
    max_count = (len(source_string) / 2) * 2
    count = 0
    while count < max_count:
        val = ord(source_string[count + 1]) * 256 + ord(source_string[count])
        print('%x'%(val))
        sum = sum + val
        sum = sum & 0xffffffff
        count = count + 2

    if max_count < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


if __name__ == '__main__':
    print('%x'%(ord('1')))
    source = ['1','0']
    print(do_checksum(source))