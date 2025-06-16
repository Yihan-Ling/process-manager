import logging

# Set up a custom logger
logger = logging.getLogger("process_manager")
logger.setLevel(logging.DEBUG)

# Create a file handler to log to a file
file_handler = logging.FileHandler("./process_manager/log/process_manager.log")
file_handler.setLevel(logging.DEBUG)

# Create a console handler to log to the console
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
# logger.addHandler(console_handler)
