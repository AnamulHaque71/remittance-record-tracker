import json
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import calendar

# File to store the data
DATA_FILE = "remittance_data.json"

# Function to get the full month name from the month number
def get_month_name(month_num):
    # Convert month_num to integer if it's a string
    if isinstance(month_num, str):
        month_num = int(month_num)

    # Ensure the month number is within the valid range (1-12)
    if 1 <= month_num <= 12:
        return calendar.month_name[month_num]
    else:
        return "Invalid Month"


# Function to load data from JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to add a new remittance record
def add_record():
    year = int(input("Enter the year: "))
    month_num = int(input("Enter the month (1-12): "))
    month_name = get_month_name(month_num)
    amount = float(input("Enter the remittance amount: "))
    purpose = input("Enter the purpose: ")

    records = load_data()

    # Check if record with the same year and month already exists
    for rec in records:
        if rec["year"] == year and rec["month"] == month_num:
            rec["amount"] += amount  # Add the new amount to the existing record
            save_data(records)
            print("Amount updated successfully!")
            return

    # Add new record if no matching year and month
    records.append({"year": year, "month": month_num, "month_name": month_name, "amount": amount, "purpose": purpose})
    save_data(records)
    print("Record added successfully!")

# Function to view all records
def view_records():
    records = load_data()
    if not records:
        print("No records found.")
        return

    # Sort records by year and month in ascending order
    sorted_records = sorted(records, key=lambda rec: (rec["year"], rec["month"]))

    table = [[rec["year"], get_month_name(rec["month"]), rec["amount"], rec["purpose"]] for rec in sorted_records]
    print(tabulate(table, headers=["Year", "Month", "Amount", "Purpose"], tablefmt="grid"))

# Function to visualize remittance data
def visualize_data():
    records = load_data()
    if not records:
        print("No records found.")
        return

    print("Choose an option to visualize:")
    print("1. Yearly remittance")
    print("2. Monthly remittance for a specific year")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        # Group data by year
        yearly_data = {}
        for record in records:
            year = record["year"]
            amount = record["amount"]
            yearly_data[year] = yearly_data.get(year, 0) + amount

        # Sort years and get corresponding totals
        sorted_years = sorted(yearly_data.keys())
        sorted_totals = [yearly_data[year] for year in sorted_years]

        # Plot yearly data
        plt.figure(figsize=(8, 5))
        plt.bar(sorted_years, sorted_totals, color='green', alpha=0.7)
        plt.title("Yearly Remittance Amount", fontsize=16)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Total Amount (in currency)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(sorted_years)
        plt.tight_layout()
        plt.show()

    elif choice == "2":
        year = int(input("Enter the year for monthly visualization: "))
        # Group data by month for the specified year
        monthly_data = {}
        for record in records:
            if record["year"] == year:
                month = record["month"]
                amount = record["amount"]
                monthly_data[month] = monthly_data.get(month, 0) + amount

        if not monthly_data:
            print(f"No data found for the year {year}.")
            return

        # Sort months numerically (1-12)
        sorted_months = sorted(monthly_data.keys())
        sorted_totals = [monthly_data[month] for month in sorted_months]

        # Plot monthly data
        plt.figure(figsize=(8, 5))
        plt.bar(sorted_months, sorted_totals, color='blue', alpha=0.7)
        plt.title(f"Monthly Remittance for {year}", fontsize=16)
        plt.xlabel("Month", fontsize=12)
        plt.ylabel("Total Amount (in currency)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(sorted_months, [get_month_name(month) for month in sorted_months])
        plt.tight_layout()
        plt.show()
    else:
        print("Invalid choice. Please select either 1 or 2.")

# Function to export data to PDF
# Function to export data to PDF with color in header and summary
def export_to_pdf():
    records = load_data()
    if not records:
        print("No records found.")
        return

    # Sort records by year and month in ascending order
    sorted_records = sorted(records, key=lambda rec: (rec["year"], rec["month"]))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.cell(200, 10, txt="Remittance Tracker Report", ln=True, align='C')
    pdf.ln(10)

    # Set header background color (e.g., light blue)
    pdf.set_fill_color(135, 206, 235)  # Light blue
    pdf.cell(40, 10, "Year", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Month", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Amount", 1, 0, 'C', fill=True)
    pdf.cell(70, 10, "Purpose", 1, 1, 'C', fill=True)  # '\n' to create new row

    # Add table rows
    for rec in sorted_records:
        pdf.cell(40, 10, str(rec["year"]), 1)
        pdf.cell(40, 10, get_month_name(rec["month"]), 1)
        pdf.cell(40, 10, f"{rec['amount']:.2f}", 1)
        pdf.cell(70, 10, rec["purpose"], 1)
        pdf.ln()

    # Add summary section (total remittance)
    total_amount = sum(rec["amount"] for rec in sorted_records)
    highest_remittance = max(sorted_records, key=lambda x: x["amount"])
    
    pdf.ln(10)  # Add space before summary
    pdf.set_font("Arial", "B", 12)  # Bold font for summary
    
    # Set summary header background color (e.g., light green)
    pdf.set_fill_color(144, 238, 144)  # Light green
    pdf.cell(0, 10, "Summary", 0, 1, 'C', fill=True)

    # Add summary data
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Total Remittance Amount: {total_amount:.2f}", 0, 1)
    pdf.cell(0, 10, f"Highest Remittance: {highest_remittance['amount']:.2f} ({highest_remittance['year']}, {get_month_name(highest_remittance['month'])})", 0, 1)

    # Save PDF
    pdf.output("remittance_report.pdf")
    print("Data exported to remittance_report.pdf successfully!")



# Function to analyze remittance data
def analyze_data():
    records = load_data()
    if not records:
        print("No records found.")
        return

    total_amount = sum(rec["amount"] for rec in records)
    max_remittance = max(records, key=lambda x: x["amount"])
    print(f"Total Remittance Amount: {total_amount:.2f}")
    print(f"Highest Remittance: {max_remittance['amount']:.2f} ({max_remittance['year']}, {get_month_name(max_remittance['month'])})")

# Main program
def main():
    while True:
        print("\n--- Remittance Tracker ---")
        print("1. Add a remittance record")
        print("2. View all records")
        print("3. Visualize remittance data")
        print("4. Export data to PDF")
        print("5. Analyze data")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_record()
        elif choice == "2":
            view_records()
        elif choice == "3":
            visualize_data()
        elif choice == "4":
            export_to_pdf()
        elif choice == "5":
            analyze_data()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
