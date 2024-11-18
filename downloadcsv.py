import pandas as pd

data = {
    "company_name": [
        "Google", "Microsoft", "Amazon", "Apple", "Meta",
        "Tesla", "Netflix", "Salesforce", "Intel", "IBM"
    ],
    "location": [
        "Mountain View", "Redmond", "Seattle", "Cupertino", "Menlo Park",
        "Palo Alto", "Los Gatos", "San Francisco", "Santa Clara", "Armonk"
    ],
    "industry": [
        "Technology", "Technology", "E-commerce", "Technology", "Social Media",
        "Automotive", "Entertainment", "Technology", "Technology", "Technology"
    ],
    "employee_count": [
        156500, 220000, 1608000, 164000, 71000,
        127855, 12900, 73000, 121000, 288300
    ]
}

companies_df = pd.DataFrame(data)

file_path = "C:/Projects/AI_web_scraper/companies.csv"
companies_df.to_csv(file_path, index=False)

file_path
