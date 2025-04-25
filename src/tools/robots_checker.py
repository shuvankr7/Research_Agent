import urllib.robotparser
import urllib.parse
import unittest

class RobotsChecker:
    def __init__(self):
        self.parser = urllib.robotparser.RobotFileParser()
        self.cache = {}
    
    def can_fetch(self, url: str) -> bool:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
            
        domain = urllib.parse.urlparse(url).netloc
        robots_url = f"https://{domain}/robots.txt"
        
        if robots_url not in self.cache:
            try:
                self.parser.set_url(robots_url)
                self.parser.read()
                self.cache[robots_url] = True
            except:
                return True
        
        return self.parser.can_fetch("*", url)

class TestRobotsChecker(unittest.TestCase):
    def setUp(self):
        self.checker = RobotsChecker()
        print("\nSetting up RobotsChecker test...")
    
    def test_valid_url(self):
        print("\nTesting valid URL...")
        url = "https://www.example.com/page"
        result = self.checker.can_fetch(url)
        print(f"Can fetch {url}: {result}")
        self.assertIsInstance(result, bool)
    
    def test_empty_url(self):
        print("\nTesting empty URL handling...")
        with self.assertRaises(ValueError):
            self.checker.can_fetch("")
        print("Empty URL test passed")
    
    def test_invalid_url(self):
        print("\nTesting invalid URL...")
        result = self.checker.can_fetch("not-a-url")
        print(f"Result for invalid URL: {result}")
        self.assertTrue(result)  # Should default to True for invalid URLs
    
    def test_cache_mechanism(self):
        print("\nTesting cache mechanism...")
        url = "https://www.test.com/page"
        first_result = self.checker.can_fetch(url)
        second_result = self.checker.can_fetch(url)
        print(f"Results match: {first_result == second_result}")
        self.assertEqual(first_result, second_result)

def run_tests():
    print("Starting RobotsChecker Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRobotsChecker)
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