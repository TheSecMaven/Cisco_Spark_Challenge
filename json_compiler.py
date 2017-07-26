def form_list_of_variations(json):
    print json
    variations = []
    RxCui = []
    x = 0
    for item in json[1]:
        variations.append(item)
        x += 1
    x=0
    for item in json[2]['RXCUIS']: 
        RxCui.append(item)
        x += 1

    summation = []
    x = 0
    for item in variations:
        summation.append(str(variations[x]) + ',' + str(RxCui[x][0]))
        x += 1

    return summation
