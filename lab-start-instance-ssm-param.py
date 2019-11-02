# Funcion Lambda to manage that flags the initial of a process and then, when finished, will stop EC2 instances

import boto3

# Declaration of boto3 clients to be used
ssm = boto3.client('ssm')
ec2 = boto3.client('ec2')


def setFlag(activate):

    ssmParam = ssm.describe_parameters(
        Filters=[
            {
                'Key': 'Name',
                'Values': [
                    'finishProcess',
                ]
            },
        ],
        MaxResults=5,
    )

    # set desired value
    value = "yes" if activate else "no"
    
    if len(ssmParam['Parameters']) > 0:
        
        # get current value
        ssmValue = ssm.get_parameter(
            Name='finishProcess',
            WithDecryption=False
        )
        
        
        # if value is different to the one already set, then update
        if ssmValue['Parameter']['Value'] == value:
            print('Do nothing, value already set')
        else:
            ssm.put_parameter(
                Name='finishProcess',
                Description='flag param to identify when we must stop the EC2 instances',
                Value=value,
                Type='String',
                Overwrite=True,
                Tier='Standard'
            )

            print("SSM Param set to --> " + value)
            
    else:
        
        ssm.put_parameter(
            Name='finishProcess',
            Description='flag param to identify when we must stop the EC2 instances',
            Value=value,
            Type='String',
            Overwrite=True,
            Tier='Standard'
        )


def lambda_handler(event, context):


    if event['status'] == 'running':
        setFlag(False)
    else: 
        setFlag(True)


    #Get all SSM Param value
    ssmValue = ssm.get_parameter(
                Name='finishProcess',
                WithDecryption=False
            )
    
    if ssmValue['Parameter']['Value'] == 'yes':    
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Flag', 'Values': ['manage']}])
        
        for instance in instances['Reservations']:
            for instanceId in instance['Instances']:
                    
                    print('Instance to stop', instanceId['InstanceId'])

                    ec2.stop_instances(InstanceIds=[instanceId['InstanceId']])
                    
                    print('Stopping instances with tag:Flag = manage...')
                    print('........................')
