
# html is seperated with other folders, images fonts and styling (CSS)
# Therefore use Multipurpose internet Mail extension to save
# It bundles it like email 
# MHTML 
# MIME (Multipurpose Internet Mail Extensions) encoding

# Any character that isn't part of the standard English alphabet or basic punctuation must be encoded. This includes symbols, currency, and accented letters.
import quopri
# Let the computer know how to read each file
from email import message_from_file 
# let the computer have the ability to know where to get the file (search it)
from pathlib import Path

def ingest_all_mhtml(input_dir, output_dir):
    # Convert string paths to Path objects for easier cross-platform file handling
    # File Can delete, move, create, or search for files.
    input_path, output_path = Path(input_dir), Path(output_dir)
    
    # Create the output folder (1_bronze) if it doesn't exist; do nothing if it does
    output_path.mkdir(parents=True, exist_ok=True)

    # Check if the source folder exists to prevent crashing (Idempotency requirement)
    if not input_path.exists():
        print(f"⚠️ Input directory {input_dir} not found.")
        return

    # Find all files ending in .mhtml in the source folder and store them in a list
    mhtml_files = list(input_path.glob("*.mhtml"))
    
    # Initialize counters for the final progress summary
    total, extracted, failed = len(mhtml_files), 0, 0
    print("🥉 Bronze:...")

    # Loop through every MHTML file found
    for file_path in mhtml_files:
        try:
            # Open the file as a standard text file, ignoring encoding errors to avoid crashes
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Convert the raw file content into an Email Message object
                msg = message_from_file(f)
            
            html_content = None
            
            # Since MHTML is 'multipart', iterate through all components (images, CSS, HTML)
            for part in msg.walk():
                # Check if the current component is the actual HTML webpage text
                if part.get_content_type() == "text/html":
                    # Extract the raw "Quoted-Printable" encoded text
                    payload = part.get_payload()
                    # Decode quopri (e.g., =3D becomes =) then convert bytes to a UTF-8 string
                    html_content = quopri.decodestring(payload).decode('utf-8', errors='ignore')
                    # Once we found the HTML part, stop looking through other components
                    break
            
            # If we successfully found and decoded HTML content
            if html_content:
                # Save the decoded HTML to the bronze folder with the same name but .html extension
                # .stem remove the extensiion only return the filename
                (output_path / f"{file_path.stem}.html").write_text(html_content, encoding='utf-8')
                print(f"✅ Extracted: {file_path.name}")
                extracted += 1
            else:
                # Track files that were valid MHTML but had no HTML payload
                print(f"⚠️  No HTML content found in: {file_path.name}.mhtml")
                failed += 1
        except:
            # Catch any unexpected errors (permissions, corrupted files, etc.) to keep the loop running
            failed += 1

    # Print the final report required by the assignment instructions
    print(f"\n📊 Bronze Summary:\nTotal: {total} | Extracted: {extracted} | Failed: {failed}")