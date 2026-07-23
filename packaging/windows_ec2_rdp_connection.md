# Windows EC2 RDP Connection

User: 
Hi! How are you doing, AI Assistant? I spun up an EC2 m5large instance with Windows Server 2025. I need to connect to it from my Ubuntu machine.

Assistant: 

Hi! I’m doing well — happy to help.

To connect from Ubuntu to a **Windows Server 2025 EC2 instance**, you’ll usually use **RDP**.

## 1. Make sure RDP is allowed in AWS

In the EC2 console:

1. Go to **EC2 → Instances**
2. Select your Windows instance
3. Open its **Security group**
4. Add an inbound rule:

| Type | Protocol | Port | Source                                |
|------|---------:|-----:|---------------------------------------|
| RDP  |      TCP | 3389 | Your Ubuntu machine’s public IP `/32` |

For example:

```text
203.0.113.25/32
```

Avoid using `0.0.0.0/0` unless it’s temporary for testing.

## 2. Get the Windows administrator password

In AWS:

1. Select the EC2 instance
2. Choose **Actions → Security → Get Windows password**
3. Upload or paste the private key file you used when launching the instance
4. Decrypt the password

Username is usually:

```text
Administrator
```

## 3. Install an RDP client on Ubuntu

A good option is **Remmina**:

```bash
sudo apt update
sudo apt install remmina remmina-plugin-rdp
```

Alternatively, use FreeRDP:

```bash
sudo apt update
sudo apt install freerdp2-x11
```

## 4. Connect using Remmina

Open Remmina and create a new connection:

- **Protocol**: RDP
- **Server**: your EC2 public IPv4 address or public DNS name
- **Username**: `Administrator`
- **Password**: decrypted Windows password
- **Domain**: leave blank

Then connect.

## 5. Or connect from terminal with FreeRDP

```bash
xfreerdp /v:YOUR_EC2_PUBLIC_IP /u:Administrator /p:'YOUR_PASSWORD'
```

Example:

```bash
xfreerdp /v:18.222.10.123 /u:Administrator /p:'SuperSecretPassword'
```

If you get certificate warnings, you can add:

```bash
xfreerdp /v:YOUR_EC2_PUBLIC_IP /u:Administrator /p:'YOUR_PASSWORD' /cert:ignore
```

## Common issues

- **Connection timeout**: security group or network ACL likely blocks TCP `3389`.
- **Authentication failed**: wrong decrypted password, wrong key pair, or username.
- **No public IP**: instance may be in a private subnet; you’ll need a VPN, bastion host, or AWS Systems Manager Session Manager setup.
- **Instance not ready**: Windows initialization can take several minutes after first launch.

If you tell me whether your EC2 instance has a **public IPv4 address** and whether you already decrypted the Administrator password, I can guide you through the exact next step.