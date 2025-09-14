import requests
from bs4 import BeautifulSoup
import csv
import os

bill_year = 2025
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
    Downloads a webpage, extracts data from the <dl> and details-tab-info sections,
    and saves it to a CSV file using shared extraction functions.
    """
    from extract_bill_info import extract_top_box, extract_details_tab_info, write_bill_summary_to_csv
    
    url = f"https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/hb{bill_number:04d}?ys={bill_year}RS"
    output_filename = f"{bill_folder}/bill_{bill_number:04d}_summary.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        top_box = extract_top_box(soup)
        details_tab = extract_details_tab_info(soup)
        csv_data = {
            'Title': top_box.get('Title', ''),
            'Sponsored by': top_box.get('Sponsored by', ''),
            'Status': top_box.get('Status', ''),
            'Synopsis': details_tab.get('Synopsis', ''),
            'Committees': details_tab.get('Committees', ''),
        }
        write_bill_summary_to_csv(csv_data, output_filename)
        print(f"Successfully scraped data and saved to {output_filename}")
        print("\nExtracted Data:")
        for field, value in csv_data.items():
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
    for bill_num in range(1, 2000):  # Loop for numbers 0001 to 0010
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