import subprocess
import os,sys
import shutil

def openvpn():
    print("\n")
    print("[*] Checking if User is Root or Sudo")
    print("\n")
    if not os.geteuid() == 0:
        sys.exit("[!] Must Be Run As Root!")
    else:
        CA_DIR = '/root/certificate_authority'
        wd = os.getcwd()
        subprocess.call("apt-get update && sudo apt-get -y install openvpn easy-rsa ufw", shell=True)
        subprocess.call("make-cadir " + CA_DIR, shell=True)

        #setup vars
        print("\n")
        print("Please enter the following certificate information:")
        print("\n")
        COUNTRY = input("Country: ")
        STATE = input("State/Province: ")
        CITY = input("City: ")
        ORG = input("Org. Name: ")
        EMAIL = input("Email: ")
        OU = input("OU:")
        file1 = open(CA_DIR+"/vars", "a")  # append mode 
        file1.write("\n")
        file1.write("set_var EASYRSA_REQ_COUNTRY    " + COUNTRY + " \n") 
        file1.write("set_var EASYRSA_REQ_PROVINCE    " + STATE + " \n")
        file1.write("set_var EASYRSA_REQ_CITY    " + CITY + " \n")
        file1.write("set_var EASYRSA_REQ_ORG    " + ORG + " \n")
        file1.write("set_var EASYRSA_REQ_EMAIL    " + EMAIL + " \n")
        file1.write("set_var EASYRSA_REQ_OU    " + OU + " \n")
        file1.close() 

        subprocess.call(CA_DIR + "/easyrsa init-pki", shell=True, cwd=CA_DIR)
        subprocess.call(CA_DIR + "/easyrsa build-ca nopass", shell=True, cwd=CA_DIR)
        subprocess.call(CA_DIR + "/easyrsa gen-req server nopass", shell=True, cwd=CA_DIR)
        subprocess.call(CA_DIR + "/easyrsa sign-req server server", shell=True, cwd=CA_DIR)
        subprocess.call(CA_DIR + "/easyrsa gen-dh", shell=True, cwd=CA_DIR)
        subprocess.call(CA_DIR + "/easyrsa gen-crl", shell=True, cwd=CA_DIR)

        subprocess.call("cp " + CA_DIR + "/pki/crl.pem /etc/openvpn", shell=True)
        subprocess.call("cp " + CA_DIR + "/pki/ca.crt /etc/openvpn", shell=True)
        subprocess.call("cp " + CA_DIR + "/pki/issued/server.crt /etc/openvpn", shell=True)
        subprocess.call("cp " + CA_DIR + "/pki/private/server.key /etc/openvpn", shell=True)
        subprocess.call("cp " + CA_DIR + "/pki/dh.pem /etc/openvpn/dh2048.pem", shell=True)

        subprocess.call("openvpn --genkey --secret /etc/openvpn/ta.key", shell=True)

        #copy server conf files 
        subprocess.call("cp configs/server.conf /etc/openvpn/server.conf", shell=True, cwd=wd)
        subprocess.call("cp configs/server1.conf /etc/openvpn/server1.conf", shell=True, cwd=wd)
        subprocess.call("cp /etc/sysctl.conf /etc/sysctl.conf.bak", shell=True)
        subprocess.call("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf", shell=True)
        subprocess.call("sysctl -p", shell=True)

        #ufw configs
        subprocess.call("cp /etc/default/ufw /etc/default/ufw.bak", shell=True)
        subprocess.call("cp /etc/ufw/before.rules /etc/ufw/before.rules.bak", shell=True)
        subprocess.call("sed -i 's/DEFAULT_FORWARD_POLICY=\"DROP\"/DEFAULT_FORWARD_POLICY=\"ACCEPT\"/g' /etc/default/ufw", shell=True)
        
        INTERFACE = input("Enter network interface: ")
        
        file2 = open("/etc/ufw/before.rules", "w")  # append mode
        file2.write("*nat\n")
        file2.write(":POSTROUTING ACCEPT [0:0]\n")
        file2.write("-A POSTROUTING -s 10.8.0.0/8 -o " + INTERFACE + " -j MASQUERADE\n")
        file2.write("-A POSTROUTING -s 10.9.0.0/8 -o " + INTERFACE + " -j MASQUERADE \n")
        file2.write("COMMIT\n\n")
        file2.close()

        subprocess.call("cat /etc/ufw/before.rules.bak >> /etc/ufw/before.rules", shell=True)
        subprocess.call("ufw allow openvpn && ufw allow https", shell=True)
        subprocess.call("ufw disable && ufw enable", shell=True)
        subprocess.call("systemctl restart openvpn@server && systemctl enable openvpn@server", shell=True)
        subprocess.call("systemctl restart openvpn@server1 && systemctl enable openvpn@server1", shell=True)
        subprocess.call("mkdir /root/client-configs && mkdir /root/client-configs/keys && mkdir /root/client-configs/files", shell=True)
        subprocess.call("cp configs/base.conf /root/client-configs/base.conf", shell=True, cwd=wd)
        subprocess.call("cp " + CA_DIR + "/pki/ca.crt /root/client-configs/keys/", shell=True)
        subprocess.call("cp /etc/openvpn/ta.key /root/client-configs/keys/", shell=True)

        VPNSERV = input("FQDN of this server: ")
        subprocess.call("sed -i \"s/JUMPSERVER/" + VPNSERV + "/g\" /root/client-configs/base.conf", shell=True)
        print("\nSetup Complete\n")
        print("Use scripts/add-openvpn-client.sh and scripts/revoke-openvpn-client.sh to create and revoke client certificates and configurations.")
