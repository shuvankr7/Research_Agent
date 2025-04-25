import unittest
from src.agents.research_agent import ResearchAgent

class TestResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResearchAgent()
        print("\nSetting up test environment...")
    
    def test_query_analysis(self):
        print("\nTesting query analysis...")
        query = "What are the impacts of AI on healthcare?"
        results = self.agent.analyze_query(query)
        print(f"Generated queries: {results}")
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 1)
    
    def test_error_handling(self):
        print("\nTesting error handling...")
        with self.assertRaises(Exception):
            self.agent.perform_search([])
        print("Error handling test passed")

def run_tests():
    print("Starting Research Agent Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResearchAgent)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    print("\nAll tests passed!" if success else "\nSome tests failed!")