# Wallet Manager

This is a Django RESTful API for managing user wallets and tracking activities related to wallet transcations.

## Requirements

    - Python 3.10.12
    - Django
    - Django Rest Framework
    - PostgreSQL

## Postman Collection

    - https://api.postman.com/collections/21654066-b0221b9b-d925-41ee-99b5-399b16491b9e?access_key=PMAT-01HT290C2X6QDJRPNV9WKTGSBM

## Installation

1. Clone the repository:

    ### commands
        - git clone https://github.com/ayushbenny/wallet_project.git
        - cd wallet_project

2. Install the packages/dependencies:
    
    ### commands
        - python3 -m venv venv
        - source venv/bin/activate
        - pip install -r requirements.txt

3. Configuration change

    - Make changes in the "config.json" file related to the DB credentials

4. Application Setup
    
    ### commands
        - python manage.py makemigrations
        - python manage.py migrate
        - python manage.py runserver


## Usage

    ### API Endpoints

        1. Register User -> `POST /user/`
            - Create new user into the system and their associated wallet.

        2. Login User -> `POST /api/token/`
            - Creates access token and refresh token based on the information that is provided.
            - Validated based on "username" and "password".

        3. Wallet Creation -> `POST /api/wallet/`
            - Independent functionality to create Wallet for corresponding user.

        3. Deposit Fund -> `POST /api/wallet/deposit`
            - Deposit Funds to the Wallets of corresponding user. It will check for the present amount and add along with it.

        4. Fetch Wallet Balance -> `GET /api/wallet/deposit`
            - Fetch wallet balance of the corresponding user.

        5. Withdraw Fund -> `POST /api/wallet/withdraw`
            - Withdraw fund from an user's wallet and reduce the amount from the wallet.
            - The amount should not exceed the wallet's current balance or else it will throw error.

        6. Acitivity Tracker (History) -> `GET /api/activity_tracker/`
            - Filter the history of the transcations with its transcation type, from date and to date.
            - If transcation type is not provided means all the related data will be displayed.

        7. Transfer Fund -> `POST /api/transfer_funds`
            - Transfer the fund from one user's wallet to another user who is present in the system.

    
    ### Authentication

        - Authentication is handled using JWT tokens.
        - To authenticate, sned a POST request to `/api/token/` with username and password.
        - The return will be a `Access Token` and `Refresh Token`.
