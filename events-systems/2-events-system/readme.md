# Description
Assume we have 2 API endpoints, create order and notify.
We expect following structure:
    - API service called gateway, which includes 2 dedicated endpoints, mimics api gateway
    - API service called orders
        - it is supposed to consume events from topic which stands for new orders
    - API service called notifications
        - it is supposed to consume events from topic which stands for notifications (for users, aka order created)

