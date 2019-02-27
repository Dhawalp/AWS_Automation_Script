import boto3

## Initialing - Checking for any running instances or RDS
global ec2, rds, elb, atc
ec2 = boto3.client('ec2')
rds = boto3.client('rds')

response = ec2.describe_subnets()
MySubnets = response['Subnets']

## Checking any Running instances
responseInst = ec2.describe_instances(Filters=[{'Name':'instance-state-name', 'Values': ['running']}])
if responseInst['Reservations'] == []:
    print('No Instances are running')
    response = ec2.describe_images(Filters=[{'Name': 'name', 'Values': ['Project2Image2']}])
    MyImageId = response['Images'][0]['ImageId']
else:
    print('There are one or more Instances running in AWS')
    for instance in ec2.instances.all():
      ID.append(instance.id)
     ec2.stop_instances(InstanceIds=ID)
    print('Stopping Instances')


responseDB = rds.describe_db_instances(DBInstanceIdentifier='bookdb')
if responseDB['DBInstances'][0]['DBInstanceStatus'] != 'available':
    print('No DB Instances are Running')
    rds.start_db_instance(DBInstanceIdentifier='bookdb')
    while(True):
        if responseDB['DBInstances'][0]['DBInstanceStatus'] == 'available':
            break
    print('Rds is up and Running')
    response = rds.describe_db_instances(DBInstanceIdentifier='bookdb')
    MyRdsAddress = response['DBInstances'][0]['Endpoint']['Address']

elb = boto3.client('elbv2')
response = elb.create_target_group(Name='MyTGBookApp', Protocol='HTTP', Port=80, VpcId=MySubnets[0]['VpcId'], TargetType='instance')
MyTG = response['TargetGroups'][0]

response = elb.create_load_balancer(Name='MyLBBookApp', Subnets=[MySubnets[0]['SubnetId'], MySubnets[1]['SubnetId'], MySubnets[2]['SubnetId'], MySubnets[4]['SubnetId'], MySubnets[5]['SubnetId']], SecurityGroups=['sg-012371e40d5caa8fd'],)
MyLB = response['LoadBalancers'][0]
response = elb.create_listener(LoadBalancerArn=MyLB['LoadBalancerArn'], Protocol='HTTP', Port=80,
DefaultActions=[{'Type': 'forward', 'TargetGroupArn': MyTG['TargetGroupArn']}])

atc = boto3.client('autoscaling')
response = atc.create_launch_configuration(LaunchConfigurationName='MyLCBookApp', ImageId=MyImageId, InstanceType='t2.micro', KeyName='Project2', SecurityGroups=['sg-012371e40d5caa8fd'])
response = atc.create_auto_scaling_group(AutoScalingGroupName='MyASGBookApp', LaunchConfigurationName='MyLCBookApp', MinSize= 1,MaxSize= 2,DesiredCapacity= 1,AvailabilityZones= ['us-east-1c'],VPCZoneIdentifier = 'subnet-806e39ca',TargetGroupARNs=[MyTG['TargetGroupArn']])




response = elb.register_targets(TargetGroupArn=MyTG['TargetGroupArn'], Targets=[{'Id': 'i-03520d51222947d67'}])
response = atc.attach_load_balancer_target_groups(AutoScalingGroupName='MyASGBookApp',TargetGroupARNs=[MyTG['TargetGroupArn']],)
RLabel = MyLB['LoadBalancerArn'].split('/', 1)[1] +'/targetgroup/' + MyTG['TargetGroupArn'].split('/', 1)[1]
response = atc.put_scaling_policy(AutoScalingGroupName='MyASGBookApp', PolicyName='test', PolicyType = 'TargetTrackingScaling', TargetTrackingConfiguration={'PredefinedMetricSpecification': { 'PredefinedMetricType':'ALBRequestCountPerTarget','ResourceLabel': 'RLabel'},'TargetValue' : 2,})


