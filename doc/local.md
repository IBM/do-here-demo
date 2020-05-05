# Run Locally

This document shows how to run the application using on your local machine.


## Steps

**Complete prerequisites**

1. [Clone the repo](https://github.com/IBM/do-here-demo#clone-the-repo)
1. [Generate an API Key from the HERE Developer Portal](https://github.com/IBM/do-here-demo#generate-an-api-key-from-the-here-developer-portal)
1. [Provision a Watson Machine Learning service](https://github.com/IBM/do-here-demo#provision-a-watson-machine-learning-service)


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

1. Install the requirements for local deployment

    ```shell
    pip install -r requirements_local.txt
    ```

**Run the demo application**

1.  Make a copy of the `.env.example` file in the `dash-app` directory, and name it `.env`.

    ```shell
    cp .env.example .env
    ```

1. Edit the newly created `.env` file and update the following variables accordingly:

    - `HERE_API_KEY` - REST API key for the HERE Location services
    - `WML_API_KEY` - API key for the Watson Machine Learning service
    - `WML_INSTANCE_ID` - Instance ID for the Watson Machine Learning service
    - `WML_URL` - URL for the Watson Machine Learning service

1. Launch the application

    ```shell
    python server.py
    ```

1. Access the application at the URL: http://localhost:8050
