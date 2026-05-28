"""Language detection pipeline for code analysis.

This module provides language detection and prioritization for security review.
Priority languages (JavaScript, TypeScript, Python) are analyzed first.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LanguageStats:
    """Statistics for a detected language."""

    language: str
    file_count: int
    total_lines: int
    total_bytes: int
    priority: int  # Lower is higher priority


# Language configuration with priorities
# Priority 1 = highest (analyzed first)
LANGUAGE_CONFIG = {
    # Priority 1: Primary web languages
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs", ".cjs"],
        "priority": 1,
        "display_name": "JavaScript",
        "security_relevant": True,
    },
    "typescript": {
        "extensions": [".ts", ".tsx", ".mts", ".cts"],
        "priority": 1,
        "display_name": "TypeScript",
        "security_relevant": True,
    },
    "python": {
        "extensions": [".py", ".pyw"],
        "priority": 1,
        "display_name": "Python",
        "security_relevant": True,
    },
    # Priority 2: Backend languages
    "java": {
        "extensions": [".java"],
        "priority": 2,
        "display_name": "Java",
        "security_relevant": True,
    },
    "go": {
        "extensions": [".go"],
        "priority": 2,
        "display_name": "Go",
        "security_relevant": True,
    },
    "csharp": {
        "extensions": [".cs"],
        "priority": 2,
        "display_name": "C#",
        "security_relevant": True,
    },
    "ruby": {
        "extensions": [".rb", ".rake"],
        "priority": 2,
        "display_name": "Ruby",
        "security_relevant": True,
    },
    "php": {
        "extensions": [".php", ".phtml"],
        "priority": 2,
        "display_name": "PHP",
        "security_relevant": True,
    },
    # Priority 3: Systems languages
    "rust": {
        "extensions": [".rs"],
        "priority": 3,
        "display_name": "Rust",
        "security_relevant": True,
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
        "priority": 3,
        "display_name": "C++",
        "security_relevant": True,
    },
    "c": {
        "extensions": [".c"],
        "priority": 3,
        "display_name": "C",
        "security_relevant": True,
    },
    # Priority 4: Shell and scripting
    "shell": {
        "extensions": [".sh", ".bash", ".zsh"],
        "priority": 4,
        "display_name": "Shell",
        "security_relevant": True,
    },
    "powershell": {
        "extensions": [".ps1", ".psm1", ".psd1"],
        "priority": 4,
        "display_name": "PowerShell",
        "security_relevant": True,
    },
    # Priority 5: Config and markup (lower priority but still analyzed)
    "yaml": {
        "extensions": [".yml", ".yaml"],
        "priority": 5,
        "display_name": "YAML",
        "security_relevant": True,  # Config files can have secrets
    },
    "json": {
        "extensions": [".json"],
        "priority": 5,
        "display_name": "JSON",
        "security_relevant": True,  # Config files can have secrets
    },
    "sql": {
        "extensions": [".sql"],
        "priority": 5,
        "display_name": "SQL",
        "security_relevant": True,
    },
}

# Build extension to language mapping
EXTENSION_TO_LANGUAGE = {}
for lang, config in LANGUAGE_CONFIG.items():
    for ext in config["extensions"]:
        EXTENSION_TO_LANGUAGE[ext] = lang


class LanguageDetector:
    """Detect and prioritize programming languages in code files."""

    def __init__(self):
        """Initialize the language detector."""
        self.language_config = LANGUAGE_CONFIG
        self.extension_map = EXTENSION_TO_LANGUAGE

    def detect_from_extension(self, file_path: str) -> str | None:
        """Detect language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language identifier or None if unknown
        """
        ext = Path(file_path).suffix.lower()
        return self.extension_map.get(ext)

    def _detect_from_shebang(self, first_line: str) -> str | None:
        """Detect language from shebang line."""
        shebang = first_line.lower()
        if "python" in shebang:
            return "python"
        if "node" in shebang or "deno" in shebang:
            return "javascript"
        if "ruby" in shebang:
            return "ruby"
        if "bash" in shebang or "sh" in shebang or "zsh" in shebang:
            return "shell"
        if "php" in shebang:
            return "php"
        return None

    def _detect_from_patterns(self, content: str) -> str | None:
        """Detect language from code patterns."""
        # TypeScript indicators
        if re.search(r"\binterface\s+\w+\s*\{", content) or re.search(
            r":\s*(string|number|boolean|any)\b", content
        ):
            return "typescript"

        # Python indicators
        if re.search(r"^def\s+\w+\s*\(", content, re.MULTILINE) or re.search(
            r"^class\s+\w+.*:", content, re.MULTILINE
        ):
            return "python"

        # Java indicators
        if re.search(r"^(public|private|protected)\s+class\s+", content, re.MULTILINE):
            return "java"

        # Go indicators
        if re.search(r"^package\s+\w+", content, re.MULTILINE) and re.search(
            r"^func\s+", content, re.MULTILINE
        ):
            return "go"

        return None

    def detect_from_content(self, content: str, file_path: str = "") -> str | None:
        """Detect language from file content using heuristics.

        Args:
            content: File content
            file_path: Optional file path for shebang detection

        Returns:
            Language identifier or None if unknown
        """
        # Check shebang line
        lines = content.split("\n", 1)
        if lines and lines[0].startswith("#!"):
            result = self._detect_from_shebang(lines[0])
            if result:
                return result

        # Content-based heuristics (check first 2KB)
        return self._detect_from_patterns(content[:2000])

    def get_language_priority(self, language: str) -> int:
        """Get priority for a language (lower = higher priority).

        Args:
            language: Language identifier

        Returns:
            Priority level (1-5, lower is higher priority)
        """
        config = self.language_config.get(language)
        if config:
            return config["priority"]
        return 99  # Unknown languages get lowest priority

    def get_display_name(self, language: str) -> str:
        """Get display name for a language.

        Args:
            language: Language identifier

        Returns:
            Human-readable language name
        """
        config = self.language_config.get(language)
        if config:
            return config["display_name"]
        return language.title()

    def is_security_relevant(self, language: str) -> bool:
        """Check if language is relevant for security analysis.

        Args:
            language: Language identifier

        Returns:
            True if security-relevant
        """
        config = self.language_config.get(language)
        if config:
            return config.get("security_relevant", False)
        return False

    def analyze_files(self, files: list[dict[str, Any]]) -> dict[str, LanguageStats]:
        """Analyze a list of files and gather language statistics.

        Args:
            files: List of file dicts with 'path' and optionally 'content', 'size'

        Returns:
            Dictionary of language to LanguageStats
        """
        stats: dict[str, dict] = {}

        for file in files:
            path = file.get("path", "")
            content = file.get("content", "")
            size = file.get("size", len(content) if content else 0)

            # Detect language
            language = self.detect_from_extension(path)
            if not language and content:
                language = self.detect_from_content(content, path)

            if not language:
                continue

            # Count lines
            lines = content.count("\n") + 1 if content else 0

            # Aggregate stats
            if language not in stats:
                stats[language] = {
                    "file_count": 0,
                    "total_lines": 0,
                    "total_bytes": 0,
                }

            stats[language]["file_count"] += 1
            stats[language]["total_lines"] += lines
            stats[language]["total_bytes"] += size

        # Convert to LanguageStats
        result = {}
        for lang, data in stats.items():
            result[lang] = LanguageStats(
                language=lang,
                file_count=data["file_count"],
                total_lines=data["total_lines"],
                total_bytes=data["total_bytes"],
                priority=self.get_language_priority(lang),
            )

        return result

    def prioritize_files(
        self,
        files: list[dict[str, Any]],
        max_files: int | None = None,
    ) -> list[dict[str, Any]]:
        """Sort and filter files by language priority.

        Args:
            files: List of file dicts with 'path' and optionally 'content'
            max_files: Maximum number of files to return

        Returns:
            Prioritized list of files
        """
        # Add language info to each file
        files_with_lang = []
        for file in files:
            path = file.get("path", "")
            content = file.get("content", "")

            language = self.detect_from_extension(path)
            if not language and content:
                language = self.detect_from_content(content, path)

            if language and self.is_security_relevant(language):
                files_with_lang.append(
                    {
                        **file,
                        "_language": language,
                        "_priority": self.get_language_priority(language),
                    }
                )

        # Sort by priority (lower first) then by path
        files_with_lang.sort(key=lambda f: (f["_priority"], f.get("path", "")))

        # Remove internal fields and limit
        result = []
        for file in files_with_lang:
            clean_file = {k: v for k, v in file.items() if not k.startswith("_")}
            clean_file["language"] = file["_language"]
            result.append(clean_file)

        if max_files:
            result = result[:max_files]

        return result


# Singleton instance
_detector: LanguageDetector | None = None


def get_language_detector() -> LanguageDetector:
    """Get or create LanguageDetector singleton."""
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector
