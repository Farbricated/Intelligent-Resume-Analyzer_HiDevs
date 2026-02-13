"""
Interactive Command Line Interface for Resume Analyzer
Provides user-friendly menu-driven interaction
"""

import os
import json
from resume_analyzer import ResumeAnalyzer


class ResumeAnalyzerCLI:
    """Command-line interface for Resume Analyzer"""
    
    def __init__(self):
        self.analyzer = ResumeAnalyzer()
        self.job_requirements = {}
        self.analyzed_resumes = []
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"{title.center(80)}")
        print("="*80 + "\n")
    
    def print_menu(self, title, options):
        """Print formatted menu"""
        self.print_header(title)
        for key, value in options.items():
            print(f"{key}. {value}")
        print()
    
    def get_input(self, prompt, input_type=str, default=None):
        """Get and validate user input"""
        while True:
            try:
                user_input = input(prompt)
                if not user_input and default is not None:
                    return default
                return input_type(user_input)
            except ValueError:
                print(f"Invalid input. Please enter a valid {input_type.__name__}.")
    
    def setup_job_requirements(self):
        """Interactive job requirements setup"""
        self.clear_screen()
        self.print_header("JOB REQUIREMENTS SETUP")
        
        position = self.get_input("Enter job position: ", str, "Software Developer")
        
        print("\nEnter required skills (comma-separated):")
        print("Example: Python, Django, SQL, Git, REST API")
        skills_input = self.get_input("Skills: ", str, "Python, SQL, Git")
        required_skills = [s.strip() for s in skills_input.split(',')]
        
        required_experience = self.get_input(
            "Enter minimum years of experience: ", 
            int, 
            3
        )
        
        print("\nEnter minimum education level:")
        print("Options: High School, Associate, Bachelor, Master, PhD")
        required_education = self.get_input("Education: ", str, "Bachelor")
        
        self.job_requirements = {
            "position": position,
            "required_skills": required_skills,
            "required_experience": required_experience,
            "required_education": required_education
        }
        
        print("\n" + "-"*80)
        print("Job requirements saved successfully!")
        print("-"*80)
        self.display_job_requirements()
        input("\nPress Enter to continue...")
    
    def display_job_requirements(self):
        """Display current job requirements"""
        if not self.job_requirements:
            print("No job requirements set.")
            return
        
        print(f"\nPosition: {self.job_requirements['position']}")
        print(f"Required Skills: {', '.join(self.job_requirements['required_skills'])}")
        print(f"Required Experience: {self.job_requirements['required_experience']} years")
        print(f"Required Education: {self.job_requirements['required_education']}")
    
    def analyze_single_resume(self):
        """Analyze a single resume"""
        self.clear_screen()
        self.print_header("ANALYZE RESUME")
        
        if not self.job_requirements:
            print("⚠ Please set up job requirements first!")
            input("\nPress Enter to continue...")
            return
        
        print("Enter resume text (type 'END' on a new line when done):")
        print("-"*80)
        
        resume_lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            resume_lines.append(line)
        
        resume_text = '\n'.join(resume_lines)
        
        if not resume_text.strip():
            print("\n⚠ No resume text entered!")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "-"*80)
        print("Analyzing resume...")
        print("-"*80)
        
        # Perform analysis
        analysis = self.analyzer.analyze_resume(resume_text, self.job_requirements)
        self.analyzed_resumes.append(analysis)
        
        # Display results
        print(analysis['report'])
        
        # Offer to save
        save = self.get_input("\nSave this report to file? (y/n): ", str, "y").lower()
        if save == 'y':
            candidate_name = analysis['resume_data']['name'].replace(' ', '_')
            filename = f"report_{candidate_name}_{len(self.analyzed_resumes)}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(analysis['report'])
            
            print(f"\n✓ Report saved to: {filename}")
        
        input("\nPress Enter to continue...")
    
    def load_resume_from_file(self):
        """Load and analyze resume from text file"""
        self.clear_screen()
        self.print_header("LOAD RESUME FROM FILE")
        
        if not self.job_requirements:
            print("⚠ Please set up job requirements first!")
            input("\nPress Enter to continue...")
            return
        
        filename = self.get_input("Enter resume file path: ")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            print("\n" + "-"*80)
            print("Analyzing resume...")
            print("-"*80)
            
            analysis = self.analyzer.analyze_resume(resume_text, self.job_requirements)
            self.analyzed_resumes.append(analysis)
            
            print(analysis['report'])
            
            # Auto-save
            candidate_name = analysis['resume_data']['name'].replace(' ', '_')
            report_filename = f"report_{candidate_name}_{len(self.analyzed_resumes)}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(analysis['report'])
            
            print(f"\n✓ Report saved to: {report_filename}")
            
        except FileNotFoundError:
            print(f"\n⚠ File not found: {filename}")
        except Exception as e:
            print(f"\n⚠ Error reading file: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def view_all_results(self):
        """Display summary of all analyzed resumes"""
        self.clear_screen()
        self.print_header("ALL ANALYZED CANDIDATES")
        
        if not self.analyzed_resumes:
            print("No resumes analyzed yet.")
            input("\nPress Enter to continue...")
            return
        
        # Sort by match score
        sorted_resumes = sorted(
            self.analyzed_resumes, 
            key=lambda x: x['match_score'], 
            reverse=True
        )
        
        print(f"{'Rank':<6} {'Name':<25} {'Email':<30} {'Score':<8} {'Status':<20}")
        print("-"*100)
        
        for i, analysis in enumerate(sorted_resumes, 1):
            name = analysis['resume_data']['name'][:24]
            email = analysis['resume_data']['email'][:29]
            score = analysis['match_score']
            status = analysis['recommendation'].split('-')[0].strip()[:19]
            
            print(f"{i:<6} {name:<25} {email:<30} {score:<8} {status:<20}")
        
        print("\n" + "="*100)
        print(f"Total Candidates Analyzed: {len(self.analyzed_resumes)}")
        
        # Statistics
        avg_score = sum(r['match_score'] for r in self.analyzed_resumes) / len(self.analyzed_resumes)
        recommended = sum(1 for r in self.analyzed_resumes if r['match_score'] >= 60)
        
        print(f"Average Match Score: {avg_score:.1f}")
        print(f"Recommended Candidates: {recommended}")
        
        input("\nPress Enter to continue...")
    
    def save_all_results(self):
        """Save all analyzed results to JSON file"""
        self.clear_screen()
        self.print_header("SAVE ALL RESULTS")
        
        if not self.analyzed_resumes:
            print("No resumes to save.")
            input("\nPress Enter to continue...")
            return
        
        filename = self.get_input(
            "Enter filename (default: all_results.json): ", 
            str, 
            "all_results.json"
        )
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        if self.analyzer.save_data(self.analyzed_resumes, filename):
            print(f"\n✓ Successfully saved {len(self.analyzed_resumes)} results to: {filename}")
        else:
            print("\n⚠ Failed to save results.")
        
        input("\nPress Enter to continue...")
    
    def load_previous_results(self):
        """Load previously saved results"""
        self.clear_screen()
        self.print_header("LOAD PREVIOUS RESULTS")
        
        filename = self.get_input(
            "Enter filename (default: all_results.json): ", 
            str, 
            "all_results.json"
        )
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        loaded_data = self.analyzer.load_data(filename)
        
        if loaded_data:
            self.analyzed_resumes.extend(loaded_data)
            print(f"\n✓ Successfully loaded {len(loaded_data)} results from: {filename}")
        else:
            print(f"\n⚠ No data found in: {filename}")
        
        input("\nPress Enter to continue...")
    
    def run_demo(self):
        """Run demonstration with sample data"""
        self.clear_screen()
        self.print_header("DEMO MODE")
        
        print("This will analyze 3 sample resumes with predefined job requirements.")
        confirm = self.get_input("Continue? (y/n): ", str, "y").lower()
        
        if confirm != 'y':
            return
        
        # Set demo job requirements
        self.job_requirements = {
            "position": "Senior Python Developer",
            "required_skills": ["Python", "Django", "SQL", "Git", "REST API"],
            "required_experience": 5,
            "required_education": "Bachelor"
        }
        
        sample_resumes = [
            """
            John Doe
            john.doe@email.com | +1-555-123-4567
            
            PROFESSIONAL SUMMARY
            Senior Software Engineer with 7 years of experience in Python development
            
            SKILLS
            Python, Django, Flask, SQL, PostgreSQL, Git, REST API, Docker, AWS
            
            EXPERIENCE
            Senior Developer at Tech Solutions Inc (2018-Present)
            Software Engineer at Digital Systems Corp (2016-2018)
            
            EDUCATION
            Bachelor of Science in Computer Science, 2016
            """,
            
            """
            Jane Smith
            jane.smith@example.com | (555) 987-6543
            
            Skills: JavaScript, HTML, CSS, React, Node.js
            
            Education: Bachelor of Arts in Design, 2023
            
            Experience: Web Development Intern (6 months)
            """,
            
            """
            Robert Johnson
            robert.j@techmail.com | 555-444-3333
            
            Full-stack developer with 10+ years of experience
            
            SKILLS: Python, Java, Django, Flask, SQL, PostgreSQL, MongoDB
            Git, Docker, Kubernetes, REST API, GraphQL, Agile, DevOps
            
            EXPERIENCE: Lead Engineer at Tech Innovations Ltd (2015-Present)
            
            EDUCATION: Master of Science in Computer Science, 2012
            """
        ]
        
        print("\n" + "-"*80)
        print("Analyzing resumes...")
        print("-"*80 + "\n")
        
        for i, resume_text in enumerate(sample_resumes, 1):
            print(f"Analyzing Resume {i}/3...")
            analysis = self.analyzer.analyze_resume(resume_text, self.job_requirements)
            self.analyzed_resumes.append(analysis)
        
        print(f"\n✓ Demo completed! {len(sample_resumes)} resumes analyzed.")
        print("\nUse 'View All Results' to see the summary.")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            
            menu_options = {
                "1": "Set Job Requirements",
                "2": "Analyze Resume (Manual Entry)",
                "3": "Load Resume from File",
                "4": "View All Results",
                "5": "Save All Results",
                "6": "Load Previous Results",
                "7": "Run Demo",
                "8": "Exit"
            }
            
            self.print_menu("INTELLIGENT RESUME ANALYZER - MAIN MENU", menu_options)
            
            # Show current job requirements
            if self.job_requirements:
                print("Current Job Requirements:")
                print("-"*80)
                self.display_job_requirements()
                print("-"*80 + "\n")
            
            choice = self.get_input("Enter your choice (1-8): ", str)
            
            if choice == "1":
                self.setup_job_requirements()
            elif choice == "2":
                self.analyze_single_resume()
            elif choice == "3":
                self.load_resume_from_file()
            elif choice == "4":
                self.view_all_results()
            elif choice == "5":
                self.save_all_results()
            elif choice == "6":
                self.load_previous_results()
            elif choice == "7":
                self.run_demo()
            elif choice == "8":
                self.clear_screen()
                print("\n" + "="*80)
                print("Thank you for using Intelligent Resume Analyzer!".center(80))
                print("="*80 + "\n")
                break
            else:
                print("\n⚠ Invalid choice. Please select 1-8.")
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    cli = ResumeAnalyzerCLI()
    cli.run()