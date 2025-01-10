# Copyright 2018-2024 MarkLogic Corporation.  All Rights Reserved.

import boto3
import logging
import hashlib

log = logging.getLogger()
log.setLevel(logging.INFO)

# global variables
ec2_client = boto3.client('ec2')

def get_physical_resource_id(request_id):
    return hashlib.md5(request_id.encode()).hexdigest()

def get_network_interface_by_id(eni_id):
    """
    Use describe network interfaces function instead of ec2_resource.NetworkInterface
    :param eni_id:
    :return:
    """
    response = ec2_client.describe_network_interfaces(
        Filters=[{
            "Name": "network-interface-id",
            "Values": [eni_id]
        }]
    )
    if len(response["NetworkInterfaces"]) == 1:
        return response["NetworkInterfaces"][0]
    else:
        log.error("Get network interface by id %s failed: %s" % (eni_id, str(response)))

def cfn_success_response(event, reuse_physical_id=False, data=None):
    return {
        "Status": "SUCCESS",
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "StackId": event["StackId"],
        "PhysicalResourceId":
            event["PhysicalResourceId"]
            if reuse_physical_id
            else get_physical_resource_id(event["RequestId"]),
        "Data": {} if not data else data
    }

def cfn_failure_response(event, reason, data=None):
    return {
        "Status": "FAILED",
        "Reason": reason,
        "LogicalResourceId": event["LogicalResourceId"],
        "StackId": event["StackId"],
        "PhysicalResourceId": get_physical_resource_id(event["RequestId"]),
        "Data": {} if not data else data
    }