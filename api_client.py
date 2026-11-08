def get_statistics(dataset_id):

    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/statistics"
    )

    response.raise_for_status()
    return response.json()


# Fetch correlation matrix
def get_correlation(dataset_id):

    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/correlation"
    )

    response.raise_for_status()
    return response.json()
