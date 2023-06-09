import socket
import pickle
from PIL import Image
import matplotlib.pyplot as plt

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip_addr = input("Enter the ip address you want to connect: ")
port = int(input("Enter the port you want to connect: "))

# Connect to the server
while True:
    try:
        client_socket.connect((ip_addr, port))
        print(f"Connected to server {ip_addr} on {port} port")
        break
    except:
        print(f"Connection to {ip_addr} on {port} port is refused")

# Show picture
def image_receive(num):
    
    for i in range(num):
        received_data = b""
        print("waiting for server")
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            received_data += data

        print("received picture, showing picture")
        received_fig = pickle.loads(received_data)
        plt.figure(received_fig.number)
        plt.show()
        print(f"show {i + 1}th figure at client side")

    # with open(image_path, 'wb') as file:
    #    file.write(received_data)
    # image = Image.open(image_path)
    # plt.imshow(image)
    # plt.show()


while True:

    # Get user's request
    db = input("Enter the database you want to use: ")
    user_input = input("Enter your request (machine_learning, mongodb_operation, data_exploration, custom_operation): ")

    if user_input == 'machine_learning':
        train_collection = input("Enter the collection you want to train on: ")
        test_collection = input("Enter the collection you want to test on: ")
        preprocessing_methods_list = []
        preprocessing_methods_string = input(
            "Do you want to remove duplicates? (y/n) \n"
        )
        if preprocessing_methods_string == "y":
            preprocessing_methods_list.append("remove_duplicates")

        preprocessing_methods_string = input(
            "If you want to apply standard scaling, please enter 1\n"
            "If you want to apply min_max scaling, please enter 2\n"
            "If you don't want to use any, please enter None\n"
        )

        if (preprocessing_methods_string == "1"):
            preprocessing_methods_list.append("standard_scaling")
        elif (preprocessing_methods_string == "2"):
            preprocessing_methods_list.append("min_max_scaling")

        preprocessing_methods_string = input(
            "If you want to impute mean, please enter 1\n"
            "If you want to impute median, please enter 2\n"
            "If you want to impute frequency, please enter 3\n"
            "If you don't want to use any, please enter None\n"
        )

        if (preprocessing_methods_string == "1"):
            preprocessing_methods_list.append("impute_mean")
        elif (preprocessing_methods_string == "2"):
            preprocessing_methods_list.append("impute_median")
        elif (preprocessing_methods_string == "3"):
            preprocessing_methods_list.append("impute_frequency")

        predict_column = input("Enter the column you want to predict: ")

        # Prepare the request for prediction
        request = {
            'database': db,
            'train_collection': train_collection,
            'test_collection': test_collection,
            'request_type': 'machine_learning',
            'preprocessing_methods': preprocessing_methods_list,
            'model': 'lightwood',
            'predict_column': predict_column,
        }

    elif user_input == 'mongodb_operation':
        db_operation = input(
            'Please enter the operation you want to do in mongosh syntax\n'
            'ex: db.getCollection("data").find({})\n'
        )
        request = {
            'database': db,
            'request_type': 'mongodb_operation',
            'db_operation': db_operation
        }

    elif user_input == 'data_exploration':
        # Prepare the request for custom operation
        collection = input("Please input the colleciton you want to explore: ")
        data_exploration_string = input(
            "If you want to show missing values, please enter 1\n"
            "If you want to show feature distributions, please enter 2\n"
        )
        data_exploration_method = []
        if data_exploration_string == "1":
            data_exploration_method.append("show_missing_values")
        if data_exploration_string == "2":
            data_exploration_method.append("show_feature_distributions")
        request = {
            'database': db,
            'request_type': 'data_exploration',
            'collection': collection,
            'data_exploration': data_exploration_method
        }

    elif user_input == 'custom_operation':
        # Prepare the request for custom operation
        custom_operation = input("Please input your custom operation: ")
        request = {
            'request_type': custom_operation
        }
    else:
        print("Invalid request")
        continue

    # Send the request to the server
    client_socket.send(pickle.dumps(request))

    # Receive the response from the server
    if request['request_type'] == 'mongodb_operation':
        received_data = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            received_data += data

        response = pickle.loads(received_data)


    else:
        data = client_socket.recv(4096)
        response = pickle.loads(data)

    # Process the response
    if response['response_type'] == 'predictions':
        print(f"Predictions: {response['data']}")
        image_receive(1)

    elif response['response_type'] == 'custom_response':
        print("Custom operation completed successfully")

    elif response['response_type'] == 'mongodb_operation':
        print(f"MongoDB operation: \n{response['data']}")

    elif response['response_type'] == 'data_exploration':
        print("Server has received the request, sending image")
        image_receive(1)

    elif response['response_type'] == 'error':
        print("An error occurred:", response['message'])
    else:
        print("Unknown response type")

    # Ask if the user wants to continue
    user_input = input("Do you want to continue (y/n)? : ")
    if user_input.lower() != 'y':
        break

# Close the connection
client_socket.close()
