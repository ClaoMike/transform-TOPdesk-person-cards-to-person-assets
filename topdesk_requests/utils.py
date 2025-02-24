def categorize_status(logger, response, showResponseTextIfSuccessfull=False):
    """
        Categorizes and handles the status code of an HTTP response.

        This function checks the response's status code and logs or raises an error depending on whether the request was successful. By default, successful responses (2xx) are simply logged, but the complete response text can be logged with the 'showResponseTextIfSuccessfull' parameter.

        Args:
            logger (object): A logging object that provides the 'info' and 'error' methods.
            response (requests.Response): The response object returned from the HTTP request.
            showResponseTextIfSuccessfull (bool, optional): If True, the full response text will be included in the success log. Defaults to False.

        Raises:
            SystemExit: If the status code is not in the 2xx range.
    """
    # If the request was not a success (status code != 2xx), then we halt the program
    match response.status_code:
        case _ if 200 <= response.status_code < 300:
            # Log success, optionally including the response text
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

def listsUnion(list1, list2):
    """
        Returns the union of two lists as a new list, without duplicates.

        This function combines the elements of 'list1' and 'list2' into a single list, discarding any duplicate elements. The order in the resulting list is  not guaranteed.

        Args:
            list1 (list): The first list.
            list2 (list): The second list.

        Returns:
            list: A list containing unique elements from both 'list1' and 'list2'.
    """
    # Convert each list to a set, perform a union operation, then convert back to a list
    return list(set(list1) | set(list2))

def listsDifference(list1, list2):
    """
        Returns the difference of two lists as a new list, removing duplicates.

        This function finds all elements that are present in 'list1' but not in 'list2'. Duplicate elements are removed. The order in the resulting list is not guaranteed.

        Args:
            list1 (list): The list from which elements are subtracted.
            list2 (list): The list whose elements should not appear in the result.

        Returns:
            list: A list of elements present in 'list1' but not in 'list2'.
    """
    # Convert each list to a set, perform a difference operation, then convert back to a list
    return list(set(list1) - set(list2))