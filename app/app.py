from argparse import ArgumentParser
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select

from helper import get_credentials, get_day_name, get_account_details

if __name__ == "__main__":
  # Create optional command line arguments
  cli_parser = ArgumentParser()
  cli_parser.add_argument("--manual", "-m", help="Run and chose time manually", action="store_true")
  cli_args = cli_parser.parse_args()

  # Do the thing
  try:
    opts = Options()
    opts.headless = True
    driver = Firefox(options=opts)

    # Direct link to the amenities site
    driver.get("https://www.avalonaccess.com/Information/Information/Amenities")

    # Login
    email, password = get_credentials(cli_args.manual)
    
    driver.find_element_by_id("UserName").send_keys(email)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("submit-sign-in").click()

    # Collect account name and number
    name, account_num = get_account_details(driver)

    # Enter reservation screen
    driver.find_element_by_id("reserve").click()

    ### Fill out form ###

    # Chose reservation time
    # The script assumes reservations are being made for the current day
    # There is a calendar selector, but it defaults to the current day
    if cli_args.manual:
      selection = driver.find_element_by_id("SelStartTime") 
      options = [option for option in selection.find_elements_by_tag_name("option")]
      
      print("Available time slots:\n")

      itr = 0
      for element in options:
        print(f"{itr}: " + element.get_attribute("value"))
        itr += 1

      choice = int(input("\nPlease enter integer value for preferred time slot: "))

      selection = Select(driver.find_element_by_id("SelStartTime"))
      selection.select_by_index(choice)
    else:
      # Default behavior is to reserve 4:00pm for the current day
      day = get_day_name()
      selection = Select(driver.find_element_by_id("SelStartTime"))
      selection.select_by_value(f"{day}-4:00 PM-5:00 PM")

    # Fill out number of people field (has to be 1)
    driver.find_element_by_id("NumberOfPeople").clear()
    driver.find_element_by_id("NumberOfPeople").send_keys("1")

    # Enter name for reservation
    driver.find_element_by_id("ReservationNames").send_keys(name)

    # Agree to TOS and submit form
    driver.find_element_by_id("reservation-terms").click()
    driver.find_element_by_id("submit-new-reservation").click()

  finally:
    driver.close()

  # After the form is submitted, an email with a link to a consent form will be sent to the user
  # Ask the user for the link, and fill out the consent form if they want
  form_url = input("Please paste the link to the consent form here (enter \"skip\" to skip): ")
  form_url = form_url.strip()

  if form_url.lower() == "skip":
    print("Reservation made, don't forget to fill out the consent form manually!\n")
  else:
    fill_consent_form(form_url, email, account_num)

def fill_consent_form(form_url, email, account_num):
  try:
    opts = Options()
    opts.headless = True
    driver = Firefox(options=opts)

    driver.get(form_url)

    # The form asks the user if they have any symptoms of COVID-19 or if they have tested positive
    # The bot selects no for every answer (as is required to make the reservation)
    # Again, a reminder to only do this if the answers are actually no - be safe, don't spread
    selection = Select(driver.find_element_by_id("testedPositive"))
    selection.select_by_value("No")
    selection = Select(driver.find_element_by_id("symptoms"))
    selection.select_by_value("No")
    selection = Select(driver.find_element_by_id("closeContact"))
    selection.select_by_value("No")
    selection = Select(driver.find_element_by_id("travelQuarantine"))
    selection.select_by_value("No")

    # Enter email and account number
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("accountId").send_keys(account_num)

    # Submit
    driver.find_element_by_id("formButton").click()
    
  finally:
    driver.close()
