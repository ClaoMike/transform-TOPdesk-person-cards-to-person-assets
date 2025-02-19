def categorize_status(logger, response, showResponseTextIfSuccessfull=False):
    # If the request was not a success (status code != 2xx), then we stop
    match response.status_code:
        case _ if 200 <= response.status_code < 300:
            if showResponseTextIfSuccessfull:
                logger.info(f"Request was successful! Status code: {response.status_code}, Message: {response.text}")
            else:
                logger.info(f"Request was successful! Status code: {response.status_code}")
        case _ if 300 <= response.status_code < 400:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _ if 400 <= response.status_code < 500:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _ if 500 <= response.status_code < 600:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit