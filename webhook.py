from itty import *
import urllib2
import json
import requests
import os
from json_compiler import form_list_of_variations
from json_compiler import form_strength_variations

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    
def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    
    return contents
def matching_interaction(interaction):
    return interaction['interactionConcept'][1]['sourceConceptItem']['name'] + ' (RXCUI: ' + interaction['interactionConcept'][1]['minConceptItem']['rxcui'] + ') ' + 'has been determined to have the following effect:\n' +  interaction['description'] + '\nVisit this website for further information on ' + interaction['interactionConcept'][1]['sourceConceptItem']['name'] + '\n' + interaction['interactionConcept'][1]['sourceConceptItem']['url']


def get_variation(json):  #Pulls Variations of a prescription from JSON output
    with open('.variations.txt') as f: 
        variations = f.readlines()
        for variation in variations:
                variations = json[1]
    return variations

def send_request(scanurl):   #This function makes a request to the X-Force Exchange API using a specific URL and headers.
    fullurl = scanurl
    response = requests.get(fullurl, params='',timeout=20)
    all_json = response.json()
    return all_json

def choose_strength(line):
    rxcui_count = 0
    linelist = line.split(',')
    for entry in linelist[1:]:
        print "CHECKING: " + str(entry)
        if(re.search('[a-zA-Z]',entry) is None):
            rxcui_count += 1
        else:
            break
    x = 0
    strengths = []
    with open('.strength_variations.txt','w+') as f:
        strengths = form_strength_variations(rxcui_count,linelist)
        for strength in strengths:
            f.write(strength + '\n')
            print strength
            x += 1
        f.close()
    with open(".strength_choose_flag",'w') as f:
        f.write('1')
        f.close()
    return strengths 

def updated_strength_flag():
    updated_flag = 0
    with open('.strength_choose_flag') as f:
        lines = f.readlines()
        for line in lines:
            updated_flag = line[0]
        f.close()
    return updated_flag

def get_specific_strength(number):   #Get's the specific variation of a prescription that is described by the user
    strength_line = ""
    with open('.strength_variations.txt') as f:
        lines = f.readlines()
        line_count = 0
        for line in lines:
            print line.split(',')
            if(number == 0):
                strength_line = get_strength(line.split(','))
                break
            if(line_count == number):
                strength_line = get_strength(line.split(','))
                print line
                break
            else:
                line_count += 1 
    return strength_line
    
def get_specific_variation(number):   #Get's the specific variation of a prescription that is described by the user
    rxcui_line = ""
    with open('.variations.txt') as f:
        lines = f.readlines()
        line_count = 0
        for line in lines:
            print line.split(',')
            if(number == 0 and line.split(',')[2] == '0\n'):
                rxcui_line = get_rxcui(line.split(','))
                break
            if (number == 0 and line.split(',')[2] != '0\n'):
                rxcui_line = choose_strength(line)
                break 
            if(line_count == number and line.split(',')[2] == '0\n'):
                rxcui_line = get_rxcui(line.split(','))
                print line
                break
            if (number == line_count and line.split(',')[2] != '0\n'):
                rxcui_line = choose_strength(line)
                break
            else:
                line_count += 1 
    return rxcui_line
               
def get_rxcui(line):         #Returns the list of RXCUIs that comes with a specific variation of a prescription
    return line[1]

def get_strength(line):
    return line[1]
@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    /batman    - replies to the room with text
    /batcave   - echoes the incoming text to the room
    /batsignal - replies to the room with an image
    """
    with open('.strength_choose_flag') as f:
        lines = f.readlines()
        for line in lines:
            strength_choose_flag = line[0]
            f.close()
 
    with open('.gotrxcui.txt') as f:
        lines = f.readlines()
        for line in lines:
            gotrxcui = line[0]
            f.close()
    with open('.lastrxcuireported.txt') as f:
        lines = f.readlines()
        for line in lines:
            lastrxcui = line
            f.close()
    with open('.prescription_count.txt') as f:
        lines = f.readlines()
        for line in lines:
            prescription_count = line[0]      
            f.close()
    with open('.variation_flag.txt') as f:
        lines = f.readlines()
        for line in lines:
            variation_flag = line[0]
            f.close()
    with open(".num_prescription_flag.txt") as f:
        lines = f.readlines()
        for line in lines:
            num_prescription_flag = line[0]
        print num_prescription_flag
        f.close()
    with open(".got_count_flag.txt") as f:
        lines = f.readlines()
        for line in lines:
            got_count = line[0]
        f.close()
    with open(".search_4_interactions.txt") as f:
        lines = f.readlines()
        for line in lines:
            search_interaction_flag = line[0]
        f.close()


    print "COUNT: " + str(got_count)
    webhook = json.loads(request.body)
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    print result
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        
        if('exit' in in_message or 'reset' in in_message):
            os.system('python reset_all_flags.py')
            msg = "You're Session has been reset. Please ask to check your prescriptions"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        if 'check' and 'prescription' in in_message:
            msg = "How many prescriptions are you taking?"
            with open(".num_prescription_flag.txt",'w') as fin:
                fin.write("1")
                fin.close()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        if (int(num_prescription_flag) == 1 and int(got_count) == 0) and ('exit' or 'reset' not in in_message):
            print "HERE"
            prescription_count = int(in_message)
            with open('.precription_count','w') as f:
                f.write(str(prescription_count))
                f.close()
            with open('.got_count_flag.txt','w') as f:
                f.write('1')
                f.close()
            msg = "What is the name of your first prescription?"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        if int(num_prescription_flag) == 1 and int(got_count) == 1 and int(variation_flag) == 0 and 'exit' and 'reset' not in in_message: 
            print "WOWOEY"
            name_of_drug = in_message.lower()
            url = 'https://clin-table-search.lhc.nlm.nih.gov/api/rxterms/v3/search?terms=' + name_of_drug + '&ef=STRENGTHS_AND_FORMS,RXCUIS'
            json_output = send_request(url)
            print json_output
            variations = get_variation(json_output) 
            x=1
            variations = form_list_of_variations(json_output)
            msg = "Which variation below is yours?\n"
            with open('.variations.txt','w+') as f: 
                for variation in variations:
                    f.write(variation + '\n')
                    print variation
                    x += 1
                f.close()    
            x=0
            for variation in variations:
                msg += str(x) + '. ' +  variation.split(',')[0] + '\n'
                x += 1
            with open('.variation_flag.txt','w') as f:
                f.write('1')
                f.close()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        if(strength_choose_flag  == '1'):
            if(int(search_interaction_flag) == 1):
                last_json = ""
		with open('.latestinteraction') as infile:
		   last_json = json.load(infile)
		for interaction in last_json['interactionTypeGroup'][0]['interactionType'][0]['interactionPair']:
		    if interaction['interactionConcept'][1]['sourceConceptItem']['name'].lower() in in_message:
			msg = matching_interaction(interaction) 
			break
		    else:
			msg = "No Matches Found."
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            else:
		strength = get_specific_strength(int(in_message))
		msg = "The RXCUI of your prescription based on your selected dosage is " + str(strength)
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
		with open('.gotrxcui.txt','w') as f:
		    f.write('1')
		    f.close()
		with open('.lastrxcuireported.txt','w') as f:
		    f.write(str(strength))
		    f.close()
		url = 'https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui=' + strength
		requester = urllib2.Request(url)
		json_output = urllib2.urlopen(requester).read()
		json_output = json.loads(json_output)
		with open('.latestinteraction','w') as outfile:
		    json.dump(json_output,outfile)
		    outfile.close()
		x = 0
		x = len(json_output['interactionTypeGroup'][0]['interactionType'][0]['interactionPair'])
		msg = 'Total # of Interaction Pairs: ' + str(x)
		with open(".search_4_interactions.txt",'w') as f:
		    f.write('1')
		    f.close()
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
		msg = 'To search the list of interactions, type in a drug to search for, otherwise simply respond with \'exit\' or \'reset\''
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})

        if int(variation_flag) == 1 and int(strength_choose_flag) == 0 and int(search_interaction_flag) == 0 and 'exit' and 'reset' not in in_message:
            rxcui = get_specific_variation(int(in_message))
            print "CURRENT RXCUI SEARCH: " + str(rxcui)
            if (updated_strength_flag() == '1'):
                x = 0
                print "MADE IT"
                msg = 'Please choose your specific dose below: \n'
                for strength in rxcui:
                    msg += str(x) + '.' + strength.split(',')[0] + '\n'
                    x += 1
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
            else:
                msg = "The RXCUI of your prescription is " + str(rxcui)
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})    
                with open('.gotrxcui.txt','w') as f:
                    f.write('1')
		    f.close()
		with open('.lastrxcuireported.txt','w') as f:
		    f.write(str(rxcui))
		    f.close()
		url = 'https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui=' + rxcui 
		requester = urllib2.Request(url)
		json_output = urllib2.urlopen(requester).read()
		json_output = json.loads(json_output)
		with open('.latestinteraction','w') as outfile:
		    json.dump(json_output,outfile)
		    outfile.close()
		x = 0 
		x = len(json_output['interactionTypeGroup'][0]['interactionType'][0]['interactionPair'])
		msg = 'Total # of Interaction Pairs: ' + str(x)
		with open('strength_choose_flag','w') as f:
                    f.write('0')
                    f.close()
                with open(".search_4_interactions.txt",'w') as f:
		    f.write('1')
		    f.close()
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
		msg = 'To search the list of interactions, type in a drug to search for, otherwise simply respond with \'exit\' or \'reset\''
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        if(int(search_interaction_flag) == 1 and int(strength_choose_flag) == 0):
            last_json = ""
            with open('.latestinteraction') as infile:
               last_json = json.load(infile)
            for interaction in last_json['interactionTypeGroup'][0]['interactionType'][0]['interactionPair']:
                if interaction['interactionConcept'][1]['sourceConceptItem']['name'].lower() in in_message:
                    msg = matching_interaction(interaction) 
                    break
                else:
                    msg = "No Matches Found."
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


    
    return "true"
            
    

 
####CHANGE THESE VALUES#####
bot_email = "connectmetodoctor@sparkbot.io"
bot_name = "Cisco_Spark_Challenge"
bearer = "MzM5ZjU1NzMtMjY1NC00ODdmLThkZjItNjRhYjYyYzY4YzI4YWYyNjdmNzUtMDcy"
run_itty(server='wsgiref', host='0.0.0.0', port=100)
if KeyboardInterrupt:
    print "INTERRUPT"
    os.system('python reset_all_flags.py')
   
