from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp'

def parse_intake_excel(file_path):
    """Parse the Insurance_Intake_Simplified.xlsx file"""
    try:
        # Read personal info
        df_personal = pd.read_excel(file_path, sheet_name='About myself', header=None)
        name = str(df_personal.iloc[5, 1]) if pd.notna(df_personal.iloc[5, 1]) else 'User'
        birthday = pd.to_datetime(df_personal.iloc[6, 1])
        age = 2026 - birthday.year
        annual_income = float(df_personal.iloc[12, 1]) if pd.notna(df_personal.iloc[12, 1]) else 0
        monthly_expenses = float(df_personal.iloc[13, 1]) if pd.notna(df_personal.iloc[13, 1]) else 0
        mortgage = float(df_personal.iloc[15, 1]) if pd.notna(df_personal.iloc[15, 1]) else 0
        dependents = str(df_personal.iloc[21, 1]) if pd.notna(df_personal.iloc[21, 1]) else ''
        
        # Read policies
        df_policies = pd.read_excel(file_path, sheet_name='My Policies', skiprows=4, header=0)
        
        policies = []
        for idx, row in df_policies.iterrows():
            policy_name = row.iloc[0]
            if pd.isna(policy_name) or str(policy_name).upper() == 'TOTAL':
                break
            
            try:
                policies.append({
                    'name': str(policy_name),
                    'insurer': str(row.iloc[2]) if pd.notna(row.iloc[2]) else '',
                    'type': str(row.iloc[3]) if pd.notna(row.iloc[3]) else '',
                    'death': float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0,
                    'tpd': float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0,
                    'early_ci': float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0,
                    'advanced_ci': float(row.iloc[9]) if pd.notna(row.iloc[9]) else 0,
                    'ltc_di_monthly': float(row.iloc[10]) if pd.notna(row.iloc[10]) else 0,
                    'pa': float(row.iloc[11]) if pd.notna(row.iloc[11]) else 0,
                    'annual_premium': float(row.iloc[12]) if pd.notna(row.iloc[12]) else 0,
                })
            except:
                continue
        
        return {
            'name': name,
            'age': age,
            'annual_income': annual_income,
            'monthly_expenses': monthly_expenses,
            'mortgage': mortgage,
            'dependents': dependents,
            'policies': policies,
            'error': None
        }
    except Exception as e:
        return {'error': f'Error parsing file: {str(e)}'}

def calculate_gaps(annual_income, monthly_expenses, mortgage, policies):
    """Calculate insurance gaps"""
    total_death = sum(p['death'] for p in policies)
    total_tpd = sum(p['tpd'] for p in policies)
    total_early_ci = sum(p['early_ci'] for p in policies)
    total_advanced_ci = sum(p['advanced_ci'] for p in policies)
    total_ltc_di = sum(p['ltc_di_monthly'] for p in policies)
    total_premium = sum(p['annual_premium'] for p in policies)
    
    # Calculate needs
    death_need = (annual_income + mortgage/20) * 20
    death_gap = max(0, death_need - total_death)
    
    di_monthly_need = annual_income * 0.7 / 12
    di_gap = max(0, di_monthly_need - total_ltc_di)
    
    ci_need = 300000
    total_ci = total_early_ci + total_advanced_ci
    ci_gap = max(0, ci_need - total_ci)
    
    ltc_monthly_need = 4000
    
    return {
        'total_death': total_death,
        'total_tpd': total_tpd,
        'total_early_ci': total_early_ci,
        'total_advanced_ci': total_advanced_ci,
        'total_ltc_di': total_ltc_di,
        'total_premium': total_premium,
        'death_need': death_need,
        'death_gap': death_gap,
        'di_monthly_need': di_monthly_need,
        'di_gap': di_gap,
        'ci_need': ci_need,
        'ci_gap': ci_gap,
        'ltc_monthly_need': ltc_monthly_need,
        'family_months': int(total_death / (monthly_expenses * 12)) if monthly_expenses > 0 else 0
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Please upload an Excel (.xlsx) file'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse the file
        data = parse_intake_excel(filepath)
        
        if data.get('error'):
            return jsonify(data), 400
        
        # Calculate gaps
        gaps = calculate_gaps(data['annual_income'], data['monthly_expenses'], data['mortgage'], data['policies'])
        data.update(gaps)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Recalculate gaps when user adjusts parameters"""
    try:
        params = request.json
        annual_income = float(params.get('annual_income', 0))
        monthly_expenses = float(params.get('monthly_expenses', 0))
        mortgage = float(params.get('mortgage', 0))
        policies = params.get('policies', [])
        
        gaps = calculate_gaps(annual_income, monthly_expenses, mortgage, policies)
        return jsonify(gaps)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
