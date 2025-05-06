from playwright.sync_api import sync_playwright
import csv
import time

SCROLL_TIME = 5
SCROLL_PAUSE = 0.5
SCROLL_STEP = 200


def wait_for_new_offers(page, seen_indexes):
    start_time = time.time()
    while time.time() - start_time < SCROLL_TIME:
        page.mouse.wheel(0, SCROLL_STEP)
        time.sleep(SCROLL_PAUSE)
        offer_cards = page.query_selector_all("div[data-index]")
        new_found = False
        for offer_card in offer_cards:
            index = offer_card.get_attribute("data-index")
            if index and index not in seen_indexes:
                return True
    return False


# Accessing the website
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Set to False for debugging
    page = browser.new_page()
    page.goto(
        "https://justjoin.it/job-offers/all-locations/data?experience-level=junior,mid&with-salary=yes&orderBy=DESC&sortBy=published"
    )

    # Wait for job cards to appear
    page.wait_for_selector("a.offer-card")

    seen_indexes = set()
    collected_links = []

    while True:
        has_new = wait_for_new_offers(page, seen_indexes)
        offer_cards = page.query_selector_all("div[data-index]")

        new_data = 0
        for offer_card in offer_cards:
            index = offer_card.get_attribute("data-index")
            if not index or index in seen_indexes:
                continue

            seen_indexes.add(index)
            link_element = offer_card.query_selector("a.offer-card")
            href = link_element.get_attribute("href") if link_element else None
            if href:
                collected_links.append(href)
                new_data += 1

        print(f"Total job offers found: {len(collected_links)}")

        if not has_new or new_data == 0:
            print("No more new offers found.")
            choice = (
                input(
                    "Enter your choice:\n"
                    "[C] to continue scrolling,\n"
                    "[S] to save the data to a CSV file,\n"
                    "[Q] to quit the program.\n"
                    "Your choice: "
                )
                .strip()
                .lower()
            )
            if choice == "q":
                print("Program terminated by user.")
                browser.close()
                exit()
            elif choice == "s":
                print("Saving data to CSV file...")
                break
            elif choice == "c":
                print("Continuing to scroll...")
                continue
            else:
                print("Invalid choice. Please enter 'C', 'S', or 'Q'.")
                continue

    with open(
        "/Users/rafalgrajewski/Desktop/"
        "Programowanie/Web Scrapping/"
        "justjoinit_offers.csv",
        mode="w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "ID",
                "Job URL",
                "Job Title",
                "Category",
                "Company",
                "Location",
                "Salary Any",
                "Salary B2B",
                "Salary Internship",
                "Salary Mandate",
                "Salary Permanent",
                "Work Type",
                "Experience",
                "Employment Type",
                "Operating Mode",
                "Tech Stack",
            ]
        )

        for i, href in enumerate(
            collected_links, start=1
        ):  # Add [:1] to limit to the first offer
            try:
                # Accessing the offer link
                job_url = "https://justjoin.it" + href
                job_page = browser.new_page()
                job_page.goto(job_url)

                # Wait for job title
                job_page.wait_for_selector("h1")

                job_title = job_page.query_selector("h1").inner_text()

                category_element = job_page.query_selector(
                    "svg:has(path[fill*='AboutIcon']) + div"
                )
                category = category_element.inner_text() if category_element else "N/A"

                company_element = job_page.query_selector(
                    "div:has(svg[data-testid='ApartmentRoundedIcon']) h2"
                )
                company = company_element.inner_text() if company_element else "N/A"

                location_element = job_page.query_selector(
                    "svg[data-testid='PlaceOutlinedIcon'] ~ div span"
                )
                location = location_element.inner_text() if location_element else "N/A"

                salary_elements = job_page.query_selector_all("div:has(svg) > div")
                salary_any = "N/A"
                salary_b2b = "N/A"
                salary_internship = "N/A"
                salary_mandate = "N/A"
                salary_perm = "N/A"

                for element in salary_elements:
                    label_element = element.query_selector("span.css-1waow8k")
                    amount_element = element.query_selector("span.css-mrzdjb")
                    if not label_element or not amount_element:
                        continue
                    label = label_element.inner_text().lower()
                    amount = amount_element.inner_text()
                    if "any" in label:
                        salary_any = amount
                    elif "b2b" in label:
                        salary_b2b = amount
                    elif "internship" in label:
                        salary_internship = amount
                    elif "mandate" in label:
                        salary_mandate = amount
                    elif "perm" in label:
                        salary_perm = amount

                work_type_element = job_page.query_selector(
                    "div:text-is('Type of work') + div"
                )
                work_type = (
                    work_type_element.inner_text() if work_type_element else "N/A"
                )

                experience_element = job_page.query_selector(
                    "div:text-is('Experience') + div"
                )
                experience = (
                    experience_element.inner_text() if experience_element else "N/A"
                )

                employment_type_element = job_page.query_selector(
                    "div:text-is('Employment Type') + div"
                )
                employment_type = (
                    employment_type_element.inner_text()
                    if employment_type_element
                    else "N/A"
                )

                operating_mode_element = job_page.query_selector(
                    "div:text-is('Operating mode') + div"
                )
                operating_mode = (
                    operating_mode_element.inner_text()
                    if operating_mode_element
                    else "N/A"
                )

                tech_stack_header = job_page.query_selector("h3:text-is('Tech stack')")
                tech_stack_section = tech_stack_header.evaluate_handle(
                    "el => el.parentElement"
                )
                skill_blocks = tech_stack_section.query_selector_all("div.css-jfr3nf")

                tech_stack = {}
                for block in skill_blocks:
                    name_element = block.query_selector("h4")
                    description_element = block.query_selector("ul + span")
                    if not name_element:
                        continue
                    name = name_element.inner_text().strip()
                    desc = (
                        description_element.inner_text()
                        if description_element
                        else "N/A"
                    )
                    tech_stack[name] = desc

                print("ID", i)
                # print("Job URL:", job_url)
                print("Job title:", job_title)
                # print("Category:", category)
                # print("Company:", company)
                # print("Location:", location)
                # print("Salary B2B:", salary_b2b)
                # print("Salary Permanent:", salary_perm)
                # print("Work type:", work_type)
                # print("Experience:", experience)
                # print("Employment type:", employment_type)
                # print("Operating mode:", operating_mode)
                # print("Tech stack:")
                # for name, desc in tech_stack.items():
                #     print(f"  {name}: {desc}")

                # print("-" * 40)

                tech_stack_formatted = "; ".join(
                    f"{name}: {desc}" for name, desc in tech_stack.items()
                )

                writer.writerow(
                    [
                        i,
                        job_url,
                        job_title,
                        category,
                        company,
                        location,
                        salary_any,
                        salary_b2b,
                        salary_internship,
                        salary_mandate,
                        salary_perm,
                        work_type,
                        experience,
                        employment_type,
                        operating_mode,
                        tech_stack_formatted,
                    ]
                )

                job_page.close()

            except Exception as e:
                print(f"Error processing job offer: {e}")
                if job_page:
                    job_page.close()
                continue

    browser.close()