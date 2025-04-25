from typing import List, Dict
import time
import unittest
from src.tools.search_tool import SearchTool

class NewsAggregator:
    def __init__(self):
        self.search_tool = SearchTool()
    
    def get_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """Get recent news articles related to the query."""
        if not query.strip():
            raise ValueError("Query cannot be empty")
            
        search_query = f"{query} news latest"
        results = self.search_tool.direct_search(
            search_query,
            max_results=max_results
        )
        
        # Filter results to ensure they're recent
        current_time = time.time()
        one_day = 24 * 60 * 60  # seconds in a day
        
        filtered_results = []
        for result in results:
            if 'timestamp' in result:
                try:
                    if current_time - result['timestamp'] <= one_day:
                        filtered_results.append(result)
                except:
                    filtered_results.append(result)
            else:
                filtered_results.append(result)
                
        return filtered_results[:max_results]

class TestNewsAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = NewsAggregator()
        print("\nSetting up NewsAggregator test...")

    def test_get_news(self):
        print("\nTesting news retrieval...")
        query = "AI technology"
        results = self.aggregator.get_news(query, max_results=3)
        print(f"Retrieved {len(results)} news articles for query: '{query}'")
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) <= 3)
        if results:
            self.assertIsInstance(results[0], dict)

    def test_empty_query(self):
        print("\nTesting empty query handling...")
        with self.assertRaises(ValueError):
            self.aggregator.get_news("")

    def test_max_results(self):
        print("\nTesting max results limit...")
        results = self.aggregator.get_news("technology", max_results=1)
        self.assertTrue(len(results) <= 1)
        print(f"Retrieved {len(results)} result as expected")

def run_tests():
    print("Starting NewsAggregator Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewsAggregator)
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