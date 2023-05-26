# Todoist-Airtable Sync Server

This is a server application that syncs data between Todoist and Airtable. It uses the Todoist webhook API to listen for events and then updates the corresponding data in Airtable.

## Features

- Listens for Todoist webhook events
- Verifies the HMAC signature of incoming requests
- Handles different types of Todoist events
- Provides an endpoint for Todoist to send webhook events to
- Provides an endpoint to get tasks from Todoist
- Provides an endpoint to authorize the application with Todoist

## Setup

1. Clone the repository
2. Install the requirements using `pip install -r requirements.txt`
3. Set up your environment variables in a `.env` file. You will need the following variables:
    - `CLIENT_ID`: Your Todoist client ID
    - `CLIENT_SECRET`: Your Todoist client secret
    - `VERIFICATION_TOKEN`: Your Todoist verification token
    - `REDIRECT_URI`: Your redirect URI for Todoist OAuth
    - `DOMAIN`: The domain where your server is hosted
    - `PORT`: The port where your server is running
4. Build the Docker images using `docker-compose build`
5. Run the Docker containers using `docker-compose up`

## Usage

Once the server is running, you can send webhook events to `http://<your-domain>:<your-port>/webhook`. You can also get tasks from Todoist by sending a GET request to `http://<your-domain>:<your-port>/tasks` with your Todoist token as a query parameter.

To authorize the application with Todoist, send a GET request to `http://<your-domain>:<your-port>/authorize`. This will return a URL that you can visit to authorize the application.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
