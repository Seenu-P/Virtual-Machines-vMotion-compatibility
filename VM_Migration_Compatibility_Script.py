#!/usr/bin/env python

# Code by: Seenu Perumal
# Contact: seenu.perumal@dell.com
# Date: 2023-08-31
# Description: This script helps to check Each Virtual Machines vMotion compatibility running on vCenter.  Feel free to use and share if you have any feedback.

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
import getpass
from urllib.parse import unquote
import sys

# ANSI color escape codes
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
#This Function checks the Virtual Machines vMotion comptability. 
def check_vm_vmotion_compatibility(content, vm, esxi_hosts):
    vmotion_checker = content.vmProvisioningChecker
    tasks = []
    esxi_host = []
    for esxi_host in esxi_hosts:
        task = vmotion_checker.QueryVMotionCompatibilityEx_Task([vm], [esxi_host])
        tasks.append(task)
    results = []

    for task in tasks:
        task_result = task.info.result
        results.append(task_result)
    return results
#This Function collect the ESXi hosts running in the cluster.
def get_esxi_hosts_in_clusters(content):
        hosts = list()
        host = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True)
        hosts = list(host.view)
        return hosts
#This Function collect the Virtual Machines running in the cluster.
def get_vms_in_clusters(content):
        vm_list = list()
        vms = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True)
        vm_list = list(vms.view)
        return vm_list

#This Function takes care of VC communication and other related function calls. And at the end prints the collected result.
def vmotion_compatible():
    # vCenter Server credentials
    def get_valid_input(prompt, is_password=False):
        while True:
            if is_password:
                user_input = getpass.getpass(prompt)
            else:
                user_input = input(prompt).strip()

            if user_input:
                return user_input
            else:
                print("Invalid input. Please provide a valid value.")
       
    while True:
        vcenter_host = get_valid_input("Provide the vCenter FQDN/IP: ")
        vcenter_user = get_valid_input("Provide the username: ")
        vcenter_password = get_valid_input("Provide the credential: ", is_password=True)
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers("DEFAULT@SECLEVEL=1")
            si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
            print("Connected to vCenter Server successfully! Kindly wait for the checks to complete....")
            # You can perform further actions using 'si' here
            break  # Break out of the loop since connection succeeded
            
            
        except Exception as e:
            print("Connection to vCenter Server failed. Please check your credentials or vCenter system availability and try again.")
            retry = input("Do you want to retry? (yes/no): ")
            if retry.lower() != "yes":
                print("Exiting...")
                exit()  # Exit the script if user doesn't want to retry

    # Get the ServiceInstance's content property
    content = si.RetrieveContent()
    ESXi_hosts_list = get_esxi_hosts_in_clusters(content)
    VM_list = get_vms_in_clusters(content)
    
    for vms in VM_list: 
        results = check_vm_vmotion_compatibility(content, vms, ESXi_hosts_list)
        for result_list in results:
            for result in result_list:
                vm_name = result.vm.name
                host_name = result.host.name
                if result.error:
                     print(f" {Green}VMotion compatibility result for VM {Blue}'{vm_name}' {Green}on host {Blue}'{host_name}'{Green}: {RESET}")
                     # Check for errors, warnings and print respective messages
                     for error in result.error:
                        if hasattr(error, 'msg'):
                            #print(f"  Error: {error.msg}")
                            error_message = f" {RED}Error: {RESET}" + error.msg
                            print(error_message)
                     for warning in result.warning:
                        if hasattr(warning, 'msg'):
                            warning_message = f" {YELLOW}Warning: {RESET}" + warning.msg
                            print(warning_message)
                
    Disconnect(si) # Disconnect from vCenter Server

# Call this vmotion_compat() function to check Each Virtual Machines vMotion compatibility
# Start program
if __name__ == "__main__":
    vmotion_compatible()   
    


 


        




