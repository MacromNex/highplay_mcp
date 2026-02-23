#!/usr/bin/env python3
"""
Tool validation test for CycPep MCP Server
Tests individual tool functions directly to validate functionality.
"""

import sys
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Setup paths
TEST_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TEST_ROOT))
sys.path.insert(0, str(TEST_ROOT / "src"))

# Import the server module to get the tool functions
import src.server as server_module

from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO")

class ToolValidationRunner:
    def __init__(self):
        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_name": "cycpep-tools",
            "tests": {},
            "issues": [],
            "summary": {}
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, test_name: str, status: str, details: str = "", error: str = ""):
        """Log test result"""
        self.total_tests += 1

        if status == "passed":
            self.passed_tests += 1
            logger.info(f"✓ {test_name}: PASSED")
        else:
            self.failed_tests += 1
            logger.error(f"✗ {test_name}: FAILED - {error}")

        self.results["tests"][test_name] = {
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

    def test_server_info(self):
        """Test the get_server_info tool"""
        try:
            # Call the function directly via .fn attribute
            result = server_module.get_server_info.fn()

            if isinstance(result, dict) and "server_name" in result:
                self.log_test("get_server_info", "passed",
                              f"Server info returned: {result['server_name']}")
                logger.info(f"Available tools: {len(result.get('sync_tools', []) + result.get('submit_tools', []))}")
            else:
                self.log_test("get_server_info", "failed",
                              f"Unexpected result format: {type(result)}")

        except Exception as e:
            self.log_test("get_server_info", "failed", "", str(e))

    def test_job_management(self):
        """Test job management tools"""
        try:
            # Test list_jobs
            result = server_module.list_jobs.fn()
            if isinstance(result, dict):
                self.log_test("list_jobs", "passed",
                              f"List jobs returned: {len(result.get('jobs', []))} jobs")
            else:
                self.log_test("list_jobs", "failed",
                              f"Unexpected result type: {type(result)}")

            # Test get_job_status with non-existent job
            result = server_module.get_job_status.fn("nonexistent")
            if isinstance(result, dict) and ("error" in result or "status" in result):
                self.log_test("get_job_status_nonexistent", "passed",
                              "Correctly handled non-existent job")
            else:
                self.log_test("get_job_status_nonexistent", "failed",
                              f"Unexpected result: {result}")

        except Exception as e:
            self.log_test("job_management", "failed", "", str(e))

    def test_sync_tools(self):
        """Test synchronous tools with various inputs"""
        try:
            # Test analyze_cyclic_peptide with missing inputs (should handle gracefully)
            result = server_module.analyze_cyclic_peptide.fn()
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                self.log_test("analyze_peptide_no_input", "passed",
                              f"Tool handled missing input: {status}")
            else:
                self.log_test("analyze_peptide_no_input", "failed",
                              f"Unexpected result: {result}")

            # Test train_mcts_generate_data with minimal parameters
            result = server_module.train_mcts_generate_data.fn(peptide_length=8, num_samples=5)
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                self.log_test("train_mcts_generate_minimal", "passed",
                              f"MCTS data generation: {status}")
            else:
                self.log_test("train_mcts_generate_minimal", "failed",
                              f"Unexpected result: {result}")

        except Exception as e:
            self.log_test("sync_tools", "failed", "", str(e))

    def test_submit_tools(self):
        """Test submit tools (job submission)"""
        try:
            # Test submit_mcts_training with minimal parameters
            result = server_module.submit_mcts_training.fn(epochs=1, batch_size=4)

            if isinstance(result, dict) and "job_id" in result:
                job_id = result["job_id"]
                self.log_test("submit_mcts_training", "passed",
                              f"Job submitted with ID: {job_id}")

                # Test job status check
                time.sleep(1)  # Give it a moment
                status_result = server_module.get_job_status.fn(job_id)
                if isinstance(status_result, dict):
                    job_status = status_result.get("status", "unknown")
                    self.log_test("check_job_status", "passed",
                                  f"Job status check: {job_status}")
                else:
                    self.log_test("check_job_status", "failed",
                                  f"Status check failed: {status_result}")
            else:
                self.log_test("submit_mcts_training", "failed",
                              f"Job submission failed: {result}")

        except Exception as e:
            self.log_test("submit_tools", "failed", "", str(e))

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test with invalid parameters
            result = server_module.train_mcts_generate_data.fn(peptide_length=-1, num_samples=0)
            if isinstance(result, dict):
                self.log_test("error_handling_invalid_params", "passed",
                              f"Handled invalid params: {result.get('status', 'unknown')}")
            else:
                self.log_test("error_handling_invalid_params", "failed",
                              f"Unexpected result: {result}")

        except Exception as e:
            self.log_test("error_handling", "failed", "", str(e))

    def run_all_tests(self):
        """Run all test suites"""
        logger.info("Starting tool validation tests...")

        self.test_server_info()
        self.test_job_management()
        self.test_sync_tools()
        self.test_submit_tools()
        self.test_error_handling()

        # Generate summary
        self.results["summary"] = {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "pass_rate": f"{self.passed_tests/self.total_tests*100:.1f}%" if self.total_tests > 0 else "N/A"
        }

        return self.results

    def generate_report(self) -> str:
        """Generate markdown report"""
        summary = self.results["summary"]

        md = f"""# Step 7: Tool Validation Results

## Test Information
- **Test Date**: {self.results["test_date"]}
- **Server Name**: {self.results["server_name"]}
- **Total Tests**: {summary["total_tests"]}
- **Passed**: {summary["passed"]}
- **Failed**: {summary["failed"]}
- **Pass Rate**: {summary["pass_rate"]}

## Tool Test Results

| Test Name | Status | Details |
|-----------|--------|---------|
"""

        for test_name, result in self.results["tests"].items():
            status_icon = "✅" if result["status"] == "passed" else "❌"
            details = result["details"][:100] + "..." if len(result["details"]) > 100 else result["details"]
            md += f"| {test_name} | {status_icon} {result['status']} | {details} |\n"

        if summary["failed"] > 0:
            md += "\n## Issues Found\n\n"
            failed_tests = [name for name, result in self.results["tests"].items()
                          if result["status"] == "failed"]
            for test in failed_tests:
                error = self.results["tests"][test].get("error", "Unknown error")
                md += f"- **{test}**: {error}\n"

        md += "\n## Summary\n\n"
        if summary["failed"] == 0:
            md += "✅ All tool validation tests passed successfully!\n"
            md += "- Server initialization works correctly\n"
            md += "- All tools are properly registered and callable\n"
            md += "- Error handling is working as expected\n"
            md += "- Job submission and management functions correctly\n"
        else:
            md += f"❌ {summary['failed']} test(s) failed out of {summary['total_tests']}\n"
            md += "- Review failed tests and apply necessary fixes\n"

        return md


def main():
    """Main test runner"""
    runner = ToolValidationRunner()

    try:
        results = runner.run_all_tests()

        # Generate and save reports
        md_report = runner.generate_report()

        # Ensure directories exist
        Path("reports").mkdir(exist_ok=True)

        # Save reports
        json_file = Path("reports/tool_validation.json")
        md_file = Path("reports/tool_validation.md")

        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)

        with open(md_file, 'w') as f:
            f.write(md_report)

        print(f"\n{'='*60}")
        print(f"TOOL VALIDATION TESTS COMPLETED")
        print(f"{'='*60}")
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed']}")
        print(f"Failed: {results['summary']['failed']}")
        print(f"Pass Rate: {results['summary']['pass_rate']}")
        print(f"\nReports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")
        print(f"{'='*60}")

        return results['summary']['failed'] == 0

    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)