"""
Intelligent Resume Analyzer
A Python-based application for automated resume screening and candidate matching
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class ResumeAnalyzer:
    """Main class for resume analysis and candidate matching"""
    
    def __init__(self):
        self.resumes_data = []
        self.job_requirements = {}
        self.data_file = "resume_data.json"
        
    def parse_resume(self, resume_text: str) -> Dict:
        """
        Parse resume text and extract key information
        
        Args:
            resume_text: Raw text content of the resume
            
        Returns:
            Dictionary containing extracted information
        """
        resume_data = {
            "name": self._extract_name(resume_text),
            "email": self._extract_email(resume_text),
            "phone": self._extract_phone(resume_text),
            "skills": self._extract_skills(resume_text),
            "experience": self._extract_experience(resume_text),
            "education": self._extract_education(resume_text),
            "raw_text": resume_text
        }
        
        return resume_data
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume text"""
        # Look for name in first few lines
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Name is typically 2-4 words, capitalized, at the beginning
            if line and len(line.split()) <= 4 and line[0].isupper():
                # Skip common headers
                skip_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'objective']
                if not any(word in line.lower() for word in skip_words):
                    return line
        return "Name Not Found"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Email Not Found"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from resume text"""
        # Match various phone number formats
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return "Phone Not Found"
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common technical and professional skills
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'sql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'nosql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'machine learning', 'deep learning', 'ai', 'data science', 'nlp',
            'agile', 'scrum', 'devops', 'ci/cd', 'rest api', 'graphql',
            'leadership', 'communication', 'project management', 'problem solving',
            'teamwork', 'analytical', 'critical thinking', 'time management',
            'excel', 'powerpoint', 'word', 'tableau', 'power bi',
            'text processing', 'data extraction', 'json', 'algorithms',
            'web scraping', 'automation', 'testing', 'debugging'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            # Use word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill.title())
        
        # Remove duplicates and sort
        found_skills = sorted(list(set(found_skills)))
        
        return found_skills if found_skills else ["No skills detected"]
    
    def _extract_experience(self, text: str) -> Dict:
        """Extract years of experience from resume text"""
        experience = {
            "total_years": 0,
            "companies": []
        }
        
        # Look for years of experience patterns
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                experience['total_years'] = int(matches[0])
                break
        
        # Extract company names (basic heuristic)
        company_indicators = ['inc', 'corp', 'ltd', 'llc', 'technologies', 'solutions', 'systems']
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in company_indicators):
                company = line.strip()
                if len(company.split()) <= 6:  # Reasonable company name length
                    experience['companies'].append(company)
        
        return experience
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education details from resume text"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'\b(B\.?S\.?|Bachelor|B\.?A\.?|B\.?Tech\.?|B\.?E\.?)\b.*',
            r'\b(M\.?S\.?|Master|M\.?A\.?|M\.?Tech\.?|MBA|M\.?B\.?A\.?)\b.*',
            r'\b(Ph\.?D\.?|Doctorate|Doctoral)\b.*'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return education if education else ["Education information not found"]
    
    def calculate_match_score(self, resume_data: Dict, job_requirements: Dict) -> Tuple[int, Dict]:
        """
        Calculate match score between resume and job requirements
        
        Args:
            resume_data: Parsed resume data
            job_requirements: Job requirements dictionary
            
        Returns:
            Tuple of (match_score, detailed_breakdown)
        """
        score_breakdown = {
            "skills_score": 0,
            "experience_score": 0,
            "education_score": 0,
            "total_score": 0
        }
        
        # Skills matching (50% weight)
        required_skills = [s.lower() for s in job_requirements.get('required_skills', [])]
        candidate_skills = [s.lower() for s in resume_data.get('skills', [])]
        
        if required_skills:
            matched_skills = [s for s in required_skills if s in candidate_skills]
            skills_match_rate = len(matched_skills) / len(required_skills)
            score_breakdown['skills_score'] = int(skills_match_rate * 50)
            score_breakdown['matched_skills'] = matched_skills
            score_breakdown['missing_skills'] = [s for s in required_skills if s not in candidate_skills]
        
        # Experience matching (30% weight)
        required_years = job_requirements.get('required_experience', 0)
        candidate_years = resume_data.get('experience', {}).get('total_years', 0)
        
        if required_years > 0:
            if candidate_years >= required_years:
                score_breakdown['experience_score'] = 30
            else:
                # Partial score based on percentage
                score_breakdown['experience_score'] = int((candidate_years / required_years) * 30)
        else:
            score_breakdown['experience_score'] = 30  # No requirement
        
        # Education matching (20% weight)
        required_education = job_requirements.get('required_education', '').lower()
        candidate_education = ' '.join(resume_data.get('education', [])).lower()
        
        if required_education:
            if required_education in candidate_education:
                score_breakdown['education_score'] = 20
            elif any(edu in candidate_education for edu in ['bachelor', 'master', 'phd']):
                score_breakdown['education_score'] = 10  # Partial credit
        else:
            score_breakdown['education_score'] = 20  # No requirement
        
        # Calculate total score
        score_breakdown['total_score'] = (
            score_breakdown['skills_score'] + 
            score_breakdown['experience_score'] + 
            score_breakdown['education_score']
        )
        
        return score_breakdown['total_score'], score_breakdown
    
    def generate_recommendation(self, match_score: int, score_breakdown: Dict) -> str:
        """
        Generate hiring recommendation based on match score
        
        Args:
            match_score: Overall match score (0-100)
            score_breakdown: Detailed score breakdown
            
        Returns:
            Recommendation string
        """
        if match_score >= 80:
            return "HIGHLY RECOMMENDED - Excellent match for the position"
        elif match_score >= 60:
            return "RECOMMENDED - Good candidate, consider for interview"
        elif match_score >= 40:
            return "MAYBE - Potential candidate with some skill gaps"
        else:
            return "NOT RECOMMENDED - Significant gaps in requirements"
    
    def generate_report(self, resume_data: Dict, job_requirements: Dict, 
                       match_score: int, score_breakdown: Dict) -> str:
        """
        Generate detailed analysis report
        
        Args:
            resume_data: Parsed resume data
            job_requirements: Job requirements
            match_score: Overall match score
            score_breakdown: Detailed score breakdown
            
        Returns:
            Formatted report string
        """
        recommendation = self.generate_recommendation(match_score, score_breakdown)
        
        report = f"""
{'='*80}
CANDIDATE ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

CANDIDATE INFORMATION
{'-'*80}
Name:           {resume_data.get('name', 'N/A')}
Email:          {resume_data.get('email', 'N/A')}
Phone:          {resume_data.get('phone', 'N/A')}

MATCH SCORE: {match_score}/100
RECOMMENDATION: {recommendation}

DETAILED BREAKDOWN
{'-'*80}
Skills Match:       {score_breakdown['skills_score']}/50 points
Experience Match:   {score_breakdown['experience_score']}/30 points
Education Match:    {score_breakdown['education_score']}/20 points

SKILLS ANALYSIS
{'-'*80}
Candidate Skills: {', '.join(resume_data.get('skills', ['None']))}

"""
        
        if 'matched_skills' in score_breakdown:
            report += f"Matched Skills:   {', '.join(score_breakdown['matched_skills']) if score_breakdown['matched_skills'] else 'None'}\n"
            report += f"Missing Skills:   {', '.join(score_breakdown['missing_skills']) if score_breakdown['missing_skills'] else 'None'}\n"
        
        report += f"""
EXPERIENCE
{'-'*80}
Total Years: {resume_data.get('experience', {}).get('total_years', 0)} years
Required:    {job_requirements.get('required_experience', 0)} years

EDUCATION
{'-'*80}
{', '.join(resume_data.get('education', ['Not specified']))}

{'='*80}
END OF REPORT
{'='*80}
"""
        
        return report
    
    def save_data(self, data: List[Dict], filename: Optional[str] = None) -> bool:
        """
        Save resume data to JSON file
        
        Args:
            data: List of resume data dictionaries
            filename: Optional filename (defaults to self.data_file)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = filename or self.data_file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False
    
    def load_data(self, filename: Optional[str] = None) -> List[Dict]:
        """
        Load resume data from JSON file
        
        Args:
            filename: Optional filename (defaults to self.data_file)
            
        Returns:
            List of resume data dictionaries
        """
        try:
            filename = filename or self.data_file
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return []
    
    def analyze_resume(self, resume_text: str, job_requirements: Dict) -> Dict:
        """
        Complete analysis pipeline for a single resume
        
        Args:
            resume_text: Raw resume text
            job_requirements: Job requirements dictionary
            
        Returns:
            Complete analysis results
        """
        # Parse resume
        resume_data = self.parse_resume(resume_text)
        
        # Calculate match score
        match_score, score_breakdown = self.calculate_match_score(resume_data, job_requirements)
        
        # Generate report
        report = self.generate_report(resume_data, job_requirements, match_score, score_breakdown)
        
        # Compile results
        results = {
            "resume_data": resume_data,
            "match_score": match_score,
            "score_breakdown": score_breakdown,
            "recommendation": self.generate_recommendation(match_score, score_breakdown),
            "report": report,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return results


def main():
    """Main function demonstrating the resume analyzer"""
    
    print("="*80)
    print("INTELLIGENT RESUME ANALYZER")
    print("="*80)
    print()
    
    # Initialize analyzer
    analyzer = ResumeAnalyzer()
    
    # Sample job requirements
    job_requirements = {
        "position": "Senior Python Developer",
        "required_skills": ["Python", "Django", "SQL", "Git", "REST API"],
        "required_experience": 5,
        "required_education": "Bachelor"
    }
    
    print(f"Job Position: {job_requirements['position']}")
    print(f"Required Skills: {', '.join(job_requirements['required_skills'])}")
    print(f"Required Experience: {job_requirements['required_experience']} years")
    print(f"Required Education: {job_requirements['required_education']}")
    print()
    
    # Sample resumes
    sample_resumes = [
        """
        John Doe
        john.doe@email.com | +1-555-123-4567
        
        PROFESSIONAL SUMMARY
        Senior Software Engineer with 7 years of experience in Python development
        
        SKILLS
        Python, Django, Flask, SQL, PostgreSQL, MongoDB, Git, REST API, Docker, AWS
        Data extraction algorithms, JSON file handling, Problem solving
        
        EXPERIENCE
        Senior Developer at Tech Solutions Inc (2018-Present)
        - Led development of microservices architecture
        - Implemented REST APIs serving 1M+ requests daily
        
        Software Engineer at Digital Systems Corp (2016-2018)
        - Developed Python-based data processing pipelines
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2016
        """,
        
        """
        Jane Smith
        jane.smith@example.com
        (555) 987-6543
        
        Objective: Looking for entry-level position
        
        Skills: JavaScript, HTML, CSS, React, Node.js
        
        Education:
        Bachelor of Arts in Design
        State University, 2023
        
        Internship Experience:
        Web Development Intern at StartupXYZ (6 months)
        - Assisted in frontend development
        - Learned JavaScript and React
        """,
        
        """
        Robert Johnson
        robert.j@techmail.com | 555-444-3333
        
        SUMMARY
        Full-stack developer with 10+ years of experience
        
        TECHNICAL SKILLS
        Python, Java, C++, JavaScript, Django, Flask, Spring Boot
        SQL, PostgreSQL, MongoDB, Redis
        Git, Docker, Kubernetes, Jenkins, AWS, Azure
        REST API, GraphQL, Microservices, Agile, DevOps
        
        PROFESSIONAL EXPERIENCE
        Lead Engineer - Tech Innovations Ltd (2015-Present)
        Principal Developer - Solutions Corp (2012-2015)
        
        EDUCATION
        Master of Science in Computer Science
        MIT, 2012
        Bachelor of Technology in Computer Engineering
        Stanford University, 2010
        """
    ]
    
    # Analyze all resumes
    results = []
    for i, resume_text in enumerate(sample_resumes, 1):
        print(f"\n{'='*80}")
        print(f"ANALYZING RESUME {i}/3")
        print('='*80)
        
        analysis = analyzer.analyze_resume(resume_text, job_requirements)
        results.append(analysis)
        
        print(analysis['report'])
        
        # Save individual report
        report_filename = f"candidate_{i}_report.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(analysis['report'])
        print(f"\nReport saved to: {report_filename}")
    
    # Save all results to JSON
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print('='*80)
    
    if analyzer.save_data(results, "all_candidates_analysis.json"):
        print("✓ All results saved to: all_candidates_analysis.json")
    
    # Generate summary
    print(f"\n{'='*80}")
    print("ANALYSIS SUMMARY")
    print('='*80)
    
    sorted_results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    
    print(f"\n{'Rank':<6} {'Name':<25} {'Score':<10} {'Recommendation':<30}")
    print('-'*80)
    
    for i, result in enumerate(sorted_results, 1):
        name = result['resume_data']['name']
        score = result['match_score']
        recommendation = result['recommendation'].split('-')[0].strip()
        print(f"{i:<6} {name:<25} {score:<10} {recommendation:<30}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print('='*80)


if __name__ == "__main__":
    main()