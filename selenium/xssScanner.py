import random
import sys
from selenium import webdriver
from autotest_lib.client.common_lib.cros import chromedriver
with chromedriver.chromedriver() as chromedriver_instance:
    driver = chromedriver_instance.driver
    driver = webdriver.chrome()
    url = sys.argv[1]
    driver.get(url)

ran_input=[]



def inital_form():
	#look for text and emial inputs and textarea
	if driver.find_element(By.XPATH, "//input[@type='text']"):		
		text_inputs= driver.find_elements(By.XPATH, "//input[@type='text']")
		for text_input in text_inputs:	
            #check if it has a pattern and is required
			if text_input.get_attribute('pattern'):
				if text_input.get_attribute('required'):
					print("there's a requried input with a specific text pattern required")
                else:
                    print("this isn't required")
			#otherwise generate random string and send keys
            else:
                ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                ran_input.append(ran)
                text_input.send_keys(ran)
                
    if driver.find_element(By.XPATH, '//textarea'):		
		textAreas= driver.find_elements(By.XPATH, "//textarea")
		for textArea in textAreas:			
			if textArea.get_attribute('pattern'):
				if textArea.get_attribute('required'):
					print("there's a requried input with a specific text pattern required")
			else:
                ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                ran_input.append(ran)
                textArea.send_keys(ran)
         
    if driver.find_element(By.XPATH, "//input[@type='email']"):		
		emails= driver.find_elements(By.XPATH, "//input[@type='email']")
		for email in emails:			
            ran = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            ran_input.append(ran)
            text_input.send_keys(ran + "@gmail.com")
    #find and click button to submit form        
    button=driver.find_element_by_xpath('//button[text]')
    button.click()

if __name__ == "__main__":
    inital_form()
    
			 
                                 
			
			
		
		
		
	
	
