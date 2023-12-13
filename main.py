from cfanalyzer import NSAnalyzer

test_file = "test.plist"

with open(test_file, "rb") as f:
    analyzer = NSAnalyzer(f)
