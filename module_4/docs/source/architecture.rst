Architecture
============

Overview
--------

This project is a Flask and PostgreSQL application for analyzing GradCafe applicant data. The application is organized into three main layers:

* ETL and data loading
* PostgreSQL database storage
* Flask web application and analysis display

Data Flow
---------

The main data flow is:

.. code-block:: text

   JSON applicant data
          |
          v
   load_data.py / pull_new_data.py
          |
          v
   PostgreSQL applicants table
          |
          v
   query_data.py
          |
          v
   Flask /analysis route
          |
          v
   HTML dashboard

ETL Layer
---------

The ETL layer prepares applicant records and loads them into PostgreSQL.

``load_data.py`` loads existing cleaned JSON records into the database. It creates the ``applicants`` table if needed and inserts records while avoiding duplicates.

``pull_new_data.py`` supports pulling additional GradCafe records, cleaning them, saving JSON output files, and inserting new records into PostgreSQL.

Database Layer
--------------

The database layer uses PostgreSQL. The primary table is ``applicants``. It stores applicant metadata such as program, comments, date added, application status, term, GPA, GRE scores, degree type, and LLM-generated standardized fields.

Duplicate records are avoided by using ``p_id`` as the unique applicant record identifier.

Analysis Layer
--------------

``query_data.py`` contains SQL queries that answer the analysis questions shown on the web dashboard. It calculates counts, percentages, average GPA/GRE values, acceptance rates, and biology-related Johns Hopkins PhD applicant statistics.

Web Layer
---------

``app.py`` defines the Flask application. The main route is ``/analysis``, which renders the analysis dashboard. The application also includes POST routes for pulling new data and refreshing the analysis results.

Testing and CI
--------------

The project uses pytest for Flask route tests, button behavior tests, database tests, formatting tests, and integration tests. GitHub Actions starts a PostgreSQL service, initializes the database, installs dependencies, and runs the full pytest suite with coverage.