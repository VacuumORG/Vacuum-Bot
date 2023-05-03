def chunks(lst, chunk_size):
    ret = []
    temp = list(lst)
    while temp:
        chunk, temp = temp[:chunk_size], temp[chunk_size:]
        ret.append(chunk)
    return ret
