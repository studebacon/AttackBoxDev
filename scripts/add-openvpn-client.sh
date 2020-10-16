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
KEY_DIR=~/client-configs/keys
OUTPUT_DIR=~/client-configs/files
BASE_CONFIG=~/client-configs/base.conf

cd ${CA_DIR}

${CA_DIR}/easyrsa gen-req ${1} nopass

cp ${CA_DIR}/pki/private/${1}.key ${KEY_DIR}

${CA_DIR}/easyrsa sign-req client ${1}

cp ${CA_DIR}/pki/issued/${1}.crt ${KEY_DIR}

cat ${BASE_CONFIG} \
    <(echo -e '<ca>') \
    ${KEY_DIR}/ca.crt \
    <(echo -e '</ca>\n<cert>') \
    ${KEY_DIR}/${1}.crt \
    <(echo -e '</cert>\n<key>') \
    ${KEY_DIR}/${1}.key \
    <(echo -e '</key>\n<tls-auth>') \
    ${KEY_DIR}/ta.key \
    <(echo -e '</tls-auth>') \
    > ${OUTPUT_DIR}/${1}.ovpn

echo "Done. Copy ${OUTPUT_DIR}/${1}.ovpn to client device."

