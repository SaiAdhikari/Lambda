import boto3
import os
import time

ecs = boto3.client('ecs')

def get_all_services(cluster):
    """
    Get all the services in the specified cluster using pagination.
    """
    services = []
    next_token = None

    while True:
        if next_token:
            response = ecs.list_services(cluster=cluster, nextToken=next_token)
        else:
            response = ecs.list_services(cluster=cluster)

        services.extend([arn.split("/")[-1] for arn in response['serviceArns']])

        next_token = response.get('nextToken')
        if not next_token:
            break

    return services

def lambda_handler(event, context):
    # Read the cluster.txt file from the Lambda function's filesystem
    with open('/var/task/clusters.txt', 'r') as f:
        clusters = f.read().splitlines()

    for i, cluster in enumerate(clusters, start=1):
        print(f"Processing cluster {i}: {cluster}")
        
        # Set the environment variable for the current cluster
        os.environ['CLUSTER_NAME'] = cluster
        
        # Set the services file to use based on the current cluster
        services_file = f'/var/task/services{i}.txt'
        if not os.path.isfile(services_file):
            print(f"Services file '{services_file}' not found, skipping...")
            continue

        desired_count = os.environ.get('DESIRED_COUNT')
        if not desired_count:
            desired_count = int(event['desired_count'])
        else:
            desired_count = int(desired_count)

        # Read the services.txt file from the Lambda function's filesystem
        service_names = []
        with open(services_file, 'r') as f:
            service_names = f.read().splitlines()

        # Get the list of services in the cluster
        service_list = get_all_services(cluster)

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
