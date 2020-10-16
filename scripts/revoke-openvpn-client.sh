#!/bin/bash

# First argument: Client identifier
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit
fi

CA_DIR=~/certificate_authority

cd ${CA_DIR}

${CA_DIR}/easyrsa revoke ${1}
${CA_DIR}/easyrsa gen-crl

cp ${CA_DIR}/pki/crl.pem /etc/openvpn

systemctl restart openvpn@server && systemctl restart openvpn@server1
