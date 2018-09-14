def do_checksum(source_string):
    """  Verify the packet integritity """
    sum = 0
    max_count = (len(source_string) / 2) * 2
    count = 0
    while count < max_count:
        val = ord(source_string[count + 1]) + ord(source_string[count])
        # print('%x'%(val))
        sum = sum + val
        count = count + 2

    if max_count < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
    answer = sum % 256
    return answer

if __name__ == '__main__':
    # print('%x'%(ord('1')))
    source = ['x','a','f','e','g','h','e','e','r','g','g','h','w']
    print(do_checksum(source))