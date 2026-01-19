import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

URL = "https://www.daiict.ac.in/faculty"
BASE = "https://www.daiict.ac.in"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------
# Fetch main page
# -------------------------
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

faculty_list = []
all_faculty = soup.find_all("div", class_="facultyDetails")

# -------------------------
# Profile page scraper
# -------------------------
def scrape_profile(profile_url):
    try:
        r = requests.get(profile_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return {
            "Biography": "N/A",
            "Research Interests": "N/A",
            "Teaching": "N/A",
            "Publications": "N/A"
        }

    data = {
        "Biography": "N/A",
        "Research Interests": "N/A",
        "Teaching": "N/A",
        "Publications": "N/A"
    }

    # -------------------------
    # Biography
    # -------------------------
    bio_div = soup.find("div", class_="about")
    if bio_div:
        paragraphs = bio_div.find_all("p")
        data["Biography"] = " ".join(
            p.text.strip() for p in paragraphs if p.text.strip()
        )

    # -------------------------
    # Helper for h2 sections
    # -------------------------
    def extract_section(heading_text):
        h2 = soup.find("h2", string=lambda x: x and heading_text.lower() in x.lower())
        if not h2:
            return "N/A"

        content = []
        for sib in h2.find_next_siblings():
            if sib.name == "h2":
                break

            for p in sib.find_all("p"):
                if p.text.strip():
                    content.append(p.text.strip())

            for li in sib.find_all("li"):
                if li.text.strip():
                    content.append(li.text.strip())

        return ", ".join(content) if content else "N/A"

    # -------------------------
    # Research / Teaching
    # -------------------------
    data["Research Interests"] = extract_section("Specialization")
    data["Teaching"] = extract_section("Teaching")

    # -------------------------
    # Publications (DEEP SCRAPE)
    # -------------------------
    pub_div = soup.find("div", class_="education overflowContent")
    publications = []

    if pub_div:
        current_section = None

        for tag in pub_div.find_all(["h4", "li"]):
            if tag.name == "h4":
                current_section = tag.text.strip()
            elif tag.name == "li" and tag.text.strip():
                if current_section:
                    publications.append(f"{current_section} {tag.text.strip()}")
                else:
                    publications.append(tag.text.strip())

    if publications:
        data["Publications"] = " | ".join(publications)

    return data


# -------------------------
# Main loop
# -------------------------
for faculty in all_faculty:

    # Name
    name_tag = faculty.find("h3")
    name = name_tag.text.strip() if name_tag else "N/A"

    # Profile link
    link = name_tag.find("a")["href"] if name_tag and name_tag.find("a") else "N/A"
    full_link = link if link.startswith("http") else BASE + link if link != "N/A" else "N/A"

    # Qualification
    edu = faculty.find("div", class_="facultyEducation")
    qualification = edu.text.strip() if edu else "N/A"

    # Phone
    phone = faculty.find("span", class_="facultyNumber")
    phone = phone.text.strip() if phone else "N/A"

    # Address
    address = faculty.find("span", class_="facultyAddress")
    address = address.text.strip() if address else "N/A"

    # Email
    email = faculty.find("span", class_="facultyEmail")
    email = email.text.strip() if email else "N/A"

    # Specialization (summary)
    spec = faculty.find_next("div", class_="areaSpecialization")
    specialization = spec.text.strip() if spec else "N/A"

    # Image
    img = faculty.find_previous("img")
    image_url = img["src"] if img else "N/A"

    # -------- PROFILE PAGE --------
    if full_link != "N/A":
        print("Scraping:", full_link)
        profile_data = scrape_profile(full_link)
        time.sleep(1)
    else:
        profile_data = {
            "Biography": "N/A",
            "Research Interests": "N/A",
            "Teaching": "N/A",
            "Publications": "N/A"
        }

    faculty_list.append({
        "Name": name,
        "Profile URL": full_link,
        "Qualification": qualification,
        "Phone": phone,
        "Address": address,
        "Email": email,
        "Specialization": specialization,
        "Image URL": image_url,
        "Biography": profile_data["Biography"],
        "Research Interests": profile_data["Research Interests"],
        "Teaching": profile_data["Teaching"],
        "Publications": profile_data["Publications"]
    })


# -------------------------
# Save CSV
# -------------------------
df = pd.DataFrame(faculty_list)
df.to_csv("daiict_full_faculty_data.csv", index=False)

print("\n✅ DONE! File saved as daiict_full_faculty_data.csv")
