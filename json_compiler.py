import csv
def iterate_list(RxCui,x,y): 
    msg = ""
    for item in RxCui[x:y-1]:
        msg += ','
        msg += item 
    return msg   

def form_strength_variations(rxcui_count,linelist):
    strengths = []
    rxcui = []
    x = 1
    print "RX COUNT" + str(rxcui_count)
    while(x<=rxcui_count):
        print "RX: " + repr(linelist[x])
        rxcui.append(linelist[x])
        x += 1
    while(x<= len(linelist)-1):
        print "STRENG: " + repr((linelist[x]).strip('\n'))
        strengths.append(str(linelist[x]).strip('\n'))
        x += 1
    summation = []
    x = 0
    for strength in strengths:
        print str(strengths[x]) + ',' + str(rxcui[x])
        summation.append(str(strengths[x]) + ',' + str(rxcui[x]))
        x += 1
    return summation

def print_file(x):
    msg = ""
    with open('.out.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            msg += row
        print "GOT: " + msg
    return msg
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
        for rxcui in item:
            RxCui.append(rxcui)
        x += 1

    summation = []
    x = 0
    print RxCui
    strengths=1
    for strengthvar in json[2]['STRENGTHS_AND_FORMS'][x]:
        print strengthvar
        if(len(strengthvar) > 1):
            strengths = len(strengthvar)
    print "FORMS: " + str(strengths) 
    for item in variations:
        if(len(json[2]['RXCUIS'][x]) > 1):
            summation.append(str(variations[x]) + str((iterate_list(RxCui,x,x+len(json[2]['RXCUIS'][x])))) + str(iterate_list(json[2]['STRENGTHS_AND_FORMS'][x],0,len(json[2]['STRENGTHS_AND_FORMS'][x]))).replace(',,',','))
            x += len(json[2]['STRENGTHS_AND_FORMS'][x])
        else:
            summation.append(str(variations[x]) + ',' + str(RxCui[x]).strip('[u\']') + ',0')
            x += 1

    return summation
