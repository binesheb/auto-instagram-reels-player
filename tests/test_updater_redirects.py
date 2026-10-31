import unittest
from unittest.mock import Mock, call, patch

from updater import (
    GITHUB_RAW,
    GITHUB_RAW_PATH_PREFIX,
    MAX_REDIRECTS,
    _http_get,
    _is_allowed_raw_url,
)


class UpdaterRedirectTests(unittest.TestCase):
    @staticmethod
    def _response(status_code, url, text="", location=None):
        response = Mock()
        response.status_code = status_code
        response.url = url
        response.headers = {}
        if location is not None:
            response.headers["Location"] = location
        response.text = text
        response.raise_for_status.return_value = None
        return response

    def test_only_https_urls_for_expected_repository_path_are_allowed(self):
        self.assertTrue(_is_allowed_raw_url(f"{GITHUB_RAW}/version.txt"))
        invalid_urls = [
            f"http://raw.githubusercontent.com{GITHUB_RAW_PATH_PREFIX}version.txt",
            "https://github.com/binesheb/auto-instagram-reels-player/main/version.txt",
            f"https://raw.githubusercontent.com:8443{GITHUB_RAW_PATH_PREFIX}version.txt",
            f"https://raw.githubusercontent.com@evil.example{GITHUB_RAW_PATH_PREFIX}version.txt",
            "https://raw.githubusercontent.com/another/repository/main/version.txt",
            f"https://raw.githubusercontent.com{GITHUB_RAW_PATH_PREFIX}../other/version.txt",
            f"https://raw.githubusercontent.com{GITHUB_RAW_PATH_PREFIX}%2e%2e/other/version.txt",
            f"{GITHUB_RAW}/version.txt?download=1",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(_is_allowed_raw_url(url))

    def test_direct_request_disables_automatic_redirects(self):
        url = f"{GITHUB_RAW}/version.txt"
        response = self._response(200, url, "0.1.5\n")
        with patch("updater.requests.get", return_value=response) as get:
            self.assertEqual(_http_get("version.txt"), "0.1.5\n")
        get.assert_called_once_with(url, timeout=10, allow_redirects=False)
        response.close.assert_called_once()

    def test_follows_relative_redirects_only_within_the_expected_repository(self):
        initial = f"{GITHUB_RAW}/version.txt"
        final = f"{GITHUB_RAW}/CHANGELOG.md"
        redirect = self._response(302, initial, location="CHANGELOG.md")
        response = self._response(200, final, "# changelog")
        with patch("updater.requests.get", side_effect=[redirect, response]) as get:
            self.assertEqual(_http_get("version.txt"), "# changelog")
        self.assertEqual(
            get.call_args_list,
            [
                call(initial, timeout=10, allow_redirects=False),
                call(final, timeout=10, allow_redirects=False),
            ],
        )
        redirect.close.assert_called_once()
        response.close.assert_called_once()

    def test_rejects_untrusted_redirect_before_requesting_its_target(self):
        initial = f"{GITHUB_RAW}/version.txt"
        redirect = self._response(
            302, initial, location="https://evil.example/payload"
        )
        with patch("updater.requests.get", return_value=redirect) as get:
            with self.assertRaisesRegex(RuntimeError, "redirect target is not trusted"):
                _http_get("version.txt")
        get.assert_called_once_with(initial, timeout=10, allow_redirects=False)
        redirect.close.assert_called_once()

    def test_rejects_http_and_nonstandard_port_redirects(self):
        initial = f"{GITHUB_RAW}/version.txt"
        locations = [
            f"http://raw.githubusercontent.com{GITHUB_RAW_PATH_PREFIX}version.txt",
            f"https://raw.githubusercontent.com:8443{GITHUB_RAW_PATH_PREFIX}version.txt",
        ]
        for location in locations:
            with self.subTest(location=location):
                redirect = self._response(302, initial, location=location)
                with patch("updater.requests.get", return_value=redirect) as get:
                    with self.assertRaisesRegex(RuntimeError, "redirect target is not trusted"):
                        _http_get("version.txt")
                get.assert_called_once()
                redirect.close.assert_called_once()

    def test_rejects_redirects_without_location(self):
        initial = f"{GITHUB_RAW}/version.txt"
        redirect = self._response(302, initial)
        with patch("updater.requests.get", return_value=redirect):
            with self.assertRaisesRegex(RuntimeError, "missing Location"):
                _http_get("version.txt")
        redirect.close.assert_called_once()

    def test_enforces_a_finite_redirect_limit(self):
        initial = f"{GITHUB_RAW}/version.txt"
        redirects = [
            self._response(302, initial, location="version.txt")
            for _ in range(MAX_REDIRECTS + 1)
        ]
        with patch("updater.requests.get", side_effect=redirects) as get:
            with self.assertRaisesRegex(RuntimeError, "redirect limit"):
                _http_get("version.txt")
        self.assertEqual(get.call_count, MAX_REDIRECTS + 1)
        for response in redirects:
            response.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
