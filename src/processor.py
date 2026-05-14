import json  # Serialize parsed job listings to JSON.
from pathlib import Path  # Work with filesystem paths safely.
from bs4 import BeautifulSoup  # Parse HTML job pages.
from pydantic import BaseModel, Field  # Define and validate job listing schema.

class JobListing(BaseModel):  # Schema for the extracted job listing fields.
    source_id: str  # JobStreet source ID or filename fallback.
    job_title: str  # Extracted job title text.
    company: str  # Company name text.
    description: str  # Job description text.
    # tech_stack: list[str] = Field(default_factory=list)  # Detected skills/techs.

# def extract_tech_stack(text: str) -> list[str]:  # Find known tech keywords in text.
#     if not text:  # Guard against empty description.
#         return []  # Return empty list when no text to scan.

#     keywords = {  # Canonical list of tech keywords to detect.
#         "python", "java", "javascript", "typescript", "c#", "c++", "go", "golang",
#         "ruby", "php", "scala", "kotlin", "swift", "rust",
#         "react", "vue", "angular", "svelte", "node", "node.js", "express",
#         "django", "flask", "fastapi", "spring", "spring boot", ".net", "laravel",
#         "mysql", "postgres", "postgresql", "sqlite", "mongodb", "redis",
#         "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
#         "pandas", "numpy", "spark", "hadoop", "airflow",
#     }

#     lowered = text.lower()  # Case-normalize for matching.
#     found = {kw for kw in keywords if kw in lowered}  # Collect matches.
#     return sorted(found)  # Return sorted list for stable output.

def process_all_html(input_dir, output_dir):  # Convert HTML files into JSON listings.
    input_path, output_path = Path(input_dir), Path(output_dir)  # Resolve paths.
    output_path.mkdir(parents=True, exist_ok=True)  # Ensure output folder exists.
    # parent - make directory if there isnt one
    # exits_ok - if already exits dont crash just skip this line

    html_files = list(input_path.glob("*.html"))  # Find all input HTML files. any file that matches this pattern
    total, processed, skipped = len(html_files), 0, 0  # Track progress counts.
    print("🥈 Silver:...")  # Status banner for the stage.

    for file_path in html_files:  # Iterate over each HTML file.
        try:  # Guard against parsing/IO errors per file.
            # with is a Context Manager - enture that resources (files, network connection, database) are automatic cleaned up of closed when done using them
            with open(file_path, 'r', encoding='utf-8') as f:  # Open HTML file. r as the file descriptor
                soup = BeautifulSoup(f, 'html.parser')  # Parse HTML content., other parser (lxml, xml, html5lib)

            # Extract source_id from og:url; fallback to filename stem
            og_url = soup.find("meta", property="og:url")  # Locate og:url meta.
            # Sample
            # <head>
            #     <meta charset="UTF-8">
            #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
            #     <meta property="og:url" content="https://www.seek.com.au/job/12345">
            #     <meta property="og:title" content="Python Developer Role">
            # </head>
            # return a tag body : <meta property="og:url" content="[https://site.com/job/123](https://site.com/job/123)">
            # ( tag that are searching, filter with this property ) - search for first item that matches
            # open graph is like a passport 
            # passport number  - og:url (unique)
            # full name - og:title
            # photo - og:image
            # citisenship - og:type

            sid = og_url["content"].rstrip('/').split('/')[-1] if og_url else None  # Parse ID.
            # convert 
            # [https://www.seek.com.au/job/7891234/](https://www.seek.com.au/job/7891234/)
            # ['https:', '', '[www.seek.com](https://www.seek.com).au', 'job', '7891234']

            if not sid:  # Fallback when og:url is missing.
                sid = file_path.stem  # Use filename stem as source_id.

            title_container = soup.find(attrs={"data-automation": "job-detail-title"})
            title = title_container.get_text(separator=" ", strip=True) if title_container and title_container.get_text(strip=True) else None  # Title text.
            # Sample
            # <h1 data-automation="job-detail-title" class="css-1abc123">
            #     Senior Software Engineer
            # </h1>
            # Extract from data attributes  # Title node.

            

            # only use get_text when it is wrapper word 
            # for open graph since is attribute so done need get_text
            # separator ensure if there are more attribute in the tag thn seperate with space " "
            # strip removes unnecesarry newline and spaces

            # if not title:  # Fallback if job-detail-title missing.
            #     # Fallback to page <title>
            #     page_title = soup.find('title')  # Document title node.
            #     if page_title and " Job in " in page_title.get_text():  # JobStreet pattern.
            #         title = page_title.get_text().split(" Job in ")[0].strip()  # Trim location.

            # if not title:  # Final fallback attempts.
            #     # Additional fallback to og:title or h1
            #     og_title = soup.find("meta", property="og:title")  # og:title meta.
            #     if og_title and og_title.get("content"):  # Use og:title when present.
            #         title = og_title.get("content").strip()  # Title from meta.
            #     else:
            #         h1 = soup.find("h1")  # First h1 tag as fallback.
            #         if h1 and h1.get_text(strip=True):  # Ensure h1 has text.
            #             title = h1.get_text(separator=" ", strip=True)  # Title from h1.

            comp_container = soup.find(attrs={"data-automation": "advertiser-name"})  # Company node.
            comp = comp_container.get_text(separator=" ", strip=True) if comp_container else ""
            # and comp_container.get_text(strip=True) else "Confidential"  # Company text.

            # Clean description
            desc_tag = soup.find(attrs={"data-automation": "jobAdDetails"})  # Description node.
            desc = desc_tag.get_text(separator=" ", strip=True) if desc_tag else "" 
            # and desc_tag.get_text(strip=True) else "No description available"  # Description text.

            # Validation logic
            if not all([sid, title, comp, desc]):  # Skip if any required field missing.
                if not title: print(f"⚠️ Missing job_title in: {file_path.name}")  # Missing title.
                elif not desc: print(f"⚠️ Missing description in: {file_path.name}")  # Missing description.
                elif not comp: print(f"⚠️ Missing company in: {file_path.name}")  # Missing company.
                elif not sid: print(f"⚠️ Missing sid in: {file_path.name}")  # Missing ID.
                skipped += 1  # Count skipped file.
                continue  # Skip output for this file.

            # tech_stack = extract_tech_stack(desc)  # Detect tech keywords in description.
            job = JobListing(  # Build validated listing object.
                source_id=sid,
                job_title=title,
                company=comp,
                description=desc,
                # tech_stack=tech_stack,
            )

            with open(output_path / f"{file_path.stem}.json", 'w', encoding='utf-8') as f:  # Output file.
                json.dump(job.model_dump(), f, ensure_ascii=False, indent=2)  # Write JSON.

            print(f"✅ Processed: {file_path.name}")  # Per-file success.
            processed += 1  # Count processed file.
        except Exception as e:  # Catch any unexpected error per file.
            print(f"❌ Exception in {file_path.name}: {e}")  # Log error.
            skipped += 1  # Count skipped on error.

    print(f"\n📊 Silver Summary:\nTotal: {total} | Processed: {processed} | Skipped: {skipped}")  # Final summary.