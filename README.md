# Smart India Hackathon 2024 Solution by Team *Captcha*

## Problem Statement ID: 1727  
**Title:** Universal Switch Set with Data Encryption and Decryption for Legacy Applications without Cyber Safety Measures

### Problem Statement Description
**Background:**  
In metro systems, OEMs install switches and bind them to their MAC addresses, making it difficult to install or upgrade switches in the network without compromising cybersecurity. Retrofitting these systems with modern security protocols can be challenging and costly, especially for organizations with limited resources or technical expertise.

**Description:**  
The problem statement aims to develop a universal switch set equipped with data encryption and decryption capabilities. This set should seamlessly integrate into various legacy applications lacking cyber safety measures. It will provide a standardized interface for encrypting sensitive data before transmission and decrypting it upon receipt, enhancing the security of legacy systems. The switch set will support industry-standard encryption algorithms and protocols to ensure compatibility with a wide range of applications. It will include robust key management features for securely generating, storing, and distributing encryption keys to authorized users, ensuring the integrity and confidentiality of sensitive information.

**Expected Solution:**  
The solution involves developing a universal switch set with encryption and decryption capabilities, tailored for legacy applications. This switch set will consist of modular components, including encryption/decryption engines, key management systems, and integration interfaces. The switch set will integrate with existing infrastructure and protocols, requiring minimal configuration and customization. This will enable organizations to safeguard sensitive information without the need for costly system upgrades or replacements.

---

### Organization:  
**Ministry of Housing and Urban Affairs**

**Department:**  
Smart Cities Mission

**Category:**  
Software

**Theme:**  
Blockchain & Cybersecurity

---

## Solution Overview

### One Bug Approach

We install a virtual client on the user side and add an IoT device before the legacy application that decrypts data before sending it to the legacy application (e.g., old DB server or Excel server). This ensures seamless transition and end-to-end encryption.

### Data Flow

#### User -> Legacy Application
1. All data/queries are encrypted at the application layer on the user side, leaving network and data link headers unchanged.
2. The encrypted data is intercepted by the IoT bug before reaching the legacy application. The bug decrypts the data and sends it as plain text to the legacy application.
3. The legacy application processes the plain-text data.

#### Legacy Application -> User
1. The legacy application sends a plain-text response to the IoT bug.
2. The bug encrypts the plain-text response and forwards it to the user.
3. The user’s virtual client decrypts the data and renders it as plain text.

---

## Encryption: RSA 2048 Bit

**RSA** is an asymmetric encryption algorithm used for secure data transmission, relying on the difficulty of factoring large prime numbers.

### Key Features:
- **Asymmetric encryption**: RSA uses a public key for encryption and a private key for decryption.
- **Security**: The security of RSA is based on the computational difficulty of factoring large prime numbers.

### Practical Considerations:
- **Long-Term Security**: For sensitive data, RSA-3072 or higher can be considered for future-proofing.

---

## Prototype Flow

### 1. Key Generation & Exchange
Upon establishing a connection, both the client and the server dynamically generate new RSA key pairs. The server transmits its public key to the client, which is stored in a designated variable. Subsequently, the client responds by sending its own public key back to the server, where it is securely stored for further communication.

### 2. Client Application
- Connects to the bug server and sends encrypted commands.
- The bug server decrypts these commands and forwards them to the legacy application.
- Upon receiving the response, the bug server encrypts it and sends it back to the client.
- The client decrypts the response.

### 3. Bug Server
- Listens for incoming connections on a specific port.
- Decrypts data and forwards it as plain text to the legacy application.
- Encrypts the plain-text response and sends it back to the client.

### 4. Legacy Application
- Listens for plain-text messages from the bug server.
- Processes requests and responds with plain-text data.

---

### Data Flow Overview

```plaintext
[Client] --> (Encrypted Command) --> [Bug Server] --> (Plain Text Command) --> [Legacy Application]
[Client] <-- (Encrypted Response) <-- [Bug Server] <-- (Plain Text Response) <-- [Legacy Application]
```

### Example Commands:
- **`data`**: Requests specific data from the legacy application.
- **`SIH`**: Requests another specific dataset.
- **`RST`**: Closes the connection between the client and bug server.

---

## Installation and Usage

### 1. Dependencies
- **Python 3.x**
- Install the `cryptography` library:
  ```bash
  pip install cryptography
  ```

### 2. How to Run

- **Step 1**: Generate RSA keys:
  ```bash
  python generate_keys.py
  ```
  
- **Step 2**: Start the legacy application:
  ```bash
  python legacy_application.py
  ```

- **Step 3**: Start the bug server:
  ```bash
  python bug.py
  ```

- **Step 4**: Run the client application:
  ```bash
  python client.py
  ```

---

## Debugging

Enable debugging mode for detailed logs of encrypted and decrypted messages. At the start of each script, type `Y` when prompted for debugging mode:

```plaintext
Debugging (Y/N): Y
```

---

## Future Improvements
- **Additional Encryption Support**: Add support for AES and other encryption algorithms.
- **Session Management**: Implement session-based encryption for dynamic key management.
- **Authentication**: Introduce client-server authentication to ensure authorized access.

---

## Contributing

### Steps to Contribute:
1. Fetch the latest changes from the remote:
   ```bash
   git fetch origin
   ```
   
2. Reset your local branch to match the remote:
   ```bash
   git reset --hard origin/master
   ```

3. Clean untracked files and directories:
   ```bash
   git clean -fd
   ```

4. Pull the latest changes:
   ```bash
   git pull origin master
   ```

---

