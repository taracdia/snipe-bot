import config
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# To change the chrome driver version because chrome updated, go to programfiles 86/chromedriver/chromedriver.exe and replace it with new file

options = webdriver.ChromeOptions()
# Using profile data allows the user to bypass the two step verification
options.add_argument("user-data-dir=" + config.location)
# The screen needs to be maximized so that the filter options are visible on the page so they can be interacted with
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get("http://atoz.amazon.work/")

# --------Basic log in start------------
# Wrapping this in a try-catch block because if the user exits the program by closing the terminal window rather than the chrome window, the browser will still be logged in next time the program is run and trying to find the missing login component will crash the program if the exception is not handled
try:
    WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
        (By.NAME, "login"))).send_keys(config.username)
    driver.find_element_by_name("password").send_keys(config.password)
    driver.find_element_by_name("SubmitButton").send_keys(Keys.ENTER)
except:
    print("You are already logged in, no further action is needed")
# --------Basic log in finished------------
# Implicit wait will not be used because there are some conditions that need to be checked immediately and need to fail immediately if they are going to fail
wait = WebDriverWait(driver, 10)

# Click "Find Shifts"
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "bottom-right"))).click()

# Set appropriate hours as a filter
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//input[@aria-label='Start time']"))).send_keys("0900a")
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//input[@aria-label='End time']"))).send_keys("0500p")
for i in range(10):
    # Wait for loading element to appear and disappear
    try:
        spinner_wrapper = "//div[@class='atoz-spinner-wrapper']"
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, spinner_wrapper)))
        WebDriverWait(driver, 30).until_not(
            EC.presence_of_element_located((By.XPATH, spinner_wrapper)))
    except:
        print("No spinner")

    today = datetime.date.today()
    dayOffset = 2
    while (dayOffset < 14):
        # This is in case we get to the "sorry you were too slow for the shift" modal
        firstDay = today + datetime.timedelta(days=dayOffset)
        shiftDate = firstDay.strftime("%Y-%m-%d")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='daybutton-" + shiftDate + "']"))).click()
        try:
            # Try to add a shift by clicking "add" button. If there is no "add" button, go to the next day and try again
            driver.find_element(By.CLASS_NAME, "btn-add").click()
            try:
                # If someone else got the shift first, click the "Ok" button and get back to trying to get a shift. Do NOT increment the dayOffset counter so that the program tries again to get a shift on the same day
                driver.find_element(By.CLASS_NAME, "btn-primary").click()
                try:
                    error_spinner = "//div[@class='api-error-modal-header']"
                    driver.find_element((By.XPATH, error_spinner))
                    WebDriverWait(driver, 30).until_not(
                        EC.presence_of_element_located((By.XPATH, error_spinner)))
                except:
                    print("No error spinner")
            except:
                print("Got a shift at: ", shiftDate)
            finally:
                # Wait for loading element to appear and disappear
                TOAST_WRAPPER = "//div[@class='toast-wrapper']"
                WebDriverWait(driver, 5
                              ).until(EC.presence_of_element_located((By.XPATH, TOAST_WRAPPER)))
                WebDriverWait(driver, 30
                              ).until_not(EC.presence_of_element_located((By.XPATH, TOAST_WRAPPER)))
        except:
            dayOffset += 1
            # When we've looked at the first week, click to the next week. This ensures that the next week's "daybutton"s are available to be clicked
            if (dayOffset == 7):
                driver.execute_script(
                    "arguments[0].click();", driver.find_element(By.CLASS_NAME, "right"))
    driver.refresh()

# Tried to get shift but the loading spinner for "adding shift" took too long so shift gone then "sorry no shift" appears and then there is spinner again and then supposed to resume search but doesn't

# raceback (most recent call last):
#   File "bot.py", line 49, in <module>
#     wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='daybutton-" + shiftDate + "']"))).click()
# selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button id="daybutton-2021-01-27" data-testid="dayButton" class="dayButton btn btn-outline-primary" value="Wed Jan 27" role="tab" tabindex="0" aria-label="Wednesday, Jan 27. 2 shifts available" alt-text="Wednesday, Jan 27. 2 shifts available ">...</button> is not clickable at point (768, 131). Other element would receive the click: <div class="api-error-modal-header">...</div>
#   (Session info: chrome=87.0.4280.141)
