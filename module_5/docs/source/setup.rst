Setup and Configuration
=======================

This page describes how to install, configure, and run the GradCafe Analytics Dashboard.

Requirements
------------

The project requires:

* Python 3.12
* PostgreSQL
* Git

Environment Variables
---------------------

Database credentials are loaded from environment variables rather than hard-coded values.

Create a ``.env`` file based on ``.env.example``:

.. code-block:: text

   DB_NAME=gradcafe_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432

   DATABASE_URL=postgresql://your_user:your_password@localhost:5432/gradcafe_db

Fresh Install Using pip
-----------------------

Create and activate a virtual environment:

.. code-block:: bash

   python -m venv .venv
   source .venv/Scripts/activate

Install dependencies and install the project:

.. code-block:: bash

   pip install -r requirements.txt
   pip install -e .

Fresh Install Using uv
----------------------

Install uv:

.. code-block:: bash

   pip install uv

Create an environment and install dependencies:

.. code-block:: bash

   uv venv
   source .venv/Scripts/activate

   uv pip install -r requirements.txt
   uv pip install -e .

Loading the Database
--------------------

Load applicant data into PostgreSQL:

.. code-block:: bash

   python -m src.load_data

Running the Application
-----------------------

Start the Flask application:

.. code-block:: bash

   python src/app.py

Then open:

.. code-block:: text

   http://127.0.0.1:5000

Running Tests and Checks
------------------------

Run the test suite:

.. code-block:: bash

   pytest

Run Pylint:

.. code-block:: bash

   pylint src --fail-under=10

Generate the dependency graph:

.. code-block:: bash

   pydeps src/app.py --noshow -T svg -o dependency.svg

Run Snyk dependency scanning:

.. code-block:: bash

   snyk test