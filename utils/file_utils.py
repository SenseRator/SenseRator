import os

def get_directory_name(path):
    """
    Gets the directory name from the specified path.

    Parameters:
        path (str): The file or directory path.

    Returns:
        str: The directory name from the path.
    """
    return os.path.dirname(path)

def list_directory_contents(directory, file_extension=None):
    """
    Gets list of all files and directories within the specified directory. 

    Parameters: 
        directory (str): path of the directory

    Returns: 
        list: List of all files and directories in the specified path. 
    """
    try:
        files = os.listdir(directory)
        if file_extension:
            return [f for f in files if f.endswith(file_extension)]
        return files
    except OSError as e:
        print(f"File operation error: {e}")
        return []

def change_directory(path):
    """
    Changes the current working directory to the specified path.

    Parameters:
        path (str): The path to change to.

    Returns:
        bool: True if the directory was changed successfully, False otherwise.
    """
    try:
        os.chdir(path)
        return True
    except OSError as e:
        print(f"Error changing directory to {path}: {e}")
        return False

def join_paths(*args):
    """
    Joins given arguments into a single path.

    Parameters:
        args (tuple): Path components to be joined.

    Returns:
        str: The resulting joined path.
    """
    return os.path.join(*args)

def check_path_exists(path):
    """
    Checks if the given path exists.

    Parameters:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)

def get_current_directory():
    """
    Gets the current working directory.

    Returns:
        str: The current working directory.
    """
    return os.getcwd()

def make_directory(path, exist_ok=True):
    """
    Creates a directory at the specified path.

    Parameters:
        path (str): The directory path to create.
        exist_ok (bool, optional): If True, does not raise an error if the directory already exists.

    Returns:
        bool: True if the directory was created or already exists, False if an error occurred.
    """
    try:
        os.makedirs(path, exist_ok=exist_ok)
        return True
    except OSError as e:
        if not exist_ok or not os.path.isdir(path):
            print(f"Error creating directory {path}: {e}")
        return False