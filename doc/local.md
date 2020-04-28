# Run Locally

This document shows how to run the application using on your local machine.


## Steps

1. Complete steps 1, 2, and 3 in the [README](https://github.com/IBM/do-here-demo/blob/master/README.md)


**Install Decision Optimization**

1. Download and install the latest [IBM ILOG CPLEX Optimization Studio](https://www.ibm.com/products/ilog-cplex-optimization-studio) or the [IBM ILOG CPLEX Optimization Studio Free (Community) Edition](https://www.ibm.com/account/reg/us-en/signup?formid=urx-20028)

    > **Note**: you may need to give permissions to the Optimization Studio  
    > for example: `chmod +x cplex_studio1290-osx.app/Contents/MacOS/*`
    > https://www.ibm.com/support/pages/node/142583 

**Set up the demo application**

1. Create a Python 3 environments & activate the environment. For example, using `conda`

    ```shell
    conda create -n demoenv python=3.7
    conda activate demoenv
    ```

1. Go into the `dash-app` directory of the cloned repository

    ```shell
    cd <path_to_cloned_repo>/dash-app
    ```

1. Install requirements

    ```shell
    pip install -r requirements.txt
    ```

1. Install the `docplex` and `cplex` python libraries

    ```shell
    pip install docplex cplex
    ```

**Run the demo application**

1.  Make a copy of the `.env.example` file in the `dash-app` directory, and name it `.env`.

    ```shell
    cp .env.example .env
    ```

1. Edit the newly created `.env` file and update all variables except `WML_DEPLOYMENT_UID`

1. Launch the application

    ```shell
    python index.py
    ```

1. Access the application at the URL: http://localhost:8050
