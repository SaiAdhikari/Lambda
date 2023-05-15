import boto3
import os
import time

ecs = boto3.client('ecs')

def lambda_handler(event, context):
    cluster = os.environ['CLUSTER_NAME']

    desired_count = os.environ.get('DESIRED_COUNT')
    if not desired_count:
        desired_count = int(event['desired_count'])
    else:
        desired_count = int(desired_count)

    # Read the services.txt file from the Lambda function's filesystem
    service_names = []
    with open('/var/task/services.txt', 'r') as f:
        service_names = f.read().splitlines()

    # Get the list of services in the cluster
    response = ecs.list_services(cluster=cluster)
    service_list = [arn.split("/")[-1] for arn in response['serviceArns']]

    for service_name in service_names:
        if service_name not in service_list:
            print(f"{service_name} is not present in the cluster, skipping...")
            continue
        response = ecs.update_service(cluster=cluster, service=service_name, desiredCount=desired_count)
        print(f"{service_name} desired count is set to {desired_count}")
        time.sleep(5)
    
    return {
        'statusCode': 200,
        'body': 'All services updated successfully!'
    }
