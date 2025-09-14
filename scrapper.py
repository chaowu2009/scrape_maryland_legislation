import requests
from bs4 import BeautifulSoup
import csv
import os

bill_year = 2024
bill_folder = f'md_house_bill_{bill_year}'

os.makedirs(bill_folder, exist_ok=True)

def download_pdf(url, filename):
    """Downloads a PDF file from a given URL and saves it."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {filename}: {e}")

def scrape_and_save_dl_table(bill_number):
    """
    Downloads a webpage, extracts data from a <dl> list within a specified
    class, and saves it to a CSV file.
    """
    url = f"https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/hb{bill_number:04d}?ys={bill_year}RS"
    output_filename = f"{bill_folder}/bill_{bill_number:04d}_summary.csv"
    try:
        # Step 1: Download the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        
        # Step 2: Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 3: Find the specific <dl> element by its class
        dl_element = soup.find('dl', class_='row top-box')
        
        if not dl_element:
            print("Could not find the 'row top-box' element on the page.")
            return

        # Step 4: Extract the data
        extracted_data = {}
        dt_tags = dl_element.find_all('dt')
        dd_tags = dl_element.find_all('dd')

        for dt, dd in zip(dt_tags, dd_tags):
            field_name = dt.get_text(strip=True)
            
            # Special handling for "Sponsored by" to get all names
            if field_name == "Sponsored by":
                # Find all <a> tags within the <dd> for sponsor names
                sponsor_names = [a.get_text(strip=True) for a in dd.find_all('a')]
                field_value = ", ".join(sponsor_names)
            # Special handling for "Analysis" to get link text
            elif field_name == "Analysis":
                link_text = dd.find('a').get_text(strip=True) if dd.find('a') else "N/A"
                field_value = link_text
            # General case for all other fields
            else:
                field_value = dd.get_text(strip=True)
            
            extracted_data[field_name] = field_value
            
        # Step 5: Save the data to a CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Field", "Value"])  # Write the header row
            for field, value in extracted_data.items():
                writer.writerow([field, value]) # Write the data rows

        print(f"Successfully scraped data and saved to {output_filename}")
        print("\nExtracted Data:")
        for field, value in extracted_data.items():
            print(f"- {field}: {value}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def scrape_witness_list(bill_number):
    """Scrapes witness list and saves it to a CSV file."""
    url = f"https://mgaleg.maryland.gov/mgawebsite/Legislation/WitnessSignup/HB{bill_number:04d}?ys={bill_year}RS"
    url = f"https://mgaleg.maryland.gov/mgawebsite/Legislation/WitnessSignup/HB0001?ys={bill_year}RS"
    filename = f"{bill_folder}/bill_{bill_number:04d}_witness_list.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', id ='legislationTestimony')
        if not table:
            print(f"No witness list found for HB{bill_number:04d}.")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Name", "Organization", "Position"])
            
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip the header row
                cols = row.find_all('td')
                if len(cols) >= 3:
                    name = cols[0].get_text(strip=True)
                    organization = cols[1].get_text(strip=True)
                    position = cols[2].get_text(strip=True)
                    writer.writerow([name, organization, position])
        
        print(f"Successfully saved witness list to {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error scraping witness list for HB{bill_number:04d}: {e}")
    except AttributeError:
        print(f"Could not find the witness list table for HB{bill_number:04d}.")

if __name__ == "__main__":
    for bill_num in range(1, 2500):  # Loop for numbers 0001 to 0010
        padded_bill_num = f"{bill_num:04d}"

        print(f"\n--- Processing Bill HB{padded_bill_num} ---")
        
        # 1) Download the bill PDF
        bill_pdf_url = f"https://mgaleg.maryland.gov/{bill_year}RS/bills/hb/hb{padded_bill_num}F.pdf"
        download_pdf(bill_pdf_url, f"{bill_folder}/bill_{padded_bill_num}.pdf")
        
        # 2) Scrape and save bill summary
        scrape_and_save_dl_table(bill_num)
        
        # 3) Download the fiscal note PDF
        last_digit = int(padded_bill_num[-1])
        fiscal_note_padded_bill_num = f"{last_digit:04d}"
        fiscal_note_url = f"https://mgaleg.maryland.gov/{bill_year}RS/fnotes/bil_{fiscal_note_padded_bill_num}/hb{padded_bill_num}.pdf"
        download_pdf(fiscal_note_url, f"{bill_folder}/bill_{padded_bill_num}_fiscal_note.pdf")
        
        # 4) Scrape and save witness list
        scrape_witness_list(bill_num)