# Squirrels

This is an API framework for creating APIs that generate sql queries dynamically and runs them. 

"Squirrels" stands for "**S**tructured **QU**ery **I**nterface with **R**ealtime **R**endering and **E**laborate **L**anguage **S**ynchronization".

It's also called "squirrels" for the following reasons:
1. The name "SQURL" was also considered which is short for "SQL URL". This sounds like "squirrel"
2. Following the theme of using animal names (plural form) for useful python packages (like "pandas")

## Features Roadmap

- Provide `squirrels test [dataset]` CLI to create the parameters output and all the rendered sql files in an `outputs` folder **[DONE]**
    - Provide a `--cfg selections.cfg` option to test parameter selections as a config file and a `--data sample_lu_data.csv` option to provide an alternative file(s) for dimension table data **[DONE]**
    - Provide a `--runquery` option that lets the user produce the results by querying database **[DONE]**
- Support conditional default value for selection parameters that cascade based on dependent parameters **[DONE]**
- Write final view payload as output **[DONE]**
- Provide a `squirrels load-modules` CLI to git clone all the modules that the squirrels project references **[DONE]**
- Provide a `squirrels run` CLI to activate all REST APIs on localhost with the following resource paths:
    - `/v{framework_version}/{base_path}/{dataset}/parameters` **[DONE]**
        - get query parameters for dataset, and takes the same query parameters to allow for dependencies
    - `/v{framework_version}/{base_path}/{dataset}` **[DONE]**
        - get tabular results for dataset with selected query parameters
    - `/v{framework_version}` **[DONE]**
        - get catalog of all dataset resource paths for this project
    - `/` **[DONE]**
        - UI for sample testing interface
- Introduce context variables, and support sql templating with context variables and project variables **[DONE]**
- Provide a `squirrels init` CLI to create a squirrels project from scratch including sample files for manifest.yaml, parameters.py, functions.py, database_view.sql.j2, selections.cfg, sample_lu_data.csv, and .gitignore
- Provide a `squirrels unit-test` CLI to perform unit tests from a `tests` folder
