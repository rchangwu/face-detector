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
sudo pip install --upgrade pip setuptools wheel  
sudo pip install virtualenv

git clone project  
inside project directory, create python 2 env: virtualenv p2env  
switch to the p2env: source p2env/bin/activate  

install PIP requirements from the requirements.txt file:  
pip install -r requirements.txt

Start the server using this command:  
`uwsgi --http :8080 --gevent 1000 --http-websockets --master --wsgi-file server.py --callable app`
