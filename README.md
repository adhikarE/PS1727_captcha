Note: This repository hosts the solution for Smart India Hackathon 2024's problem statement ID **1727** engineered by team *Captcha*

### Problem Statement ID 1727

### Problem Statemnet Title
Universal Switch Set with Data Encryption and Decryption for Legacy Applications without Cyber Safety Measures

### Problem Statement Discription
Background: In metro system OEM install the switches and bind these switches with their MAC address mostly so it is difficult to install or upgrade the different switch in network without compromising the cyber security. Retrofitting these systems with modern security protocols can he challenging and costly, particularly for organizations with limited resources or technical expertise. Description: The problem statement aims to develop a universal switch set equipped with data encryption and decryption capabilities that can be seamlessly integrated into various legacy applications lacking cyber safety measures. The switch set will provide a standardized interface for encrypting sensitive data before transmission and decrypting it upon receipt, thereby enhancing the security of legacy systems. The switch set will support industry-standard encryption algorithms and protocols to ensure compatibility with a wide range of legacy applications. It will be designed to be easily configurable and customizable to accommodate different encryption requirements and data formats used by various applications. Furthermore, the switch set will include robust key management features to securely generate. store, and distribute encryption keys to authorized users. This will prevent unauthorized access to encrypted data and ensure the integrity and confidentiality of sensitive information. Expected Solution: The proposed solution will involve the development of a universal switch set with data encryption and decryption capabilities tailored for legacy applications without cyber safety measures. This switch set will consist of modular components, including encryption/decryption engines, key management systems, and integration interfaces. The switch set will seamlessly integrate with existing infrastructure and protocols. requiring minimal configuration and customization. By retrofitting legacy applications with data encryption and decryption capabilities, the proposed solution will enable organizations to safeguard their sensitive information and comply with regulatory requirements without the need for costly system upgrades or replacements

#### Organization

Ministry of Housing and Urban Affairs

#### Department

Smart Cities Mission

#### Category

Software

#### Theme

Blockchain & Cybersecurity

#  Solution

  

###  One Bug Approach

  

We install a virtual client on the user side and add a IoT device before the legacy application running our virtual client that decrypts data before sending it to the legacy application (Ex. Old DB server or Excel server not capable to run the virtual client) ensuring seamless transition and End-to-End encryption.

  

###  Data Flow

  

####  User -> Legacy Application

-  All the data / queries gets encrypted in the application layer of the user side itself then it proceeds to be transmitted to the Legacy networks without any interruption since the Network & Data link headers remain unchanged.

-  The data gets caught by the IoT bug before reaching the legacy application. The bug then proceeds to decrypt the encrypted data and transmits it to the legacy application as plain text that it can then process.

-  The legacy application receives the plain text data from the bug and processes it.

  

####  Legacy Application -> User

-  The legacy application sends back an response to the command / query issued by the user and transmits it to the bug in plain text.

-  The bug captures the data and figures out it is from the legacy application. The bug then encrypts the plain text data and forwards the encrypted response to the user. The data travels seamlessly through the legacy networks

-  The user receives the encrypted and the virtual client installed on the user side, decrypts the data and renders it for the user in plain text

  

###  Encryption (RSA 2048 Bit)

  

**RSA** is an asymmetric encryption algorithm used for secure data transmission. It is based on the difficulty of factoring large numbers, which makes it secure for modern encryption needs.

  

####  Key Features:

  

-  **Asymmetric encryption**: RSA uses a pair of keys: a **public key** for encryption and a **private key** for decryption.

-  **Security**: The security of RSA relies on the computational difficulty of factoring the product of two large prime numbers.

  

####  Practical Considerations:

  

-  **Long-Term Security**: For highly sensitive data, transitioning to RSA-3072 or higher may be considered as a future-proofing measure.

  

In summary, RSA-2048 is currently a secure and widely adopted standard for encryption, offering strong protection for data while balancing computational efficiency.

  

###  Key Generation

  

A Python script (`generate_keys.py`) generates a pair of RSA keys (private and public) to be used by the bug server and client. The private key is used for decrypting messages, while the public key is used for encrypting data sent between components.

  

#  Working

##  Prototype Flow

  

1.  **Key Generation**: A Python script (`generate_keys.py`) generates a pair of RSA keys (private and public) to be used by the bug server and client. The private key is used for decrypting messages, while the public key is used for encrypting data sent between components.

  

2.  **Client Application**:

-  The client connects to the bug server and sends its encrypted commands.

-  The bug server decrypts these commands and forwards them to the legacy application.

-  Once the legacy application processes the request and sends a response, the bug server encrypts it and sends it back to the client.

-  The client decrypts the server's response to retrieve the original data.

  

3.  **Bug Server**:

-  The bug server listens for incoming client connections on a specific port.

-  Upon receiving data, it decrypts it using its private key and forwards the plain-text data to the legacy application.

-  It receives the plain-text response from the legacy application, encrypts it using the public key, and sends the encrypted data back to the client.

  

4.  **Legacy Application**:

-  The legacy application is a simple server that listens for plain-text messages from the bug server.

-  It processes requests and responds with plain-text data to the bug server.

  

###  Data Flow Overview:

  

```

[Client] --> (Encrypted Data) --> [Bug Server] --> (Plain Text Data) --> [Legacy Application]

  

[Client] <-- (Encrypted Response) <-- [Bug Server] <-- (Plain Text Response) <--

[Legacy Application]

```

  

###  Example Commands:

  

-  `data`: Requests a specific set of data from the legacy application.

-  `SIH`: Requests another specific dataset.

-  `RST`: Closes the connection between the client and the bug server.

  

##  Installation and Usage

  

1.  **Dependencies**:

-  Python 3.x

-  `cryptography` library: Install it using `pip install cryptography`.

  

2.  **How to Run**:

  

-  **Step 1**: Generate the RSA keys by running `generate_keys.py`. This will generate the keys in the `Keys` folder:

```bash

python generate_keys.py

```

-  **Step 2**: Start the legacy application:

```bash

python legacy_application.py

```

-  **Step 3**: Start the bug server:

```bash

python bug.py

```

-  **Step 4**: Run the client application and interact with the server:

```bash

python client.py

```

  

##  Debugging

  

Both the client and server applications include a debugging mode. If you want to enable detailed logs of encrypted and decrypted messages, type `Y` when prompted for debugging mode at the start of each script.

  

```plaintext

Debugging (Y/N): Y

```

  

In debug mode, the client and server will print the original message, encrypted message, and decrypted message for better visibility and troubleshooting.

  

##  Future Improvements

  

-  **Additional Encryption Support**: Implement more encryption algorithms like AES to handle different use cases.

-  **Session Management**: Add session-based encryption for more dynamic key management.

-  **Authentication**: Implement client-server authentication to ensure only authorized clients can communicate.
