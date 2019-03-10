# Face Detector
## Server Environment Setup
instructions on creating the environment:

Use Centos 7 and do:

yum -y update
yum -y install epel-release
yum -y group install "Development Tools"
yum -y install openssl-devel
yum -y install libXext libSM libXrender
yum -y install cmake
yum -y install python-devel
yum -y install python-pip
yum -y install gcc

install virtualenv as root:
sudo pip install virtualenv

From a Python 2 environment, install PIP requirements from the requirements.txt file.

Start the server using this command:
`uwsgi --http :8080 --gevent 1000 --http-websockets --master --wsgi-file server.py --callable app`