import csv
import json
import os
from datetime import datetime

# Sample evaluation result for Yogansh Singh Bhadoria
evaluation_result = {
    'candidate_name': 'Yogansh Singh Bhadoria',
    'timestamp': '2025-05-25',
    'scores': {
        'technical_competency': 62.0,
        'communication_skills': 75.0,
        'behavioral_assessment': 82.0,
        'professional_skills': 68.0,
        'cultural_fit': 80.0,
        'overall_score': 73.4
    },
    'personality_traits': ['Responsible', 'Adaptable', 'Team-Oriented'],
    'strengths': ['Good verbal skills', 'Willingness to learn', 'Professional demeanor'],
    'areas_for_improvement': ['Deepen JavaScript skills', 'More confidence in complex coding'],
    'recommendation': 'Consider for Internship / Entry-Level Role',
    'ai_analysis': ("Yogansh Singh Bhadoria demonstrated a foundational understanding of Python and showed a professional "
                    "attitude throughout the evaluation. While his JavaScript knowledge is currently limited, his communication "
                    "skills and willingness to grow position him well for collaborative environments. His responses indicated "
                    "he's motivated and capable of integrating with a team. With mentorship and structured learning, he can "
                    "quickly scale up technically.")
}

def generate_marks_document(evaluation_result):
    """Generate evaluation report data structure"""
    candidate_name = evaluation_result['candidate_name']
    scores = evaluation_result['scores']
    recommendation = evaluation_result['recommendation']

    marks_data = []

    # Add all the report data
    marks_data.extend([
        ['CANDIDATE INFORMATION', 'Name', '', '', '', candidate_name],
        ['CANDIDATE INFORMATION', 'Assessment Date', '', '', '', evaluation_result['timestamp']],
        ['TECHNICAL COMPETENCY', 'Programming Knowledge', f"{scores['technical_competency']:.1f}", '100', f"{scores['technical_competency']:.1f}%", 'Assessment based on technical responses and problem-solving approach'],
        ['COMMUNICATION SKILLS', 'Verbal Communication', f"{scores['communication_skills']:.1f}", '100', f"{scores['communication_skills']:.1f}%", 'Clarity, articulation, and response quality'],
        ['BEHAVIORAL ASSESSMENT', 'Professional Behavior', f"{scores['behavioral_assessment']:.1f}", '100', f"{scores['behavioral_assessment']:.1f}%", 'Professionalism, confidence, and interview conduct'],
        ['PROFESSIONAL SKILLS', 'Response Quality', f"{scores['professional_skills']:.1f}", '100', f"{scores['professional_skills']:.1f}%", 'Quality and depth of responses during interview'],
        ['CULTURAL FIT', 'Team Integration Potential', f"{scores['cultural_fit']:.1f}", '100', f"{scores['cultural_fit']:.1f}%", 'Alignment with organizational values and team dynamics'],
        ['OVERALL ASSESSMENT', 'Composite Score', f"{scores['overall_score']:.1f}", '100', f"{scores['overall_score']:.1f}%", 'Weighted average of all assessment components'],
        ['PERSONALITY PROFILE', 'Key Traits', '', '', '', ', '.join(evaluation_result['personality_traits'])],
        ['STRENGTHS', 'Identified Strengths', '', '', '', ' | '.join(evaluation_result['strengths'])],
        ['DEVELOPMENT AREAS', 'Areas for Improvement', '', '', '', ' | '.join(evaluation_result['areas_for_improvement'])],
        ['FINAL RECOMMENDATION', 'Hiring Decision', '', '', '', recommendation],
        ['AI ANALYSIS SUMMARY', 'Detailed Assessment', '', '', '', evaluation_result['ai_analysis'][:500] + "..." if len(evaluation_result['ai_analysis']) > 500 else evaluation_result['ai_analysis']]
    ])

    return marks_data

def save_to_csv(data, filename):
    """Save data to CSV file"""
    headers = ['Category', 'Component', 'Score', 'Max Score', 'Percentage', 'Details']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def save_to_json(evaluation_result, filename):
    """Save evaluation result to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(evaluation_result, jsonfile, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def generate_text_report(evaluation_result):
    """Generate a formatted text report"""
    report = []
    report.append("=" * 60)
    report.append("CANDIDATE EVALUATION REPORT")
    report.append("=" * 60)
    report.append(f"Candidate Name: {evaluation_result['candidate_name']}")
    report.append(f"Assessment Date: {evaluation_result['timestamp']}")
    report.append("")
    
    report.append("SCORES:")
    report.append("-" * 30)
    scores = evaluation_result['scores']
    for category, score in scores.items():
        formatted_category = category.replace('_', ' ').title()
        report.append(f"{formatted_category:.<25} {score:.1f}/100")
    
    report.append("")
    report.append("PERSONALITY TRAITS:")
    report.append("-" * 30)
    report.append(", ".join(evaluation_result['personality_traits']))
    
    report.append("")
    report.append("STRENGTHS:")
    report.append("-" * 30)
    for strength in evaluation_result['strengths']:
        report.append(f"• {strength}")
    
    report.append("")
    report.append("AREAS FOR IMPROVEMENT:")
    report.append("-" * 30)
    for area in evaluation_result['areas_for_improvement']:
        report.append(f"• {area}")
    
    report.append("")
    report.append("RECOMMENDATION:")
    report.append("-" * 30)
    report.append(evaluation_result['recommendation'])
    
    report.append("")
    report.append("AI ANALYSIS:")
    report.append("-" * 30)
    report.append(evaluation_result['ai_analysis'])
    
    return "\n".join(report)

def main():
    # Generate report data
    marks_data = generate_marks_document(evaluation_result)
    
    # Get current directory
    current_dir = os.getcwd()
    base_filename = "Yogansh_Singh_Bhadoria_Evaluation_Report"
    
    # Save in multiple formats
    csv_path = os.path.join(current_dir, f"{base_filename}.csv")
    json_path = os.path.join(current_dir, f"{base_filename}.json")
    txt_path = os.path.join(current_dir, f"{base_filename}.txt")
    
    print("Generating evaluation report...")
    
    # Save CSV
    if save_to_csv(marks_data, csv_path):
        print(f"✓ CSV report saved: {csv_path}")
    else:
        print("✗ Failed to save CSV report")
    
    # Save JSON
    if save_to_json(evaluation_result, json_path):
        print(f"✓ JSON report saved: {json_path}")
    else:
        print("✗ Failed to save JSON report")
    
    # Save text report
    try:
        text_report = generate_text_report(evaluation_result)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"✓ Text report saved: {txt_path}")
    except Exception as e:
        print(f"✗ Failed to save text report: {e}")
    
    # Display preview
    print("\n" + "="*50)
    print("REPORT PREVIEW:")
    print("="*50)
    headers = ['Category', 'Component', 'Score', 'Max Score', 'Percentage', 'Details']
    print(f"{headers[0]:<20} {headers[1]:<25} {headers[2]:<8} {headers[3]:<8} {headers[4]:<10}")
    print("-" * 80)
    
    for row in marks_data[:8]:  # Show first 8 rows
        details = row[5][:30] + "..." if len(row[5]) > 30 else row[5]
        print(f"{row[0]:<20} {row[1]:<25} {row[2]:<8} {row[3]:<8} {row[4]:<10}")
    
    print(f"\nTotal rows: {len(marks_data)}")

if __name__ == "__main__":
    main()
