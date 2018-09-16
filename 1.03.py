import urllib
import    sys, re, base64, json, csv, time
from urllib import request, parse
from pprint import pprint

def get_input_parameter(parameter):
    username_filter = re.search(r'User_Name=(\S+)', parameter)
    if username_filter:
        username = username_filter.group(1)
        print('Username: %s' % username)
    else:
        print('Wrong username, please check')
    password_filter = re.search(r'Password=(\S+)', parameter)
    if password_filter:
        password = password_filter.group(1)
        print('Password: %s' % password)
    else:
        print('Wrong password, please check')
    nburl_filter = re.search(r'NetBrain_URL=(\S+)', parameter)
    if nburl_filter:
        nburl = nburl_filter.group(1)
        print('NetBrain URL: %s' % nburl)
    else:
        print('Wrong URL, please check')
    Tenant_Name = re.search(r'Tenant_Name=(.*)', parameter)
    if Tenant_Name:
        tn_name = Tenant_Name.group(1)
        print('Tenant Name: %s' % tn_name)
    else:
        print('Wrong Tenant Name, please check')

    domain_name_filter = re.search(r'Domain_Name=(.*)', parameter)
    if domain_name_filter:
        domain_name = domain_name_filter.group(1)
        print('Domain name: %s' % domain_name)
    else:
        print('Wrong domain name, please check')

    dic = {'nburl': nburl,
           'username': username,
           'password': password,
           'Tenant_Name': tn_name,
           'Domain_Name': domain_name,
           }
    return dic

def getoken(nburl, username, password):
    nb_api_url = nburl + '/ServicesAPI/API/V1/Session'
    base64string = base64.encodebytes(bytes(username + ':' + password, 'utf8'))
    base64string = base64string.decode('utf8')
    base64string = base64string.strip('\n')
    token_req = urllib.request.Request(url=nb_api_url)
    token_req.add_header("Authorization", "Basic %s" % base64string)
    response_nb = urllib.request.urlopen(token_req)
    token_content = response_nb.read()
    if token_content:
        token_content = token_content.decode('utf-8')
    re_token = re.search(r'token\":\"+\S+\"+,', token_content)
    token = re_token.group(0)
    token = token.strip('token\":')
    token = token.strip('\",')
    return (token)


def get_tenantid(nburl, token):
    nb_tenantid_url = nburl + '/ServicesAPI/API//V1/CMDB/Tenants?Token=' + token
    request_nb = urllib.request.Request(nb_tenantid_url)
    response_nb = urllib.request.urlopen(request_nb)
    tn_content = response_nb.read()
    if tn_content:
        tn_content = tn_content.decode('utf-8')
    return (tn_content)

def search_tenant(tnname, tn_content):
    tn_key_word = tnname
    if tn_key_word in tn_content:
        tn_object = re.search(r'\S{36}","tenantName":"' + tn_key_word + '\"', tn_content)
        if tn_object:
            tn_string = tn_object.group(0)
            tnid = tn_string[0:36]
            #tnid = tn_string.strip(r'"tenantName":"%s' % tn_key_word)
            #tnid = tnid.strip(r'",')
            return (tnid)

def get_domainid(nburl, token, tenantId):
    nb_domainid_url = nburl + '/ServicesAPI/API//V1/CMDB/Domains?Token=' + token + '&tenantId=' + tenantId
    request_nb = urllib.request.Request(nb_domainid_url)
    response_nb = urllib.request.urlopen(request_nb)
    dm_content = response_nb.read()
    if dm_content:
        dm_content = dm_content.decode('utf-8')
    return(dm_content)


def search_domain(dmname, dm_content):
    dm_key_word = dmname
    if dm_key_word in dm_content:

        dm_object = re.search(r'\S{36}","domainName":"' + dm_key_word +'\"', dm_content)
        if dm_object:
            tn_string = dm_object.group(0)
            #print (tn_string)
            dmid = tn_string[0:36]
            return (dmid)

def specify_domain(nburl, token, tnid, dmid):
    NetBrain_API_Address = nburl + '/ServicesAPI/API//V1/Session/CurrentDomain'
    data = ("""{
  "tenantId": "%s",
  "domainId": "%s"
}
""" % (tnid, dmid))
    en_data = data.encode('utf-8')
    request_nb = urllib.request.Request(url=NetBrain_API_Address, data=en_data)
    request_nb.add_header("Token", token)
    request_nb.add_header("Content-Type", 'application/json')
    request_nb.get_method = lambda: 'PUT'
    response_nb = urllib.request.urlopen(request_nb)
    cu_domain_result = response_nb.read()
    if cu_domain_result:
        cu_domain_result = cu_domain_result.decode('utf-8')
    return (cu_domain_result)

def get_oneiptable(nburl, token):
    NetBrain_API_Address = nburl + '/ServicesAPI/API//V1/CMDB/Topology/OneIPTable?Token=' +token +'&beginIndex=0&count=0'
    request_nb = urllib.request.Request(NetBrain_API_Address)
    response_nb = urllib.request.urlopen(request_nb)
    oneip_content = response_nb.read()
    if oneip_content:
        oneip_content = oneip_content.decode('utf-8')
    return(oneip_content)

def write_json(oneip_content):
    json_one_ip_table = json.loads(oneip_content)
    f = open('OneIPTable.json', 'w+')
    json.dump(json_one_ip_table, f, indent=2)
    f.close()

#json2csv


##
# Convert to string keeping encoding in mind...
##
def to_string(s):
    try:
        return str(s)
    except:
        # Change the encoding type if needed
        return s.encode('utf-8')


##
# This function converts an item like
# {
#   "item_1":"value_11",
#   "item_2":"value_12",
#   "item_3":"value_13",
#   "item_4":["sub_value_14", "sub_value_15"],
#   "item_5":{
#       "sub_item_1":"sub_item_value_11",
#       "sub_item_2":["sub_item_value_12", "sub_item_value_13"]
#   }
# }
# To
# {
#   "node_item_1":"value_11",
#   "node_item_2":"value_12",
#   "node_item_3":"value_13",
#   "node_item_4_0":"sub_value_14",
#   "node_item_4_1":"sub_value_15",
#   "node_item_5_sub_item_1":"sub_item_value_11",
#   "node_item_5_sub_item_2_0":"sub_item_value_12",
#   "node_item_5_sub_item_2_0":"sub_item_value_13"
# }
##
def reduce_item(key, value):
    global reduced_item

    # Reduction Condition 1
    if type(value) is list:
        i = 0
        for sub_item in value:
            reduce_item(key + '_' + to_string(i), sub_item)
            i = i + 1

    # Reduction Condition 2
    elif type(value) is dict:
        sub_keys = value.keys()
        for sub_key in sub_keys:
            reduce_item(key + '_' + to_string(sub_key), value[sub_key])

    # Base Condition
    else:
        reduced_item[to_string(key)] = to_string(value)

if __name__ == '__main__':
    # Get input parameter #
    input_string = open('config.txt')
    parameter = input_string.read()
    #get_input_parameter(parameter)
    parameter_dic = get_input_parameter(parameter)
    input_string.close()

    username = parameter_dic['username']
    password = parameter_dic['password']
    nburl = parameter_dic['nburl']
    Tenant_Name = parameter_dic['Tenant_Name']
    Domain_Name = parameter_dic['Domain_Name']
    print('Connecting to the Server, please wait...')
    token = getoken(nburl ,username, password)
    print('Successfully connected to the server, the token is %s' % token)

    print('Getting Tenant id...')
    tn_result = get_tenantid(nburl ,token)
    print('Got Tenant information raw data:\n %s\n' % tn_result)
    tnid = search_tenant(Tenant_Name, tn_result)
    print('Got Tenant id: %s\n' % tnid)

    print('Getting Domain id...')
    dm_content = get_domainid(nburl, token, tnid)
    print('Got Domain information raw data:\n %s\n' % dm_content)
    dmid = search_domain(Domain_Name, dm_content)
    print('Got domain id: %s\n' % dmid)


    print('Setting current domain to <%s> (id:%s)' % (Domain_Name , dmid))
    cudomain_result = specify_domain(nburl, token, tnid, dmid)
    print('Succeed\n')


    print('Retrieving One-IP-Table...')
    json_OneIPTable = get_oneiptable(nburl, token)
    # export CSV
    # Reading arguments
    node = 'OneIPList'
    #json_file_path = 'OneIPTable02.json'
    cutime = time.strftime("%Y%m%d%H%M%S")
    csv_file_path = ('OneIPTable-%s.csv' % cutime)

    #fp = open(json_file_path, 'r')
    #json_value = fp.read()
    #raw_data = json.loads(json_value)
    raw_data = json.loads(json_OneIPTable)

    try:
        data_to_be_processed = raw_data[node]
    except:
        data_to_be_processed = raw_data

    processed_data = []
    header = []
    for item in data_to_be_processed:
        reduced_item = {}
        reduce_item(node, item)

        header += reduced_item.keys()

        processed_data.append(reduced_item)

    header = list(set(header))
    header.sort()

    with open(csv_file_path, 'w+') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)

    print("Just completed exporting the OneIPTable-%s.csv file with %d columns" %  (cutime ,len(header)))
    input('Press any key to quit')

#Created by Edel Wang
