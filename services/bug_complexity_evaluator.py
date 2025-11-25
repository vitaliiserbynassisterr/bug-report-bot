"""Bug complexity evaluation service using Claude AI."""

import logging
from typing import Dict, Literal
from anthropic import Anthropic

from config.settings import settings

logger = logging.getLogger(__name__)

ComplexityLevel = Literal["SIMPLE", "MODERATE", "COMPLEX"]


class BugComplexityEvaluator:
    """Evaluates bug complexity to determine if it can be auto-fixed."""

    def __init__(self):
        """Initialize the evaluator with Claude API."""
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-haiku-20241022"  # Fast and cheap for evaluation

    async def evaluate_complexity(self, bug_data: Dict) -> Dict[str, any]:
        """
        Evaluate bug complexity using Claude AI.

        Args:
            bug_data: Bug information including description, console logs, etc.

        Returns:
            Dictionary with complexity level, confidence, and reasoning
        """
        try:
            prompt = self._build_evaluation_prompt(bug_data)

            logger.info(f"Evaluating complexity for bug {bug_data.get('bug_id', 'unknown')}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,  # Deterministic evaluation
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse Claude's response
            content = response.content[0].text
            result = self._parse_evaluation_response(content)

            logger.info(
                f"Bug {bug_data.get('bug_id')} evaluated as {result['complexity']} "
                f"(confidence: {result['confidence']})"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to evaluate bug complexity: {e}")
            # Default to COMPLEX on error (safe fallback)
            return {
                "complexity": "COMPLEX",
                "confidence": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "can_auto_fix": False
            }

    def _build_evaluation_prompt(self, bug_data: Dict) -> str:
        """Build the evaluation prompt for Claude."""
        description = bug_data.get("description", "No description provided")
        console_logs = bug_data.get("console_logs", "No logs provided")
        environment = bug_data.get("environment", "Unknown")
        priority = bug_data.get("priority", "Unknown")
        tags = bug_data.get("tags", [])

        return f"""You are an expert software engineer evaluating whether a bug can be automatically fixed by an AI agent.

**Bug Details:**
- Priority: {priority}
- Environment: {environment}
- Tags: {", ".join(tags) if tags else "None"}

**Description:**
{description}

**Console Logs/Stack Trace:**
{console_logs}

**Task:** Evaluate the complexity of this bug and determine if it can be automatically fixed by an AI agent with high confidence.

**Criteria for SIMPLE bugs (can be auto-fixed):**
- Clear, specific error message with file and line number
- Likely affects a single file or small number of files
- Common patterns: typos, missing null checks, simple validation errors, import errors
- No architecture or design changes required
- Can be fixed without extensive context of business logic
- Test changes are straightforward

**Criteria for MODERATE bugs (manual fix recommended):**
- Error location unclear or affects multiple files
- Requires understanding of business logic
- May need refactoring or pattern changes
- Tests may need significant updates

**Criteria for COMPLEX bugs (requires human developer):**
- No clear error message or stack trace
- Architectural or design issues
- Cross-cutting concerns
- Performance or security issues
- Requires user research or product decisions

**Output Format (strict JSON):**
{{
  "complexity": "SIMPLE|MODERATE|COMPLEX",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of the complexity assessment",
  "likely_files": ["file1.py", "file2.py"],
  "fix_approach": "Brief description of likely fix approach",
  "can_auto_fix": true|false
}}

Respond ONLY with the JSON object, no additional text."""

    def _parse_evaluation_response(self, content: str) -> Dict:
        """Parse Claude's JSON response."""
        import json

        # Extract JSON from response (in case there's extra text)
        content = content.strip()

        # Find JSON object
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")

        json_str = content[start_idx:end_idx]
        result = json.loads(json_str)

        # Validate required fields
        required_fields = ["complexity", "confidence", "reasoning", "can_auto_fix"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")

        # Ensure complexity is valid
        if result["complexity"] not in ["SIMPLE", "MODERATE", "COMPLEX"]:
            raise ValueError(f"Invalid complexity level: {result['complexity']}")

        return result

    def should_auto_fix(self, evaluation: Dict) -> bool:
        """
        Determine if bug should be auto-fixed based on evaluation.

        Args:
            evaluation: Result from evaluate_complexity()

        Returns:
            True if bug should be auto-fixed
        """
        # Only auto-fix SIMPLE bugs with high confidence
        return (
            evaluation.get("complexity") == "SIMPLE"
            and evaluation.get("confidence", 0.0) >= 0.7
            and evaluation.get("can_auto_fix", False)
        )


# Singleton instance
_evaluator = None


def get_evaluator() -> BugComplexityEvaluator:
    """Get or create the bug complexity evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = BugComplexityEvaluator()
    return _evaluator
