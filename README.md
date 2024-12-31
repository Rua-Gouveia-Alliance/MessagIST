# A61 MessagIST Project Read Me

## Team

| Number  | Name              | User                              | E-mail                                          |
| --------|-------------------|-----------------------------------| ------------------------------------------------|
| 102611  | João Gouveia      | <https://github.com/joaotgouveia> | <mailto:joao.talone.gouveia@tecnico.ulisboa.pt> |
| 102606  | Rodrigo Arêde     | <https://github.com/rodasarede>   | <mailto:rodrigo.arede@tecnico.ulisboa.pt>       |
| 102604  | Gonçalo Rua       | <https://github.com/goncrust>     | <mailto:goncalonrua@tecnico.ulisboa.pt>         |


![João Gouveia](img/joao.png) ![Rodrigo Arêde](img/arede.png) ![Gonçalo Rua](img/goncalo.png)

*(add face photos with 150px height; faces should have similar size and framing)*

## Contents

This repository contains documentation and source code for the *Network and Computer Security (SIRS)* project.

The [REPORT](REPORT.md) document provides a detailed overview of the key technical decisions and various components of the implemented project.
It offers insights into the rationale behind these choices, the project's architecture, and the impact of these decisions on the overall functionality and performance of the system.

This document presents installation and demonstration instructions.

## Installation

To see the project in action, it is necessary to setup a virtual environment, with 2 networks and 5 machines.

The following diagram shows the networks and machines:

![diagram](img/diagram.png)

The `NAT Firewall 1` server connects to the internet with an IP address obtained via DHCP.

### Prerequisites

All the virtual machines are based on: `Ubuntu Server 24.04.1 LTS`.

[Download](https://ubuntu.com/download/server) and [install](https://ubuntu.com/tutorials/install-ubuntu-server#4-choose-your-language) a virtual machine of `Ubuntu Server 24.04.1 LTS`.

**Notes for the installation**:
- The steps not specifically specified were left as default.
- In the step **Choose the type of installation**, choose the `Ubuntu Server` option (not `Ubuntu Server (minimized)`).
- In the step **Profile configuration**, we used the following configuration (choose another values as you which, keep in mind the rest of the guide uses these ones where needed):
  - **Your name**: (blank)
  - **Server's name**: ubuntuserver
  - **Userame**: serveradmin
  - **Password**: (choose a password)

Clone the base machine to create four other machines and set up the networks according to the diagram above.

### Machine configurations

For each machine, there is an initialization script with the machine name, with prefix `init-` and suffix `.sh`, that installs all the necessary packages and makes all required configurations in the a clean machine.

Inside each machine, use Git to obtain a copy of all the scripts and code.

```sh
$ git clone https://github.com/tecnico-sec/A61
```

Next we have custom instructions for each machine.

#### Machine 1 (NAT Firewall 1)

This machine runs the NAT firewall for the DMZ.

**First, run the initialization script:**

```sh
$ sudo ./config_scripts/init-natfirewall1.sh
```

**To verify:**

```sh
$ sudo systemctl status init-natfirewall1
```

Ensure the service is active. If not, enable and start it:

```sh
$ sudo systemctl enable init-natfirewall1
$ sudo systemctl start init-natfirewall1
```

**To test:**

```sh
$ test command
```

*(replace with actual commands)*

The expected results are ...

*(explain what is supposed to happen if all goes well)*

If you receive the following message ... then ...

*(explain how to fix some known problem)*

#### Machine 2 (DMZ Server)

This machine runs the gRPC service to handle external requests to the MessagIST server.

**First, run the initialization script:**

```sh
$ sudo ./config_scripts/init-dmzserver.sh
```

**To verify:**

```sh
$ sudo systemctl status init-dmzserver
```

Ensure the service is active. If not, enable and start it:

```sh
$ sudo systemctl enable init-dmzserver
$ sudo systemctl start init-dmzserver
```

**To test:**

```sh
$ test command
```

*(replace with actual commands)*

The expected results are ...

*(explain what is supposed to happen if all goes well)*

If you receive the following message ... then ...

*(explain how to fix some known problem)*

#### Machine 3 (NAT Firewall 2)

This machine runs the NAT firewall for the internal network.

**First, run the initialization script:**

```sh
$ sudo ./config_scripts/init-natfirewall2.sh
```

**To verify:**

```sh
$ sudo systemctl status init-natfirewall2
```

Ensure the service is active. If not, enable and start it:

```sh
$ sudo systemctl enable init-natfirewall2
$ sudo systemctl start init-natfirewall2
```

**To test:**

```sh
$ test command
```

*(replace with actual commands)*

The expected results are ...

*(explain what is supposed to happen if all goes well)*

If you receive the following message ... then ...

*(explain how to fix some known problem)*

#### Machine 4 (MessagIST Server)

This machine runs the main server of the application.
It runs a gRPC service for handling requests from the DMZ server and communicates with the PostgreSQL database.

**First, run the initialization script:**

```sh
$ sudo ./config_scripts/init-messagistserver.sh
```

**To verify:**

```sh
$ sudo systemctl status init-messagistserver
```

Ensure the service is active. If not, enable and start it:

```sh
$ sudo systemctl enable init-messagistserver
$ sudo systemctl start init-messagistserver
```

**To test:**

```sh
$ test command
```

*(replace with actual commands)*

The expected results are ...

*(explain what is supposed to happen if all goes well)*

If you receive the following message ... then ...

*(explain how to fix some known problem)*

#### Machine 5

This machine runs the PostgreSQL database (version).

**First, run the initialization script:**

```sh
$ sudo ./config_scripts/init-messagistserver.sh
```

**To verify:**

```sh
$ sudo systemctl status init-messagistserver
```

Ensure the service is active. If not, enable and start it:

```sh
$ sudo systemctl enable init-messagistserver
$ sudo systemctl start init-messagistserver
```

**To test:**

```sh
$ test command
```

*(replace with actual commands)*

The expected results are ...

*(explain what is supposed to happen if all goes well)*

If you receive the following message ... then ...

*(explain how to fix some known problem)*

## Demonstration

Now that all the networks and machines are up and running, ...

*(give a tour of the best features of the application; add screenshots when relevant)*

```sh
$ demo command
```

*(replace with actual commands)*

*(IMPORTANT: show evidence of the security mechanisms in action; show message payloads, print relevant messages, perform simulated attacks to show the defenses in action, etc.)*

This concludes the demonstration.

## Additional Information

### Links to Used Tools and Libraries

- [Java 11.0.16.1](https://openjdk.java.net/)
- [Maven 3.9.5](https://maven.apache.org/)
- ...

### Versioning

We use [SemVer](http://semver.org/) for versioning.  

### License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) for details.

*(switch to another license, or no license, as you see fit)*

----
END OF README
