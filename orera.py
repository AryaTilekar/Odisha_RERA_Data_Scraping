import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def setup_driver():
    """Initialize and configure the Chrome WebDriver in headless mode."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def extract_project_details(driver, project_url):
    """Scrape project and promoter details from an individual project page."""
    driver.execute_script("window.open(arguments[0]);", project_url)
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    rera_no = soup.find("strong", string="RERA Regd. No:")
    project_name = soup.find("strong", string="Project Name:")

    rera_no = rera_no.find_next().text.strip() if rera_no else "N/A"
    project_name = project_name.find_next().text.strip() if project_name else "N/A"

    try:
        driver.find_element(By.LINK_TEXT, "Promoter Details").click()
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        promoter_name = soup.find("strong", string="Company Name:")
        promoter_address = soup.find("strong", string="Registered Office Address:")
        gst_no = soup.find("strong", string="GST No:")

        promoter_name = promoter_name.find_next().text.strip() if promoter_name else "N/A"
        promoter_address = promoter_address.find_next().text.strip() if promoter_address else "N/A"
        gst_no = gst_no.find_next().text.strip() if gst_no else "N/A"
    except:
        promoter_name = promoter_address = gst_no = "N/A"

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return {
        "RERA Regd. No": rera_no,
        "Project Name": project_name,
        "Promoter Name": promoter_name,
        "Promoter Address": promoter_address,
        "GST No": gst_no
    }

def save_to_csv(data, filename="rera_projects.csv"):
    """Save list of project dictionaries to a CSV file."""
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")

def main():
    url = "https://rera.odisha.gov.in/projects/project-list"
    driver = setup_driver()

    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    view_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")[:6]
    project_urls = [link.get_attribute("href") for link in view_links]

    all_projects = []
    for url in project_urls:
        details = extract_project_details(driver, url)
        all_projects.append(details)

    driver.quit()
    save_to_csv(all_projects)

if __name__ == "__main__":
    main()

