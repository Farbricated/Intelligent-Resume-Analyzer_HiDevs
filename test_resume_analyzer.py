"""
Test Suite for Intelligent Resume Analyzer
Comprehensive unit tests for all major components
"""

import unittest
import json
import os
from resume_analyzer import ResumeAnalyzer


class TestResumeAnalyzer(unittest.TestCase):
    """Test cases for ResumeAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ResumeAnalyzer()
        
        self.sample_resume = """
        John Doe
        john.doe@email.com | +1-555-123-4567
        
        PROFESSIONAL SUMMARY
        Senior Software Engineer with 7 years of experience in Python development
        
        SKILLS
        Python, Django, Flask, SQL, PostgreSQL, MongoDB, Git, REST API, Docker
        
        EXPERIENCE
        Senior Developer at Tech Solutions Inc (2018-Present)
        Software Engineer at Digital Systems Corp (2016-2018)
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2016
        """
        
        self.job_requirements = {
            "position": "Senior Python Developer",
            "required_skills": ["Python", "Django", "SQL", "Git"],
            "required_experience": 5,
            "required_education": "Bachelor"
        }
    
    def test_extract_name(self):
        """Test name extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        self.assertEqual(resume_data['name'], 'John Doe')
    
    def test_extract_email(self):
        """Test email extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        self.assertEqual(resume_data['email'], 'john.doe@email.com')
    
    def test_extract_phone(self):
        """Test phone number extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        self.assertIn('555', resume_data['phone'])
    
    def test_extract_skills(self):
        """Test skills extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        skills = [s.lower() for s in resume_data['skills']]
        
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertIn('sql', skills)
    
    def test_extract_experience(self):
        """Test experience extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        self.assertEqual(resume_data['experience']['total_years'], 7)
    
    def test_extract_education(self):
        """Test education extraction"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        education_str = ' '.join(resume_data['education']).lower()
        self.assertIn('bachelor', education_str)
    
    def test_calculate_match_score(self):
        """Test match score calculation"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        match_score, breakdown = self.analyzer.calculate_match_score(
            resume_data, 
            self.job_requirements
        )
        
        # Should have high score (has required skills and experience)
        self.assertGreaterEqual(match_score, 60)
        self.assertLessEqual(match_score, 100)
        
        # Check breakdown components
        self.assertIn('skills_score', breakdown)
        self.assertIn('experience_score', breakdown)
        self.assertIn('education_score', breakdown)
    
    def test_generate_recommendation(self):
        """Test recommendation generation"""
        # High score
        rec_high = self.analyzer.generate_recommendation(85, {})
        self.assertIn('HIGHLY RECOMMENDED', rec_high)
        
        # Medium score
        rec_med = self.analyzer.generate_recommendation(65, {})
        self.assertIn('RECOMMENDED', rec_med)
        
        # Low score
        rec_low = self.analyzer.generate_recommendation(30, {})
        self.assertIn('NOT RECOMMENDED', rec_low)
    
    def test_generate_report(self):
        """Test report generation"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        match_score, breakdown = self.analyzer.calculate_match_score(
            resume_data,
            self.job_requirements
        )
        
        report = self.analyzer.generate_report(
            resume_data,
            self.job_requirements,
            match_score,
            breakdown
        )
        
        self.assertIn('CANDIDATE ANALYSIS REPORT', report)
        self.assertIn('John Doe', report)
        self.assertIn('MATCH SCORE', report)
    
    def test_save_and_load_data(self):
        """Test data persistence"""
        test_data = [
            {"name": "Test Candidate", "score": 75},
            {"name": "Another Candidate", "score": 60}
        ]
        
        test_file = "test_data.json"
        
        # Test save
        success = self.analyzer.save_data(test_data, test_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        # Test load
        loaded_data = self.analyzer.load_data(test_file)
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['name'], "Test Candidate")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_analyze_resume_complete(self):
        """Test complete analysis pipeline"""
        results = self.analyzer.analyze_resume(
            self.sample_resume,
            self.job_requirements
        )
        
        self.assertIn('resume_data', results)
        self.assertIn('match_score', results)
        self.assertIn('score_breakdown', results)
        self.assertIn('recommendation', results)
        self.assertIn('report', results)
        self.assertIn('analyzed_at', results)
    
    def test_edge_case_empty_resume(self):
        """Test handling of empty resume"""
        empty_resume = ""
        resume_data = self.analyzer.parse_resume(empty_resume)
        
        self.assertEqual(resume_data['name'], 'Name Not Found')
        self.assertEqual(resume_data['email'], 'Email Not Found')
    
    def test_edge_case_minimal_resume(self):
        """Test handling of minimal resume"""
        minimal_resume = """
        Jane Smith
        jane@example.com
        """
        
        resume_data = self.analyzer.parse_resume(minimal_resume)
        self.assertEqual(resume_data['name'], 'Jane Smith')
        self.assertEqual(resume_data['email'], 'jane@example.com')
    
    def test_skills_matching_case_insensitive(self):
        """Test that skills matching is case-insensitive"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        
        # Mix of cases in requirements
        mixed_requirements = {
            "required_skills": ["PYTHON", "django", "SQL"],
            "required_experience": 5,
            "required_education": "Bachelor"
        }
        
        match_score, breakdown = self.analyzer.calculate_match_score(
            resume_data,
            mixed_requirements
        )
        
        # Should still match despite case differences
        self.assertGreater(breakdown['skills_score'], 0)
    
    def test_partial_experience_matching(self):
        """Test partial credit for experience"""
        resume_data = self.analyzer.parse_resume(self.sample_resume)
        
        # Require more experience than candidate has
        high_exp_requirements = {
            "required_skills": ["Python"],
            "required_experience": 15,  # Candidate has 7
            "required_education": "Bachelor"
        }
        
        _, breakdown = self.analyzer.calculate_match_score(
            resume_data,
            high_exp_requirements
        )
        
        # Should get partial credit
        self.assertGreater(breakdown['experience_score'], 0)
        self.assertLess(breakdown['experience_score'], 30)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.analyzer = ResumeAnalyzer()
    
    def test_multiple_email_addresses(self):
        """Test resume with multiple emails"""
        resume = """
        John Doe
        john@email.com
        Alternative: johndoe@gmail.com
        """
        
        resume_data = self.analyzer.parse_resume(resume)
        # Should extract the first valid email
        self.assertIn('@', resume_data['email'])
    
    def test_various_phone_formats(self):
        """Test different phone number formats"""
        formats = [
            "+1-555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "5551234567"
        ]
        
        for phone in formats:
            resume = f"John Doe\n{phone}\njohn@email.com"
            resume_data = self.analyzer.parse_resume(resume)
            self.assertNotEqual(resume_data['phone'], 'Phone Not Found')
    
    def test_special_characters_in_resume(self):
        """Test handling of special characters"""
        resume = """
        José García
        jose.garcia@email.com
        Skills: Python, C++, C#, Node.js
        """
        
        resume_data = self.analyzer.parse_resume(resume)
        self.assertIn('José', resume_data['name'])
    
    def test_zero_requirements(self):
        """Test matching with no requirements"""
        resume_data = self.analyzer.parse_resume("John Doe\njohn@email.com")
        
        empty_requirements = {
            "required_skills": [],
            "required_experience": 0,
            "required_education": ""
        }
        
        match_score, _ = self.analyzer.calculate_match_score(
            resume_data,
            empty_requirements
        )
        
        # Should still calculate a score
        self.assertIsInstance(match_score, int)


class TestDataPersistence(unittest.TestCase):
    """Test data saving and loading"""
    
    def setUp(self):
        self.analyzer = ResumeAnalyzer()
        self.test_file = "test_persistence.json"
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_save_load_cycle(self):
        """Test complete save and load cycle"""
        original_data = [
            {
                "name": "John Doe",
                "match_score": 85,
                "skills": ["Python", "Django"]
            },
            {
                "name": "Jane Smith",
                "match_score": 70,
                "skills": ["JavaScript", "React"]
            }
        ]
        
        # Save
        self.analyzer.save_data(original_data, self.test_file)
        
        # Load
        loaded_data = self.analyzer.load_data(self.test_file)
        
        # Verify
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['name'], "John Doe")
        self.assertEqual(loaded_data[1]['match_score'], 70)
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file"""
        data = self.analyzer.load_data("nonexistent_file.json")
        self.assertEqual(data, [])
    
    def test_unicode_in_saved_data(self):
        """Test saving and loading Unicode characters"""
        unicode_data = [
            {
                "name": "José García",
                "skills": ["Python", "数据科学"]
            }
        ]
        
        self.analyzer.save_data(unicode_data, self.test_file)
        loaded_data = self.analyzer.load_data(self.test_file)
        
        self.assertEqual(loaded_data[0]['name'], "José García")


def run_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResumeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPersistence))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)