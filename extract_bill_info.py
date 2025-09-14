
import sys
import csv
from bs4 import BeautifulSoup

# Usage: python extract_bill_info.py test.html

def extract_top_box(soup):
    result = {}
    top_box = soup.find('dl', class_='row top-box')
    if not top_box:
        return result
    dt_dd = list(top_box.children)
    key = None
    for tag in top_box.find_all(['dt', 'dd'], recursive=False):
        if tag.name == 'dt':
            key = tag.get_text(strip=True)
        elif tag.name == 'dd' and key:
            result[key] = tag.get_text(strip=True)
            key = None
    return result

def extract_details_tab_info(soup):
    result = {}
    details_tab = soup.find('div', class_='row details-tab-info')
    if not details_tab:
        return result
    # Find all rows inside details-tab-info
    for row in details_tab.find_all('div', class_='row', recursive=True):
        cols = row.find_all('div', recursive=False)
        if len(cols) >= 2:
            label = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            if label == 'Synopsis':
                result['Synopsis'] = value
            elif label == 'Committees':
                # Committees may have links, get text from all links
                committees = []
                for a in cols[1].find_all('a'):
                    committees.append(a.get_text(strip=True))
                result['Committees'] = committees if committees else value
    return result


def write_bill_summary_to_csv(data, csv_path):
    """
    Write extracted data to a CSV file, one row per field (rotated/vertical format).
    """
    # If Committees is a list, join as string
    data = data.copy()

    if isinstance(data.get('Committees'), list):
        data['Committees'] = '; '.join(data['Committees'])

    # Add a space after 'Delegate' or 'Delegates' in 'Sponsored by' value
    sponsored = data.get('Sponsored by')
    if sponsored:
        import re
        # Add a space after 'Delegate' or 'Delegates' if not already followed by a space
        sponsored = re.sub(r'\b(Delegate|Delegates)(?=[A-Za-z])', r'\1 ', sponsored)
        # Also handle cases like 'Delegate,Name' (add space after comma)
        sponsored = re.sub(r'(Delegate|Delegates),', r'\1, ', sponsored)
        # Remove double spaces if any
        sponsored = re.sub(r'  +', ' ', sponsored)
        data['Sponsored by'] = sponsored.rstrip(" ")  # Remove trailing space if any

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Field', 'Value'])
        for key, value in data.items():
            writer.writerow([key, value])

def main(html_path):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    top_box = extract_top_box(soup)
    details_tab = extract_details_tab_info(soup)
    print('Top Box:')
    for k in ['Title', 'Sponsored by', 'Status']:
        print(f'{k}: {top_box.get(k, "N/A")}')
    print('\nDetails Tab Info:')
    print(f'Synopsis: {details_tab.get("Synopsis", "N/A")}')
    print(f'Committees: {details_tab.get("Committees", "N/A")}')

    # Combine all data for CSV
    csv_data = {
        'Title': top_box.get('Title', ''),
        'Sponsored by': top_box.get('Sponsored by', ''),
        'Status': top_box.get('Status', ''),
        'Synopsis': details_tab.get('Synopsis', ''),
        'Committees': details_tab.get('Committees', ''),
    }
    write_bill_summary_to_csv(csv_data, 'bill_info_output.csv')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python extract_bill_info.py test.html')
        sys.exit(1)
    main(sys.argv[1])
