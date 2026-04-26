"""
Unit tests for application runtime mode detection utilities.

This module validates detection of execution context signals and the resolution of a single runtime mode based on those signals, including frozen executable environments, test execution contexts, and default source-based execution, as well as consistency of the module-level constant with the detection logic.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/utils/test__app_mode.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Direct mutation of os.environ to simulate presence or absence of test-related environment variables.
	- Direct mutation of sys.modules to simulate loaded modules and submodules indicating test execution.
	- Direct mutation of sys attributes to simulate frozen executable environments.
	- Preservation and restoration of os.environ, sys.modules, and sys attributes in setUp and tearDown to maintain isolation between tests.

Dependencies:
	- Python version: >= 3.10
	- Standard Library: unittest, os, sys

Notes:
	- Tests rely on interpreter-level state mutation and assume proper restoration to maintain determinism.
	- Detection of test execution includes both environment variable and module inspection strategies as exercised by the tests.
	- Resolution logic is validated in priority order by simulating mutually exclusive environment conditions.
	- The module-level constant is validated against the detection function without altering environment state during that specific test.

License:
	- Internal Use Only
"""

import os
import sys
import unittest

# noinspection PyProtectedMember
import src.utils._app_mode as am


class TestIsRunningAsExecutable(unittest.TestCase):
    """
    Unit tests for the `_is_running_as_executable` function in `env.py`.

    These tests ensure that the function correctly detects whether the
    application is running in frozen (executable) mode or not.
    """

    def setUp(self):
        """
        Preserve the original sys.frozen attribute before each test.
        """
        self.original_frozen = getattr(sys, "frozen", None)

    def tearDown(self):
        """
        Restore the original sys.frozen attribute after each test.
        """
        if self.original_frozen is None:
            if hasattr(sys, "frozen"):
                del sys.frozen
        else:
            sys.frozen = self.original_frozen

    def test_returns_true_when_frozen(self):
        """
        Should return True when `sys.frozen` is set to True.
        """
        # ARRANGE
        sys.frozen = True
        expected = True

        # ACT
        result = am._is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_returns_false_when_not_frozen(self):
        """
        Should return False when `sys.frozen` is not set.
        """
        # ARRANGE
        if hasattr(sys, "frozen"):
            del sys.frozen
        expected = False

        # ACT
        result = am._is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsRunningAUnittest(unittest.TestCase):
    """
    Unit tests for the `_is_running_a_unittest` function in `env.py`.

    These tests ensure that the function correctly detects whether the
    application is running under unittest or pytest environments.
    """

    def setUp(self):
        """
        Preserve the original environment and sys.modules state before each test.
        """
        self.original_environ = dict(os.environ)
        self.original_modules = dict(sys.modules)

    def tearDown(self):
        """
        Restore the original environment and sys.modules after each test.
        """
        os.environ.clear()
        os.environ.update(self.original_environ)

        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_when_pytest_env_var_set(self):
        """
        Should return True when `PYTEST_CURRENT_TEST` environment variable is set.
        """
        # ARRANGE
        os.environ["PYTEST_CURRENT_TEST"] = "some_test_info"
        expected = True

        # ACT
        result = am._is_running_a_unittest()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_when_unittest_submodule_loaded(self):
        """
        Should return True when unittest and a unittest submodule are in sys.modules.
        """
        # ARRANGE
        sys.modules["unittest"] = unittest
        # noinspection PyTypeChecker
        sys.modules["unittest.mock"] = object()  # fake submodule
        expected = True

        # ACT
        result = am._is_running_a_unittest()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_when_no_unittest_and_no_pytest(self):
        """
        Should return False when neither unittest modules nor pytest env var exist.
        """
        # ARRANGE
        os.environ.pop("PYTEST_CURRENT_TEST", None)
        sys.modules.pop("unittest", None)
        sys.modules.pop("unittest.mock", None)
        expected = False

        # ACT
        result = am._is_running_a_unittest()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsRunningFromSource(unittest.TestCase):
    """
    Unit tests for the `_is_running_from_source` function in `env.py`.

    These tests ensure that the function correctly detects whether the
    application is running directly from source code (non-frozen).
    """

    def setUp(self):
        """
        Preserve the original sys.frozen attribute before each test.
        """
        self.original_frozen = getattr(sys, "frozen", None)

    def tearDown(self):
        """
        Restore the original sys.frozen attribute after each test.
        """
        if self.original_frozen is None:
            if hasattr(sys, "frozen"):
                del sys.frozen
        else:
            sys.frozen = self.original_frozen

    def test_when_not_frozen(self):
        """
        Should return True when `sys.frozen` attribute is not set.
        """
        # ARRANGE
        if hasattr(sys, "frozen"):
            del sys.frozen
        expected = True

        # ACT
        result = am._is_running_from_source()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_when_frozen(self):
        """
        Should return False when `sys.frozen` attribute exists.
        """
        # ARRANGE
        sys.frozen = True
        expected = False

        # ACT
        result = am._is_running_from_source()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestDetermineAppMode(unittest.TestCase):
    """
    Unit tests for the `_determine_app_mode` function in `env.py`.

    Verifies the function correctly selects:
      - EXECUTABLE when running as a frozen binary.
      - UNITTEST when running under unittest/pytest.
      - DEVELOPMENT when running from source with no test signals.
    """

    def setUp(self):
        """
        Preserve the original environment, sys.frozen, and sys.modules state
        before each test for isolation.
        """
        self.original_environ = dict(os.environ)
        self.original_frozen = getattr(sys, "frozen", None)
        self.original_modules = dict(sys.modules)

    def tearDown(self):
        """
        Restore environment, sys.frozen, and sys.modules state after each test.
        """
        os.environ.clear()
        os.environ.update(self.original_environ)

        if self.original_frozen is None:
            if hasattr(sys, "frozen"):
                del sys.frozen
        else:
            sys.frozen = self.original_frozen

        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_when_frozen(self):
        """
        Should return AppMode.EXECUTABLE when `sys.frozen` is truthy.
        """
        # ARRANGE
        sys.frozen = True
        expected = am.AppMode.EXECUTABLE

        # ACT
        result = am._determine_app_mode()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertIs(result, expected)

    def test_when_unittest(self):
        """
        Should return AppMode.UNITTEST when code is running under unittest.
        """
        # ARRANGE
        if hasattr(sys, "frozen"):
            del sys.frozen
        expected = am.AppMode.UNITTEST

        # ACT
        result = am._determine_app_mode()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertIs(result, expected)

    def test_when_not_frozen_and_no_unittest(self):
        """
        Should return AppMode.DEVELOPMENT when not frozen and no test signals exist.
        """
        # ARRANGE
        if hasattr(sys, "frozen"):
            del sys.frozen
        os.environ.pop("PYTEST_CURRENT_TEST", None)
        sys.modules.pop("unittest", None)
        expected = am.AppMode.DEVELOPMENT

        # ACT
        result = am._determine_app_mode()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertIs(result, expected)


class TestAppModeConstant(unittest.TestCase):
    """
    Unit test for the `APP_MODE` constant in `env.py`.

    Ensures the constant reflects the same mode as `_determine_app_mode()`
    at test time (no environment manipulation).
    """

    def test_app_mode(self):
        """
        Should equal the result of `_determine_app_mode()`.
        """
        # ARRANGE
        # Expected mode computed directly from the function
        expected = am._determine_app_mode()

        # ACT
        # Module-level constant evaluated at import time
        result = am.APP_MODE

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertIs(result, expected)


if __name__ == "__main__":
    unittest.main()
