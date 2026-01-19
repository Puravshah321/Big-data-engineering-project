import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

URLS = [
    "https://www.daiict.ac.in/faculty",
    "https://www.daiict.ac.in/adjunct-faculty",
    "https://www.daiict.ac.in/adjunct-faculty-international",
    "https://www.daiict.ac.in/distinguished-professor",
    "https://www.daiict.ac.in/professor-practice"
]

BASE = "https://www.daiict.ac.in"

headers = {
    "User-Agent": "Mozilla/5.0"
}

faculty_list = []

# -------------------------
# Profile page scraper
# -------------------------
def scrape_profile(profile_url):
    try:
        r = requests.get(profile_url, headers=headers, timeout=15)
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

    # Biography
    bio_div = soup.find("div", class_="about")
    if bio_div:
        data["Biography"] = " ".join(
            p.text.strip() for p in bio_div.find_all("p") if p.text.strip()
        )

    # Helper for sections
    def extract_section(title):
        h2 = soup.find("h2", string=lambda x: x and title.lower() in x.lower())
        if not h2:
            return "N/A"

        content = []
        for sib in h2.find_next_siblings():
            if sib.name == "h2":
                break
            for tag in sib.find_all(["p", "li"]):
                if tag.text.strip():
                    content.append(tag.text.strip())

        return ", ".join(content) if content else "N/A"

    data["Research Interests"] = extract_section("Specialization")
    data["Teaching"] = extract_section("Teaching")

    # Publications
    pub_div = soup.find("div", class_="education") or soup.find("div", class_="overflowContent")
    if pub_div:
        pubs = [li.text.strip() for li in pub_div.find_all("li") if li.text.strip()]
        if pubs:
            data["Publications"] = " | ".join(pubs)

    return data


# -------------------------
# MAIN SCRAPING LOOP
# -------------------------
for URL in URLS:
    print(f"\n🔹 Fetching: {URL}")
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    all_faculty = soup.select(
        "div.facultyDetails, div.views-row, article.node"
    )
    print(f"Found {len(all_faculty)} faculty on this page")

    for faculty in all_faculty:

        # Profile link (MOST IMPORTANT)
        link_tag = faculty.find("a", href=True)
        link = link_tag["href"] if link_tag else "N/A"
        full_link = link if link.startswith("http") else BASE + link if link != "N/A" else "N/A"

        # Name
        name = link_tag.text.strip() if link_tag and link_tag.text.strip() else "N/A"

        # Qualification
        edu = faculty.find(class_="facultyEducation")
        qualification = edu.text.strip() if edu else "N/A"

        # Phone
        phone = faculty.find(class_="facultyNumber")
        phone = phone.text.strip() if phone else "N/A"

        # Address
        address = faculty.find(class_="facultyAddress")
        address = address.text.strip() if address else "N/A"

        # Email
        email = faculty.find(class_="facultyEmail")
        email = email.text.strip() if email else "N/A"

        # Specialization
        spec = faculty.find(class_="areaSpecialization")
        specialization = spec.text.strip() if spec else "N/A"

        # Image
        img = faculty.find("img")
        image_url = img["src"] if img and img.get("src") else "N/A"

        # Profile page
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

print("\n✅ DONE! Total faculty scraped:", len(faculty_list))
