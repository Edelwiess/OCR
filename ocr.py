def ocr(img_path):
    import urllib, sys, re, base64
    from urllib import request, parse
    import ssl
    APIKey = 'yourbaiduAPIkey'
    SecretKey = 'yourbaidusecretkey'
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+APIKey+'&client_secret='\
           +SecretKey
    request1 = urllib.request.Request(host)
    request1.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request1)
    content = response.read()
    if (content):
        content = content.decode("utf-8")
        #print(content + '\n')

        tk = re.search(r'\"\d+\.+\S+\d+\"', content)
        if tk:
            tk = (tk.group(0))
            tk = tk.strip('\"')
            url1 = ('https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=' + tk)
            #print(url1)

    post_content = {}
    post_content['detect_direction'] = "false"


    with open(img_path, 'rb') as f1:
        image = f1.read()
        f1.close()

    img64 = base64.b64encode(image)
    post_content['image'] = img64
    decoded_post_content = parse.urlencode(post_content).encode('utf-8')
    req = urllib.request.Request(url=url1, data=decoded_post_content)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    response = request.urlopen(req)
    ocr_result = response.read()
    if ocr_result:
        ocr_result = ocr_result.decode("utf-8")
        #print(parsing_result)
    result = re.findall(r'\{\"words+\"\:+[^\}]*\}', ocr_result)
    formatted_result = []

    for i in range(len(result)):
        lines = result[i]
        lines = lines.strip('\{\"words\"\: \"')
        lines = lines.strip('\"\}')
        formatted_result.append(lines)

    return(formatted_result)
