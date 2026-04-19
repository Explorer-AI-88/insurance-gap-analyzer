# Insurance Coverage Gap Analysis Tool

An interactive web application for analyzing personal insurance coverage and identifying gaps based on financial scenarios.

## Features

- **File Upload & Parsing**: Upload your insurance intake spreadsheet (.xlsx format)
- **Interactive Parameter Adjustment**: Adjust annual income, monthly expenses, and mortgage balance with real-time recalculation
- **Coverage Gap Analysis**: Visualize current vs. recommended coverage for:
  - Death benefit
  - Disability income
  - Critical illness
  - Long-term care
- **Scenario Analysis**: Model financial impact across three key scenarios
- **Real-time Visualization**: Chart.js graphs update instantly as you adjust parameters

## Project Structure

```
.
├── app.py                          # Flask backend server
├── templates/
│   └── index.html                 # Interactive web interface
├── Insurance_Intake_Simplified.xlsx # Template and sample data
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## How to Use

### Step 1: Upload Your Insurance Data

1. Open http://localhost:5000 in your browser
2. Click the upload area or drag-and-drop your Insurance_Intake_Simplified.xlsx file
3. The application will parse your data and display:
   - Your profile (name, age, income, dependents)
   - Current insurance premiums
   - Current coverage breakdown by type

### Step 2: Analyze Gaps

The dashboard shows your coverage status with color-coded indicators:
- **Critical** (Red): Coverage gap exceeds recommended need
- **Warning** (Yellow): Partial coverage
- **Good** (Green): Adequate coverage

### Step 3: Adjust Parameters & Explore Scenarios

Use the interactive sliders to adjust:
- **Annual Income**: SGD 60,000 - 300,000
- **Monthly Expenses**: SGD 1,000 - 10,000
- **Mortgage Balance**: SGD 0 - 1,000,000

Watch the coverage metrics and chart update in real-time. The Scenario Analysis cards show:
- **Death Scenario**: How many months your family can sustain on current coverage
- **Critical Illness Scenario**: Medical costs vs. available coverage
- **Long-term Care Scenario**: Monthly care needs vs. current coverage at age 75+

## How Gap Calculations Work

### Death Benefit Need
```
Need = (Annual Income × 20) + (Mortgage ÷ 20)
```
This assumes your family needs 20 years of income replacement plus mortgage payoff.

### Disability Income Need
```
Monthly Need = Annual Income × 0.7 ÷ 12
```
Assumes 70% income replacement during disability period.

### Critical Illness Need
```
Need = SGD 300,000 (fixed)
```
Covers medical expenses and income protection during recovery.

### Long-term Care Need
```
Monthly Need = SGD 4,000 (at age 75+)
```
Estimated monthly cost for retirement care facilities.

## Troubleshooting

### "OSError: [Errno 30] Read-only file system"
- Ensure the application has write permissions to /tmp directory
- Run the application in an environment with proper file system permissions

### "TypeError: unsupported operand type(s)"
- Verify your Excel file matches the Insurance_Intake_Simplified.xlsx format
- Ensure all numeric fields (income, premiums, etc.) are properly filled

### Charts Not Displaying
- Clear browser cache (Ctrl+Shift+Delete)
- Ensure JavaScript is enabled in your browser
- Check browser console for any errors (F12 → Console tab)

## File Format Requirements

Your Insurance_Intake_Simplified.xlsx must have exactly 2 sheets:

**Sheet 1: "About myself"**
- Row 5, Col B: Name
- Row 6, Col B: Birthday (date format)
- Row 12, Col B: Annual Income
- Row 13, Col B: Monthly Expenses
- Row 15, Col B: Mortgage Balance
- Row 21, Col B: Dependents

**Sheet 2: "My Policies"**
- Columns (starting from row 5):
  1. Policy Name
  2. Start Date
  3. Insurer
  4. Type
  5. (Reserved)
  6. (Reserved)
  7. Death Benefit (SGD)
  8. TPD Benefit (SGD)
  9. Early CI Benefit (SGD)
  10. Advanced CI Benefit (SGD)
  11. LTC/DI Monthly (SGD)
  12. PA Benefit (SGD)
  13. Hospital Limit (SGD)
  14. (Reserved)
  15. Annual Premium (SGD)

## API Reference

### POST /upload
Upload and parse insurance intake file.

**Request:**
- `file`: .xlsx file (multipart/form-data)

**Response:**
```json
{
  "name": "Christopher",
  "age": 35,
  "annual_income": 120000,
  "monthly_expenses": 5000,
  "mortgage": 500000,
  "dependents": "Wife, 2 kids",
  "policies": [...],
  "total_death": 800000,
  "total_ltc_di": 2500,
  "death_gap": 1600000,
  "di_gap": 2000,
  ...
}
```

### POST /calculate
Recalculate gaps when parameters are adjusted.

**Request:**
```json
{
  "annual_income": 150000,
  "monthly_expenses": 6000,
  "mortgage": 600000,
  "policies": [...]
}
```

**Response:** Updated gap metrics in same format as /upload

## Next Steps

- **Authentication**: Add user login to track multiple profiles
- **PDF Export**: Generate downloadable coverage reports
- **Database Integration**: Store submitted analyses for trend analysis
- **Mobile App**: Develop mobile version for on-the-go access
- **Recommendations Engine**: AI-powered suggestions for coverage gaps

## Support

For issues or questions, review the troubleshooting section above or check the application logs for detailed error messages.
