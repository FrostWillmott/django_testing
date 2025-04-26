

# Django Testing Project - README

## Project Overview

This Django project demonstrates comprehensive testing techniques for Django applications. It consists of two separate Django applications, each with its own set of tests:

1. **ya_news** - A news application with comments functionality
2. **ya_note** - A personal notes application

Each application is tested using different testing approaches:
- **ya_news** uses pytest
- **ya_note** uses Django's built-in TestCase class

## Requirements

The project requires:
- Python 3.12
- Django 5.1
- pytest and related plugins
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Create a virtual environment:
```shell script
python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```shell script
pip install -r requirements.txt
```


## Running Tests

### Running All Tests

Use the provided shell script:
```shell script
./run_tests.sh
```


### Running Tests for Specific Applications

To run tests for the ya_news application:
```shell script
pytest ya_news/news/pytest_tests/ -v --ds=yanews.settings
```


To run tests for the ya_note application:
```shell script
python manage.py test notes.tests -v
```


Or with pytest:
```shell script
pytest ya_note/notes/tests/ -v --ds=yanote.settings
```


## Test Structure

### ya_news (pytest-based tests)

The tests are organized into three categories:
- **test_content.py**: Tests the content rendered on pages, including:
  - Number of news items displayed
  - Order of news items
  - Comment sorting
  - Comment form visibility

- **test_logic.py**: Tests application business logic, including:
  - Comment creation/editing/deletion permissions
  - Handling of inappropriate content
  - User permissions and restrictions

- **test_routes.py**: Tests URL routes and access permissions, including:
  - Anonymous user access
  - Authenticated user access
  - HTTP status codes for different user roles

### ya_note (Django TestCase-based tests)

Similar to ya_news, but using Django's TestCase class:
- **test_content.py**: Tests page content
- **test_logic.py**: Tests note creation, editing, and deletion logic
- **test_routes.py**: Tests URL routes and access permissions

## Important Files

- **conftest.py**: Contains pytest fixtures
- **pytest.ini**: Configuration for pytest
- **requirements.txt**: Project dependencies
- **run_tests.sh**: Script to run all tests

## Note on Dependencies

The project uses specific versions of pytest and related plugins to ensure compatibility. If encountering issues with newer Python versions, you may need to adjust the dependency versions.