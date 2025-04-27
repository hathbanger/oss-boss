import json
import requests
from agno.tools import Toolkit

class NpmTools(Toolkit):
    """
    Agno Toolkit for NPM package analysis using the public npm registry API.
    """
    def __init__(self):
        super().__init__(name="npm_tools")
        self.register(self.get_package_info)
        self.register(self.get_package_versions)
        self.register(self.search_packages)
        self.register(self.get_downloads_stats)
        self.register(self.get_dependents_count)
        self.register(self.get_package_score)

    def get_package_info(self, package_name: str) -> str:
        """
        Fetch metadata for a given NPM package.
        Args:
            package_name: The name of the NPM package
        Returns:
            JSON-formatted string containing package metadata
        """
        url = f"https://registry.npmjs.org/{package_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            info = {
                "name": data.get("name"),
                "description": data.get("description"),
                "latest_version": data.get("dist-tags", {}).get("latest"),
                "homepage": data.get("homepage"),
                "repository": data.get("repository", {}).get("url"),
                "license": data.get("license"),
                "author": data.get("author", {}).get("name"),
                "maintainers": [m.get("name") for m in data.get("maintainers", [])],
                "keywords": data.get("keywords"),
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching info for package '{package_name}': {str(e)}"
            }, indent=2)

    def get_package_versions(self, package_name: str) -> str:
        """
        Fetch all available versions for a given NPM package.
        Args:
            package_name: The name of the NPM package
        Returns:
            JSON-formatted string containing a list of versions
        """
        url = f"https://registry.npmjs.org/{package_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            versions = list(data.get("versions", {}).keys())
            return json.dumps({"name": package_name, "versions": versions}, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching versions for package '{package_name}': {str(e)}"
            }, indent=2)

    def search_packages(self, query: str) -> str:
        """
        Search for NPM packages by keyword or name.
        Args:
            query: The search query string
        Returns:
            JSON-formatted string containing a list of matching packages
        """
        url = f"https://registry.npmjs.org/-/v1/search?text={query}&size=10"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for pkg in data.get("objects", []):
                package = pkg.get("package", {})
                results.append({
                    "name": package.get("name"),
                    "version": package.get("version"),
                    "description": package.get("description"),
                    "links": package.get("links", {}),
                })
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error searching for packages with query '{query}': {str(e)}"
            }, indent=2)

    def get_downloads_stats(self, package_name: str, period: str = "last-month") -> str:
        """
        Fetch download counts for a package over a given period.
        Args:
            package_name: The name of the NPM package
            period: 'last-day', 'last-week', or 'last-month' (default)
        Returns:
            JSON-formatted string containing download stats
        """
        url = f"https://api.npmjs.org/downloads/point/{period}/{package_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching download stats for package '{package_name}': {str(e)}"
            }, indent=2)

    def get_dependents_count(self, package_name: str) -> str:
        """
        Estimate the number of packages that depend on the given package using npms.io API.
        Args:
            package_name: The name of the NPM package
        Returns:
            JSON-formatted string containing dependents count
        """
        url = f"https://api.npms.io/v2/package/{package_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            dependents_count = data.get("collected", {}).get("npm", {}).get("dependentsCount")
            return json.dumps({"name": package_name, "dependents_count": dependents_count}, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching dependents count for package '{package_name}': {str(e)}"
            }, indent=2)

    def get_package_score(self, package_name: str) -> str:
        """
        Fetch package quality, maintenance, and popularity scores from npms.io.
        Args:
            package_name: The name of the NPM package
        Returns:
            JSON-formatted string containing package scores
        """
        url = f"https://api.npms.io/v2/package/{package_name}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            score = data.get("score", {})
            return json.dumps({"name": package_name, "score": score}, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching score for package '{package_name}': {str(e)}"
            }, indent=2) 