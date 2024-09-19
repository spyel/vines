class RequestAborted(Exception):
    """The request was closed before it was completed, or timed out."""
    pass
